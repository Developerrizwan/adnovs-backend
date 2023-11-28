from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
# from config.storage_backends import PrivateMediaStorage
# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    state = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    users = models.ManyToManyField(get_user_model(), blank=True)
    language_address = models.CharField(max_length=500, blank=True, null=True)
    language_name = models.CharField(max_length=500, blank=True, null=True)
    vat_number = models.CharField(max_length=200, blank=True, null=True)
    vat = models.CharField(max_length=200,blank=True,null=True)
    account_name=models.CharField(max_length=200,blank=True,null=True)
    bank_name=models.CharField(max_length=200,blank=True,null=True)
    account_number=models.CharField(max_length=200,blank=True,null=True)
    iban_code=models.CharField(max_length=200,blank=True,null=True)
    swift_code=models.CharField(max_length=200,blank=True,null=True)
    company_name_lang=models.CharField(max_length=200, blank=True, null=True)
    sinv_count = models.BigIntegerField(default=0)
    pinv_count = models.BigIntegerField(default=0)
    job_count = models.BigIntegerField(default=0)
    enquiry_count = models.BigIntegerField(default=0)


class CoaGroup(models.Model):
    Dr = 'Dr'
    Cr = 'Cr'
    DR_CR_CHOICES = (
        ('Dr', 'Dr'),
        ('Cr', 'Cr'),
    )
    EQUITY = 'EQUITY'
    ASSET = 'ASSET'
    EXPENSE = 'EXPENSE'
    INCOME = 'INCOME'
    LIABILITY = 'LIABILITY'
    TYPE_CHOICES=(
        (EQUITY,'EQUITY'),
        (ASSET,'ASSET'),
        (EXPENSE,'EXPENSE'),
        (INCOME,'INCOME'),
        (LIABILITY,'LIABILITY')
    )
    code = models.CharField(max_length=200,blank=True, null=True)
    name= models.CharField(max_length=200,blank=True, null=True) 
    type = models.CharField(max_length=200,blank=True, null=True,choices=TYPE_CHOICES) 
    dr_cr = models.CharField(max_length=200,blank=True, null=True,choices=DR_CR_CHOICES)
    language_name = models.CharField(max_length=200, blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)


class Coa(models.Model):
    
    BS = 'Balance Sheet'
    PL = 'Profit and Loss'
    
    COA_CHOICES = (    
        ('BS', 'Balance Sheet'),         
        ('PL', 'Profit and Loss'),    
    )
    
    Direct = 'Direct'
    Indirect = 'Indirect'
    
    
    DIRECT_INDIRECT_CHOICES = (
        ('Direct', 'Direct'),
        ('Indirect', 'Indirect'),
    ) 
    
    Dr = 'Dr'
    Cr = 'Cr'
    
    DR_CR_CHOICES = (
        ('Dr', 'Dr'),
        ('Cr', 'Cr'),
    )

    code = models.CharField(max_length=200,blank=True, null=True)
    name = models.CharField(max_length=200,blank=True, null=True) 
    status = models.BooleanField(blank=True, null=True)
    subledger_requried = models.BooleanField(blank=True, null=True)
    charge_required = models.BooleanField(blank=True, null=True)
    job_required = models.BooleanField(blank=True, null=True)
    asset_required = models.BooleanField(blank=True, null=True)
    coa_type = models.CharField(max_length=200,blank=True, null=True)
    is_direct_indirect = models.CharField(max_length=200, blank=True, null=True)
    dr_cr = models.CharField(max_length=200,choices=DR_CR_CHOICES)
    category = models.CharField(max_length=200,blank=True, null=True)
    group = models.ForeignKey(CoaGroup, on_delete=models.CASCADE, blank=False, null=True, related_name='groups')
    subgroup = models.ForeignKey(CoaGroup, on_delete=models.CASCADE, blank=False, null=True, related_name='sub_groups')
    type= models.CharField(max_length=200,blank=True, null=True)
    short_name = models.CharField(max_length=200,blank=True, null=True)
    long_name = models.CharField(max_length=200,blank=True, null=True) 
    language_name = models.CharField(max_length=200,blank=True, null=True)
    currency=models.CharField(max_length=500,blank=True,null=True)
    additional_reference_code=models.CharField(max_length=200,blank=True,null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, null=True)
    remarks=models.TextField(blank=True,null=True)


