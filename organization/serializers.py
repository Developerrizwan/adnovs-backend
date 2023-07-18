from rest_framework import serializers
from organization.models import Company

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


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
