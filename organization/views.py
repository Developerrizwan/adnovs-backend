from typing import Any
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status, mixins, generics, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django.contrib.auth.models import Group
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from adnov.users.models import generate_token
from django.contrib.auth.hashers import make_password, check_password
import jwt
from django.shortcuts import get_object_or_404
from organization.models import Company
from organization.serializers import *
from organization.pagination import CustomPagination
from organization.filters import *
from datetime import datetime
from django.db.models import Q, Sum, Value, DecimalField
from decimal import Decimal, ROUND_HALF_UP
# Create your views here.
from django.db.models.functions import Coalesce
from decimal import Decimal

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
            return Response({"Error": "Company already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if user_model.objects.filter(email=email).exists():
            return Response({"Error": "User with this email already exist."}, status=status.HTTP_400_BAD_REQUEST)

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
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            token = Token.objects.get(user=user)
            company = Company.objects.get(users__email=user)
            if user.check_password(password):
                groups = [group.name for group in user.groups.all()]
                return Response({"Response": "user logged in successfully",
                                 "token": token.key,
                                 "id": user.id,
                                 "first_name": user.first_name,
                                 "last_name": user.last_name,
                                 "mobile": user.mobile,
                                 "email": user.email,
                                 "groups": groups,
                                 "company_id": company.id
                                 })
            else:
                return Response({"Error": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "Email does not exists"}, status=status.HTTP_400_BAD_REQUEST)


class UserCreateViewSet(generics.GenericAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny, ]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            company_id = serializer.validated_data.get('company_id')
            password = serializer.validated_data.get('password')
            email = serializer.validated_data.get('email')
            role = serializer.validated_data.get('role')
            user_model = get_user_model()

            if user_model.objects.filter(email=email).exists():
                return Response({"Error": "User with this email already exist."}, status=status.HTTP_400_BAD_REQUEST)
            user = user_model.objects.create_user(
                username=serializer.validated_data['email'],
                email=serializer.validated_data['email'],
                password=password,
                mobile=serializer.validated_data['mobile'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
            )
            user_role = Group.objects.get(name=role)
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

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = generate_otp()
        if get_user_model().objects.filter(email=email).exists():

            user = get_user_model().objects.get(email=email)
            user.otp = '1234'
            user.save()
            return Response({"Response": "OTP sent to your email"})
        else:
            return Response({"Error": "email does not exists"},  status=status.HTTP_400_BAD_REQUEST)


class ForgetpasswordVerifyViewSet(generics.GenericAPIView):
    serializer_class = ForgetPasswordVerifySerializer
    permission_classes = [AllowAny,]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        if get_user_model().objects.filter(email=email).exists():
            user = get_user_model().objects.get(email=email)
            if user.otp == str(otp):
                user.password = make_password(new_password)
                user.save()
                return Response({"Response": "password updated successfully"})
            else:
                return Response({"Response": "Otp did not match"},  status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "email does not exists"},  status=status.HTTP_400_BAD_REQUEST)


class GoogleTokenViewSet(generics.GenericAPIView):
    serializer_class = GoogleTokenSerializer
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        jwt_token = serializer.validated_data['gtoken']
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False}, algorithms=['HS256'])
        email = decoded_token['email']

        if get_user_model().objects.filter(email=decoded_token['email']).exists() and decoded_token['email_verified'] == True:
            user = get_user_model().objects.get(email=email)
            groups = [group.name for group in user.groups.all()]
            token = Token.objects.get(user=user)
            return Response({"Response": "User Verified",
                            "token": token.key,
                             "id": user.id,
                             "mobile": user.mobile,
                             "email": user.email,
                             "groups": groups})
        elif not get_user_model().objects.filter(email=decoded_token['email']).exists() and decoded_token['email_verified'] == True:
            payload = {'email': email,
                       'password': decoded_token['sub'],
                       'username': email,
                       'last_name': email,
                       'first_name': decoded_token['name']}
        user = get_user_model().objects.create_user(**payload)
        user_group = Group.objects.get(name='user')
        user.groups.add(user_group)
        user.save()
        token = generate_token(user)
        groups = [group.name for group in user.groups.all()]
        return Response({"Response": "User created",
                         "token": token,
                         "id": user.id,
                         "mobile": user.mobile,
                         "email": user.email,
                         "groups": groups
                         })


class CompanyViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Company in the Database"""

    permission_classes = (IsAuthenticated, )
    queryset = Company.objects.all().order_by('-id')
    serializer_class = CompanySerializer
    filter_backends = [CompanyFliter]


class JobViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    """Manage Job in the Database"""

    permission_classes = (IsAuthenticated, )
    queryset = Job.objects.all().order_by('-id')
    serializer_class = JobSerializer
    filter_backends = [TypeFilter]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Generate the enquiry_number and job_number based on the job type, branch, current year, and auto-generated id
        year = datetime.now().year
        job_id = serializer.save().id
        type = serializer.validated_data['type']
        branch = serializer.validated_data['branch']
        job_type = serializer.validated_data['job_type']
        company = serializer.validated_data['company']
        job_number = None
        enquiry_number = None
        job_status_first_chars = "".join(word[0] for word in type.split())
        # job_number = f"{branch[:3]}{job_status_first_chars}{str(year)[-2:]}{job_id:02}"
        company = Company.objects.get(id=company.id)
        print(company)
        if 'job_number' in serializer.validated_data:
            job_number = serializer.validated_data['job_number']
        
        if 'enquiry_number' in serializer.validated_data:
            enquiry_number = serializer.validated_data['enquiry_number']

        if job_type == 'Job':
            job_number = job_number = f"{branch[:3].upper()}{job_status_first_chars}{str(year)[-2:]}{company.job_count + 1}"
            company.job_count = company.job_count + 1
        else:
            # enquiry_number = f"ENQ{str(year)[-2:]}{job_id:02}"     
            enquiry_number = f"ENQ{str(year)[-2:]}{company.enquiry_count+1}" 
            company.enquiry_count = company.enquiry_count + 1  
            
        serializer.save(enquiry_number=enquiry_number, job_number=job_number)
        company.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JobGetSerializer
        return JobSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.isdeleted = True 
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)



class VouchersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    """Manage Vouchers in the Database"""

    permission_classes = (IsAuthenticated, )
    queryset = Vouchers.objects.all().order_by('-id')
    serializer_class = VouchersSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VoucherGetSerializer
        return VouchersSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        voucher_type = serializer.validated_data['voucher_type']
        branch = serializer.validated_data['branch']
        company_id = serializer.validated_data['company']
        job_id = serializer.validated_data['job']

        yymm_part = timezone.now().strftime("%y")
        prefix = branch[0] if branch else ''

        if voucher_type == 'Journal':
            company = Company.objects.get(id=company_id.id)
            journal_count = company.journal_count
            voucher_number = f"{prefix}JV{yymm_part}{journal_count+1}"
            company.journal_count = journal_count+1
            company.save()

        if voucher_type == 'Payment':
            company = Company.objects.get(id=company_id.id)
            payment_count = company.payment_count
            voucher_number = f"{prefix}PV{yymm_part}{payment_count+1}"
            company.payment_count = payment_count+1
            company.save()

        if voucher_type == 'Receipt':
            company = Company.objects.get(id=company_id.id)
            receipt_count = company.receipt_count
            voucher_number =  f"{prefix}RV{yymm_part}{receipt_count+1}"
            company.receipt_count = receipt_count+1
            company.save()

        if voucher_type == 'CreditNote':
            company = Company.objects.get(id=company_id.id)
            creditnote_count = company.creditnote_count
            voucher_number =f"{prefix}CV{yymm_part}{creditnote_count+1}"
            company.creditnote_count = creditnote_count+1
            company.save()
        
        if voucher_type == 'DebitNote':
            company = Company.objects.get(id=company_id.id)
            debitnote_count = company.debitnote_count
            voucher_number = f"{prefix}DV{yymm_part}{debitnote_count+1}"
            company.debitnote_count = debitnote_count+1
            company.save()

        serializer.save(voucher_number=voucher_number)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvoicesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    """Manage Invoices in the Database"""

    permission_classes = (IsAuthenticated, )
    queryset = Invoices.objects.all().order_by('-id')
    serializer_class = InvoicesSerializer
    filter_backends=[InvoicesMasterFilter]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InvoicesGetSerializer
        return InvoicesSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invoice_type = serializer.validated_data['invoice_type']
        company_id = serializer.validated_data['company']

        if invoice_type == 'Sales':
            company = Company.objects.get(id=company_id.id)
            scount = company.sinv_count
            invoice_number = "SINV" + str(scount+1)
            company.sinv_count = scount+1
            company.save()

        if invoice_type == 'Purchase':
            company = Company.objects.get(id=company_id.id)
            pcount = company.pinv_count
            invoice_number = "PINV" + str(pcount+1)
            company.pinv_count = pcount+1
            company.save()

        serializer.save(invoice_number=invoice_number)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # cost_entry = get_object_or_404(CostEntry, invoice=instance)
            cost_entrys = CostEntry.objects.filter(invoice=instance)
            for cost_entry in cost_entrys:
                cost_entry.is_included = False
                cost_entry.save()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(f"An error occurred: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetusersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
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


class GetcompanyViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """ Get all Companys"""

    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Company.objects.all().order_by('-id')
    serializer_class = CompanySerializer


class GetjobViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all Jobs"""

    # pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Job.objects.all().order_by('-id')
    serializer_class = JobGetSerializer
    filter_backends = [TypeFilter]


class GetvoucherViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all Vouchers"""

    # pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Vouchers.objects.all().order_by('-id')
    serializer_class = VoucherGetSerializer
    filter_backends = [VoucherFliter]


class GetinvoiceViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all Invoices"""

    # pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Invoices.objects.all().order_by('-id')
    serializer_class = InvoicesGetSerializer
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
        jobs = Job.objects.filter(company__users__email=user.email)
        jobss = jobs.filter(job_type='Job')
        jobs_active = jobs.filter(job_status='Finished')
        jobs_inactive = jobs.filter(job_status='Cancelled')
        enquiry = jobs.filter(job_type='Enquiry')
        enquiry_active = enquiry.filter(job_status='Finished')
        enquiry_inactive = enquiry.filter(job_status='Cancelled')
        voucher_count = Vouchers.objects.filter(job__company__users__email=user.email).count()

        # Serialize the counts and return the response
        counts_serializer = UserRelatedCountsSerializer({
            'invoice_count': invoice_count,
            'job_count': jobss.count,
            'voucher_count': voucher_count,
            'jobs_active': jobs_active.count,
            'jobs_inactive': jobs_inactive.count,
            'enquiry_count': enquiry.count,
            'enquiry_active': enquiry_active.count,
            'enquiry_inactive': enquiry_inactive.count
        })

        return Response(counts_serializer.data, status=status.HTTP_200_OK)


class CoaViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Coa in the Database"""
    permission_classes = (IsAuthenticated, )
    queryset = Coa.objects.all().order_by('-id')
    serializer_class = CoaSerializer
    filter_backends = [CoaFilter]


class GetCoaViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all coa"""

    permission_classes = (IsAuthenticated,)
    queryset = Coa.objects.all().order_by('-id')
    serializer_class = CoaGetSerializer
    filter_backends = [CoaFilter]


class CoaCategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage CoaCategory in the Database"""
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = CoaCategory.objects.all().order_by('id')
    serializer_class = CoaCategorySerializer


class CoaGroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage CoaGroup in the Database"""
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = CoaGroup.objects.all().order_by('id')
    serializer_class = CoaGroupSerializer
    filter_backends = [CoaGroupFilter]


class GetCoaGroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all coa group"""
   
    permission_classes = (IsAuthenticated,)
    queryset = CoaGroup.objects.all().order_by('-id')
    serializer_class = CoaGroupSerializer
    filter_backends = [CoaGroupFilter]


class PodViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Pod in the Database"""
    # pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Pod.objects.all().order_by('-id')
    serializer_class = PodSerializer
    filter_backends = [SearchFilter]


class PoaViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage Poa in the Database"""
    # pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Poa.objects.all().order_by('-id')
    serializer_class = PoaSerializer
    filter_backends = [SearchFilter]

# class PolViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
#     """Manage Pol in the Database"""
#     pagination_class = CustomPagination
#     permission_classes = (IsAuthenticated, )
#     queryset = Pol.objects.all()
#     serializer_class = PolSerializer
#     filter_backends = [SearchFilter]


class OrganizationViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    """Manage Organization in the Database"""
    # pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Organization.objects.all().order_by('-id')
    serializer_class = OrganizationSerializer
    filter_backends = [OrganizationFilter]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrganizationGetSerializer
        return OrganizationSerializer


class GetOrganzationViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all Organizations"""
    permission_classes = (IsAuthenticated, )
    queryset = Organization.objects.all().order_by('-id')
    serializer_class = OrganizationGetSerializer
    filter_backends = [OrganizationFilter]


class ChargeViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage charge in the Database"""
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Charge.objects.all().order_by('-id')
    serializer_class = ChargeSerializer
    filter_backends = [ChargeFilter]


class GetchargeViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all charges"""
    permission_classes = (IsAuthenticated, )
    queryset = Charge.objects.all().order_by('-id')
    serializer_class = ChargeGetSerializer
    filter_backends = [ChargeFilter]


class CostEntryViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """Manage costentry in the Database"""
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = CostEntry.objects.all().order_by('-id')
    serializer_class = CostEntrySerializer


class GetCostEntryViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all CostEntry"""
    permission_classes = (IsAuthenticated, )
    queryset = CostEntry.objects.all().order_by('-id')
    serializer_class = CostEntryGetSerializer
    filter_backends = [CostEntryFilter]


class AccountDetailsViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    """Manage costentry in the Database"""
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)
    queryset = AccountDetails.objects.all().order_by('-id')
    serializer_class = AccountDetailsSerializer
    filter_backends = [AccountFilter]

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountDetailsGetSerializer
        return AccountDetailsSerializer


class ProfitLossViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Coa.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        job = request.query_params.get('job', None)
        start_date = request.query_params.get('start_time', None)
        end_date = request.query_params.get('end_time',None)
        organization = request.query_params.get('organization', None)
        coa_type = request.query_params.get('type', None) 
        queryset = Coa.objects.filter(company__users__email=request.user.email)

        if coa_type is not None:
            queryset = queryset.filter(coa_type=coa_type)
        # page = self.paginate_queryset(queryset)

        if queryset is not None:
            cost_entry_list = []
            for coa in queryset:
                cost_entry = CostEntry.objects.filter(Q(charge__coa=coa) | Q(invoice__party_account__coa=coa)).filter(is_included=True).exclude(invoice=None).filter(invoice__company__users__email=request.user.email)
                if start_date and end_date:
                    cost_entry = cost_entry.filter(invoice__date__range=[start_date, end_date])

                if job is not None and job.strip() :
                    cost_entry = cost_entry.filter(job_no__id=job)

                income_amount=0
                expenses_amount=0


                for cost in cost_entry:
                     
                    if cost.invoice.invoice_type=='Sales':
                        income_amount += float(cost.amount if cost.amount else 0.0)
                    else:
                        expenses_amount += float(cost.amount if cost.amount else 0.0)

                serializer = CostEntrySerializer(cost_entry, many=True)
                company_serializer = CompanySerializer(coa.company)
                
                #including vouchers
                
                voucher_accounts = AccountDetails.objects.filter(vouchers__date__range=[start_date, end_date], vouchers__company__users__email=request.user.email)
                coa_account_details = voucher_accounts.filter(Q(ac_name='{0}'.format(coa.id), ac_name_type='coa') | Q(charge__coa=coa))
                organizations = Organization.objects.filter(coa=coa, company__users__email=request.user.email)
                
                for org in organizations:
                    org_account_details = voucher_accounts.filter(ac_name='{0}'.format(org.id), ac_name_type='organization')
                    coa_account_details = coa_account_details.union(org_account_details)

                if job is not None and job.strip() :
                    cost_entry = cost_entry.filter(job_no__id=job)
                    coa_account_details = coa_account_details.filter(vouchers__job__id=job)
                    
                for acc in coa_account_details:   
                    if acc.dr_cr == 'Cr':
                        fcy_amount = float(acc.fcy_amount if acc.fcy_amount else 0.0)
                        amount=float(acc.amount_sar if acc.amount_sar else 0.0)
                        vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
                        vat_amount = float((vat_percent * amount)/100)
                        total_amount = float(amount)
                        income_amount += float(total_amount)
                    else:
                        fcy_amount = float(acc.fcy_amount if acc.fcy_amount else 0.0)
                        amount=float(acc.amount_sar if acc.amount_sar else 0.0)
                        vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
                        vat_amount = float((vat_percent * amount)/100)
                        total_amount = float(amount)
                        expenses_amount += float(total_amount)
                
                cost_entry_list.append({
                    'coa_id': coa.id,
                    'code': coa.code,
                    'name': coa.name,
                    # 'status': coa.status,
                    # 'subledger_requried': coa.subledger_requried,
                    # 'charge_required': coa.charge_required,
                    # 'job_required': coa.job_required,
                    # 'asset_required': coa.asset_required,
                    'coa_type': coa.coa_type,
                    # 'is_direct_indirect': coa.is_direct_indirect,
                    'dr_cr': coa.dr_cr,
                    'category': coa.category,
                    # 'group': coa.group.code,
                    # 'subgroup': coa.subgroup.code,
                    'type': coa.type,
                    'expense_type':coa.group.name if coa.group else None,
                    'short_name': coa.short_name,
                    'long_name': coa.long_name,
                    'language_name': coa.language_name,
                    'currency': coa.currency,
                    # 'additional_reference_code': coa.additional_reference_code,
                    'company': company_serializer.data,
                    'remarks': coa.remarks,
                    'cost_entry': serializer.data,
                    # 'account_details': acc_serializer.data,
                    'income_amount': income_amount,
                    'expenses_amount': expenses_amount
                })
                
            return Response(cost_entry_list)
        else:
            return Response([])


def get_vat_input_coa_response(coa, start_date, end_date, user):

    invoices = Invoices.objects.filter(date__range=[start_date, end_date], invoice_type='Purchase', company__users__email=user.email).order_by('date')
    respone =[]
    res_obj={}
    for invoice in invoices:
        cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id, is_included=True)
        
        for cost_entry in cost_entrys:

            res_obj = {
                "account":invoice.client_name.name if invoice.client_name else "",
                "date":invoice.date,
                "currency":invoice.currency_sar,
                "invoice_number":invoice.invoice_number,
                "vat_percent":0,
                "fcy_amount":0,
                "vat_amount":0,
                "amount":0,
                "dr_amount":0,
                "cr_amount":0,
                "net_amount":0,
                "type":"Invoice",
                "voucher":"",
                "party_account":invoice.party_account.name if invoice.party_account else "",
                "job_no":invoice.job.job_number if invoice.job.job_number else "",
                "narrations":invoice.narration if invoice.narration else "",
                "branch":invoice.branch if invoice.branch else "",
                "language_name":coa.language_name if coa.language_name else ""
                }

            fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            vat_amount = float((vat_percent * amount)/100)
            total_amount = float(vat_amount)

            res_obj['vat_percent']= vat_percent
            res_obj['fcy_amount'] = fcy_amount
            res_obj['amount'] = amount
            res_obj['vat_amount'] = vat_amount
            res_obj['dr_amount']=total_amount
            res_obj['net_amount']=total_amount

            if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
                respone.append(res_obj)
    
    # try:
    coa_account_details = AccountDetails.objects.filter(vouchers__date__range=[start_date, end_date], vouchers__company__users__email=user.email)
    # organizations = Organization.objects.filter(company__users__email=user.email).values_list('id')
    # organizations = list(map(str, organizations))
    # org_account_details = AccountDetails.objects.filter(ac_name__in=organizations, ac_name_type='organization')

    # account_details = coa_account_details.union(org_account_details)
    account_details = coa_account_details
    direct_input_details = account_details.filter(ac_name='429', ac_name_type='coa') 
    account_details = account_details.exclude(ac_name='430', ac_name_type='coa').exclude(ac_name='429', ac_name_type='coa')
    account_details = account_details.union(direct_input_details)
    
    for acc in account_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()
            
        res_obj = {
                "account":coa.name,
                "date":acc.vouchers.date if acc.vouchers.date else '',
                "currency":acc.currency,
                "invoice_number":"",
                "vat_percent":0,
                "fcy_amount":0,
                "vat_amount":0,
                "amount":0,
                "dr_amount":0,
                "cr_amount":0,
                "net_amount":0,
                "type": acc.vouchers.voucher_type + " Voucher",
                "voucher":acc.vouchers.voucher_number if acc.vouchers else "",
                "party_account": party_account.name if party_account else '',
                "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
                "narrations": acc.narration,
                "branch":acc.vouchers.branch if acc.vouchers else "",
                "language_name":coa.language_name if coa.language_name else ""
                }
        # fcy_amount = float(acc.fcy_amount if acc.fcy_amount else 0.0)
        fcy_amount_str = acc.fcy_amount if acc.fcy_amount else "0.0"
        # Check if the string contains a decimal point
        if '.' in fcy_amount_str:
            # If the string contains a decimal point, remove the extra decimal point and convert to float
            fcy_amount_str_without_extra_decimal = fcy_amount_str.replace('.', '', 1)  # Remove the first occurrence of the decimal point
            fcy_amount = float(fcy_amount_str_without_extra_decimal)
        else:
            # If the string does not contain a decimal point, convert to float directly
            fcy_amount = float(fcy_amount_str)
        amount=float(acc.amount_sar if acc.amount_sar else 0.0)
        vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
        vat_amount = float((vat_percent * amount)/100)
        total_amount = float(vat_amount)
        
        if acc.ac_name == '429' and acc.ac_name_type == 'coa':
            total_amount = amount
        
        res_obj['vat_percent']= vat_percent
        res_obj['fcy_amount'] = fcy_amount
        res_obj['amount'] = amount
        res_obj['vat_amount'] = vat_amount
        
        if acc.dr_cr == 'Cr':
            res_obj['cr_amount']=total_amount
        else:
            res_obj['dr_amount']=total_amount
        
        res_obj['net_amount']=total_amount

        if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
            respone.append(res_obj)
    # except:
    #     pass
    
    balance = 0
    results = []
    for res in respone:
        balance = float(balance) + float(float(res['dr_amount']) - float(res['cr_amount']))
        res['net_amount'] = balance
        results.append(res)
        
    return results


def get_vat_output_coa_response(coa, start_date, end_date, user):

    invoices = Invoices.objects.filter(date__range=[start_date, end_date], invoice_type='Sales', company__users__email=user.email).order_by('date')
    respone =[]
    res_obj={}
    for invoice in invoices:
        cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id, is_included=True)
        
        for cost_entry in cost_entrys:
            res_obj = {
                "account":invoice.client_name.name if invoice.client_name else "",
                "date":invoice.date,
                "currency":invoice.currency_sar,
                "invoice_number":invoice.invoice_number,
                "vat_percent":0,
                "fcy_amount":0,
                "vat_amount":0,
                "amount":0,
                "dr_amount":0,
                "cr_amount":0,
                "net_amount":0,
                "type":"Invoice",
                "voucher":"",
                "party_account":invoice.party_account.name if invoice.party_account else "",
                "job_no":invoice.job.job_number if invoice.job.job_number else "",
                "narrations":invoice.narration if invoice.narration else "",
                "branch":invoice.branch if invoice.branch else "",
                "language_name":coa.language_name if coa.language_name else ""
                }
            
            fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            vat_amount = float((vat_percent * amount)/100)
            total_amount = float(vat_amount)
            res_obj['vat_percent']= vat_percent
            res_obj['fcy_amount'] = fcy_amount
            res_obj['amount'] = amount
            res_obj['vat_amount'] = vat_amount
            res_obj['cr_amount']=total_amount
            res_obj['net_amount']=total_amount   

            if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
                respone.append(res_obj)

    # try:
    coa_account_details = AccountDetails.objects.filter(vouchers__date__range=[start_date, end_date], vouchers__company__users__email=user.email)
    # organizations = Organization.objects.filter(company__users__email=user.email).values_list('id')
    # organizations = list(map(str, organizations))
    # org_account_details = AccountDetails.objects.filter(ac_name__in=organizations, ac_name_type='organization')

    # account_details = coa_account_details.union(org_account_details)
    account_details = coa_account_details
    direct_output_details = account_details.filter(ac_name='430', ac_name_type='coa') 
    # account_details = account_details.exclude(ac_name='430', ac_name_type='coa').exclude(ac_name='429', ac_name_type='coa')
    # account_details = account_details.union(direct_output_details)

    for acc in direct_output_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()
            
        res_obj = {
            "account":coa.name,
            "date":acc.vouchers.date if acc.vouchers.date else '',
            "currency":acc.currency,
            "invoice_number":"",
            "vat_percent":0,
            "fcy_amount":0,
            "vat_amount":0,
            "amount":0,
            "dr_amount":0,
            "cr_amount":0,
            "net_amount":0,
            "type": acc.vouchers.voucher_type + " Voucher",
            "voucher":acc.vouchers.voucher_number if acc.vouchers else "",
            "party_account": party_account.name if party_account else '',
            "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
            "narrations": acc.narration,
            "branch":acc.vouchers.branch if acc.vouchers else "",
            "language_name":coa.language_name if coa.language_name else ""
            }
        # fcy_amount = float(acc.fcy_amount if acc.fcy_amount else 0.0)
        fcy_amount_str = acc.fcy_amount if acc.fcy_amount else "0.0"
        # Check if the string contains a decimal point
        if '.' in fcy_amount_str:
            # If the string contains a decimal point, remove the extra decimal point and convert to float
            fcy_amount_str_without_extra_decimal = fcy_amount_str.replace('.', '', 1)  # Remove the first occurrence of the decimal point
            fcy_amount = float(fcy_amount_str_without_extra_decimal)
        else:
            # If the string does not contain a decimal point, convert to float directly
            fcy_amount = float(fcy_amount_str)
        amount=float(acc.amount_sar if acc.amount_sar else 0.0)
        vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
        vat_amount = float((vat_percent * amount)/100)
        total_amount = float(vat_amount)
        
        if acc.ac_name == '430' and acc.ac_name_type == 'coa':
            total_amount = amount
        
        res_obj['vat_percent']= vat_percent
        res_obj['fcy_amount'] = fcy_amount
        res_obj['amount'] = amount
        res_obj['vat_amount'] = vat_amount
        
        if acc.dr_cr == 'Cr':
            res_obj['cr_amount']=total_amount
        else:
            res_obj['dr_amount']=total_amount
        
        res_obj['net_amount']=total_amount
        
        if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
            respone.append(res_obj)
    # except:
    #     pass
    
    balance = 0
    results = []
    for res in respone:
        balance = float(balance) + float(float(res['cr_amount']) - float(res['dr_amount']))
        res['net_amount'] = balance
        results.append(res)
        
    return results

from django.db.models import Sum, Q, Value, FloatField
from django.db.models.functions import Coalesce, Cast

def calculate_opening_balance(coa, start_date, user, job=None):
    if not start_date or not coa:
        return 0.0

    base_qs = AccountDetails.objects.filter(
        vouchers__date__lt=start_date,
        vouchers__company__users__email=user.email
    )

    if job:
        base_qs = base_qs.filter(vouchers__job=job)

    # Direct COA match (ac_name is string of coa.pk)
    qs1 = base_qs.filter(
        ac_name=str(coa.pk),
        ac_name_type='coa'
    )

    # Via charge
    qs2 = base_qs.filter(charge__coa_id=coa.pk)

    # Via linked organization
    orgs = Organization.objects.filter(
        coa=coa,
        company__users__email=user.email
    )
    org_ids = [str(org.pk) for org in orgs]

    qs3 = AccountDetails.objects.none()
    if org_ids:
        qs3 = base_qs.filter(
            ac_name__in=org_ids,
            ac_name_type='organization'
        )

    # Combine all matching lines
    qs = qs1 | qs2 | qs3

    # Sum with proper casting (CharField → Float)
    dr_total = qs.filter(dr_cr='Dr').aggregate(
        total=Coalesce(
            Sum(Cast('amount_sar', FloatField())),
            Value(0.0)
        )
    )['total'] or 0.0

    cr_total = qs.filter(dr_cr='Cr').aggregate(
        total=Coalesce(
            Sum(Cast('amount_sar', FloatField())),
            Value(0.0)
        )
    )['total'] or 0.0

    net = float(dr_total - cr_total)

    # Flip sign if account is naturally credit-balanced
    if coa.dr_cr == 'Cr':
        net = -net

    return round(net, 2)



def get_other_coa_response(coa, start_date, end_date, user):
    respone = []
    res_obj = {}

    opening_balance = calculate_opening_balance(coa, start_date, user)

    cost_entrys = CostEntry.objects.filter(
        Q(charge__coa=coa) | Q(invoice__party_account__coa=coa),
        invoice__date__range=[start_date, end_date],
        is_included=True,
        invoice__company__users__email=user.email
    ).order_by('created_at')

    for cost_entry in cost_entrys:
        if cost_entry.invoice:
            res_obj = {
                "account": cost_entry.invoice.client_name.name if cost_entry.invoice and cost_entry.invoice.client_name else "",
                "date": cost_entry.invoice.date if cost_entry.invoice else cost_entry.created_at,
                "currency": cost_entry.invoice.currency_sar if cost_entry.invoice else cost_entry.currency,
                "invoice_number": cost_entry.invoice.invoice_number if cost_entry.invoice else '',
                "vat_percent": 0,
                "fcy_amount": 0,
                "vat_amount": 0,
                "amount": 0,
                "dr_amount": 0,
                "cr_amount": 0,
                "net_amount": 0,
                "type": "Invoice",
                "voucher": "",
                "charge": cost_entry.charge.name if cost_entry.charge else '',
                "party_account": cost_entry.invoice.party_account.name if cost_entry.invoice and cost_entry.invoice.party_account else '',
                "job_no": cost_entry.invoice.job.job_number if cost_entry.invoice and cost_entry.invoice.job else "",
                "narrations": cost_entry.invoice.narration if cost_entry.invoice else "",
                "branch": cost_entry.invoice.branch if cost_entry.invoice else "",
                "language_name": coa.language_name if coa.language_name else ""
            }

            if cost_entry.invoice.invoice_type == 'Sales':
                fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                amount = float(cost_entry.amount if cost_entry.amount else 0.0)
                vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                vat_amount = float((vat_percent * amount) / 100)
                total_amount = float(amount + vat_amount)
                res_obj['vat_percent'] = vat_percent
                res_obj['fcy_amount'] = fcy_amount
                res_obj['amount'] = amount
                res_obj['vat_amount'] = vat_amount
                res_obj['cr_amount'] = total_amount
                res_obj['net_amount'] = total_amount

                if not (res_obj["dr_amount"] == 0 and res_obj["cr_amount"] == 0):
                    respone.append(res_obj)
            else:
                fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                amount = float(cost_entry.amount if cost_entry.amount else 0.0)
                vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                vat_amount = float((vat_percent * amount) / 100)
                total_amount = float(amount + vat_amount)
                res_obj['vat_percent'] = vat_percent
                res_obj['fcy_amount'] = fcy_amount
                res_obj['amount'] = amount
                res_obj['vat_amount'] = vat_amount
                res_obj['dr_amount'] = total_amount
                res_obj['net_amount'] = total_amount

                if not (res_obj["dr_amount"] == 0 and res_obj["cr_amount"] == 0):
                    respone.append(res_obj)

    voucher_accounts = AccountDetails.objects.filter(
        vouchers__date__range=[start_date, end_date],
        vouchers__company__users__email=user.email
    )

    coa_account_details = voucher_accounts.filter(
        Q(ac_name=str(coa.id), ac_name_type='coa') | Q(charge__coa=coa)
    )

    organizations = Organization.objects.filter(
        coa=coa,
        company__users__email=user.email
    )

    # FIX: Use pipe operator (|) instead of union() to avoid mixed type errors
    for org in organizations:
        org_account_details = voucher_accounts.filter(
            ac_name=str(org.id),
            ac_name_type='organization'
        )
        coa_account_details = coa_account_details | org_account_details

    for acc in coa_account_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()

        fcy_amount_str = acc.fcy_amount if acc.fcy_amount else "0.0"
        if '.' in fcy_amount_str:
            fcy_amount_str = fcy_amount_str.replace('.', '', 1)
        fcy_amount = float(fcy_amount_str)

        # ── FIXED: use taxable_amount + tax_amount (same as Day Book fix) ──
        taxable    = Decimal(acc.taxable_amount or "0.00")
        tax_amt    = Decimal(acc.tax_amount     or "0.00")
        base       = Decimal(acc.amount_sar     or "0.00")
        total_dec  = (taxable + tax_amt) if taxable else base
        total_amount = float(total_dec)

        vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
        vat_amount  = float(tax_amt)
        amount      = float(taxable if taxable else base)
        # ────────────────────────────────────────────────────────────────────

        if acc.dr_cr == 'Cr':
            res_obj = {
                "account": coa.name,
                "date": acc.vouchers.date if acc.vouchers.date else '',
                "currency": acc.currency,
                "invoice_number": "",
                "vat_percent": vat_percent,
                "fcy_amount": fcy_amount,
                "vat_amount": vat_amount,
                "amount": amount,
                "dr_amount": 0,
                "cr_amount": total_amount,   # ← now includes VAT
                "net_amount": 0,
                "charge": acc.charge.name if acc.charge else '',
                "type": acc.vouchers.voucher_type + " Voucher",
                "voucher": acc.vouchers.voucher_number if acc.vouchers else "",
                "party_account": party_account.name if party_account else '',
                "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
                "narrations": acc.narration,
                "branch": acc.vouchers.branch if acc.vouchers else "",
                "language_name": coa.language_name if coa.language_name else ""
            }
        else:
            res_obj = {
                "account": coa.name,
                "date": acc.vouchers.date if acc.vouchers.date else '',
                "currency": acc.currency,
                "invoice_number": "",
                "vat_percent": vat_percent,
                "fcy_amount": fcy_amount,
                "vat_amount": vat_amount,
                "amount": amount,
                "dr_amount": total_amount,   # ← now includes VAT
                "cr_amount": 0,
                "net_amount": 0,
                "charge": acc.charge.name if acc.charge else '',
                "type": acc.vouchers.voucher_type + " Voucher",
                "voucher": acc.vouchers.voucher_number if acc.vouchers else "",
                "party_account": party_account.name if party_account else '',
                "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
                "narrations": acc.narration,
                "branch": acc.vouchers.branch if acc.vouchers else "",
                "language_name": coa.language_name if coa.language_name else ""
            }

        if not (res_obj["dr_amount"] == 0 and res_obj["cr_amount"] == 0):
            respone.append(res_obj)

    respone = sorted(respone, key=lambda obj: obj['date'])

    opening_row = {
        "account": coa.name,
        "date": start_date,
        "currency": coa.currency or "SAR",
        "invoice_number": "",
        "vat_percent": 0,
        "fcy_amount": 0,
        "vat_amount": 0,
        "amount": 0,
        "dr_amount": max(opening_balance, 0),
        "cr_amount": max(-opening_balance, 0),
        "net_amount": opening_balance,
        "type": "Opening Balance",
        "voucher": "",
        "charge": "",
        "party_account": "",
        "job_no": "",
        "narrations": "Opening balance brought forward",
        "branch": "",
        "language_name": coa.language_name or ""
    }

    respone.insert(0, opening_row)

    balance = opening_balance
    results = []

    for res in respone:
        if res['type'] == "Opening Balance":
            # Opening row already has correct dr/cr/net — just ensure it's set
            res['net_amount'] = round(balance, 2)
        else:
            dr = float(res.get('dr_amount', 0))
            cr = float(res.get('cr_amount', 0))
            
            # Adjust for account natural balance (Dr vs Cr accounts)
            if coa.dr_cr == 'Dr':
                # Debit accounts: Dr increases balance, Cr decreases it
                balance += (dr - cr)
            else:
                # Credit accounts: Cr increases balance, Dr decreases it
                balance += (cr - dr)
            
            res['net_amount'] = round(balance, 2)
        
        results.append(res)

    return results


def get_job_ledger_statement_response(job, start_date, end_date, user):
    respone = []
    res_obj = {}

    # Calculate opening balance for this job before start_date
    opening_balance = calculate_opening_balance(None, start_date, user, job=job)

    cost_entrys = CostEntry.objects.filter(
        invoice__date__range=[start_date, end_date],
        is_included=True,
        invoice__company__users__email=user.email
    ).order_by('created_at')

    cost_entrys = cost_entrys.filter(invoice__job=job)

    for cost_entry in cost_entrys:
        if cost_entry.invoice:
            res_obj = {
                "account": cost_entry.invoice.client_name.name if cost_entry.invoice and cost_entry.invoice.client_name else "",
                "date": cost_entry.invoice.date if cost_entry.invoice else cost_entry.created_at,
                "currency": cost_entry.invoice.currency_sar if cost_entry.invoice else cost_entry.currency,
                "invoice_number": cost_entry.invoice.invoice_number if cost_entry.invoice else '',
                "vat_percent": 0,
                "fcy_amount": 0,
                "vat_amount": 0,
                "amount": 0,
                "dr_amount": 0,
                "cr_amount": 0,
                "net_amount": 0,
                "type": "Invoice",
                "voucher": "",
                "charge": cost_entry.charge.name if cost_entry.charge else '',
                "party_account": cost_entry.invoice.party_account.name if cost_entry.invoice and cost_entry.invoice.party_account else '',
                "job_no": job.job_number,
                "narrations": cost_entry.invoice.narration if cost_entry.invoice else "",
                "branch": cost_entry.invoice.branch if cost_entry.invoice else "",
                "language_name": ""
            }

            if cost_entry.invoice.invoice_type == 'Sales':
                fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                amount = float(cost_entry.amount if cost_entry.amount else 0.0)
                vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                vat_amount = float((vat_percent * amount) / 100)
                total_amount = float(amount + vat_amount)
                res_obj['vat_percent'] = vat_percent
                res_obj['fcy_amount'] = fcy_amount
                res_obj['amount'] = amount
                res_obj['vat_amount'] = vat_amount
                res_obj['cr_amount'] = total_amount
                res_obj['net_amount'] = total_amount

                if not (res_obj["dr_amount"] == 0 and res_obj["cr_amount"] == 0):
                    respone.append(res_obj)
            else:
                fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                amount = float(cost_entry.amount if cost_entry.amount else 0.0)
                vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                vat_amount = float((vat_percent * amount) / 100)
                total_amount = float(amount + vat_amount)
                res_obj['vat_percent'] = vat_percent
                res_obj['fcy_amount'] = fcy_amount
                res_obj['amount'] = amount
                res_obj['vat_amount'] = vat_amount
                res_obj['dr_amount'] = total_amount
                res_obj['net_amount'] = total_amount

                if not (res_obj["dr_amount"] == 0 and res_obj["cr_amount"] == 0):
                    respone.append(res_obj)

    voucher_accounts = AccountDetails.objects.filter(
        vouchers__date__range=[start_date, end_date],
        vouchers__company__users__email=user.email
    )

    account_details = voucher_accounts.filter(vouchers__job=job)

    for acc in account_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()

        fcy_amount = float(acc.fcy_amount if acc.fcy_amount else 0.0)

        # ── FIXED: use taxable_amount + tax_amount ──
        taxable      = Decimal(acc.taxable_amount or "0.00")
        tax_amt      = Decimal(acc.tax_amount     or "0.00")
        base         = Decimal(acc.amount_sar     or "0.00")
        total_dec    = (taxable + tax_amt) if taxable else base
        total_amount = float(total_dec)

        vat_percent  = float(acc.tax_group_code if acc.tax_group_code else 0.0)
        vat_amount   = float(tax_amt)
        amount       = float(taxable if taxable else base)
        # ────────────────────────────────────────────

        if acc.dr_cr == 'Cr':
            res_obj = {
                "account": job.client_name.name if job.client_name else '',
                "date": acc.vouchers.date if acc.vouchers.date else '',
                "currency": acc.currency,
                "invoice_number": "",
                "vat_percent": vat_percent,
                "fcy_amount": fcy_amount,
                "vat_amount": vat_amount,
                "amount": amount,
                "dr_amount": 0,
                "cr_amount": total_amount,   # ← now includes VAT
                "net_amount": 0,
                "charge": acc.charge.name if acc.charge else '',
                "type": acc.vouchers.voucher_type + " Voucher",
                "voucher": acc.vouchers.voucher_number if acc.vouchers else "",
                "party_account": party_account.name if party_account else '',
                "job_no": job.job_number,
                "narrations": acc.narration,
                "branch": acc.vouchers.branch if acc.vouchers else "",
                "language_name": ""
            }
        else:
            res_obj = {
                "account": job.client_name.name if job.client_name else '',
                "date": acc.vouchers.date if acc.vouchers.date else '',
                "currency": acc.currency,
                "invoice_number": "",
                "vat_percent": vat_percent,
                "fcy_amount": fcy_amount,
                "vat_amount": vat_amount,
                "amount": amount,
                "dr_amount": total_amount,   # ← now includes VAT
                "cr_amount": 0,
                "net_amount": 0,
                "charge": acc.charge.name if acc.charge else '',
                "type": acc.vouchers.voucher_type + " Voucher",
                "voucher": acc.vouchers.voucher_number if acc.vouchers else "",
                "party_account": party_account.name if party_account else '',
                "job_no": job.job_number,
                "narrations": acc.narration,
                "branch": acc.vouchers.branch if acc.vouchers else "",
                "language_name": ""
            }

        if not (res_obj["dr_amount"] == 0 and res_obj["cr_amount"] == 0):
            respone.append(res_obj)

    respone = sorted(respone, key=lambda obj: obj['date'])

    # Add opening balance row as the first entry
    opening_row = {
        "account": job.client_name.name if job.client_name else job.job_number,
        "date": start_date,
        "currency": "SAR",
        "invoice_number": "",
        "vat_percent": 0,
        "fcy_amount": 0,
        "vat_amount": 0,
        "amount": 0,
        "dr_amount": max(opening_balance, 0),
        "cr_amount": max(-opening_balance, 0),
        "net_amount": opening_balance,
        "type": "Opening Balance",
        "voucher": "",
        "charge": "",
        "party_account": "",
        "job_no": job.job_number,
        "narrations": "Opening balance brought forward",
        "branch": "",
        "language_name": ""
    }

    respone.insert(0, opening_row)

    # Calculate running balance starting from opening balance
    balance = opening_balance
    results = []

    for res in respone:
        if res['type'] == "Opening Balance":
            # Opening row already has correct dr/cr/net — just ensure it's set
            res['net_amount'] = round(balance, 2)
        else:
            dr = float(res.get('dr_amount', 0))
            cr = float(res.get('cr_amount', 0))
            balance += (dr - cr)
            
            res['net_amount'] = round(balance, 2)
        
        results.append(res)

    return results


def get_sundry_creditors_coa_response(coa, start_date, end_date, user):

    invoices = Invoices.objects.filter(date__range=[start_date, end_date], invoice_type='Purchase', company__users__email=user.email).order_by('date')
    respone =[]
    res_obj={}
    for invoice in invoices:
        cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id, is_included=True)
        
        for cost_entry in cost_entrys:

            res_obj = {
                "account":invoice.client_name.name if invoice.client_name else "",
                "date":invoice.date,
                "currency":invoice.currency_sar,
                "invoice_number":invoice.invoice_number,
                "vat_percent":0,
                "fcy_amount":0,
                "vat_amount":0,
                "amount":0,
                "dr_amount":0,
                "cr_amount":0,
                "net_amount":0,
                "type":"Invoice",
                "voucher":"",
                "party_account":invoice.party_account.name if invoice.party_account else "",
                "job_no":invoice.job.job_number if invoice.job.job_number else "",
                "narrations":invoice.narration if invoice.narration else "",
                "branch":invoice.branch if invoice.branch else "",
                "language_name":coa.language_name if coa.language_name else ""
                }

            fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            vat_amount = float((vat_percent * amount)/100)
            total_amount = float(amount + vat_amount)

            res_obj['vat_percent']= vat_percent
            res_obj['fcy_amount'] = fcy_amount
            res_obj['amount'] = amount
            res_obj['vat_amount'] = vat_amount
            res_obj['cr_amount']=total_amount
            res_obj['net_amount']=total_amount

            if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
                respone.append(res_obj)
    
    coa_account_details = AccountDetails.objects.filter(vouchers__date__range=[start_date, end_date], vouchers__company__users__email=user.email)
    account_details = coa_account_details.exclude(vouchers__voucher_type="Receipt").exclude(vouchers__voucher_type="CreditNote")
    direct_input_details = account_details.filter(ac_name='429', ac_name_type='coa') 
    account_details = account_details.exclude(ac_name='430', ac_name_type='coa').exclude(ac_name='429', ac_name_type='coa')
    account_details = account_details.union(direct_input_details)
    
    for acc in account_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()
            
        res_obj = {
                "account":coa.name,
                "date":acc.vouchers.date if acc.vouchers.date else '',
                "currency":acc.currency,
                "invoice_number":"",
                "vat_percent":0,
                "fcy_amount":0,
                "vat_amount":0,
                "amount":0,
                "dr_amount":0,
                "cr_amount":0,
                "net_amount":0,
                "type": acc.vouchers.voucher_type + " Voucher",
                "voucher":acc.vouchers.voucher_number if acc.vouchers else "",
                "party_account": party_account.name if party_account else '',
                "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
                "narrations": acc.narration,
                "branch":acc.vouchers.branch if acc.vouchers else "",
                "language_name":coa.language_name if coa.language_name else ""
                }
        fcy_amount_str = acc.fcy_amount if acc.fcy_amount else "0.0"
        if '.' in fcy_amount_str:
            fcy_amount_str_without_extra_decimal = fcy_amount_str.replace('.', '', 1)
            fcy_amount = float(fcy_amount_str_without_extra_decimal)
        else:
            fcy_amount = float(fcy_amount_str)
        amount=float(acc.amount_sar if acc.amount_sar else 0.0)
        vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
        vat_amount = float((vat_percent * amount)/100)
        total_amount = float(vat_amount)
        
        # if acc.ac_name == '429' and acc.ac_name_type == 'coa':
        #     total_amount = amount
        
        res_obj['vat_percent']= vat_percent
        res_obj['fcy_amount'] = fcy_amount
        res_obj['amount'] = amount
        res_obj['vat_amount'] = vat_amount
        
        if acc.dr_cr == 'Cr':
            if not acc.vouchers.voucher_type == 'DebitNote':
                res_obj['cr_amount']=total_amount
        else:
            if not acc.vouchers.voucher_type == 'Payment':
                res_obj['dr_amount']=total_amount
        
        res_obj['net_amount']=total_amount

        if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
            respone.append(res_obj)

    # ── NEW: Payment vouchers on Organization (supplier) account ─────────────
    payment_details = AccountDetails.objects.filter(
        vouchers__date__range=[start_date, end_date],
        vouchers__company__users__email=user.email,
        ac_name_type='organization',
        vouchers__voucher_type__in=['Payment', 'DebitNote']  # ← add DebitNote
    )

    for acc in payment_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()

        org = Organization.objects.filter(id=acc.ac_name).first()

        res_obj = {
            "account": org.name if org else acc.ac_name,
            "date": acc.vouchers.date if acc.vouchers.date else '',
            "currency": acc.currency,
            "invoice_number": "",
            "vat_percent": 0,
            "fcy_amount": 0,
            "vat_amount": 0,
            "amount": 0,
            "dr_amount": 0,
            "cr_amount": 0,
            "net_amount": 0,
            "type": acc.vouchers.voucher_type + " Voucher",  # ← dynamic type
            "voucher": acc.vouchers.voucher_number if acc.vouchers else "",
            "party_account": party_account.name if party_account else '',
            "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
            "narrations": acc.narration,
            "branch": acc.vouchers.branch if acc.vouchers else "",
            "language_name": coa.language_name if coa.language_name else ""
        }

        amount = float(acc.amount_sar if acc.amount_sar else 0.0)
        res_obj['amount'] = amount

        if acc.dr_cr == 'Dr':
            res_obj['dr_amount'] = amount  # Payment/DebitNote = debit creditor (we paid / supplier owes us more)
        else:
            res_obj['cr_amount'] = amount  # supplier owes us

        res_obj['net_amount'] = amount

        if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:
            respone.append(res_obj)
    # ── END NEW ──────────────────────────────────────────────────────────────

    balance = 0
    results = []
    for res in respone:
        balance = float(balance) + float(float(res['cr_amount']) - float(res['dr_amount']))
        res['net_amount'] = balance
        results.append(res)
        
    return results


def get_sundry_debtors_coa_response(coa, start_date, end_date, user):

    invoices = Invoices.objects.filter(date__range=[start_date, end_date], invoice_type='Sales', company__users__email=user.email).order_by('date')
    respone =[]
    res_obj={}
    for invoice in invoices:
        cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id, is_included=True)
        
        for cost_entry in cost_entrys:
            res_obj = {
                "account":invoice.client_name.name if invoice.client_name else "",
                "date":invoice.date,
                "currency":invoice.currency_sar,
                "invoice_number":invoice.invoice_number,
                "vat_percent":0,
                "fcy_amount":0,
                "vat_amount":0,
                "amount":0,
                "dr_amount":0,
                "cr_amount":0,
                "net_amount":0,
                "type":"Invoice",
                "voucher":"",
                "party_account":invoice.party_account.name if invoice.party_account else "",
                "job_no":invoice.job.job_number if invoice.job.job_number else "",
                "narrations":invoice.narration if invoice.narration else "",
                "branch":invoice.branch if invoice.branch else "",
                "language_name":coa.language_name if coa.language_name else ""
                }
            
            fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            vat_amount = float((vat_percent * amount)/100)
            total_amount = float(amount + vat_amount)
            res_obj['vat_percent']= vat_percent
            res_obj['fcy_amount'] = fcy_amount
            res_obj['amount'] = amount
            res_obj['vat_amount'] = vat_amount
            res_obj['dr_amount']=total_amount
            res_obj['net_amount']=total_amount   

            if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
                respone.append(res_obj)

    coa_account_details = AccountDetails.objects.filter(vouchers__date__range=[start_date, end_date], vouchers__company__users__email=user.email)
    account_details = coa_account_details
    direct_output_details = account_details.filter(ac_name='430', ac_name_type='coa').exclude(vouchers__voucher_type="Payment").exclude(vouchers__voucher_type="DebitNote")

    for acc in direct_output_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()
            
        res_obj = {
            "account":coa.name,
            "date":acc.vouchers.date if acc.vouchers.date else '',
            "currency":acc.currency,
            "invoice_number":"",
            "vat_percent":0,
            "fcy_amount":0,
            "vat_amount":0,
            "amount":0,
            "dr_amount":0,
            "cr_amount":0,
            "net_amount":0,
            "type": acc.vouchers.voucher_type + " Voucher",
            "voucher":acc.vouchers.voucher_number if acc.vouchers else "",
            "party_account": party_account.name if party_account else '',
            "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
            "narrations": acc.narration,
            "branch":acc.vouchers.branch if acc.vouchers else "",
            "language_name":coa.language_name if coa.language_name else ""
            }
        fcy_amount_str = acc.fcy_amount if acc.fcy_amount else "0.0"
        if '.' in fcy_amount_str:
            fcy_amount_str_without_extra_decimal = fcy_amount_str.replace('.', '', 1)
            fcy_amount = float(fcy_amount_str_without_extra_decimal)
        else:
            fcy_amount = float(fcy_amount_str)
        amount=float(acc.amount_sar if acc.amount_sar else 0.0)
        vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
        vat_amount = float((vat_percent * amount)/100)
        total_amount = float(vat_amount)
        
        # if acc.ac_name == '430' and acc.ac_name_type == 'coa':
        #     total_amount = amount
        
        res_obj['vat_percent']= vat_percent
        res_obj['fcy_amount'] = fcy_amount
        res_obj['amount'] = amount
        res_obj['vat_amount'] = vat_amount
        
        if acc.dr_cr == 'Cr':
            if not acc.vouchers.voucher_type == 'Receipt':
                res_obj['cr_amount']=total_amount
        else:
            if not acc.vouchers.voucher_type == 'CreditNote':
                res_obj['dr_amount']=total_amount
        
        res_obj['net_amount']=total_amount
        
        if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
            respone.append(res_obj)

    # ── NEW: Receipt vouchers on Organization (customer) account ─────────────
    # ── NEW: Receipt & CreditNote vouchers on Organization (customer) account ────
    receipt_details = account_details.filter(
        ac_name_type='organization',
        vouchers__voucher_type__in=['Receipt', 'CreditNote']  # ← add CreditNote
    )

    for acc in receipt_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()

        org = Organization.objects.filter(id=acc.ac_name).first()

        res_obj = {
            "account": org.name if org else acc.ac_name,
            "date": acc.vouchers.date if acc.vouchers.date else '',
            "currency": acc.currency,
            "invoice_number": "",
            "vat_percent": 0,
            "fcy_amount": 0,
            "vat_amount": 0,
            "amount": 0,
            "dr_amount": 0,
            "cr_amount": 0,
            "net_amount": 0,
            "type": acc.vouchers.voucher_type + " Voucher",  # ← dynamic type
            "voucher": acc.vouchers.voucher_number if acc.vouchers else "",
            "party_account": party_account.name if party_account else '',
            "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
            "narrations": acc.narration,
            "branch": acc.vouchers.branch if acc.vouchers else "",
            "language_name": coa.language_name if coa.language_name else ""
        }

        amount = float(acc.amount_sar if acc.amount_sar else 0.0)
        res_obj['amount'] = amount

        if acc.dr_cr == 'Cr':
            res_obj['cr_amount'] = amount  # Receipt/CreditNote = credit debtor
        else:
            res_obj['dr_amount'] = amount

        res_obj['net_amount'] = amount

        if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:
            respone.append(res_obj)
# ── END NEW ──────────────────────────────────────────────────────────────
    # ── END NEW ──────────────────────────────────────────────────────────────

    balance = 0
    results = []
    for res in respone:
        balance = float(balance) + float(float(res['dr_amount']) - float(res['cr_amount']))
        res['net_amount'] = balance
        results.append(res)
        
    return results


class GeneralledgerViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Coa.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        coa_id = request.query_params.get('coa', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date',None)
        job_id = request.query_params.get('job', None)
        
        if coa_id is not None and Coa.objects.filter(id=coa_id).exists():
            coa = Coa.objects.filter(id=coa_id).first()
            if coa.name == 'VAT INPUT': # For VAT INPUT 429
                response = get_vat_input_coa_response(coa, start_date, end_date, request.user)
            elif coa.name == 'VAT OUTPUT': # For VAT OUTPUT 430
                response = get_vat_output_coa_response(coa, start_date, end_date, request.user)
            elif coa.name == 'SUNDRY CREDITORS': # For Sundry Creditors 405
                response = get_sundry_creditors_coa_response(coa, start_date, end_date, request.user)
            elif coa.name == 'SUNDRY DEBTORS': # For Sundry Debtors 406
                response = get_sundry_debtors_coa_response(coa, start_date, end_date, request.user)
            else:     
                response = get_other_coa_response(coa, start_date, end_date, request.user)
            
            if job_id is not None and Job.objects.filter(id=job_id).exists():
                job =  Job.objects.filter(id=job_id).first()
                res_ = []
                for res in response:
                    if res['job_no'] == job.job_number:
                        res_.append(res)
                response = res_ 
                               
            return Response(response)
        
        if coa_id is None and job_id is not None and Job.objects.filter(id=job_id).exists():
            job =  Job.objects.filter(id=job_id).first()
            response = get_job_ledger_statement_response(job, start_date, end_date, request.user)
            return Response(response)

        
        return Response([])


def get_account_invoices_response(id, user):

    invoices = Invoices.objects.filter(company__users__email=user.email).filter(Q(client_name__id=id) | Q(consignee_name__id=id) | Q(party_account__id=id)).order_by('date')
    respone =[]
    res_obj={}
    for invoice in invoices:
        res_obj = {
                "id":invoice.id,
                "date":invoice.date,
                "amount":0,
                "invoice_number":invoice.invoice_number,
                "payment_status":invoice.payment_status,
                "paid_amount":invoice.paid_amount,
                "type":invoice.invoice_type
                }
        
        cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id)
        
        total_amount = 0

        for cost_entry in cost_entrys:
            fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            total_amount += float(amount)+float((vat_percent * amount)/100)
        
        res_obj['amount']=total_amount  
        respone.append(res_obj)
        
    return respone

class GetCoaInvoicesViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
   
    queryset = Coa.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        acc_id = request.query_params.get('account', None)
    
        if acc_id:
            response = get_account_invoices_response(acc_id, request.user)
            return Response(response)
        else:
            return Response([])


def get_account_payment_statement(invoices, org_id, start_date, end_date, payment_status):
    response =[]
    for invoice in invoices:
        res_obj = {
            "account":invoice.client_name.name if invoice.client_name else "",
            "date":invoice.date,
            "currency":invoice.currency_sar,
            "type":"Invoice",
            "voucher_number":"",
            "invoice_number":invoice.supplier_inv_number,
            "net_amount":0,
            "cr_amount": 0,
            "dr_amount":0,
            "party_account":invoice.party_account.name if invoice.party_account else "",
            "job_no":invoice.job.job_number if invoice.job.job_number else "",
            "narrations":invoice.narration if invoice.narration else "",
            "branch":invoice.branch if invoice.branch else "",
            # "language_name":coa.language_name if coa.language_name else ""
        }
        cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id)
        total_amount = 0

        for cost_entry in cost_entrys:
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            total_amount += (amount)+(float((vat_percent * amount)/100))
        res_obj["dr_amount"] = total_amount
        res_obj['net_amount']= float(res_obj['dr_amount']) - float(res_obj['cr_amount'])  
        response.append(res_obj)
    
    # try:
    vouchers = Vouchers.objects.filter(party_account=org_id, party_account_type='organization', date__range=[start_date, end_date])
    payment_vouchers = vouchers.filter(voucher_type='Payment')
    
    if not payment_status == 'Unpaid':
        for voucher in payment_vouchers:
            voucher_accounts = AccountDetails.objects.filter(vouchers=voucher).exclude(ac_name='260', ac_name_type='coa').exclude(narration__contains="BANK CHARGES")  # excluding bank charges
            account = Organization.objects.filter(id=voucher.party_account).first()
            total_amount = 0
            dr_amount = 0
            cr_amount = 0
            res_obj = {
                "account": account.name if account else "",
                "date":voucher.date,
                "currency":voucher.currency,
                "type": voucher.voucher_type + " Voucher",
                "voucher_number":voucher.id,
                "invoice_number":"",
                "cr_amount":  0,
                "dr_amount": 0,
                "net_amount": 0,
                "party_account":account.name if account else "",
                "job_no": voucher.job.job_number if voucher.job else "",
                "narrations":voucher.naration if voucher.naration else "",
                "branch":voucher.branch if voucher.branch else "",
            }
            for acc in voucher_accounts:
                amount=float(acc.amount_sar if acc.amount_sar else 0.0)
                vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
                vat_amount = float((vat_percent * amount)/100)
                total_amt = float(amount  + vat_amount)

                if acc.dr_cr == "Cr":
                    cr_amount = float(cr_amount) + total_amt

            total_amount = float(dr_amount) - float(cr_amount)
            res_obj['dr_amount'] =dr_amount
            res_obj['cr_amount'] = cr_amount
            res_obj['net_amount'] = total_amount
            response.append(res_obj)
        
    debit_credit_vouchers = vouchers.filter(Q(voucher_type='CreditNote') | Q(voucher_type='DebitNote'), voucher_for='Vendor')
    for voucher in debit_credit_vouchers:
        voucher_accounts = AccountDetails.objects.filter(vouchers=voucher)
        account = Organization.objects.filter(id=voucher.party_account).first()
        total_amount = 0
        dr_amount = 0
        cr_amount = 0 
        res_obj = {
            "account": account.name if account else "",
            "date":voucher.date,
            "currency":voucher.currency,
            "type": voucher.voucher_type + " Voucher",
            "voucher_number":voucher.id,
            "invoice_number":"",
            "cr_amount":  0,
            "dr_amount": 0,
            "net_amount": 0,
            "party_account":account.name if account else "",
            "job_no": voucher.job.job_number if voucher.job else "",
            "narrations":voucher.naration if voucher.naration else "",
            "branch":voucher.branch if voucher.branch else "",
        }
        for acc in voucher_accounts:
            amount=float(acc.amount_sar if acc.amount_sar else 0.0)
            vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
            vat_amount = float((vat_percent * amount)/100)
            total_amt = float(amount  + vat_amount)

            if acc.dr_cr == "Cr":
                cr_amount = float(cr_amount) + total_amt

        total_amount = float(dr_amount) - float(cr_amount)
        res_obj['dr_amount'] =dr_amount
        res_obj['cr_amount'] = cr_amount
        res_obj['net_amount'] = total_amount
        response.append(res_obj)
    # except:
    #     pass
        
    return response


def get_account_receivable_statement(invoices, org_id, start_date, end_date, payment_status):   
    
    response=[]
    for invoice in invoices:
        res_obj = {
            "account":invoice.client_name.name if invoice.client_name else "",
            "date":invoice.date,
            "currency":invoice.currency_sar,
            "type": "Invoice",
            "voucher_number": "",
            "invoice_number":invoice.invoice_number,
            "cr_amount": 0,
            "dr_amount":0,
            "net_amount":0,
            "party_account":invoice.party_account.name if invoice.party_account else "",
            "job_no":invoice.job.job_number if invoice.job.job_number else "",
            "narrations":invoice.narration if invoice.narration else "",
            "branch":invoice.branch if invoice.branch else "",
            # "language_name":coa.language_name if coa.language_name else ""
        }
        cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id)
        # print(cost_entrys)
        # if invoice.invoice_type=='Sales':
        total_amount = 0

        for cost_entry in cost_entrys:
            amount=float(cost_entry.amount if cost_entry.amount else 0.0)
            vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
            total_amount += (amount)+(float((vat_percent * amount)/100))
        
        res_obj['cr_amount'] = total_amount
        res_obj['net_amount']= float(res_obj['dr_amount']) - float(res_obj['cr_amount'])   
        response.append(res_obj)
    
    # try:
    vouchers = Vouchers.objects.filter(party_account=org_id, party_account_type='organization', date__range=[start_date, end_date])
    
    if not payment_status == 'Unpaid':
        receipt_vouchers = vouchers.filter(voucher_type='Receipt')
        
        for voucher in receipt_vouchers:
            voucher_accounts = AccountDetails.objects.filter(vouchers=voucher)
            account = Organization.objects.filter(id=voucher.party_account).first()
            total_amount = 0
            dr_amount = 0
            cr_amount = 0

            res_obj = {
                "account": account.name if account else "",
                "date":voucher.date,
                "currency":voucher.currency,
                "type": voucher.voucher_type + " Voucher",
                "voucher_number": voucher.id,
                "invoice_number":"",
                "cr_amount":  0,
                "dr_amount": 0,
                "net_amount": 0,
                "party_account":account.name if account else "",
                "job_no": voucher.job.job_number if voucher.job else "",
                "narrations":voucher.naration if voucher.naration else "",
                "branch":voucher.branch if voucher.branch else "",
            }

            for acc in voucher_accounts:
                amount=float(acc.amount_sar if acc.amount_sar else 0.0)
                vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
                vat_amount = float((vat_percent * amount)/100)
                total_amt = float(amount  + vat_amount)

                if acc.dr_cr == "Dr":
                    dr_amount = float(dr_amount) + total_amt

            total_amount = float(dr_amount) - float(cr_amount)
            res_obj['dr_amount'] =dr_amount
            res_obj['cr_amount'] = cr_amount
            res_obj['net_amount'] = total_amount
            response.append(res_obj)
        
    debit_credit_vouchers = vouchers.filter(Q(voucher_type='CreditNote') | Q(voucher_type='DebitNote'), voucher_for='Customer')
    for voucher in debit_credit_vouchers:
        voucher_accounts = AccountDetails.objects.filter(vouchers=voucher)
        account = Organization.objects.filter(id=voucher.party_account).first() 
        total_amount = 0
        dr_amount = 0
        cr_amount = 0
        res_obj = {
            "account": account.name if account else "",
            "date":voucher.date,
            "currency":voucher.currency,
            "type": voucher.voucher_type + " Voucher",
            "voucher_number": voucher.id,
            "invoice_number":"",
            "cr_amount":  0,
            "dr_amount": 0,
            "net_amount": 0,
            "party_account":account.name if account else "",
            "job_no": voucher.job.job_number if voucher.job else "",
            "narrations":voucher.naration if voucher.naration else "",
            "branch":voucher.branch if voucher.branch else "",
        }
        for acc in voucher_accounts:
            amount=float(acc.amount_sar if acc.amount_sar else 0.0)
            vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
            vat_amount = float((vat_percent * amount)/100)
            total_amt = float(amount  + vat_amount)

            if acc.dr_cr == "Dr":
                dr_amount = float(dr_amount) + total_amt

        total_amount = float(dr_amount) - float(cr_amount)
        res_obj['dr_amount'] =dr_amount
        res_obj['cr_amount'] = cr_amount
        res_obj['net_amount'] = total_amount
        response.append(res_obj)
    # except:
    #     pass       
    return response

class AccountStatementViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Invoices.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        organization_id = request.query_params.get('organization', None)
        type = request.query_params.get('type', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date',None)
        payment = request.query_params.get('payment',None)
        
        invoices = Invoices.objects.filter(Q(consignee_name=organization_id) | Q(client_name=organization_id) | Q(party_account=organization_id),date__range=[start_date, end_date]).order_by('date')
        if payment is not None:
            invoices = invoices.filter(payment_status=payment)
        response =[]
        res_obj = {}
        if type =='receive':
            invoices= invoices.filter(invoice_type='Sales')
            response= get_account_receivable_statement(invoices, organization_id, start_date, end_date, payment)
        elif type =='pay':
            invoices= invoices.filter(invoice_type='Purchase', party_account=organization_id)
            response = get_account_payment_statement(invoices, organization_id, start_date, end_date, payment)
        elif type == 'both':
            invoices_sales = invoices.filter(invoice_type='Sales')
            invoices_purchases = invoices.filter(invoice_type='Purchase', party_account=organization_id)
            response1 = get_account_receivable_statement(invoices_sales, organization_id, start_date, end_date, payment)
            response2 = get_account_payment_statement(invoices_purchases, organization_id, start_date, end_date, payment)
            response = response + response1 + response2
            
        response = sorted(response, key=lambda obj: obj['date']) 
        balance = 0
        results = []

        for res in response:
            b = Decimal(balance)
            da = Decimal(res['dr_amount'])
            ca = Decimal(res['cr_amount'])
            balance = (b + da - ca).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
            res['net_amount'] = balance
            results.append(res)

        return Response(results)


def get_coa_sheet_response(coa, start_date, end_date, user):
    respone =[]
    res_obj={}

    cost_entrys = CostEntry.objects.filter(Q(charge__coa=coa) | Q(invoice__party_account__coa=coa), invoice__date__range=[start_date, end_date], is_included=True, invoice__company__users__email=user.email).exclude(invoice=None).order_by('created_at')
    for cost_entry in cost_entrys:
        if cost_entry.invoice:
            res_obj = {
                    "account":cost_entry.invoice.client_name.name if cost_entry.invoice and cost_entry.invoice.client_name else "",
                    "date":cost_entry.invoice.date if cost_entry.invoice else cost_entry.created_at,
                    "currency":cost_entry.invoice.currency_sar if cost_entry.invoice else cost_entry.currency,
                    "invoice_number":cost_entry.invoice.invoice_number if cost_entry.invoice else '',
                    "vat_percent":0,
                    "fcy_amount":0,
                    "vat_amount":0,
                    "amount":0,
                    "dr_amount":0,
                    "cr_amount":0,
                    "net_amount":0,
                    "type":"Invoice",
                    "voucher":"",
                    "charge": cost_entry.charge.name if cost_entry.charge else '',
                    "party_account":cost_entry.invoice.party_account.name if cost_entry.invoice and cost_entry.invoice.party_account else '',
                    "job_no":cost_entry.invoice.job.job_number if cost_entry.invoice and cost_entry.invoice.job else "",
                    "narrations":cost_entry.invoice.narration if cost_entry.invoice else "",
                    "branch":cost_entry.invoice.branch if cost_entry.invoice else "",
                    "language_name":coa.language_name if coa.language_name else ""
                    }
            

            if cost_entry.invoice.invoice_type=='Sales':
                fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                amount=float(cost_entry.amount if cost_entry.amount else 0.0)
                vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                vat_amount = float((vat_percent * amount)/100)
                total_amount = float(amount)
                res_obj['vat_percent']= vat_percent
                res_obj['fcy_amount'] = fcy_amount
                res_obj['amount'] = amount
                res_obj['vat_amount'] = vat_amount
                res_obj['cr_amount']=total_amount
                res_obj['net_amount']=total_amount   
                
                if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
                    respone.append(res_obj)
            else:
                fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                amount=float(cost_entry.amount if cost_entry.amount else 0.0)
                vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                vat_amount = float((vat_percent * amount)/100)
                total_amount = float(amount)
                res_obj['vat_percent']= vat_percent
                res_obj['fcy_amount'] = fcy_amount
                res_obj['amount'] = amount
                res_obj['vat_amount'] = vat_amount
                res_obj['dr_amount']=total_amount
                res_obj['net_amount']=total_amount   
                
                if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
                    respone.append(res_obj)
    

    voucher_accounts = AccountDetails.objects.filter(vouchers__date__range=[start_date, end_date], vouchers__company__users__email=user.email)
    coa_account_details = voucher_accounts.filter(Q(ac_name='{0}'.format(coa.id), ac_name_type='coa') | Q(charge__coa=coa))
    organizations = Organization.objects.filter(coa=coa, company__users__email=user.email)
    # organizations = list(map(str, organizations))
    for org in organizations:
        org_account_details = voucher_accounts.filter(ac_name='{0}'.format(org.id), ac_name_type='organization')
        coa_account_details = coa_account_details.union(org_account_details)

    for acc in coa_account_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()
        
        if acc.dr_cr == 'Cr':
            res_obj = {
                "account":coa.name,
                "date":acc.vouchers.date if acc.vouchers.date else '',
                "currency":acc.currency,
                "invoice_number":"",
                "vat_percent":0,
                "fcy_amount":0,
                "vat_amount":0,
                "amount":0,
                "dr_amount":0,
                "cr_amount":0,
                "net_amount":0,
                "charge": acc.charge.name if acc.charge else '',
                "type": acc.vouchers.voucher_type + " Voucher",
                "voucher":acc.vouchers.voucher_number if acc.vouchers else "",
                "party_account": party_account.name if party_account else '',
                "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
                "narrations": acc.narration,
                "branch":acc.vouchers.branch if acc.vouchers else "",
                "language_name":coa.language_name if coa.language_name else ""
                }
            fcy_amount = float(acc.fcy_amount if acc.fcy_amount else 0.0)
            amount=float(acc.amount_sar if acc.amount_sar else 0.0)
            vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
            vat_amount = float((vat_percent * amount)/100)
            total_amount = float(amount)
            res_obj['vat_percent']= vat_percent
            res_obj['fcy_amount'] = fcy_amount
            res_obj['amount'] = amount
            res_obj['vat_amount'] = vat_amount
            res_obj['cr_amount']=total_amount
            res_obj['net_amount']=total_amount
            
            if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
                respone.append(res_obj)
        else:
            res_obj = {
                "account":coa.name,
                "date":acc.vouchers.date if acc.vouchers.date else '',
                "currency":acc.currency,
                "invoice_number":"",
                "vat_percent":0,
                "fcy_amount":0,
                "vat_amount":0,
                "amount":0,
                "dr_amount":0,
                "cr_amount":0,
                "net_amount":0,
                "charge": acc.charge.name if acc.charge else '',
                "type": acc.vouchers.voucher_type + " Voucher",
                "voucher":acc.vouchers.voucher_number if acc.vouchers else "",
                "party_account": party_account.name if party_account else '',
                "job_no": acc.vouchers.job.job_number if acc.vouchers and acc.vouchers.job else "",
                "narrations": acc.narration,
                "branch":acc.vouchers.branch if acc.vouchers else "",
                "language_name":coa.language_name if coa.language_name else ""
                }
            # fcy_amount = float(acc.fcy_amount if acc.fcy_amount else 0.0)
            fcy_amount_str = acc.fcy_amount if acc.fcy_amount else "0.0"
            # Check if the string contains a decimal point
            if '.' in fcy_amount_str:
                # If the string contains a decimal point, remove the extra decimal point and convert to float
                fcy_amount_str_without_extra_decimal = fcy_amount_str.replace('.', '', 1)  # Remove the first occurrence of the decimal point
                fcy_amount = float(fcy_amount_str_without_extra_decimal)
            else:
                # If the string does not contain a decimal point, convert to float directly
                fcy_amount = float(fcy_amount_str)
            amount=float(acc.amount_sar if acc.amount_sar else 0.0)
            vat_percent = float(acc.tax_group_code if acc.tax_group_code else 0.0)
            vat_amount = float((vat_percent * amount)/100)
            total_amount = float(amount)
            res_obj['vat_percent']= vat_percent
            res_obj['fcy_amount'] = fcy_amount
            res_obj['amount'] = amount
            res_obj['vat_amount'] = vat_amount
            res_obj['dr_amount']=total_amount
            res_obj['net_amount']=total_amount
            
            if not res_obj["dr_amount"] == 0 or not res_obj["cr_amount"] == 0:   
                respone.append(res_obj)
    
    respone = sorted(respone, key=lambda obj:obj['date'])      
    return respone


class SheetReportViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Coa.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        branch = request.query_params.get('branch', None)
        queryset = Coa.objects.filter(company__users__email=request.user.email).filter(Q(type='ASSET')| Q(type = 'EQUITY')| Q(type = 'LIABILITY'))

        #date_object = datetime.strptime(date, "%Y-%m-%d").date()

        # Calculate start time and end time for the given date
        #start_date = datetime.combine(date_object, datetime.min.time())
        #end_date = datetime.combine(date_object, datetime.max.time())

        response=[]
        for coa in queryset:
            amount=0
            dr_amount = 0
            cr_amount =0
            amounts = []
            if coa.id == 429: # For VAT INPUT
                amounts = get_vat_input_coa_response(coa, start_date, end_date, request.user)
            elif coa.id == 430: # For VAT OUTPUT
                amounts = get_vat_output_coa_response(coa, start_date, end_date, request.user)
            else:
                amounts = get_coa_sheet_response(coa, start_date, end_date, request.user)
            
            for amt in amounts:
                dr_amount += amt['dr_amount']
                cr_amount += amt['cr_amount']
                amount += float(float(amt['dr_amount']) - float(amt['cr_amount']))
    
            res_obj = {
                "type": coa.type,
                "account_name": coa.name,
                "group": coa.group.name,
                "total_dr_amount":dr_amount,
                "total_cr_amount":cr_amount,
                "total_amount":amount
            }
            
            response.append(res_obj)

        return Response(response, status=status.HTTP_200_OK)

def get_trial_balance_coa_response(coa, start_date, end_date, user):
    """
    Like get_coa_sheet_response but uses | instead of .union()
    to avoid Django ORM type mismatch errors that silently drop rows.
    """
    response = []

    # --- Invoice / CostEntry entries ---
    cost_entries = CostEntry.objects.filter(
        Q(charge__coa=coa) | Q(invoice__party_account__coa=coa),
        invoice__date__range=[start_date, end_date],
        is_included=True,
        invoice__company__users__email=user.email
    ).exclude(invoice=None).order_by('created_at')

    for cost_entry in cost_entries:
        invoice = cost_entry.invoice
        if not invoice:
            continue

        amount = float(cost_entry.amount or 0.0)
        fcy_amount = float(cost_entry.fcy_amount or 0.0)
        vat_percent = float(cost_entry.tax_group_code or 0.0)
        vat_amount = (vat_percent * amount) / 100
        total_amount = amount + vat_amount  # VAT added here (matches get_coa_sheet_response)

        is_sales = invoice.invoice_type == 'Sales'
        res_obj = {
            "account": invoice.client_name.name if invoice.client_name else "",
            "date": invoice.date,
            "currency": invoice.currency_sar,
            "invoice_number": invoice.invoice_number,
            "vat_percent": vat_percent,
            "fcy_amount": fcy_amount,
            "vat_amount": vat_amount,
            "amount": amount,
            "dr_amount": 0.0 if is_sales else total_amount,
            "cr_amount": total_amount if is_sales else 0.0,
            "net_amount": total_amount,
            "type": "Invoice",
            "voucher": "",
            "charge": cost_entry.charge.name if cost_entry.charge else '',
            "party_account": invoice.party_account.name if invoice.party_account else '',
            "job_no": invoice.job.job_number if invoice.job else "",
            "narrations": invoice.narration or "",
            "branch": invoice.branch or "",
            "language_name": coa.language_name or ""
        }

        if res_obj["dr_amount"] != 0 or res_obj["cr_amount"] != 0:
            response.append(res_obj)

    # --- Voucher / AccountDetails entries ---
    voucher_accounts = AccountDetails.objects.filter(
        vouchers__date__range=[start_date, end_date],
        vouchers__company__users__email=user.email
    )

    # FIX: Use | (pipe) not .union() to avoid type mismatch silently dropping rows
    coa_account_details = voucher_accounts.filter(
        Q(ac_name=str(coa.id), ac_name_type='coa') | Q(charge__coa=coa)
    )

    organizations = Organization.objects.filter(
        coa=coa,
        company__users__email=user.email
    )
    for org in organizations:
        org_details = voucher_accounts.filter(
            ac_name=str(org.id),
            ac_name_type='organization'
        )
        coa_account_details = coa_account_details | org_details  # FIX: was .union()

    for acc in coa_account_details:
        party_account = None
        if acc.vouchers.party_account:
            if acc.vouchers.party_account_type == 'coa':
                party_account = Coa.objects.filter(id=acc.vouchers.party_account).first()
            else:
                party_account = Organization.objects.filter(id=acc.vouchers.party_account).first()

        # FIX: handle fcy_amount that may be a string with extra decimal points
        fcy_amount_str = acc.fcy_amount or "0.0"
        if fcy_amount_str.count('.') > 1:
            fcy_amount_str = fcy_amount_str.replace('.', '', 1)
        fcy_amount = float(fcy_amount_str)

        amount = float(acc.amount_sar or 0.0)
        vat_percent = float(acc.tax_group_code or 0.0)
        vat_amount = (vat_percent * amount) / 100
        total_amount = amount + vat_amount  # VAT added here (matches get_coa_sheet_response)

        res_obj = {
            "account": coa.name,
            "date": acc.vouchers.date or '',
            "currency": acc.currency,
            "invoice_number": "",
            "vat_percent": vat_percent,
            "fcy_amount": fcy_amount,
            "vat_amount": vat_amount,
            "amount": amount,
            "dr_amount": 0.0 if acc.dr_cr == 'Cr' else total_amount,
            "cr_amount": total_amount if acc.dr_cr == 'Cr' else 0.0,
            "net_amount": total_amount,
            "charge": acc.charge.name if acc.charge else '',
            "type": acc.vouchers.voucher_type + " Voucher",
            "voucher": acc.vouchers.voucher_number or "",
            "party_account": party_account.name if party_account else '',
            "job_no": acc.vouchers.job.job_number if acc.vouchers.job else "",
            "narrations": acc.narration,
            "branch": acc.vouchers.branch or "",
            "language_name": coa.language_name or ""
        }

        if res_obj["dr_amount"] != 0 or res_obj["cr_amount"] != 0:
            response.append(res_obj)

    return response
    
class TrialBalanceViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Coa.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        branch = request.query_params.get('branch', None)
        queryset = Coa.objects.filter(company__users__email=request.user.email)

        response=[]
        for coa in queryset:
            total_amount=0
            dr_amount = 0
            cr_amount =0
            amount = []
            if coa.id == 429: # For VAT INPUT
                amount = get_vat_input_coa_response(coa, start_date, end_date, request.user)
            elif coa.id == 430: # For VAT OUTPUT
                amount = get_vat_output_coa_response(coa, start_date, end_date, request.user)
            else:
                amount = get_coa_sheet_response(coa, start_date, end_date, request.user)
            
            for amt in amount:
                dr_amount += amt['dr_amount']
                cr_amount += amt['cr_amount']
                total_amount += float(float(amt['dr_amount']) - float(amt['cr_amount']))
            # amount += int(response['net_amount'])
            
            res_obj = {
                "type": coa.type,
                "account_name": coa.name,
                "group": coa.group.name,
                "total_dr_amount":dr_amount,
                "total_cr_amount":cr_amount,
                "total_amount":total_amount
            }
            
            response.append(res_obj)

        return Response(response, status=status.HTTP_200_OK)

# job_voucher, job_invoice return related to job
class JobVoucherViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Vouchers.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)
    serializer_class = VouchersJobSerializer

    def list(self, request, *args, **kwargs):
        job = request.query_params.get('job', None)
        queryset = self.queryset.filter(job__id=job)
        serializers = self.serializer_class(queryset, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
class JobInvoiceViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Invoices.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)
    serializer_class = InvoiceJobSerializer

    def list(self, request, *args, **kwargs):
        job = request.query_params.get('job', None)
        queryset = self.queryset.filter(job__id=job)
        serializers = self.serializer_class(queryset, many=True)
        response = serializers.data

        # data = serializers.data

        # for invoice in queryset:
        #     cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id)
        #     total_amount = 0
        #     fcy_amount = 0
        #     for cost_entry in cost_entrys:
        #         fy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
        #         amount=float(cost_entry.amount if cost_entry.amount else 0.0)
        #         vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
        #         total_amount += (amount)+(float((vat_percent * amount)/100))
        #         fcy_amount = fcy_amount + fy_amount
            
        #     invoice['amount_sar'] = total_amount
        #     invoice['fc_amount'] = fcy_amount
        #     response.append(invoice)

        return Response(response, status=status.HTTP_200_OK)

# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.db.models import Sum, Q, Value, DecimalField
# from django.db.models.functions import Coalesce, Cast

class AccountsReceivableViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Accounts Receivable Statement
    URL: GET /api/account/receivable/?organization=ID_or_'all'&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    
    For single customer: organization=51
    For all customers: organization=all
    """
    permission_classes = (IsAuthenticated,)
    queryset = Invoices.objects.none()

    # ----------------------------
    # Helpers
    # ----------------------------
    def _parse_date(self, date_str):
        return datetime.strptime(date_str.split('T')[0], "%Y-%m-%d").date()

    def _invoice_total_with_tax(self, inv):
        cost_total = Decimal('0.00')

        for ce in inv.costentry_set.all():  # assuming related_name is default
            base = Decimal(str(ce.amount or '0.00'))
            rate = Decimal(str(ce.tax_group_code or '0.00'))
            tax = base * (rate / Decimal('100'))
            cost_total += base + tax

        if cost_total == 0:
            cost_total = Decimal(str(inv.amount_sar or '0.00'))

        return cost_total.quantize(Decimal('0.00'))

    def _sum_customer_credit_lines_for_vouchers(self, vouchers_qs):
        return (
            AccountDetails.objects.filter(vouchers__in=vouchers_qs, dr_cr='Cr')
            .exclude(amount_sar__isnull=True)
            .exclude(amount_sar='')  # ← exclude empty strings before Cast
            .aggregate(
                total=Coalesce(
                    Sum(Cast('amount_sar', output_field=models.DecimalField(max_digits=15, decimal_places=2))),
                    Value(Decimal('0.00'))
                )
            )['total']
            or Decimal('0.00')
        ).quantize(Decimal('0.00'))

    # ----------------------------
    # Main List
    # ----------------------------
    def list(self, request, *args, **kwargs):
        organization_id = request.query_params.get('organization')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not start_date_str or not end_date_str:
            return Response({"error": "start_date and end_date are required"}, status=400)

        try:
            start_date = self._parse_date(start_date_str)
            end_date = self._parse_date(end_date_str)
        except ValueError:
            return Response({"error": "Invalid date format. Expected YYYY-MM-DD"}, status=400)

        company_filter = Q(company__users=request.user)

        if organization_id == 'all':
            # ───────────────────────────────────────────────
            # Summary for ALL customers (clients)
            # ───────────────────────────────────────────────
            customers = Organization.objects.filter(
                type__contains=['Client'],              # FIXED: correct lookup for ArrayField
                company__users=request.user
            ).distinct().order_by('name')

            summary_rows = []
            total_inv_amount = Decimal('0.00')
            total_received_amount = Decimal('0.00')
            total_balance = Decimal('0.00')

            for cust in customers:
                # Opening balance (before start_date)
                opening_invoices_qs = Invoices.objects.filter(
                    client_name=cust,
                    invoice_type='Sales',
                    date__date__lt=start_date
                ).filter(company_filter)

                opening_invoice_total = sum(self._invoice_total_with_tax(inv) for inv in opening_invoices_qs)

                opening_receipts_qs = Vouchers.objects.filter(
                    party_account=str(cust.id),  # assuming party_account is CharField storing str(id)
                    party_account_type='organization',
                    voucher_type='Receipt',
                    date__date__lt=start_date
                ).filter(company_filter)

                opening_receipt_total = self._sum_customer_credit_lines_for_vouchers(opening_receipts_qs)

                opening_creditnotes_qs = Vouchers.objects.filter(
                    party_account=str(cust.id),
                    party_account_type='organization',
                    voucher_type='CreditNote',
                    date__date__lt=start_date
                ).filter(company_filter)

                opening_creditnote_total = self._sum_customer_credit_lines_for_vouchers(opening_creditnotes_qs)

                opening = opening_invoice_total - opening_receipt_total - opening_creditnote_total

                # Period transactions
                period_invoices_qs = Invoices.objects.filter(
                    client_name=cust,
                    invoice_type='Sales',
                    date__date__range=[start_date, end_date]
                ).filter(company_filter)

                total_debit = sum(self._invoice_total_with_tax(inv) for inv in period_invoices_qs)

                period_receipts_qs = Vouchers.objects.filter(
                    party_account=str(cust.id),
                    party_account_type='organization',
                    voucher_type='Receipt',
                    date__date__range=[start_date, end_date]
                ).filter(company_filter)

                total_receipt = self._sum_customer_credit_lines_for_vouchers(period_receipts_qs)

                period_cns_qs = Vouchers.objects.filter(
                    party_account=str(cust.id),
                    party_account_type='organization',
                    voucher_type='CreditNote',
                    date__date__range=[start_date, end_date]
                ).filter(company_filter)

                total_cn = self._sum_customer_credit_lines_for_vouchers(period_cns_qs)

                total_credit = total_receipt + total_cn

                closing = opening + total_debit - total_credit

                # Only include if there's activity or balance
                if opening != 0 or total_debit != 0 or total_credit != 0 or closing != 0:
                    summary_rows.append({
                        'si_no': 0,  # will be set later
                        'customer_name': cust.name or "Unnamed",
                        'inv_amount': float(total_debit),
                        'received_amount': float(total_credit),
                        'balance': float(closing),
                    })

                    total_inv_amount += total_debit
                    total_received_amount += total_credit
                    total_balance += closing

            # Sort alphabetically by customer name
            summary_rows.sort(key=lambda x: x['customer_name'].lower())

            # Assign proper SI.NO
            for i, row in enumerate(summary_rows, 1):
                row['si_no'] = i

            return Response({
                'is_summary': True,
                'rows': summary_rows,
                'totals': {
                    'inv_amount': float(total_inv_amount),
                    'received_amount': float(total_received_amount),
                    'balance': float(total_balance),
                },
                'currency': 'SAR',
            })

        else:
            # ───────────────────────────────────────────────
            # Detailed statement for SINGLE customer
            # ───────────────────────────────────────────────
            if not organization_id:
                return Response({"error": "organization parameter is required"}, status=400)

            try:
                organization_id = int(organization_id)
            except ValueError:
                return Response({"error": "Invalid organization ID"}, status=400)

            try:
                org = Organization.objects.get(id=organization_id)
                party_name = org.name or "Customer"
            except Organization.DoesNotExist:
                return Response({"error": "Organization not found"}, status=404)

            # Opening balance
            opening_invoices = Invoices.objects.filter(
                client_name_id=organization_id,
                invoice_type='Sales',
                date__date__lt=start_date
            ).filter(company_filter).select_related('client_name', 'job')

            opening_invoice_total = Decimal('0.00')
            for inv in opening_invoices:
                opening_invoice_total += self._invoice_total_with_tax(inv)

            opening_receipts = Vouchers.objects.filter(
                party_account=str(organization_id),
                party_account_type='organization',
                voucher_type='Receipt',
                date__date__lt=start_date
            ).filter(company_filter)

            opening_receipt_total = self._sum_customer_credit_lines_for_vouchers(opening_receipts)

            opening_creditnotes = Vouchers.objects.filter(
                party_account=str(organization_id),
                party_account_type='organization',
                voucher_type='CreditNote',
                date__date__lt=start_date
            ).filter(company_filter)

            opening_creditnote_total = self._sum_customer_credit_lines_for_vouchers(opening_creditnotes)

            opening_balance_dec = opening_invoice_total - opening_receipt_total - opening_creditnote_total
            opening_balance = float(opening_balance_dec)

            # Period transactions
            rows = []

            # Sales Invoices
            invoices = Invoices.objects.filter(
                client_name_id=organization_id,
                invoice_type='Sales',
                date__date__range=[start_date, end_date]
            ).filter(company_filter).select_related('client_name', 'job').order_by('date')

            for inv in invoices:
                total = self._invoice_total_with_tax(inv)
                rows.append({
                    'date': inv.date.date().isoformat(),
                    'inv_no': inv.invoice_number or inv.supplier_inv_number or '',
                    'job_no': inv.job.job_number if inv.job else '',
                    'party_name': party_name,
                    'debit': float(total),
                    'credit': 0.00,
                    'narration': inv.narration or f"Sales Invoice {inv.invoice_number or 'N/A'}",
                    'voucher_no': '',
                })

            # Receipts
            receipts = Vouchers.objects.filter(
                party_account=str(organization_id),
                party_account_type='organization',
                voucher_type='Receipt',
                date__date__range=[start_date, end_date]
            ).filter(company_filter).select_related('job').order_by('date')

            for rec in receipts:
                amount = self._sum_customer_credit_lines_for_vouchers(Vouchers.objects.filter(id=rec.id))
                if amount == Decimal('0.00'):
                    amount = Decimal(str(rec.amount_sar or '0.00'))
                rows.append({
                    'date': rec.date.date().isoformat(),
                    'inv_no': '',
                    'voucher_no': rec.voucher_number or 'N/A',
                    'job_no': rec.job.job_number if rec.job else '',
                    'party_name': party_name,
                    'debit': 0.00,
                    'credit': float(amount),
                    'narration': rec.naration or f"Receipt {rec.voucher_number or 'N/A'}",
                })

            # Credit Notes
            credit_notes = Vouchers.objects.filter(
                party_account=str(organization_id),
                party_account_type='organization',
                voucher_type='CreditNote',
                date__date__range=[start_date, end_date]
            ).filter(company_filter).select_related('job').order_by('date')

            for cn in credit_notes:
                amount = self._sum_customer_credit_lines_for_vouchers(Vouchers.objects.filter(id=cn.id))
                if amount == Decimal('0.00'):
                    amount = Decimal(str(cn.amount_sar or '0.00'))
                rows.append({
                    'date': cn.date.date().isoformat(),
                    'inv_no': '',
                    'voucher_no': cn.voucher_number or '',
                    'job_no': cn.job.job_number if cn.job else '',
                    'party_name': party_name,
                    'debit': 0.00,
                    'credit': float(amount),
                    'narration': cn.naration or f"Credit Note {cn.voucher_number or 'N/A'}",
                })

            rows.sort(key=lambda x: x['date'])

            # Running balance
            balance = opening_balance_dec.quantize(Decimal('0.00'))
            final_rows = [{
                'date': start_date.isoformat(),
                'type': 'Opening Balance',
                'inv_no': '',
                'job_no': '',
                'party_name': party_name,
                'debit': 0.00,
                'credit': 0.00,
                'balance': float(balance),
                'narration': 'Opening balance brought forward',
                'voucher_no': '',
            }]

            for row in rows:
                debit = Decimal(str(row.get('debit', 0))).quantize(Decimal('0.00'))
                credit = Decimal(str(row.get('credit', 0))).quantize(Decimal('0.00'))
                balance = (balance + debit - credit).quantize(Decimal('0.00'))
                row['balance'] = float(balance)
                final_rows.append(row)

            return Response({
                'is_summary': False,
                'opening_balance': float(opening_balance_dec.quantize(Decimal('0.00'))),
                'rows': final_rows,
                'closing_balance': float(balance),
                'currency': 'SAR',
            })  

class AccountsPayableViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Accounts Payable Statement – now includes Supplier, Broker and Counterpart
    URL: GET /api/account/payable/?organization=ID_or_'all'&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    permission_classes = (IsAuthenticated,)
    queryset = Invoices.objects.none()

    def _parse_date(self, date_str):
        return datetime.strptime(date_str.split('T')[0], "%Y-%m-%d").date()

    def _invoice_total_with_tax(self, inv):
        cost_total = Decimal('0.00')
        for ce in inv.costentry_set.all():
            base = Decimal(str(ce.amount or '0.00'))
            rate = Decimal(str(ce.tax_group_code or '0.00'))
            tax = base * (rate / Decimal('100'))
            cost_total += base + tax
        if cost_total == 0:
            cost_total = Decimal(str(inv.amount_sar or '0.00'))
        return cost_total.quantize(Decimal('0.00'))

    def _sum_vendor_debit_lines(self, vouchers_qs):
        """Sum debit (Dr) lines in AccountDetails for given vouchers"""
        return (
            AccountDetails.objects.filter(
                vouchers__in=vouchers_qs,
                dr_cr='Dr'
            )
            .exclude(amount_sar='')           # skip empty strings
            .exclude(amount_sar__isnull=True)
            .aggregate(
                total=Coalesce(
                    Sum(Cast('amount_sar', DecimalField(max_digits=15, decimal_places=2))),
                    Value(Decimal('0.00'))
                )
            )['total']
            .quantize(Decimal('0.00'))
        )

    def list(self, request, *args, **kwargs):
        organization_id = request.query_params.get('organization')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not start_date_str or not end_date_str:
            return Response({"error": "start_date and end_date are required"}, status=400)

        try:
            start_date = self._parse_date(start_date_str)
            end_date   = self._parse_date(end_date_str)
        except ValueError:
            return Response({"error": "Invalid date format. Expected YYYY-MM-DD"}, status=400)

        company_filter = Q(company__users=request.user)

        PAYABLE_TYPES = ['Supplier', 'Broker', 'Counterpart']

        if organization_id == 'all':
            # ───────────────────────────────────────────────
            # Summary for ALL payable parties (Supplier + Broker + Counterpart)
            # ───────────────────────────────────────────────
            parties = Organization.objects.filter(
                type__overlap=PAYABLE_TYPES,     # ← changed: uses overlap instead of contains
                company__users=request.user
            ).distinct().order_by('name')

            summary_rows = []
            total_purchase_amount = Decimal('0.00')
            total_paid_amount = Decimal('0.00')
            total_balance = Decimal('0.00')

            for party in parties:
                party_id_str = str(party.id)

                # Opening balance ────────────────
                opening_purchases_qs = Invoices.objects.filter(
                    party_account=party,
                    invoice_type='Purchase',
                    date__date__lt=start_date
                ).filter(company_filter)

                opening_purchase_total = sum(
                    self._invoice_total_with_tax(inv) for inv in opening_purchases_qs
                )

                opening_payments_qs = Vouchers.objects.filter(
                    party_account=party_id_str,
                    party_account_type='organization',
                    voucher_type='Payment',
                    date__date__lt=start_date
                ).filter(company_filter)

                opening_payment_total = self._sum_vendor_debit_lines(opening_payments_qs)

                opening_debitnotes_qs = Vouchers.objects.filter(
                    party_account=party_id_str,
                    party_account_type='organization',
                    voucher_type='DebitNote',
                    date__date__lt=start_date
                ).filter(company_filter)

                opening_debitnote_total = self._sum_vendor_debit_lines(opening_debitnotes_qs)

                opening = opening_purchase_total - opening_payment_total - opening_debitnote_total

                # Current period ─────────────────
                period_purchases_qs = Invoices.objects.filter(
                    party_account=party,
                    invoice_type='Purchase',
                    date__date__range=[start_date, end_date]
                ).filter(company_filter)

                period_credit = sum(
                    self._invoice_total_with_tax(inv) for inv in period_purchases_qs
                )

                period_payments_qs = Vouchers.objects.filter(
                    party_account=party_id_str,
                    party_account_type='organization',
                    voucher_type='Payment',
                    date__date__range=[start_date, end_date]
                ).filter(company_filter)

                period_debit_payment = self._sum_vendor_debit_lines(period_payments_qs)

                period_debitnotes_qs = Vouchers.objects.filter(
                    party_account=party_id_str,
                    party_account_type='organization',
                    voucher_type='DebitNote',
                    date__date__range=[start_date, end_date]
                ).filter(company_filter)

                period_debit_dn = self._sum_vendor_debit_lines(period_debitnotes_qs)

                period_debit = period_debit_payment + period_debit_dn

                closing = opening + period_credit - period_debit

                if opening != 0 or period_credit != 0 or period_debit != 0 or closing != 0:
                    summary_rows.append({
                        'si_no': 0,  # set later
                        'party_name': party.name or "Unnamed",
                        'party_type': ", ".join(party.type),  # optional – shows types
                        'purchase_amount': float(period_credit),
                        'paid_amount': float(period_debit),
                        'balance': float(closing),
                    })

                    total_purchase_amount += period_credit
                    total_paid_amount += period_debit
                    total_balance += closing

            summary_rows.sort(key=lambda x: x['party_name'].lower())
            for i, row in enumerate(summary_rows, 1):
                row['si_no'] = i

            return Response({
                'is_summary': True,
                'rows': summary_rows,
                'totals': {
                    'purchase_amount': float(total_purchase_amount),
                    'paid_amount': float(total_paid_amount),
                    'balance': float(total_balance),
                },
                'currency': 'SAR',
            })

        else:
            # ───────────────────────────────────────────────
            # Single supplier - detailed (your original logic, cleaned up)
            # ───────────────────────────────────────────────
            if not organization_id:
                return Response({"error": "organization parameter is required"}, status=400)

            try:
                organization_id = int(organization_id)
            except ValueError:
                return Response({"error": "Invalid organization ID"}, status=400)

            try:
                org = Organization.objects.get(id=organization_id)
                vendor_name = org.name or "Vendor"
            except Organization.DoesNotExist:
                return Response({"error": "Organization not found"}, status=404)

            # Opening balance (same as before)
            opening_purchases = Invoices.objects.filter(
                party_account_id=organization_id,
                invoice_type='Purchase',
                date__date__lt=start_date
            ).filter(company_filter)

            opening_purchase_total = Decimal('0.00')
            for inv in opening_purchases:
                opening_purchase_total += self._invoice_total_with_tax(inv)

            opening_payments = Vouchers.objects.filter(
                party_account=str(organization_id),
                party_account_type='organization',
                voucher_type='Payment',
                date__date__lt=start_date
            ).filter(company_filter)

            opening_payment_total = self._sum_vendor_debit_lines(opening_payments)

            opening_debitnotes = Vouchers.objects.filter(
                party_account=str(organization_id),
                party_account_type='organization',
                voucher_type='DebitNote',
                date__date__lt=start_date
            ).filter(company_filter)

            opening_debitnote_total = self._sum_vendor_debit_lines(opening_debitnotes)

            opening_balance_dec = opening_purchase_total - opening_payment_total - opening_debitnote_total
            opening_balance = float(opening_balance_dec)

            # Period rows (your original code, kept similar)
            rows = []

            purchases = Invoices.objects.filter(
                party_account_id=organization_id,
                invoice_type='Purchase',
                date__date__range=[start_date, end_date]
            ).filter(company_filter).select_related('party_account', 'job').order_by('date')

            for inv in purchases:
                total = self._invoice_total_with_tax(inv)
                rows.append({
                    'date': inv.date.date().isoformat(),
                    'type': 'Purchase Invoice',
                    'inv_no': inv.invoice_number or 'N/A',
                    'voucher_no': '',
                    'job_no': inv.job.job_number if inv.job else '',
                    'party_name': vendor_name,
                    'debit': 0.00,
                    'credit': float(total),
                    'narration': inv.narration or f"Purchase Invoice {inv.invoice_number or 'N/A'}",
                })

            payments = Vouchers.objects.filter(
                party_account=str(organization_id),
                party_account_type='organization',
                voucher_type='Payment',
                date__date__range=[start_date, end_date]
            ).filter(company_filter).select_related('job').order_by('date')

            for pay in payments:
                amount = self._sum_vendor_debit_lines(Vouchers.objects.filter(id=pay.id))
                if amount == Decimal('0.00'):
                    amount = Decimal(str(pay.amount_sar or '0.00').strip() or '0.00')
                rows.append({
                    'date': pay.date.date().isoformat(),
                    'type': 'Payment',
                    'inv_no': '',
                    'voucher_no': pay.voucher_number or 'N/A',
                    'job_no': pay.job.job_number if pay.job else '',
                    'party_name': vendor_name,
                    'debit': float(amount),
                    'credit': 0.00,
                    'narration': pay.naration or f"Payment {pay.voucher_number or 'N/A'}",
                })

            debit_notes = Vouchers.objects.filter(
                party_account=str(organization_id),
                party_account_type='organization',
                voucher_type='DebitNote',
                date__date__range=[start_date, end_date]
            ).filter(company_filter).select_related('job').order_by('date')

            for dn in debit_notes:
                amount = self._sum_vendor_debit_lines(Vouchers.objects.filter(id=dn.id))
                if amount == Decimal('0.00'):
                    amount = Decimal(str(dn.amount_sar or '0.00').strip() or '0.00')
                rows.append({
                    'date': dn.date.date().isoformat(),
                    'type': 'Debit Note',
                    'inv_no': '',
                    'voucher_no': dn.voucher_number or 'N/A',
                    'job_no': dn.job.job_number if dn.job else '',
                    'party_name': vendor_name,
                    'debit': float(amount),
                    'credit': 0.00,
                    'narration': dn.naration or f"Debit Note {dn.voucher_number or 'N/A'}",
                })

            rows.sort(key=lambda x: x['date'])

            balance = opening_balance_dec.quantize(Decimal('0.00'))
            final_rows = [{
                'date': start_date.isoformat(),
                'type': 'Opening Balance',
                'inv_no': '',
                'voucher_no': '',
                'job_no': '',
                'party_name': vendor_name,
                'debit': 0.00,
                'credit': 0.00,
                'balance': float(balance),
                'narration': 'Opening balance brought forward',
            }]

            for row in rows:
                debit = Decimal(str(row.get('debit', 0))).quantize(Decimal('0.00'))
                credit = Decimal(str(row.get('credit', 0))).quantize(Decimal('0.00'))
                balance = (balance + credit - debit).quantize(Decimal('0.00'))
                row['balance'] = float(balance)
                final_rows.append(row)

            return Response({
                'is_summary': False,
                'opening_balance': float(opening_balance_dec.quantize(Decimal('0.00'))),
                'rows': final_rows,
                'closing_balance': float(balance),
                'currency': 'SAR',
            })
        
