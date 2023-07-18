from django.urls import path, include
from rest_framework import routers
from organization.views import *

app_name = "organization"

get_company_router = routers.SimpleRouter() 
get_company_router.register('company',CompanyViewSet,basename='company') 


urlpatterns = [
    path('',include(get_company_router.urls)),
    path('signup/', UserSignUpViewSet.as_view(), name='create-user'),
    path('signin/', UserSignInViewset.as_view(), name='signin-user'),
]