from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from organization.models import *

class UserSignUpSerializer(serializers.Serializer):

    password = serializers.CharField()
    mobile = serializers.CharField(required=False,allow_blank=True)
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    company_name = serializers.CharField(required=True)
    company_email = serializers.CharField(required=True)
    company_address = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    country = serializers.CharField(required=True)


class UserSignInSerializer(serializers.Serializer):

    email = serializers.CharField()
    password = serializers.CharField()


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField()


class ForgetPasswordVerifySerializer(serializers.Serializer):
    email = serializers.CharField()
    new_password = serializers.CharField()
    otp = serializers.IntegerField()


class GoogleTokenSerializer(serializers.Serializer):
    gtoken = serializers.CharField()


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


class VouchersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vouchers
        fields = '__all__'


class InvoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoices
        fields = '__all__' 


        
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    
    class Meta:
        model = get_user_model() 
        fields = '__all__'

    def get_groups(self, obj):
        return obj.groups.values_list('name', flat=True)
    
class UserRelatedCountsSerializer(serializers.Serializer):
    invoice_count = serializers.IntegerField()
    job_count = serializers.IntegerField()
    voucher_count = serializers.IntegerField()
    jobs_active = serializers.IntegerField()
    jobs_inactive = serializers.IntegerField()
    enquiry_count = serializers.IntegerField()
    enquiry_active = serializers.IntegerField()
    enquiry_inactive = serializers.IntegerField()

class UserCreateSerializer(serializers.Serializer):

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    mobile = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    role = serializers.CharField(required=True)
    company_id = serializers.CharField(required=True)
   
class CoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coa
        fields = '__all__'

class CoaGetSerializer(serializers.ModelSerializer):
    company=CompanySerializer()
    class Meta:
        model = Coa
        fields = '__all__'
        
class CoaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CoaCategory 
        fields = '__all__' 
        
class CoaGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoaGroup
        fields = '__all__'
        
class PodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pod
        fields = '__all__'

class PoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poa
        fields = '__all__'

# class PolSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Pol
#         fields = '__all__'
        
class ChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = '__all__'

class CostEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model=CostEntry
        fields='__all__' 

class CostEntryGetSerializer(serializers.ModelSerializer):
    charge=ChargeSerializer()
    job_no = JobSerializer()
    class Meta:
        model = CostEntry
        fields = '__all__'

        
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__' 

class OrganizationGetSerializer(serializers.ModelSerializer):
    company=CompanySerializer()
    coa=CoaSerializer()
    class Meta:
        model = Organization
        fields = '__all__'
        
class JobGetSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    consignee_name =OrganizationSerializer()
    client_name = OrganizationSerializer()
    notify = OrganizationSerializer()
    broker = OrganizationSerializer()
    transporter = OrganizationSerializer()
    class Meta:
        model = Job
        fields = '__all__'

class ChargeGetSerializer(serializers.ModelSerializer):
    coa = CoaSerializer()
    class Meta:
        model = Charge
        fields = '__all__'

class InvoicesGetSerializer(serializers.ModelSerializer):
    job = JobGetSerializer()
    company=CompanySerializer()
    consignee_name=OrganizationSerializer()
    client_name = OrganizationSerializer()
    party_account = OrganizationSerializer()
    coa = CoaSerializer()
    amount_sar = serializers.SerializerMethodField()
    fc_amount = serializers.SerializerMethodField()
    
    def get_amount_sar(self, obj):
        cost_entrys = CostEntry.objects.filter(invoice__id=obj.id)
        total_amount = 0
        for cost_entry in cost_entrys:
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            total_amount += (amount)+(float((vat_percent * amount)/100))
        
        return total_amount
    
    def get_fc_amount(self, obj):
        cost_entrys = CostEntry.objects.filter(invoice__id=obj.id)
        fcy_amount = 0
        for cost_entry in cost_entrys:
            fy_amount = float(cost_entry.amount if cost_entry.amount else 0.0)
            fcy_amount = fcy_amount + fy_amount
        
        return fcy_amount
    class Meta:
        model = Invoices
        fields = '__all__' 


class VoucherGetSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    party_account = serializers.SerializerMethodField()
    
    def get_client_name(self, obj):

        if not obj.invoice:
            return None
        
        client = obj.invoice.client_name
        return OrganizationSerializer(client).data
    
    def get_party_account(self, obj):

        if not obj.party_account or not obj.party_account_type:
            return None
        
        if obj.party_account_type == 'organization' and Organization.objects.filter(id=obj.party_account).exists():
            org = Organization.objects.get(id=obj.party_account)
            return OrganizationSerializer(org).data
        
        if obj.party_account_type == 'coa' and Coa.objects.filter(id=obj.party_account).exists():
            coa = Coa.objects.get(id=obj.party_account)
            return CoaSerializer(coa).data
        
        return None

    job = JobSerializer()
    company = CompanySerializer()
    invoice = InvoicesSerializer()

    class Meta:
        model = Vouchers
        fields = '__all__'
        
class AccountDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDetails
        fields = '__all__' 
    
class AccountDetailsGetSerializer(serializers.ModelSerializer):
    ac_name = serializers.SerializerMethodField()
    def get_ac_name(self, obj):

        if not obj.ac_name or not obj.ac_name_type:
            return None
        
        if obj.ac_name_type == 'organization':
            org = Organization.objects.get(id=obj.ac_name)
            return OrganizationSerializer(org).data
        
        if obj.ac_name_type == 'coa':
            coa = Coa.objects.get(id=obj.ac_name)
            return CoaSerializer(coa).data
        
        return None
    
    vouchers = VouchersSerializer()
    charge = ChargeSerializer()
    class Meta:
        model = AccountDetails
        fields = '__all__' 

class InvoiceJobSerializer(serializers.ModelSerializer):
    consignee_name = OrganizationSerializer()
    coa = CoaSerializer()
    job = JobSerializer()
    client_name = OrganizationSerializer()
    party_account = OrganizationSerializer()
    company = CompanySerializer()
    amount_sar = serializers.SerializerMethodField()
    fc_amount = serializers.SerializerMethodField()
    
    def get_amount_sar(self, obj):
        cost_entrys = CostEntry.objects.filter(invoice__id=obj.id)
        total_amount = 0
        for cost_entry in cost_entrys:
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            total_amount += (amount)+(float((vat_percent * amount)/100))
        
        return total_amount
    
    def get_fc_amount(self, obj):
        cost_entrys = CostEntry.objects.filter(invoice__id=obj.id)
        fcy_amount = 0
        for cost_entry in cost_entrys:
            fy_amount = float(cost_entry.amount if cost_entry.amount else 0.0)
            fcy_amount = fcy_amount + fy_amount
        
        return fcy_amount

    class Meta:
        model = Invoices
        fields = '__all__' 

class VouchersJobSerializer(serializers.ModelSerializer):
    job = JobSerializer()

    class Meta:
        model = Vouchers
        fields = '__all__' 
