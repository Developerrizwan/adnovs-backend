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
from django.db.models import Q
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
        job_status_first_chars = "".join(word[0] for word in type.split())
        # job_number = f"{branch[:3]}{job_status_first_chars}{str(year)[-2:]}{job_id:02}"

        if job_type == 'Job':
            job_number = job_number = f"{branch[:3].upper()}{job_status_first_chars}{str(year)[-2:]}{job_id:02}"
            enquiry_number = None
        else:
            enquiry_number = f"ENQ{str(year)[-2:]}{job_id:02}"
            job_number = None
        serializer.save(enquiry_number=enquiry_number, job_number=job_number)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JobGetSerializer
        return JobSerializer


class VouchersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    """Manage Vouchers in the Database"""

    permission_classes = (IsAuthenticated, )
    queryset = Vouchers.objects.all().order_by('-id')
    serializer_class = VouchersSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VoucherGetSerializer
        return VouchersSerializer


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

    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Job.objects.all().order_by('-id')
    serializer_class = JobGetSerializer
    filter_backends = [TypeFilter]


class GetvoucherViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all Vouchers"""

    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Vouchers.objects.all().order_by('-id')
    serializer_class = VoucherGetSerializer
    filter_backends = [VoucherFliter]


class GetinvoiceViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all Invoices"""

    pagination_class = CustomPagination
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


class GetCoaGroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Get all coa group"""
    pagination_class = CustomPagination
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
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, )
    queryset = Organization.objects.all().order_by('-id')
    serializer_class = OrganizationSerializer

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


class AccountDetailsViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
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
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date',None)
        organization = request.query_params.get('organization', None)
        coa_type = request.query_params.get('type', None) 
        queryset = Coa.objects.filter(company__users__email=request.user.email)

        queryset = queryset.filter(coa_type=coa_type)
        # page = self.paginate_queryset(queryset)

        if queryset is not None:
            cost_entry_list = []
            for coa in queryset:
                cost_entry = CostEntry.objects.filter(charge__coa=coa)
                if start_date and end_date:
                    cost_entry = cost_entry.filter(created_at__range=(start_date, end_date))

                if job is not None and job.strip() :
                    cost_entry = cost_entry.filter(job_no__id=job)

                income_amount=0
                expenses_amount=0


                for cost in cost_entry:
                     
                    if cost.dr_cr=='Cr':
                        income_amount += float(cost.amount if cost.amount else 0.0)
                    elif cost.dr_cr=='Dr':
                        expenses_amount += float(cost.amount if cost.amount else 0.0)

                serializer = CostEntrySerializer(cost_entry, many=True)
                company_serializer = CompanySerializer(coa.company)
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
                    'short_name': coa.short_name,
                    'long_name': coa.long_name,
                    'language_name': coa.language_name,
                    'currency': coa.currency,
                    # 'additional_reference_code': coa.additional_reference_code,
                    'company': company_serializer.data,
                    'remarks': coa.remarks,
                    'cost_entry': serializer.data,
                    'income_amount': income_amount,
                    'expenses_amount': expenses_amount
                })

            return Response(cost_entry_list)
        else:
            return Response([])


class GeneralledgerViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Coa.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        coa_id = request.query_params.get('coa', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date',None)
        if Coa.objects.filter(id=coa_id).exists():
            coa = Coa.objects.filter(id=coa_id).first()

            invoices = Invoices.objects.filter(party_account__coa=coa, created_at__range=[start_date, end_date]).order_by('created_at')
            respone =[]
            res_obj={}
            for invoice in invoices:

                res_obj = {
                        "account":invoice.client_name.name if invoice.client_name else "",
                        "date":invoice.created_at,
                        "currency":invoice.currency_sar,
                        "dr_amount":0,
                        "cr_amount":0,
                        "net_amount":0,
                        "party_account":invoice.party_account.name if invoice.party_account else "",
                        "job_no":invoice.job.job_number if invoice.job.job_number else "",
                        "narrations":invoice.narration if invoice.narration else "",
                        "branch":invoice.branch if invoice.branch else "",
                        "language_name":coa.language_name if coa.language_name else ""
                        }
                cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id)
                

                if invoice.invoice_type=='Sales':
                    total_amount = 0

                    for cost_entry in cost_entrys:
                        fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                        amount=float(cost_entry.amount if cost_entry.amount else 0.0)
                        vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                        total_amount += (amount)+(float((vat_percent * fcy_amount)/100))
                    res_obj['cr_amount']=total_amount
                    res_obj['net_amount']=total_amount   
                    respone.append(res_obj)
                else:
                    total_amount = 0

                    for cost_entry in cost_entrys:
                        fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                        amount=float(cost_entry.amount if cost_entry.amount else 0.0)
                        vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                        total_amount += (amount)+(float((vat_percent * fcy_amount)/100))
                    res_obj['dr_amount']=total_amount
                    res_obj['net_amount']=total_amount   
                    respone.append(res_obj)
            return Response(respone)
        else:
            return Response([])

class AccountStatementViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = CustomPagination
    queryset = Invoices.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        organization_id = request.query_params.get('organization', None)
        type = request.query_params.get('type', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date',None)
        if self.queryset.filter(party_account=organization_id).exists():
            invoices = Invoices.objects.filter(party_account=organization_id,created_at__range=[start_date, end_date]).order_by('created_at')
            respone =[]
            res_obj = {}
            if type =='receive':
                invoices= invoices.filter(invoice_type='Sales')

                for invoice in invoices:
                    res_obj = {
                        "account":invoice.client_name.name if invoice.client_name else "",
                        "date":invoice.created_at,
                        "currency":invoice.currency_sar,
                        # "dr_amount":0,
                        # "cr_amount":0,
                        "net_amount":0,
                        "party_account":invoice.party_account.name if invoice.party_account else "",
                        "job_no":invoice.job.job_number if invoice.job.job_number else "",
                        "narrations":invoice.narration if invoice.narration else "",
                        "branch":invoice.branch if invoice.branch else "",
                        # "language_name":coa.language_name if coa.language_name else ""
                    }
                    cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id)
                    print(cost_entrys)
                    # if invoice.invoice_type=='Sales':
                    total_amount = 0

                    for cost_entry in cost_entrys:
                        fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                        amount=float(cost_entry.amount if cost_entry.amount else 0.0)
                        vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                        total_amount += (amount)+(float((vat_percent * fcy_amount)/100))
                    res_obj['net_amount']=total_amount   
                    respone.append(res_obj)

            elif type =='pay':
                invoices= invoices.filter(invoice_type='Purchase')
                for invoice in invoices:
                    res_obj = {
                        "account":invoice.client_name.name if invoice.client_name else "",
                        "date":invoice.created_at,
                        "currency":invoice.currency_sar,
                        # "dr_amount":0,
                        # "cr_amount":0,
                        "net_amount":0,
                        "party_account":invoice.party_account.name if invoice.party_account else "",
                        "job_no":invoice.job.job_number if invoice.job.job_number else "",
                        "narrations":invoice.narration if invoice.narration else "",
                        "branch":invoice.branch if invoice.branch else "",
                        # "language_name":coa.language_name if coa.language_name else ""
                    }
                    cost_entrys = CostEntry.objects.filter(invoice__id=invoice.id)
                    total_amount = 0

                    for cost_entry in cost_entrys:
                        fcy_amount = float(cost_entry.fcy_amount if cost_entry.fcy_amount else 0.0)
                        amount=float(cost_entry.amount if cost_entry.amount else 0.0)
                        vat_percent = float(cost_entry.tax_group_code if cost_entry.tax_group_code else 0.0)
                        total_amount += (amount)+(float((vat_percent * fcy_amount)/100))
                    res_obj['net_amount']=total_amount   
                    respone.append(res_obj)
            return Response(respone)
        else:
            return Response([])
