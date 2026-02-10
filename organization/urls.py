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

user_profile_router = routers.SimpleRouter() 
user_profile_router.register('user/profile', GetUserProfileViewSet, basename='userprofile')

user_delete_router = routers.SimpleRouter()
user_delete_router.register('user/delete',UserDeleteViewSet, basename='user-delete')

get_users_router = routers.SimpleRouter() 
get_users_router.register('get-users',GetusersViewSet,basename='getusers')

get_user_count_router = routers.SimpleRouter() 
get_user_count_router.register('user-related-counts', UserRelatedCountsViewSet, basename='user-related-counts')

coa_router = routers.SimpleRouter() 
coa_router.register('master/coa', CoaViewSet, basename='coa') 

get_coa_router=routers.SimpleRouter()
get_coa_router.register('get-coa',GetCoaViewSet,basename='getcoa')

coa_categoryrouter = routers.SimpleRouter() 
coa_categoryrouter.register('master/coacategory', CoaCategoryViewSet, basename='coa-category')  

coa_grouprouter = routers.SimpleRouter() 
coa_grouprouter.register('master/coagroup', CoaGroupViewSet, basename='coa-group') 

get_coa_group_router=routers.SimpleRouter()
get_coa_group_router.register('get-coagroup', GetCoaGroupViewSet,basename='getcoagroup')

pod_router = routers.SimpleRouter() 
pod_router.register('master/pod', PodViewSet, basename='pod')  

poa_router = routers.SimpleRouter() 
poa_router.register('master/poa', PoaViewSet, basename='poa')

# pol_router = routers.SimpleRouter()
# pol_router.register('master/pol',PolViewSet,basename='pol')

charge_router= routers.SimpleRouter() 
charge_router.register('master/charge', ChargeViewSet, basename='charge') 

get_charge_router= routers.SimpleRouter()
get_charge_router.register('get-charge',GetchargeViewset,basename='charge') 

cost_entry_router= routers.SimpleRouter()
cost_entry_router.register('master/cost_entry', CostEntryViewset, basename='cost_entry') 

get_cost_entry_router= routers.SimpleRouter()
get_cost_entry_router.register('get-costentry',GetCostEntryViewset,basename='cost_entry')

organization_router = routers.SimpleRouter() 
organization_router.register('master/organization', OrganizationViewSet, basename='oraganization')

get_organization_router = routers.SimpleRouter() 
get_organization_router.register('get-organization',GetOrganzationViewset, basename='oraganization')

accountdetails_router = routers.SimpleRouter() 
accountdetails_router.register('master/accountdetails', AccountDetailsViewset, basename='accountdetails')

profit_loss_router = routers.SimpleRouter() 
profit_loss_router.register('profit/loss', ProfitLossViewset, basename='profit-loss')

general_ledger_router = routers.SimpleRouter() 
general_ledger_router.register('general/ledger', GeneralledgerViewset, basename='general-ledger')

coa_invoices_router = routers.SimpleRouter() 
coa_invoices_router.register('get_coa_invoices', GetCoaInvoicesViewset, basename='general-ledger')

account_statement_router = routers.SimpleRouter()
account_statement_router.register('account/statement', AccountStatementViewset, basename='account-statement')

receivable_router = routers.SimpleRouter()
receivable_router.register('account/receivable', AccountsReceivableViewSet, basename='accounts-receivable')

sheet_report_router = routers.SimpleRouter() 
sheet_report_router.register('sheet_report', SheetReportViewset, basename='sheet-report')

trial_balance_router = routers.SimpleRouter() 
trial_balance_router.register('trial_balance', TrialBalanceViewset, basename='trial-balance')

job_voucher_router = routers.SimpleRouter() 
job_voucher_router.register('job_voucher', JobVoucherViewset, basename='trial-balance')

job_invoice_router = routers.SimpleRouter() 
job_invoice_router.register('job_invoice', JobInvoiceViewset, basename='trial-balance')

branch_router = routers.SimpleRouter() 
branch_router.register('master/branch', BranchViewset, basename='branch')


urlpatterns = [
    path('',include(get_user_count_router.urls)),
    path('',include(user_delete_router.urls)),
    path('',include(user_profile_router.urls)),
    path('',include(get_company_router.urls)),
    path('', include(company_router.urls)),
    path('',include(get_job_router.urls)),
    path('', include(job_router.urls)),
    path('',include(get_vocher_router.urls)),
    path('', include(voucher_router.urls)),
    path('',include(get_invoice_router.urls)), 
    path('', include(invoice_router.urls)),
    path('',include(get_users_router.urls)),
    path('',include(coa_router.urls)),
    path('',include(get_coa_router.urls)),
    path('',include(coa_categoryrouter.urls)),
    path('',include(pod_router.urls)),
    path('',include(poa_router.urls)),
    path('',include(coa_invoices_router.urls)),
    path('',include(get_coa_group_router.urls)),
    path('',include(coa_grouprouter.urls)),
    path('',include(organization_router.urls)),
    path('',include(charge_router.urls)),
    path('',include(get_charge_router.urls)),
    path('',include(cost_entry_router.urls)),
    path('',include(get_cost_entry_router.urls)),
    path('',include(get_organization_router.urls)),
    path('',include(account_statement_router.urls)),
    path('',include(accountdetails_router.urls)),
    path('',include(profit_loss_router.urls)),
    path('',include(general_ledger_router.urls)),
    path('',include(sheet_report_router.urls)),
    path('',include(trial_balance_router.urls)),
    path('',include(job_voucher_router.urls)),
    path('',include(job_invoice_router.urls)),
    path('',include(branch_router.urls)),
    path('', include(receivable_router.urls)),
    path('signup/', UserSignUpViewSet.as_view(), name='create-user'),
    path('signin/', UserSignInViewset.as_view(), name='signin-user'),
    path('user-create/', UserCreateViewSet.as_view(), name='user-create'),
    path('gtoken/', GoogleTokenViewSet.as_view(), name='google token'),
    path('forget-password/', ForgetpasswordViewSet.as_view(), name='forget-password'),
    path('forget-password/verify', ForgetpasswordVerifyViewSet.as_view(), name='forget-password')
]