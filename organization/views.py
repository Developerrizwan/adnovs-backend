from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status, mixins, generics, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.contrib.auth.models import Group
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password,check_password
from organization.models import Company
from organization.serializers import CompanySerializer
# Create your views here.
class CompanyViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Company in the Database"""
    
    permission_classes = (AllowAny, )
    queryset = Company.objects.all()
    serializer_class = CompanySerializer