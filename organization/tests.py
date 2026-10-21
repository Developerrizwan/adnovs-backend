from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from organization.models import AccountDetails, Coa, CoaGroup, Company, Organization, Vouchers
from organization.views import (
    get_sundry_creditors_coa_response,
    get_sundry_debtors_coa_response,
    get_supplier_side_org_ids,
)


class SupplierSideOrganizationLedgerTests(TestCase):
    """Receipt/CreditNote/Journal lines on supplier-side organizations must be
    shown in Sundry Creditors, every other organization line in Sundry Debtors."""

    START = '2024-01-01'
    END = datetime(2024, 12, 31, 23, 59, 59)

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='ledger', email='ledger@test.local', password='x')
        cls.company = Company.objects.create(name='TEST CO', email='co@test.local', country='SA', state='', address='')
        cls.company.users.add(cls.user)
        group = CoaGroup.objects.create(name='Current Assets')
        cls.debtors = Coa.objects.create(code='1028', name='SUNDRY DEBTORS', dr_cr='Dr', group=group, company=cls.company)
        cls.creditors = Coa.objects.create(code='2002', name='SUNDRY CREDITORS', dr_cr='Cr', group=group, company=cls.company)
        cls.bank = Coa.objects.create(code='1001', name='BANK', dr_cr='Dr', group=group, company=cls.company)

        cls.supplier_only = Organization.objects.create(name='SUPPLIER ONLY', type=['Supplier'], company=cls.company, coa=cls.creditors)
        cls.agent_broker_client = Organization.objects.create(
            name='AGENT BROKER CLIENT', type=['Agents', 'Broker', 'Client'], company=cls.company, coa=cls.creditors)
        cls.counterpart_on_1028 = Organization.objects.create(
            name='COUNTERPART ON 1028', type=['Counterpart'], company=cls.company, coa=cls.debtors)
        cls.plain_client = Organization.objects.create(name='PLAIN CLIENT', type=['Client'], company=cls.company, coa=cls.debtors)

    def _voucher(self, voucher_type, number, org, org_dr_cr, amount):
        voucher = Vouchers.objects.create(
            voucher_number=number, voucher_type=voucher_type, company=self.company,
            date=timezone.make_aware(datetime(2024, 6, 15, 10, 0, 0)), amount_sar=str(amount),
            party_account=str(org.id), party_account_type='organization')
        AccountDetails.objects.create(vouchers=voucher, ac_name=str(org.id), ac_name_type='organization',
                                      dr_cr=org_dr_cr, amount_sar=str(amount), currency='SAR')
        AccountDetails.objects.create(vouchers=voucher, ac_name=str(self.bank.id), ac_name_type='coa',
                                      dr_cr='Dr' if org_dr_cr == 'Cr' else 'Cr', amount_sar=str(amount), currency='SAR')
        return voucher

    def _debtors(self):
        return get_sundry_debtors_coa_response(self.debtors, self.START, self.END, self.user)

    def _creditors(self):
        return get_sundry_creditors_coa_response(self.creditors, self.START, self.END, self.user)

    @staticmethod
    def _rows_for(rows, voucher_number):
        return [r for r in rows if r['voucher'] == voucher_number]

    def test_helper_classifies_organizations(self):
        ids = get_supplier_side_org_ids(self.company)
        self.assertIn(str(self.supplier_only.id), ids)
        self.assertIn(str(self.counterpart_on_1028.id), ids)
        self.assertNotIn(str(self.agent_broker_client.id), ids)
        self.assertNotIn(str(self.plain_client.id), ids)

    def test_supplier_only_org_receipt_goes_to_creditors(self):
        self._voucher('Receipt', 'RV1', self.supplier_only, 'Cr', 250)
        self.assertEqual(self._rows_for(self._debtors(), 'RV1'), [])
        rows = self._rows_for(self._creditors(), 'RV1')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['account'], 'SUPPLIER ONLY')
        self.assertEqual(rows[0]['cr_amount'], 250.0)
        self.assertEqual(rows[0]['dr_amount'], 0)

    def test_supplier_journal_goes_to_creditors_with_sign(self):
        self._voucher('Journal', 'JV1', self.supplier_only, 'Cr', 9776)
        self._voucher('Journal', 'JV2', self.supplier_only, 'Dr', 1.10)
        debtors = self._debtors()
        self.assertEqual(self._rows_for(debtors, 'JV1') + self._rows_for(debtors, 'JV2'), [])
        creditors = self._creditors()
        self.assertEqual(self._rows_for(creditors, 'JV1')[0]['cr_amount'], 9776.0)
        self.assertEqual(self._rows_for(creditors, 'JV2')[0]['dr_amount'], 1.10)
        # Cr increases the payable, Dr reduces it: running balance is Cr - Dr
        self.assertAlmostEqual(creditors[-1]['net_amount'], 9776 - 1.10, places=2)

    def test_agents_broker_client_org_receipt_stays_in_debtors(self):
        self._voucher('Receipt', 'RV2', self.agent_broker_client, 'Cr', 20629)
        rows = self._rows_for(self._debtors(), 'RV2')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['account'], 'AGENT BROKER CLIENT')
        self.assertEqual(rows[0]['cr_amount'], 20629.0)
        self.assertEqual(self._rows_for(self._creditors(), 'RV2'), [])

    def test_counterpart_only_org_on_1028_goes_to_creditors(self):
        self._voucher('Receipt', 'RV3', self.counterpart_on_1028, 'Cr', 500)
        self.assertEqual(self._rows_for(self._debtors(), 'RV3'), [])
        rows = self._rows_for(self._creditors(), 'RV3')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['cr_amount'], 500.0)

    def test_plain_client_receipt_stays_in_debtors(self):
        self._voucher('Receipt', 'RV4', self.plain_client, 'Cr', 100)
        self.assertEqual(len(self._rows_for(self._debtors(), 'RV4')), 1)
        self.assertEqual(self._rows_for(self._creditors(), 'RV4'), [])