class Organization(models.Model):
    Consignee = 'Consignee'
    Client = 'Client' 
    Supplier = 'Supplier'
    Shipper = 'Shipper'
    Notify = 'Notify'
    Counterpart = 'Counterpart'
    Broker = 'Broker'
    Agents = 'Agents'
    Others = 'Others'
    
    Type_Choice = (
        (Consignee,'Consignee'),
        (Client,'Client'),
        (Supplier,'Supplier'),
        (Shipper, 'Shipper'),
        (Notify, 'Notify'),
        (Counterpart, 'Counterpart'),
        (Broker, 'Broker'),
        (Agents, 'Agents'),
        (Others, 'Others')
    )
    name = models.CharField(max_length=200,blank=True,null=True)
    type = ArrayField(models.CharField(max_length=255), default=list, blank=False, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, null=False) 
    coa = models.ForeignKey(Coa, on_delete=models.CASCADE, blank=False, null=False) 
    language_name = models.CharField(max_length=200,blank=True,null=True)
    language_address = models.CharField(max_length=500, blank=True, null=True)
    address = models.TextField(blank=True,null=True)   
    vat_trn_number = models.CharField(max_length=200,blank=True,null=True)
    currency = models.CharField(max_length=500, blank=True, null=True)
    branch = models.CharField(max_length=500, blank=True, null=True)
    payment_terms = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=250, blank=True, null=True) 
    zip_code = models.CharField(max_length=250, blank=True, null=True)
    mobile = models.CharField(max_length=250, blank=True, null=True)
    email = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=250, blank=True, null=True)
    state_code = models.CharField(max_length=250, blank=True, null=True) 
    building_name = models.CharField(max_length=250, blank=True, null=True)
    port_name = models.CharField(max_length=250, blank=True, null=True)
    post_box_no = models.CharField(max_length=250, blank=True, null=True)
    gstin_registered = models.BooleanField(default=False)
    gstin = models.CharField(max_length=250, blank=True, null=True)
    # browse_logo = models.FileField(storage=PrivateMediaStorage(), blank=True, null=True)
    website = models.CharField(max_length=200,blank=True,null=True)
    remarks = models.TextField(blank=True,null=True)

