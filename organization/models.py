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


    D2D ='D2D'
    EXW = 'EXW'
    FOB = 'FOB'
    CIF = 'CIF'
    CNF = 'CNF'
    CANDF = 'C&F'
    DDP = 'DDP'
    DAP = 'DAP'
    CPT = 'CPT'
    TRANS = 'TRANS'
    Delivered = 'Delivered'
    Invoiced = 'Invoiced'
    Finished = 'Finished'
    Cancelled = 'Cancelled'
    DTRANS = "D-TRANS"
    OTHERS = "OTHERS"


    SOCPE_OF_WORK = (
        (D2D, 'D2D'),
        (EXW, 'EXW'),
        (FOB, 'FOB'),
        (CIF, 'CIF'),
        (CNF, 'CNF'),
        (CANDF, 'C&F'),
        (DDP, 'DDP'),
        (DAP, 'DAP'),
        (CPT, 'CPT'),
        (TRANS, 'TRANS'),
        (DTRANS, 'D-TRANS'),
        (OTHERS, 'OTHERS')

    )

    CONTAINER_CHOICES = (
            ('20DC', '20’DC'),
            ('20RF', '20’RF'),
            ('20ST', '20’ST'),
            ('20OT', '20’OT'),
            ('20HC', '20’HC'),
            ('40DC', '40’DC'),
            ('40RF', '40’RF'),
            ('40ST', '40’ST'),
            ('40OT', '40’OT'),
            ('40HC', '40’HC'),
            ('FLAT_RACK', 'FLAT RACK'),
            ('FTL', 'FTL'),
            ('LTL', 'LTL'),
        )
    
    FREIGHT_CHOICES = [
        ('Air_Freight', 'Air Freight'),
        ('Sea_Freight', 'Sea Freight'),
        ('Land_Freight', 'Land Freight'),
        ('Transportation', 'Transportation'),
        ('Warehousing', 'Warehousing'),
    ]

    bl_number = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField("Job Type", max_length=255, choices=JOB_TYPE_CHOICES)
    job_status = models.CharField("Job Status", max_length=255, choices=JOB_STATUS_CHOICES)
    scope_of_work = models.CharField("Scope of Work ", max_length=255, choices=SOCPE_OF_WORK, blank=True, null=True)
    container_type = models.CharField("Container Type", max_length=10,choices=CONTAINER_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=20,choices=FREIGHT_CHOICES, blank=True, null=True)
    bayan_number = models.CharField(max_length=255, blank=True, null=True)
    pod = models.CharField(max_length=255, blank=True, null=True)
    poa = models.CharField(max_length=255, blank=True, null=True)
    por = models.TextField(blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    consignee_name = models.CharField(max_length=255, blank=True, null=True)
    shipper_name = models.CharField(max_length=255, blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, null=False)
    is_deleted = models.BooleanField(default=True)
    deleted_by = models.ForeignKey(get_user_model(),on_delete=models.CASCADE, null=True, blank=False, related_name='deleted_jobs')
    deleted_at = models.DateTimeField(default=timezone.now)
    created_by =  models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=False, related_name='created_jobs')
    created_at = models.DateTimeField(default=timezone.now)
    job_number = models.CharField(max_length=250,blank=True,null=True)
    enquiry_number = models.CharField(max_length=250,blank=True,null=True)


class Vouchers(models.Model):

    Journal = 'Journal'
    Payment= 'Payment'
    Receipt= 'Receipt'
    Credit = 'Credit'
    Debit ='Debit'
    
    VOUCHER_TYPE_CHOICES = (
        (Journal, 'Journal'),
        (Payment, 'Payment'),
        (Receipt, 'Receipt'),
        (Credit, 'Credit'),
        (Debit,'Debit')
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

