from organization.models import  *
from rest_framework import filters

class TypeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            # print(type)
            if queryset.filter(job_type=type).exists():
                queryset = queryset.filter(job_type=type)
            else:
                queryset=queryset.all()
            return queryset

class VoucherFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            if queryset.filter(voucher_type=type).exists():
                queryset = queryset.filter(voucher_type=type)
            else:
                queryset=queryset.all() 
            return queryset   
        
class InvoicesFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            if queryset.filter(invoice_type=type).exists():
                queryset = queryset.filter(invoice_type=type) 
            else:
                queryset=queryset.all()
            return queryset   
        
        
        