class Job(models.Model):

    Enquiry = 'Enquiry'
    Job= 'Job'
    
    JOB_TYPE_CHOICES = (
        (Enquiry, 'Enquiry'),
        (Job, 'Job')
    )

    Cargo_Collected ='Cargo Collected'
    Under_Export_Clearance = 'Under Export Clearance'
    Departed = 'Departed'
    In_Transit = 'In Transit'
    Arrived = 'Arrived'
    Under_Import_Clearance = 'Under Import Clearance'
    Do_Collected = 'Do Collected'
    Gate_Pass_Issued = 'Gate Pass Issued'
    Under_Delivery = 'Under Delivery'
    In_Warehouse_Storage = 'In Warehouse Storage'
    Delivered = 'Delivered'
    Invoiced = 'Invoiced'
    Finished = 'Finished'
    Cancelled = 'Cancelled'
    RFQ = 'RFQ'


    JOB_STATUS_CHOICES = (
        (Cargo_Collected, 'Cargo Collected'),
        (Under_Export_Clearance, 'Under Export Clearance'),
        (Departed, 'Departed'),
        (In_Transit, 'In Transit'),
        (Arrived, 'Arrived'),
        (Under_Import_Clearance, 'Under Import Clearance'),
        (Do_Collected, 'Do Collected'),
        (Gate_Pass_Issued, 'Gate Pass Issued'),
        (Under_Delivery, 'Under Delivery'),
        (In_Warehouse_Storage, 'In Warehouse Storage'),
        (Delivered, 'Delivered'),
        (Invoiced, 'Invoiced'),
        (Finished, 'Finished'),
        (Cancelled, 'Cancelled'),
        (RFQ, 'RFQ')
    )


    D2D ='D2D'
    EXW = 'EXW'
    FOB = 'FOB'
    CIF = 'CIF'
    CNF = 'CNF'
    CANDF = 'C&F'
    DDP = 'DDP'
    DAP = 'DAP'
    CPT = 'CPT'
    TRANS = 'TRANS'
    Delivered = 'Delivered'
    Invoiced = 'Invoiced'
    Finished = 'Finished'
    Cancelled = 'Cancelled'
    DTRANS = "D-TRANS"
    OTHERS = "OTHERS"


    SOCPE_OF_WORK = (
        (D2D, 'D2D'),
        (EXW, 'EXW'),
        (FOB, 'FOB'),
        (CIF, 'CIF'),
        (CNF, 'CNF'),
        (CANDF, 'C&F'),
        (DDP, 'DDP'),
        (DAP, 'DAP'),
        (CPT, 'CPT'),
        (TRANS, 'TRANS'),
        (DTRANS, 'D-TRANS'),
        (OTHERS, 'OTHERS')

    )

    CONTAINER_CHOICES = (
            ('20DC', '20’DC'),
            ('20RF', '20’RF'),
            ('20ST', '20’ST'),
            ('20OT', '20’OT'),
            ('20HC', '20’HC'),
            ('40DC', '40’DC'),
            ('40RF', '40’RF'),
            ('40ST', '40’ST'),
            ('40OT', '40’OT'),
            ('40HC', '40’HC'),
            ('40HQ', '40’HC'),
            ('FLAT_RACK', 'FLAT RACK'),
            ('FTL', 'FTL'),
            ('LTL', 'LTL'),
            ('Pallets','Pallets'),
            ('Boxes','Boxes'),
            ('Cartons','Cartons')
        )
    Air_Freight='Air Freight'
    Sea_Freight = 'Sea Freight'
    Land_Freight = 'Land Freight'
    Transportation = 'Transportation'
    Warehousing = 'Warehousing'
    Customs_Clearance = 'Customs Clearance'
    Other = 'Other' 
    
    FREIGHT_CHOICES = (
        (Air_Freight, 'Air Freight'),
        (Sea_Freight, 'Sea Freight'),
        (Land_Freight, 'Land Freight'),
        (Transportation, 'Transportation'),
        (Warehousing, 'Warehousing'),
        (Customs_Clearance,'Customs Clearance'),
        ( Other, 'Other')
    )

    ORGANIZATION_CHOICES = (
        ('Consignee', 'Consignee'),
        ('Client', 'Client'),
        ('Notify', 'Notify'),
        ('Shipper', 'Shipper'),
        ('Broker', 'Broker'),
        ('Transporter', 'Transporter'),
        ('Counterpart', 'Counterpart'),
        ('Coloader', 'Coloader'),
        ('Supplier', 'Supplier'),
        ('Other', 'Other'),
    )

    bl_number = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField("Job Type", max_length=255, choices=JOB_TYPE_CHOICES)
    job_status = models.CharField("Job Status", max_length=255, choices=JOB_STATUS_CHOICES)
    scope_of_work = models.CharField("Scope of Work ", max_length=255, choices=SOCPE_OF_WORK, blank=True, null=True)
    container_type = models.CharField("Container Type", max_length=10,choices=CONTAINER_CHOICES, blank=True, null=True)
    type = models.CharField("Freight Choice",max_length=20,choices=FREIGHT_CHOICES, blank=True, null=True)
    organization_type = ArrayField(models.CharField(max_length=255), default=list, blank=True, null=True)
    bayan_number = models.CharField(max_length=255, blank=True, null=True)
    pod = models.CharField(max_length=255, blank=True, null=True)
    poa = models.CharField(max_length=255, blank=True, null=True)
    por = models.TextField(blank=True, null=True)
    pol = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    consignee_name = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True, related_name='consignee_name_jobs')
    shipper_name = models.CharField(max_length=255, blank=True, null=True)
    client_name = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True, related_name='client_name_jobs')
    remarks = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, null=False)
    isdeleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE, null=True, blank=False, related_name='deleted_jobs')
    deleted_at = models.DateTimeField(default=timezone.now)
    created_by =  models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=False, related_name='created_jobs')
    created_at = models.DateTimeField(default=timezone.now)
    job_number = models.CharField(max_length=250,blank=True,null=True)
    enquiry_number = models.CharField(max_length=250,blank=True,null=True)
    parties = models.ManyToManyField(Organization, blank=True, null=True)
    eta = models.DateTimeField(blank=True,null=True)
    etd = models.DateTimeField(blank=True,null=True)
    client_ref = models.TextField(blank=True,null=True)
    commodity = models.TextField(blank=True,null=True)
    quantity_text =models.TextField(max_length=250,blank=True,null=True)
    notify = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True, related_name='notify_jobs')
    broker = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True, related_name='broker_jobs')
    transporter = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True, related_name='transporter_jobs')


    
