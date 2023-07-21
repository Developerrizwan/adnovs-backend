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
import jwt
from django.shortcuts import get_object_or_404
from organization.models import Company
from organization.serializers import *
from organization.pagination import CustomPagination
from organization.filters import * 
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
            return Response({"Error":"Company already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if user_model.objects.filter(email=email).exists():
            return  Response({"Error": "User with this email already exist."}, status=status.HTTP_400_BAD_REQUEST)

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
        user_role = Group.objects.get(name="admin")
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
            company = Company.objects.get(users__email=user)
            if user.check_password(password):
                groups = [group.name for group in user.groups.all()]
                return Response({"Response":"user logged in successfully",
                            "token": token.key,
                            "id":user.id,
                            "first_name":user.first_name,
                            "last_name":user.last_name,
                            "mobile":user.mobile,
                            "email":user.email,
                            "groups":groups,
                            "company_id": company.id
                            })
            else:
                return Response({"Error":"Incorrect Password"},status=status.HTTP_400_BAD_REQUEST)        
        else: 
            return Response({"Error":"Email does not exists"},status=status.HTTP_400_BAD_REQUEST)


class UserCreateViewSet(generics.GenericAPIView):
    serializer_class = UserSignUpSerializer
    permission_classes = [AllowAny, ]

    def post(self, request):
        try:
            company_id = request.query_params.get('company_id')
            print(company_id)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            password = serializer.validated_data.get('password')
            email = serializer.validated_data.get('email')
            user_model = get_user_model()

            if user_model.objects.filter(email=email).exists():
                print(email)
                return  Response({"Error": "User with this email already exist."}, status=status.HTTP_400_BAD_REQUEST)
            user = user_model.objects.create_user(
                username=serializer.validated_data['email'],
                email=serializer.validated_data['email'],
                password=password,
                mobile=serializer.validated_data['mobile'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
            )
            user_role = Group.objects.get(name="user")
            user.groups.add(user_role)
            user.save()
            generate_token(user)
            
            if company_id:
                company = get_object_or_404(Company, id=company_id)
                company.users.add(user)  
                company.save()
            
            return Response({'Response': 'User created Successfully'}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDeleteViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """User Delete"""
    
    permission_classes = (IsAuthenticated, )
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

class CompanyViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Company in the Database"""
    
    permission_classes = (AllowAny, )
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


def generate_otp():
    import random
    import math
    digits = [i for i in range(0, 10)]
    random_str = ''
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])
    return random_str

class ForgetpasswordViewSet(generics.GenericAPIView):
    serializer_class = ForgetPasswordSerializer
    permission_classes = [AllowAny,]

    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = generate_otp()
        if get_user_model().objects.filter(email = email).exists():
            

            user = get_user_model().objects.get(email = email)
            user.otp = '1234'
            user.save()
            return Response({"Response":"OTP sent to your email"})        
        else: 
            return Response({"Error":"email does not exists"},  status=status.HTTP_400_BAD_REQUEST)

class ForgetpasswordVerifyViewSet(generics.GenericAPIView):
    serializer_class = ForgetPasswordVerifySerializer
    permission_classes = [AllowAny,]

    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        if get_user_model().objects.filter(email = email).exists():
            user = get_user_model().objects.get(email = email)
            if user.otp == str(otp):
                user.password = make_password(new_password)
                user.save()
                return Response({"Response":"password updated successfully"})  
            else:
                return Response({"Response":"Otp did not match"},  status=status.HTTP_400_BAD_REQUEST)  
        else: 
            return Response({"Error":"email does not exists"},  status=status.HTTP_400_BAD_REQUEST)
        

class GoogleTokenViewSet(generics.GenericAPIView):
    serializer_class = GoogleTokenSerializer
    permission_classes = [AllowAny, ]

    def post(self,request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
    
        jwt_token = serializer.validated_data['gtoken']
        decoded_token = jwt.decode(jwt_token,options={"verify_signature": False},algorithms=['HS256'])
        email = decoded_token['email']
        
        if get_user_model().objects.filter(email = decoded_token['email']).exists() and decoded_token['email_verified'] == True:
            user = get_user_model().objects.get(email = email)
            groups = [group.name for group in user.groups.all()]
            token = Token.objects.get(user = user)
            return Response({"Response":"User Verified",
                            "token": token.key,
                            "id":user.id,
                            "mobile":user.mobile,
                            "email":user.email,
                            "groups":groups})
        elif not get_user_model().objects.filter(email = decoded_token['email']).exists() and decoded_token['email_verified'] == True:
            payload = {'email':email,
                   'password':decoded_token['sub'],
                   'username':email,
                   'last_name':email,
                   'first_name':decoded_token['name']}
        user = get_user_model().objects.create_user(**payload)
        user_group = Group.objects.get(name='user')
        user.groups.add(user_group)
        user.save()
        token = generate_token(user)
        groups = [group.name for group in user.groups.all()]
        return Response({"Response":"User created",
                            "token": token,
                            "id":user.id,
                            "mobile":user.mobile,
                            "email":user.email,
                            "groups":groups
                            }) 


class CompanyViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Company in the Database"""
    
    permission_classes = (IsAuthenticated, )
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class JobViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Job in the Database"""
    
    permission_classes = (IsAuthenticated, )
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class VouchersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Vouchers in the Database"""
    
    permission_classes = (IsAuthenticated, )
    queryset = Vouchers.objects.all()
    serializer_class = VouchersSerializer

class InvoicesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Invoices in the Database"""
    
    permission_classes = (IsAuthenticated, )
    queryset = Invoices.objects.all()
    serializer_class = InvoicesSerializer

class GetusersViewSet(viewsets.GenericViewSet,mixins.ListModelMixin):
    """Get all Users"""
    
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = get_user_model().objects.all() 
    serializer_class = UserSerializer 

    def get_queryset(self):
        # Get the requesting user
        requesting_user = self.request.user
        if requesting_user.company_set.exists():
            # Get the company of the requesting user
            requesting_user_company = requesting_user.company_set.first()
            # Get all users associated with the same company as the requesting user
            users = requesting_user_company.users.all()
        else:
            users = get_user_model().objects.all()
        return users
    
class GetcompanyViewset(viewsets.GenericViewSet,mixins.ListModelMixin):
    """ Get all Companys"""
    
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Company.objects.all() 
    serializer_class = CompanySerializer 
    
class GetjobViewset(viewsets.GenericViewSet,mixins.ListModelMixin):
    """Get all Jobs"""
    
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Job.objects.all() 
    serializer_class = JobSerializer
    filter_backends = [TypeFilter]
    
class GetvoucherViewset(viewsets.GenericViewSet,mixins.ListModelMixin):
    """Get all Vouchers"""
    
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Vouchers.objects.all() 
    serializer_class = VouchersSerializer 
    filter_backends = [VoucherFliter]
    
class GetinvoiceViewset(viewsets.GenericViewSet,mixins.ListModelMixin):
    """Get all Invoices"""
    
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Invoices.objects.all() 
    serializer_class = InvoicesSerializer
    filter_backends = [InvoicesFliter]

class GetUserProfileViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """Get user details for the requested user"""

    permission_classes = (IsAuthenticated,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        print(self.request.user.id)
        queryset = self.queryset.get(id=self.request.user.id)
        return queryset
    
class UserRelatedCountsViewSet(viewsets.GenericViewSet):
    """Get the count of invoices, jobs, and vouchers related to the requesting user"""

    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        # Get the count of related objects for the user
        invoice_count = Invoices.objects.filter(company__users=user).count()
        job_count = Job.objects.filter(company__users__email=user.email).count()
        voucher_count = Vouchers.objects.filter(job__company__users__email=user.email).count()

        # Serialize the counts and return the response
        counts_serializer = UserRelatedCountsSerializer({
            'invoice_count': invoice_count,
            'job_count': job_count,
            'voucher_count': voucher_count
        })

        return Response(counts_serializer.data, status=status.HTTP_200_OK)
