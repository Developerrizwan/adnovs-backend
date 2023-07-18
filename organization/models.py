from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    state = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    users = models.ManyToManyField(get_user_model(), blank=True)

class Job(models.Model):

    Enquiry = 'Enquiry'
    Job= 'Job'
    
    JOB_TYPE_CHOICES = (
        (Enquiry, 'Enquiry'),
        (Job, 'Job')
    )

    Cargo_Collected ='Cargo Collected'
    Under_Export_Clearance = 'Under Export Clearance'
    Departed = 'Departed'
    In_Transit = 'In Transit'
    Arrived = 'Arrived'
    Under_Import_Clearance = 'Under Import Clearance'
    Do_Collected = 'Do Collected'
    Gate_Pass_Issued = 'Gate Pass Issued'
    Under_Delivery = 'Under Delivery'
    In_Warehouse_Storage = 'In Warehouse Storage'
    Delivered = 'Delivered'
    Invoiced = 'Invoiced'
    Finished = 'Finished'
    Cancelled = 'Cancelled'


    JOB_STATUS_CHOICES = (
        (Cargo_Collected, 'Cargo Collected'),
        (Under_Export_Clearance, 'Under Export Clearance'),
        (Departed, 'Departed'),
        (In_Transit, 'In Transit'),
        (Arrived, 'Arrived'),
        (Under_Import_Clearance, 'Under Import Clearance'),
        (Do_Collected, 'Do Collected'),
        (Gate_Pass_Issued, 'Gate Pass Issued'),
        (Under_Delivery, 'Under Delivery'),
        (In_Warehouse_Storage, 'In Warehouse Storage'),
        (Delivered, 'Delivered'),
        (Invoiced, 'Invoiced'),
        (Finished, 'Finished'),
        (Cancelled, 'Cancelled')
    )


    bl_number = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField("Job Type", max_length=255, choices=JOB_TYPE_CHOICES)
    job_status = models.CharField("Job Status", max_length=255, choices=JOB_STATUS_CHOICES)
    bayan_number = models.CharField(max_length=255, blank=True, null=True)
    pod = models.CharField(max_length=255, blank=True, null=True)
    poa = models.CharField(max_length=255, blank=True, null=True)
    consignee_name = models.CharField(max_length=255, blank=True, null=True)
    shipper_name = models.CharField(max_length=255, blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, null=False)
    is_deleted = models.BooleanField(default=True)
    deleted_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE, null=False, blank=False, related_name='deleted_jobs')
    deleted_at = models.DateTimeField(default=timezone.now)
    created_by =  models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=False, blank=False, related_name='created_jobs')
    created_at = models.DateTimeField(default=timezone.now)



class Vouchers(models.Model):

    Journal = 'Journal'
    Payment= 'Payment'
    Receipt= 'Receipt'
    
    VOUCHER_TYPE_CHOICES = (
        (Journal, 'Journal'),
        (Payment, 'Payment'),
        (Receipt, 'Receipt'),
    )

    voucher_type = models.CharField("Voucher Type", max_length=255, choices=VOUCHER_TYPE_CHOICES)
    date = models.DateTimeField(default=timezone.now, blank=False, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    gl_date = models.DateTimeField(default=timezone.now, blank=False, null=True)
    start_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    end_date = models.DateTimeField(default=timezone.now, blank=True,null=True)
    fc_amount = models.CharField(max_length=255, blank=True, null=True)
    amount_sar = models.CharField(max_length=255, blank=True, null=True)
    party_account = models.CharField(max_length=255, blank=True, null=True)
    division = models.CharField(max_length=255, blank=True, null=True)
    naration = models.CharField(max_length=255, blank=True, null=True)
    outstanding_amount = models.CharField(max_length=255, blank=True, null=True)
    dr_account = models.CharField(max_length=255, blank=True, null=True)
    cr_account = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=False, null=False)


class Invoices(models.Model):

    Sales= 'Sales'
    Purchase= 'Purchase'
    
    INVOICE_TYPE_CHOICES = (
        (Sales, 'Sales'),
        (Purchase, 'Purchase'),
    )

    bl_number = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    invoice_type = models.CharField("Invoice Type", max_length=255, choices=INVOICE_TYPE_CHOICES, blank=False, null=False)
    consignee_name = models.CharField(max_length=255, blank=True, null=True)
    currency_sar = models.CharField(max_length=255, blank=True, null=True)
    bayan_number = models.CharField(max_length=255, blank=True, null=True)
    shipper_name = models.CharField(max_length=255, blank=True, null=True)
    ex_rate = models.CharField(max_length=255, blank=True, null=True) 
    pod = models.CharField(max_length=255, blank=True, null=True)
    poa = models.CharField(max_length=255, blank=True, null=True)
    fc_amount = models.CharField(max_length=255, blank=True, null=True)
    amount_sar = models.CharField(max_length=255, blank=True, null=True)
    ref_data = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    bill_amount = models.CharField(max_length=255, blank=True, null=True)
    narration = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, null=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=False, null=False)

