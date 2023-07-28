from organization.models import  *
from rest_framework import filters
from django.db.models import Q

class TypeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            search = request.query_params.get('search', None)
            if queryset.filter(company__users=request.user):
                queryset=queryset.filter(company__users=request.user)
                if search:
                    queryset = queryset.filter(Q(job_type__contains=search)|Q(job_status__contains=search)|Q(scope_of_work__contains=search)|
                            Q(type__contains=search)|Q(pod__contains=search)|Q(poa__contains=search)|Q(por__contains=search)|
                            Q(branch__contains=search)|Q(consignee_name__contains=search)|Q(shipper_name__contains=search)|Q(client_name__contains=search)|
                            Q(job_number__contains=search)|Q(enquiry_number__contains=search))
                    # return queryset
                queryset = queryset.filter(job_type=type)
            else:
                queryset=[]
            return queryset

class VoucherFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            search = request.query_params.get('search', None)
            if queryset.filter(job__company__users=request.user):
                queryset = queryset.filter(job__company__users=request.user)
                if search:
                    queryset = queryset.filter(Q(voucher_type__contains=search)|Q(branch__contains=search)|Q(amount_sar__contains=search)|
                            Q(party_account__contains=search)|Q(division__contains=search)|Q(naration__contains=search)|Q(outstanding_amount__contains=search))
                    # return queryset
                queryset = queryset.filter(voucher_type=type)
            else:
                queryset=[]
            return queryset   
        
class InvoicesFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            search = request.query_params.get('search', None)
            if queryset.filter(company__users=request.user):
                queryset = queryset.filter(company__users=request.user)
                if search:
                    queryset = queryset.filter(Q(bl_number__contains=search)|Q(invoice_type__contains=search)|Q(consignee_name__contains=search)|
                            Q(shipper_name__contains=search)|Q(ex_rate__contains=search)|Q(poa__contains=search)|Q(pod__contains=search)|
                            Q(amount_sar__contains=search)|Q(fc_amount__contains=search)|Q(narration__contains=search))
                    # return queryset
                queryset = queryset.filter(invoice_type=type)
            else:
                queryset=[]
            return queryset   
        
        
class OrganizationFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            type = request.query_params.get('type', None)
            search = request.query_params.get('search', None)
            if queryset.filter(company__users=request.user):
                queryset = queryset.filter(company__users=request.user)
                if search:
                    queryset = queryset.filter(Q(name__contains=search)|Q(type__contains=search)|Q(language_name__contains=search)|
                            Q(address__contains=search)|Q(vat_trn_number__contains=search)|Q(website__contains=search))
                    # return queryset
                queryset = queryset.filter(type=type)
            else:
                queryset=[]
            return queryset        
        
class CoaFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            search = request.query_params.get('search', None)
            print(search)
            if queryset.filter(voucher__job__company__users=request.user):
                queryset = queryset.filter(voucher__job__company__users=request.user)
                if search:
                    queryset = queryset.filter(Q(code__contains=search)|Q(name__contains=search)|Q(type___contains=search)|
                            Q(coa_type__contains=search)|Q(is_direct_indirect__contains=search)|Q(dr_cr__contains=search)|
                            Q(subgroup__contains=search)|Q(category__contains=search)|Q(group__contains=search)|Q(language_name__contains=search)|
                            Q(long_name__contains=search)|Q(additional_reference_code__contains=search))
            else:
                queryset=[]
            return queryset  
        
class ChargeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            search = request.query_params.get('search', None)
            print(search)
            if queryset.filter(coa__job__company__users=request.user):
                queryset = queryset.filter(voucher__job__company__users=request.user)
                if search:
                    queryset = queryset.filter(Q(code__contains=search)|Q(name__contains=search)|Q(iata_code___contains=search)|
                            Q(type__contains=search)|Q(description__contains=search)|Q(remarks__contains=search)|
                            Q(tax__contains=search)|Q(language_name__contains=search))
        
            else:
                queryset=[]
            return queryset  
        
class CostEntryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            search = request.query_params.get('search', None)
            print(search)
            if queryset.filter(job__company__users=request.user):
                queryset = queryset.filter(job__company__users=request.user)
                if search:
                    queryset = queryset.filter(Q(currency__contains=search)|Q( sale_cost__contains=search)|Q(description___contains=search)|
                            Q(ex_rate__contains=search)|Q(dr_cr__contains=search)|Q(fcy_amount__contains=search)|
                            Q(prorate_method=search)|Q(shipment_no__contains=search))|Q(amount=search)|Q(tax_group_code__contains=search)
            else:
                queryset=[]
            return queryset