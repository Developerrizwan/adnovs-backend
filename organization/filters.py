from organization.models import  *
from rest_framework import filters

class TypeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            if queryset.filter(company__users=request.user):
                queryset=queryset.filter(company__users=request.user)
                queryset = queryset.filter(job_type=type)
            else:
                queryset=[]
            return queryset

class VoucherFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            # queryset = queryset.filter(job__company__users=request.user)
            if queryset.filter(job__company__users=request.user):
                queryset = queryset.filter(job__company__users=request.user)
                print(len(queryset))
                queryset = queryset.filter(voucher_type=type)
                print(len(queryset))
            else:
                queryset=[]
            return queryset   
        
class InvoicesFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            if queryset.filter(company__users=request.user):
                queryset = queryset.filter(company__users=request.user)
                queryset = queryset.filter(invoice_type=type)
            else:
                queryset=[]
            return queryset   
        
        
        