from decimal import Decimal
from datetime import datetime
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Coa, AccountDetails, CostEntry, Organization


class TrialBalancesViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        queryset = Coa.objects.filter(
            company__users__email=request.user.email
        ).select_related('group')

        response = []
        for coa in queryset:
            raw_dr = 0.0
            raw_cr = 0.0
            entries = []

            if coa.name == 'VAT INPUT':
                entries = get_vat_input_coa_response(coa, start_date, end_date, request.user)
            elif coa.name == 'VAT OUTPUT':
                entries = get_vat_output_coa_response(coa, start_date, end_date, request.user)
            elif coa.name == 'SUNDRY CREDITORS':
                entries = get_sundry_creditors_coa_response(coa, start_date, end_date, request.user)
            elif coa.name == 'SUNDRY DEBTORS':
                entries = get_sundry_debtors_coa_response(coa, start_date, end_date, request.user)
            else:
                entries = get_trial_balance_coa_response(coa, start_date, end_date, request.user)

            for amt in entries:
                raw_dr += float(amt.get('dr_amount', 0))
                raw_cr += float(amt.get('cr_amount', 0))

            if raw_dr == 0 and raw_cr == 0:
                continue

            # ─────────────────────────────────────────────────────
            # KEY FIX: Compute NET balance based on account nature
            # For DR accounts (Asset/Expense): net = Dr - Cr
            #   positive net → show on Dr side
            #   negative net → abnormal, show absolute on Cr side
            #
            # For CR accounts (Liability/Equity/Income): net = Cr - Dr  
            #   positive net → show on Cr side
            #   negative net → abnormal, show absolute on Dr side
            # ─────────────────────────────────────────────────────
            
            if coa.dr_cr == 'Dr':
                # Asset / Expense accounts — naturally debit
                net = raw_dr - raw_cr
                if net >= 0:
                    display_dr = round(net, 2)
                    display_cr = 0.0
                else:
                    # Abnormal credit balance (e.g. overpaid petty cash)
                    display_dr = 0.0
                    display_cr = round(abs(net), 2)
            else:
                # Liability / Equity / Income accounts — naturally credit
                net = raw_cr - raw_dr
                if net >= 0:
                    display_dr = 0.0
                    display_cr = round(net, 2)
                else:
                    # Abnormal debit balance
                    display_dr = round(abs(net), 2)
                    display_cr = 0.0

            if display_dr == 0 and display_cr == 0:
                continue

            res_obj = {
                "type": coa.type,
                "account_name": coa.name,
                "group": coa.group.name if coa.group else "",
                "total_dr_amount": display_dr,
                "total_cr_amount": display_cr,
                # Signed net: positive = Dr balance, negative = Cr balance
                "total_amount": round(raw_dr - raw_cr, 2),
                # Extra info for debugging / frontend flexibility
                "nature": coa.dr_cr,
            }
            response.append(res_obj)

        return Response(response, status=status.HTTP_200_OK)

