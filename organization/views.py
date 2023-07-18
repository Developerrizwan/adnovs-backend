from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status, mixins, generics, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.contrib.auth.models import Group
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from adnov.users.models import generate_token
from django.contrib.auth.hashers import make_password,check_password
from organization.models import Company
from organization.serializers import *
# Create your views here.

class UserSignUpViewSet(generics.GenericAPIView):
    serializer_class = UserSignUpSerializer
    permission_classes = [AllowAny, ]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.pop('password')

        user_model = get_user_model()
        company_email = serializer.validated_data.get('company_email', None)
        email = serializer.validated_data.get('email', None)

        # Check if both the user email and company email already exist
        if Company.objects.filter(email=company_email).exists():
            return Response({"Response":"Company already exists"})
        if user_model.objects.filter(email=email).exists():
            return  Response({"Response": "User with this email already exist."})

        company = Company.objects.create(
            name=serializer.validated_data['company_name'],
            email=serializer.validated_data['company_email'],
            country=serializer.validated_data['country'],
            state=serializer.validated_data['state'],
            address=serializer.validated_data['company_address']
        )
        # Create the user
        user = user_model.objects.create_user(
            username=serializer.validated_data['email'],
            email=serializer.validated_data['email'],
            password=password,
            mobile=serializer.validated_data['mobile'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
        )

        # Add the user to the company (if a company was created)
        if company:
            company.users.add(user)
            company.save()

        # Set user role and generate token
        user_role = Group.objects.get(name="user")
        user.groups.add(user_role)
        user.save()
        generate_token(user)
        return Response("User Created Successfully", status=status.HTTP_201_CREATED)
    

class UserSignInViewset(generics.GenericAPIView):
    serializer_class = UserSignInSerializer
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        User=get_user_model()
        if User.objects.filter(email = email).exists():
            user = User.objects.get(email = email)
            token = Token.objects.get(user = user)
            if user.check_password(password):
                groups = [group.name for group in user.groups.all()]
                return Response({"Response":"user logged in successfully",
                            "token": token.key,
                            "id":user.id,
                            "mobile":user.mobile,
                            "email":user.email,
                            "groups":groups,
                            })
            else:
                return Response({"Error":"Incorrect Password"},status=status.HTTP_400_BAD_REQUEST)        
        else: 
            return Response({"Error":"Email does not exists"},status=status.HTTP_400_BAD_REQUEST)


class CompanyViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Company in the Database"""
    
    permission_classes = (AllowAny, )
    queryset = Company.objects.all()
    serializer_class = CompanySerializer