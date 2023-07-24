from organization.models import  *
from rest_framework import filters

class TypeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            if queryset.filter(job_type=type):
                print(request.user)
                queryset = queryset.filter(company__users=request.user)
            else:
                queryset=[]
            return queryset

class VoucherFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            if queryset.filter(voucher_type=type):
                queryset = queryset.filter(job__company__users__email=request.user)
            else:
                queryset=[]
            return queryset   
        
class InvoicesFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            if queryset.filter(invoice_type=type):
                queryset = queryset.filter(company__users=request.user)
            else:
                queryset=[]
            return queryset   
        
        
        