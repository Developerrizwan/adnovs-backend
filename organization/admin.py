from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Company)
admin.site.register(Job)
admin.site.register(Vouchers)
admin.site.register(Invoices)
admin.site.register(Coa)
admin.site.register(CoaCategory)
admin.site.register(CoaGroup)
admin.site.register(Pod)
admin.site.register(Poa)
# admin.site.register(Pol)
admin.site.register(Organization)
admin.site.register(Charge)
admin.site.register(CostEntry)