class Invoices(models.Model):

    Sales= 'Sales'
    Purchase= 'Purchase'
    
    INVOICE_TYPE_CHOICES = (
        (Sales, 'Sales'),
        (Purchase, 'Purchase'),
    )

    invoice_number = models.CharField(max_length=255, default='NA')
    bl_number = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    invoice_type = models.CharField("Invoice Type", max_length=255, choices=INVOICE_TYPE_CHOICES, blank=False, null=False)
    consignee_name = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True, related_name="consigneename_Invoice")
    client_name = models.ForeignKey(Organization, on_delete=models.CASCADE, blank=True, null=True, related_name="clientinvoice")
    currency_sar = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=255,default='Unpaid', blank=True, null=True)
    paid_amount = models.CharField(max_length=255, default=0, blank=True, null=True)
    paid_time = models.DateTimeField(default=timezone.now)
    bayan_number = models.CharField(max_length=255, blank=True, null=True)
    shipper_name = models.CharField(max_length=255, blank=True, null=True)
    ex_rate = models.CharField(max_length=255, blank=True, null=True) 
    pod = models.CharField(max_length=255, blank=True, null=True)
    poa = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255,default='JEDDAH', blank=True, null=True)
    fc_amount = models.CharField(max_length=255, blank=True, null=True)
    amount_sar = models.CharField(max_length=255, blank=True, null=True)
    ref_data = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    bill_amount = models.CharField(max_length=255, blank=True, null=True)
    narration = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    coa =models.ForeignKey(Coa, on_delete=models.SET_NULL, blank=True, null=True)
    party_account =models.ForeignKey(Organization,on_delete=models.CASCADE,blank=True,null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, null=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=False, null=False)
    language_address = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_time_generated = models.DateTimeField(default=timezone.now)
    supplier_inv_number = models.CharField(max_length=225, blank=True, null=True)
    
