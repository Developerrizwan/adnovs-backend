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