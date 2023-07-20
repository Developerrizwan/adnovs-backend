from django.urls import path, include
from rest_framework import routers
from organization.views import *

app_name = "organization"

# get_company_router = routers.SimpleRouter() 
# get_company_router.register('company',CompanyViewSet,basename='company') 

get_company_router = routers.SimpleRouter() 
get_company_router.register('get-companys',GetcompanyViewset,basename='getcompany') 

company_router = routers.SimpleRouter()
company_router.register('master/company', CompanyViewSet, basename='company')

get_job_router = routers.SimpleRouter() 
get_job_router.register('get-jobs',GetjobViewset,basename='getjob') 

job_router = routers.SimpleRouter()
job_router.register('master/job', JobViewSet, basename='job-master')

get_vocher_router = routers.SimpleRouter() 
get_vocher_router.register('get-voucher',GetvoucherViewset,basename='getvocher')  

voucher_router = routers.SimpleRouter()
voucher_router.register('master/voucher', VouchersViewSet, basename='voucher')

get_invoice_router = routers.SimpleRouter() 
get_invoice_router.register('get-invoices',GetinvoiceViewset,basename='getinvoice')   

invoice_router = routers.SimpleRouter()
invoice_router.register('master/invoice', InvoicesViewSet, basename='invoice')

get_users_router = routers.SimpleRouter() 
get_users_router.register('get-users',GetusersViewSet,basename='getusers')

urlpatterns = [
    path('',include(get_company_router.urls)),
    path('', include(company_router.urls)),
    path('',include(get_job_router.urls)),
    path('', include(job_router.urls)),
    path('',include(get_vocher_router.urls)),
    path('', include(voucher_router.urls)),
    path('',include(get_invoice_router.urls)), 
    path('', include(invoice_router.urls)),
    path('',include(get_users_router.urls)),
    path('signup/', UserSignUpViewSet.as_view(), name='create-user'),
    path('signin/', UserSignInViewset.as_view(), name='signin-user'),
    # path('user-create/', UserCreateViewSet.as_view(), name='user-create'),
    path('gtoken/', GoogleTokenViewSet.as_view(), name='google token'),
    path('forget-password/', ForgetpasswordViewSet.as_view(), name='forget-password'),
    path('forget-password/verify', ForgetpasswordVerifyViewSet.as_view(), name='forget-password')
]