class Vouchers(models.Model):

    Journal = 'Journal'
    Payment= 'Payment'
    Receipt= 'Receipt'
    CreditNote = 'CreditNote'
    DebitNote ='DebitNote'
    
    VOUCHER_TYPE_CHOICES = (
        (Journal, 'Journal'),
        (Payment, 'Payment'),
        (Receipt, 'Receipt'),
        (CreditNote, 'CreditNote'),
        (DebitNote,'DebitNote')
    )
    
    Customer = 'Customer'
    Vendor= 'Vendor'
    
    VOUCHER_FOR_CHOICES = (
        (Customer, 'Customer'),
        (Vendor, 'Vendor'),
    )

    voucher_type = models.CharField("Voucher Type", max_length=255, choices=VOUCHER_TYPE_CHOICES)
    date = models.DateTimeField(default=timezone.now, blank=False, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    book = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    party_state_code = models.CharField(max_length=500, blank=True, null=True)
    period = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=500, blank=True, null=True)
    currency = models.CharField(max_length=500, blank=True, null=True)
    ex_rate = models.CharField(max_length=250, blank=True, null=True)
    pay_to = models.CharField(max_length=500, blank=True, null=True)
    received_from = models.CharField(max_length=500, blank=True, null=True)
    instrument_type = models.CharField(max_length=500, blank=True, null=True)
    gl_date = models.DateTimeField(default=timezone.now, blank=False, null=True)
    start_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    end_date = models.DateTimeField(default=timezone.now, blank=True,null=True)
    fc_amount = models.CharField(max_length=255, blank=True, null=True)
    amount_sar = models.CharField(max_length=255, blank=True, null=True)
    party_account = models.CharField(max_length=255, blank=True, null=True)
    party_account_type = models.CharField(max_length=255, blank=True, null=True)
    division = models.CharField(max_length=255, blank=True, null=True)
    naration = models.CharField(max_length=255, blank=True, null=True)
    outstanding_amount = models.CharField(max_length=255, blank=True, null=True)
    dr_account = models.CharField(max_length=255, blank=True, null=True)
    cr_account = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True)
    ref_no = models.CharField(max_length=255, blank=True, null=True)
    ref_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    voucher_from = models.CharField(max_length=255, blank=True, null=True)
    voucher_from_type = models.CharField(max_length=255, blank=True, null=True)
    voucher_to = models.CharField(max_length=255, blank=True, null=True)
    voucher_to_type = models.CharField(max_length=255, blank=True, null=True)
    voucher_for = models.CharField("Voucher For", max_length=255, choices=VOUCHER_FOR_CHOICES, blank=True, null=True) 
    invoice = models.ForeignKey(Invoices, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True) 


class CoaCategory(models.Model):
    Dr = 'Dr'
    Cr = 'Cr'
    DR_CR_CHOICES = (
        ('Dr', 'Dr'),
        ('Cr', 'Cr'),
    ) 
    
    code = models.CharField(max_length=200,blank=True, null=True)
    name= models.CharField(max_length=200,blank=True, null=True) 
    status = models.BooleanField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True) 
    dr_cr = models.CharField(max_length=200,blank=True, null=True,choices=DR_CR_CHOICES)  
    
    
class Pod(models.Model):
    name = models.CharField(max_length=255,blank=False)
    code = models.CharField(max_length=255,blank=False)
    country=models.CharField(max_length=255,blank=False)

class Poa(models.Model):
    name = models.CharField(max_length=255,blank=False) 
    code = models.CharField(max_length=255,blank=False)
    country=models.CharField(max_length=255,blank=False)

# class Pol(models.Model):
#     name = models.CharField(max_length=255,blank=False) 
#     code = models.CharField(max_length=255,blank=False)
#     country=models.CharField(max_length=255,blank=False)

class Charge(models.Model):

    code=models.CharField(max_length=200,blank=False,null=False)
    name=models.CharField(max_length=200,blank=False,null=False)
    status=models.BooleanField(default=False) 
    iata_code=models.CharField(max_length=255,blank=True,null=True)
    type=models.CharField(max_length=255,blank=True,null=True)
    language_name=models.CharField(max_length=255,blank=True,null=True)
    description=models.TextField(max_length=255,blank=True,null=True)
    remarks=models.TextField(max_length=255,blank=True,null=True)
    coa = models.ForeignKey(Coa, on_delete=models.CASCADE, blank=False, null=True)
    tax = models.IntegerField(blank=True, null=True)

class CostEntry(models.Model):
    Dr = 'Dr'
    Cr = 'Cr'
    DR_CR_CHOICES = (
        (Dr, 'Dr'),
        (Cr, 'Cr'),
    ) 
    Journal = 'Journal'
    Payment= 'Payment'
    Receipt= 'Receipt'
    Credit = 'CREDIT NOTE'
    Debit ='DEBIT NOTE'
    
    VOUCHER_TYPE_CHOICES = (
        (Journal, 'Journal'),
        (Payment, 'Payment'),
        (Receipt, 'Receipt'),
        (Credit, 'CREDIT NOTE'),
        (Debit,'DEBIT NOTE')
    )
    charge=models.ForeignKey(Charge, on_delete=models.CASCADE, blank=False, null=False)
    currency=models.CharField(max_length=200,blank=True,null=True)
    sale_cost=models.CharField(max_length=200,blank=True,null=True)
    description=models.CharField(max_length=200,blank=True,null=True)
    ex_rate=models.CharField(max_length=200,blank=True,null=True)
    dr_cr=models.CharField(max_length=200,blank=True,null=True,choices=DR_CR_CHOICES)
    job_no= models.ForeignKey(Job, on_delete=models.CASCADE, blank=False, null=True)
    invoice = models.ForeignKey(Invoices, on_delete=models.SET_NULL, blank=True, null=True)
    voucher_type = models.CharField("Voucher Type", max_length=255, choices=VOUCHER_TYPE_CHOICES, blank=True, null=True)
    fcy_amount=models.CharField(max_length=200,blank=True,null=True)
    prorate_method=models.CharField(max_length=200,blank=True,null=True)
    shipment_no=models.CharField(max_length=200,blank=True,null=True)
    amount=models.CharField(max_length=200,blank=True,null=True)
    tax_group_code=models.CharField(max_length=200,blank=True,null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_included = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    
class AccountDetails(models.Model):
    Dr = 'Dr'
    Cr = 'Cr'
    DR_CR_CHOICES = (
        (Dr, 'Dr'),
        (Cr, 'Cr'),
    ) 
    line_no = models.CharField(max_length=200,blank=True,null=True)
    ac_name = models.CharField(max_length=255, blank=False, null=True)
    ac_name_type = models.CharField(max_length=200,blank=True,null=True)
    vouchers = models.ForeignKey(Vouchers, on_delete=models.CASCADE, blank=False, null=True)
    dr_cr = models.CharField(max_length=200,blank=True,null=True,choices=DR_CR_CHOICES)
    narration = models.CharField(max_length=200,blank=True,null=True)
    qty = models.CharField(max_length=200,blank=True,null=True)
    currency = models.CharField(max_length=200,blank=True,null=True)
    ex_rate = models.CharField(max_length=200,blank=True,null=True)
    amount_qty = models.CharField(max_length=200,blank=True,null=True)
    fcy_amount= models.CharField(max_length=200,blank=True,null=True)
    amount_sar = models.CharField(max_length=200,blank=True,null=True)
    tax_group_code = models.CharField(max_length=200,blank=True,null=True)
    taxable_amount= models.CharField(max_length=200,blank=True,null=True)
    tax_amount = models.CharField(max_length=200,blank=True,null=True)
    division= models.CharField(max_length=200,blank=True,null=True)
    asset = models.CharField(max_length=200,blank=True,null=True)
    inter_branch = models.CharField(max_length=200,blank=True,null=True)
    sac_code = models.CharField(max_length=200,blank=True,null=True)
    remarks= models.TextField(max_length=200,blank=True,null=True)
    department = models.CharField(max_length=200,blank=True,null=True)
    shipment_no = models.CharField(max_length=200,blank=True,null=True)
    job_no = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True)  