class AccountsReceivableJournalTests(SupplierSideOrganizationLedgerTests):
    """Journal vouchers whose party account is a client hit the receivable report:
    Dr lines increase the balance, Cr lines reduce it."""

    def _receivable(self, organization):
        from rest_framework.test import APIRequestFactory, force_authenticate
        from organization.views import AccountsReceivableViewSet
        request = APIRequestFactory().get('/api/account/receivable/', {
            'organization': organization, 'start_date': '2024-01-01', 'end_date': '2024-12-31'})
        force_authenticate(request, user=self.user)
        return AccountsReceivableViewSet.as_view({'get': 'list'})(request).data

    def test_client_journal_in_detail_and_summary(self):
        self._voucher('Journal', 'JV10', self.plain_client, 'Dr', 300)
        self._voucher('Journal', 'JV11', self.plain_client, 'Cr', 50)

        detail = self._receivable(str(self.plain_client.id))
        journals = {r['voucher_no']: r for r in detail['rows'] if r.get('type') == 'Journal'}
        self.assertEqual((journals['JV10']['debit'], journals['JV10']['credit']), (300.0, 0.0))
        self.assertEqual((journals['JV11']['debit'], journals['JV11']['credit']), (0.0, 50.0))
        self.assertEqual(detail['closing_balance'], 250.0)

        summary = [r for r in self._receivable('all')['rows'] if r['customer_name'] == 'PLAIN CLIENT'][0]
        self.assertEqual((summary['inv_amount'], summary['received_amount'], summary['balance']), (300.0, 50.0, 250.0))

    def test_non_client_journal_excluded(self):
        self._voucher('Journal', 'JV12', self.supplier_only, 'Dr', 300)
        detail = self._receivable(str(self.supplier_only.id))
        self.assertEqual([r for r in detail['rows'] if r.get('type') == 'Journal'], [])