class DayBookReportViewSet(viewsets.GenericViewSet):
    """
    Day Book Report – chronological journal of all accounting entries.

    Running Balance rule (same as a cash book / general journal):
        running_balance += Debit - Credit
        positive result → Dr balance
        negative result → Cr balance

    GET /api/daybook/?date=2025-03-15
    GET /api/daybook/?start_date=2025-03-01&end_date=2025-03-31
    GET /api/daybook/?start_date=2025-03-01&end_date=2025-03-31&type=Receipt
    GET /api/daybook/?start_date=2025-03-01&end_date=2025-03-31&branch=JEDDAH
    """
    permission_classes = [IsAuthenticated]
    pagination_class   = None

    def list(self, request, *args, **kwargs):
        user = request.user

        # ── Date filtering ────────────────────────────────────────────────────
        single_date_str = request.query_params.get('date')
        start_str       = request.query_params.get('start_date')
        end_str         = request.query_params.get('end_date')
        branch          = request.query_params.get('branch')
        type_filter     = request.query_params.get('type')

        if single_date_str:
            try:
                target_date = datetime.strptime(single_date_str, "%Y-%m-%d").date()
                date_filter = Q(date__date=target_date)
                date_title  = target_date.strftime("%d-%b-%Y")
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        elif start_str and end_str:
            try:
                start = datetime.strptime(start_str, "%Y-%m-%d").date()
                end   = datetime.strptime(end_str,   "%Y-%m-%d").date()
                date_filter = Q(date__date__range=[start, end])
                date_title  = f"{start.strftime('%d-%b-%Y')} to {end.strftime('%d-%b-%Y')}"
            except ValueError:
                return Response({"error": "Invalid date range format"}, status=400)
        else:
            return Response(
                {"error": "Provide ?date=YYYY-MM-DD or ?start_date=...&end_date=..."},
                status=400,
            )

        # ── Base filters ──────────────────────────────────────────────────────
        base_filter = Q(company__users=user)
        if branch:
            base_filter &= Q(branch__iexact=branch)

        # ── Pre-fetch VAT / Sundry COA names ─────────────────────────────────
        # Must be defined BEFORE voucher loop so both vouchers and invoices can use them
        try:
            sundry_debtors   = Coa.objects.filter(company__users=user, name__iexact="SUNDRY DEBTORS").first()
            sundry_creditors = Coa.objects.filter(company__users=user, name__iexact="SUNDRY CREDITORS").first()
            vat_input        = Coa.objects.filter(company__users=user, name__iexact="VAT INPUT").first()
            vat_output       = Coa.objects.filter(company__users=user, name__iexact="VAT OUTPUT").first()

            sundry_debtors_name   = f"{sundry_debtors.code or ''} {sundry_debtors.name}".strip()    if sundry_debtors   else "SUNDRY DEBTORS"
            sundry_creditors_name = f"{sundry_creditors.code or ''} {sundry_creditors.name}".strip() if sundry_creditors else "SUNDRY CREDITORS"
            vat_input_name        = f"{vat_input.code or ''} {vat_input.name}".strip()               if vat_input        else "VAT INPUT"
            vat_output_name       = f"{vat_output.code or ''} {vat_output.name}".strip()             if vat_output       else "VAT OUTPUT"
        except Exception:
            sundry_debtors_name   = "SUNDRY DEBTORS"
            sundry_creditors_name = "SUNDRY CREDITORS"
            vat_input_name        = "VAT INPUT"
            vat_output_name       = "VAT OUTPUT"

        # ─────────────────────────────────────────────────────────────────────
        #  1. VOUCHERS  (Journal / Payment / Receipt / CreditNote / DebitNote)
        #     Each AccountDetails line = one Dr or Cr row in the day book.
        #     VAT amount is split into a separate line.
        # ─────────────────────────────────────────────────────────────────────
        voucher_filter = base_filter
        if type_filter:
            voucher_filter &= Q(voucher_type=type_filter)

        vouchers = (
            Vouchers.objects
            .filter(date_filter, voucher_filter)
            .select_related('job', 'company')
            .order_by('date', 'voucher_number')
        )

        voucher_entries = []
        for v in vouchers:
            lines = AccountDetails.objects.filter(vouchers=v).order_by('line_no')
            for line in lines:
                taxable = Decimal(line.taxable_amount or "0.00")
                tax_amt = Decimal(line.tax_amount     or "0.00")
                base    = Decimal(line.amount_sar     or "0.00")

                # Main line uses base amount only (without VAT)
                # If taxable_amount is set use that, otherwise use amount_sar
                main_amount = taxable if taxable else base

                is_dr = line.dr_cr == "Dr"

                # ── Main account line ─────────────────────────────────────
                voucher_entries.append({
                    "date":           v.date.strftime("%Y-%m-%d"),
                    "voucher_type":   v.voucher_type,
                    "voucher_no":     v.voucher_number or "—",
                    "narration":      line.narration or v.naration or "",
                    "account":        self._get_account_display(line),
                    "debit":          float(main_amount) if is_dr     else 0.0,
                    "credit":         float(main_amount) if not is_dr else 0.0,
                    "taxable_amount": float(taxable),
                    "tax_amount":     float(tax_amt),
                    "tax_group_code": line.tax_group_code or "",
                    "job_no":         v.job.job_number if v.job else "",
                    "branch":         v.branch or "",
                    "source":         "Voucher",
                })

                # ── Separate VAT line (only when tax_amount exists) ───────
                if tax_amt > Decimal("0.00"):
                    # Dr line (expense/asset) → VAT Input
                    # Cr line (income/liability) → VAT Output
                    vat_account = vat_input_name if is_dr else vat_output_name

                    voucher_entries.append({
                        "date":           v.date.strftime("%Y-%m-%d"),
                        "voucher_type":   v.voucher_type,
                        "voucher_no":     v.voucher_number or "—",
                        "narration":      line.narration or v.naration or "",
                        "account":        vat_account,
                        "debit":          float(tax_amt) if is_dr     else 0.0,
                        "credit":         float(tax_amt) if not is_dr else 0.0,
                        "taxable_amount": float(taxable),
                        "tax_amount":     float(tax_amt),
                        "tax_group_code": line.tax_group_code or "",
                        "job_no":         v.job.job_number if v.job else "",
                        "branch":         v.branch or "",
                        "source":         "Voucher",
                    })

        # ─────────────────────────────────────────────────────────────────────
        #  2. INVOICES  (Sales / Purchase) — Full Double Entry
        # ─────────────────────────────────────────────────────────────────────
        VOUCHER_ONLY_TYPES = {"Journal", "Payment", "Receipt", "CreditNote", "DebitNote"}
        invoice_entries = []

        if not type_filter or type_filter not in VOUCHER_ONLY_TYPES:
            inv_filter = base_filter
            if type_filter:
                inv_filter &= Q(invoice_type=type_filter)

            invoices = (
                Invoices.objects
                .filter(date_filter, inv_filter)
                .select_related('job', 'client_name', 'consignee_name', 'party_account')
            )

            for inv in invoices:
                is_sales    = inv.invoice_type == "Sales"
                is_purchase = not is_sales

                # Try included entries first, fall back to all entries
                cost_entries = CostEntry.objects.filter(invoice=inv, is_included=True).select_related('charge', 'charge__coa')
                if not cost_entries.exists():
                    cost_entries = CostEntry.objects.filter(invoice=inv).select_related('charge', 'charge__coa')

                date_str   = inv.date.strftime("%Y-%m-%d")
                job_no     = inv.job.job_number if inv.job else ""
                inv_branch = inv.branch or ""
                inv_no     = inv.invoice_number
                narration  = inv.narration or f"{inv.invoice_type} Invoice"

                if cost_entries.exists():
                    # ── Calculate grand total for party line ──────────────
                    grand_total = Decimal("0.00")
                    for ce in cost_entries:
                        base     = Decimal(str(ce.amount or "0"))
                        tax_rate = Decimal(str(ce.tax_group_code or "0"))
                        grand_total += base + base * (tax_rate / Decimal("100"))

                    # LINE 1: Party line (Sundry Debtors / Sundry Creditors)
                    invoice_entries.append({
                        "date":         date_str,
                        "voucher_type": inv.invoice_type,
                        "voucher_no":   inv_no,
                        "narration":    narration,
                        "account":      sundry_debtors_name   if is_sales    else sundry_creditors_name,
                        "debit":        float(grand_total)    if is_sales    else 0.0,
                        "credit":       float(grand_total)    if is_purchase else 0.0,
                        "job_no":       job_no,
                        "branch":       inv_branch,
                        "source":       "Invoice",
                    })

                    # LINES 2+: One charge line + optional VAT line per CostEntry
                    for ce in cost_entries:
                        base     = Decimal(str(ce.amount or "0"))
                        tax_rate = Decimal(str(ce.tax_group_code or "0"))
                        vat_amt  = base * (tax_rate / Decimal("100"))

                        if base == Decimal("0.00"):
                            continue

                        # Resolve charge COA account name
                        if ce.charge and ce.charge.coa:
                            coa_obj        = ce.charge.coa
                            charge_account = f"{coa_obj.code or ''} {coa_obj.name}".strip()
                        elif ce.charge:
                            charge_account = ce.charge.name
                        else:
                            charge_account = "Income/Expense"

                        ce_narration = ce.description or narration

                        # Charge line
                        invoice_entries.append({
                            "date":         date_str,
                            "voucher_type": inv.invoice_type,
                            "voucher_no":   inv_no,
                            "narration":    ce_narration,
                            "account":      charge_account,
                            "debit":        float(base) if is_purchase else 0.0,
                            "credit":       float(base) if is_sales    else 0.0,
                            "job_no":       job_no,
                            "branch":       inv_branch,
                            "source":       "Invoice",
                        })

                        # VAT line
                        if vat_amt > Decimal("0.00"):
                            invoice_entries.append({
                                "date":         date_str,
                                "voucher_type": inv.invoice_type,
                                "voucher_no":   inv_no,
                                "narration":    ce_narration,
                                "account":      vat_input_name  if is_purchase else vat_output_name,
                                "debit":        float(vat_amt)  if is_purchase else 0.0,
                                "credit":       float(vat_amt)  if is_sales    else 0.0,
                                "job_no":       job_no,
                                "branch":       inv_branch,
                                "source":       "Invoice",
                            })

                else:
                    # ── Absolute fallback: no cost entries, use invoice header ──
                    total = Decimal(str(inv.amount_sar or "0"))
                    if total == Decimal("0.00"):
                        continue

                    invoice_entries.append({
                        "date":         date_str,
                        "voucher_type": inv.invoice_type,
                        "voucher_no":   inv_no,
                        "narration":    narration,
                        "account":      sundry_debtors_name   if is_sales    else sundry_creditors_name,
                        "debit":        float(total)          if is_sales    else 0.0,
                        "credit":       float(total)          if is_purchase else 0.0,
                        "job_no":       job_no,
                        "branch":       inv_branch,
                        "source":       "Invoice",
                    })

        # ── Combine & sort chronologically ───────────────────────────────────
        all_entries = voucher_entries + invoice_entries
        all_entries.sort(key=lambda x: (x["date"], x["voucher_no"] or "ZZZ"))

        # ── Running Balance ───────────────────────────────────────────────────
        running_balance = Decimal("0.00")
        total_debit     = Decimal("0.00")
        total_credit    = Decimal("0.00")

        for e in all_entries:
            dr = Decimal(str(e["debit"]))
            cr = Decimal(str(e["credit"]))

            total_debit     += dr
            total_credit    += cr
            running_balance += dr - cr

            balance_value = float(abs(running_balance))
            balance_side  = "Dr" if running_balance >= 0 else "Cr"

            e["running_balance"]      = float(running_balance)
            e["running_balance_abs"]  = balance_value
            e["running_balance_side"] = balance_side

        return Response({
            "report_title": f"Day Book – {date_title}",
            "branch":       branch or "All Branches",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "entries":      all_entries,
            "summary": {
                "total_debit":          float(total_debit),
                "total_credit":         float(total_credit),
                "difference":           float(total_debit - total_credit),
                "closing_balance":      float(abs(running_balance)),
                "closing_balance_side": "Dr" if running_balance >= 0 else "Cr",
            },
        })

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_account_display(self, line: AccountDetails):
        if line.ac_name_type == "coa":
            try:
                coa = Coa.objects.get(id=line.ac_name)
                return f"{coa.code or ''} {coa.name or line.ac_name}".strip()
            except Exception:
                return f"COA {line.ac_name}"
        elif line.ac_name_type == "organization":
            try:
                org = Organization.objects.get(id=line.ac_name)
                return org.name or f"Party {line.ac_name}"
            except Exception:
                return f"Party {line.ac_name}"
        return line.ac_name or "—"

    def _get_party_display(self, invoice: Invoices):
        if invoice.invoice_type == "Sales":
            return invoice.client_name.name if invoice.client_name else "Customer"
        return invoice.party_account.name if invoice.party_account else "Supplier"

class BranchViewset(viewsets.GenericViewSet,mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticated,)
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer