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
                    search_lower = search.lower()
                    search_upper = search.upper()
                    search_capitalize = search.capitalize()
                    queryset = queryset.filter(
                        Q(job_type__contains=search_lower) | Q(job_type__contains=search_upper) | Q(job_type__contains=search_capitalize) |
                        Q(job_status__contains=search_lower) | Q(job_status__contains=search_upper) | Q(job_status__contains=search_capitalize) |
                        Q(scope_of_work__contains=search_lower) | Q(scope_of_work__contains=search_upper) | Q(scope_of_work__contains=search_capitalize) |
                        Q(type__contains=search_lower) | Q(type__contains=search_upper) | Q(type__contains=search_capitalize) |
                        Q(pod__contains=search_lower) | Q(pod__contains=search_upper) | Q(pod__contains=search_capitalize) |
                        Q(pod__istartswith=search.lower()) |Q(pod__istartswith=search.upper()) |
                        Q(poa__contains=search_lower) | Q(poa__contains=search_upper) | Q(poa__contains=search_capitalize) |
                        Q(poa__istartswith=search.lower()) |Q(poa__istartswith=search.upper()) |
                        Q(por__contains=search_lower) | Q(por__contains=search_upper) | Q(por__contains=search_capitalize) |
                        Q(por__istartswith=search.lower()) |Q(por__istartswith=search.upper()) |
                        Q(branch__contains=search_lower) | Q(branch__contains=search_upper) | Q(branch__contains=search_capitalize) |
                        Q(consignee_name__contains=search_lower) | Q(consignee_name__contains=search_upper) | Q(consignee_name__contains=search_capitalize) |
                        Q(shipper_name__contains=search_lower) | Q(shipper_name__contains=search_upper) | Q(shipper_name__contains=search_capitalize) |
                        Q(client_name__contains=search_lower) | Q(client_name__contains=search_upper) | Q(client_name__contains=search_capitalize) |
                        Q(job_number__contains=search_lower) | Q(job_number__contains=search_upper) | Q(job_number__contains=search_capitalize) |
                        Q(enquiry_number__contains=search_lower) | Q(enquiry_number__contains=search_upper) | Q(enquiry_number__contains=search_capitalize)
                    )

                    # queryset = queryset.filter(Q(job_type__contains=search)|Q(job_status__contains=search)|Q(scope_of_work__contains=search)|
                    #         Q(type__contains=search)|Q(pod__contains=search)|Q(poa__contains=search)|Q(por__contains=search)|
                    #         Q(branch__contains=search)|Q(consignee_name__contains=search)|Q(shipper_name__contains=search)|Q(client_name__contains=search)|
                    #         Q(job_number__contains=search)|Q(enquiry_number__contains=search))
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
                queryset = queryset.filter(job__company__users__email=request.user.email)
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
                queryset = queryset.filter(company__users__email=request.user.email)
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
            if queryset.filter(company__users__email=request.user.email):
                queryset = queryset.filter(company__users__email=request.user.email)
                # company = Company.objects.get(user=request.user)
                # queryset = queryset.filter(company=company)
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
            if queryset.filter(company__users__email=request.user.email):
                queryset = queryset.filter(company__users__email=request.user.email)
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
            if queryset.filter(coa__company__users__email=request.user.email).exists():
                queryset = queryset.filter(coa__company__users__email=request.user.email)
                if search:
                    queryset = queryset.filter(Q(code__contains=search)|Q(name__contains=search)|Q(iata_code___contains=search)|
                            Q(type__contains=search)|Q(description__contains=search)|Q(remarks__contains=search)|
                            Q(tax__contains=search)|Q(language_name__contains=search))
            else:
                queryset = CostEntry.objects.none()
            return queryset  
        
class CostEntryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            search = request.query_params.get('search', None)
            shipment_no = request.query_params.get('shipment_no', None)
            job_id = request.query_params.get('job_id', None)
            invoice_id = request.query_params.get('invoice_id', None)
            cost_id = request.query_params.get('cost_id', None)
            start_date = request.query_params.get('start_date',None)
            end_date = request.query_params.get('end_date',None)
            is_included = request.query_params.get('is_included',None)
            sale_cost=request.query_params.get('sale_cost',None)
            print(search)
            if queryset.filter(job_no__company__users__email=request.user.email):
                queryset = queryset.filter(job_no__company__users__email=request.user.email)
                if search:
                    queryset = queryset.filter(Q(currency__contains=search)|Q( sale_cost__contains=search)|Q(description___contains=search)|
                            Q(ex_rate__contains=search)|Q(dr_cr__contains=search)|Q(fcy_amount__contains=search)|
                            Q(prorate_method=search)|Q(shipment_no__contains=search)|Q(amount=search)|Q(tax_group_code__contains=search))
                if shipment_no:
                    queryset = queryset.filter(shipment_no=shipment_no)
                if job_id:
                    queryset = queryset.filter(job_no__id=job_id)
                if cost_id:
                    queryset = queryset.filter(charge__id=cost_id)
                
                if start_date and end_date:
                    queryset = queryset.filter(created_at__range=[start_date, end_date])
                if is_included == 'false':
                    queryset = queryset.filter(is_included=False)
                
                if is_included == 'true':
                    queryset = queryset.filter(is_included=True)

                if sale_cost:
                    queryset = queryset.filter(sale_cost=sale_cost)
                
                if invoice_id:
                    queryset = queryset.filter(invoice__id=invoice_id)
            else:
                queryset = CostEntry.objects.none()
            return queryset
        

class CompanyFliter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.filter(users=request.user):
            queryset = queryset.filter(users__email=request.user.email)
        else:
            queryset=[]
        return queryset   


class SearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if queryset.model:
            search = request.query_params.get('search', None)  
            if  search :
                queryset = queryset.filter(Q(name__contains=search.lower())|Q(name__contains=search.upper())|
                Q(name__istartswith=search.lower()) |Q(name__istartswith=search.upper()) )
                return queryset
            else:
                return queryset