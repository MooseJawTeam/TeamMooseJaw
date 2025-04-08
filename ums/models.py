# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import os
from django.conf import settings
from django.utils import timezone


class Users(models.Model):

    id = models.CharField(primary_key=True, max_length=100, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=100)
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Active")
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Basicuser', 'Basic User'),
    ]
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='Basicuser')

    class Meta:
        app_label = 'ums'
        managed = True
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.role})-{self.status}"

    def is_admin(self):
        return self.role == "Admin"

    def is_basic_user(self):
        return self.role == "Basicuser"
    

''' Document Model '''

class DocumentTemplate(models.Model):
    """Model to store HTML templates for PDF generation"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    html_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class GeneratedDocument(models.Model):
    """Model to store generated PDF documents"""
    title = models.CharField(max_length=200)
    template = models.ForeignKey(DocumentTemplate, on_delete=models.PROTECT)
    created_by = models.ForeignKey(Users, on_delete=models.PROTECT, related_name='created_documents')
    signed_by = models.ManyToManyField(Users, through='DocumentSignature')
    file_path = models.CharField(max_length=255)
    context_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_file_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.file_path)


class DocumentSignature(models.Model):
    """Model to track document signatures"""
    document = models.ForeignKey(GeneratedDocument, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.PROTECT)
    signature_data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.document.title} signed by {self.user.name} at {self.timestamp}"


class DocumentApproval(models.Model):
    """The Approval Process"""
    document = models.ForeignKey(GeneratedDocument, on_delete=models.CASCADE)
    approver = models.ForeignKey(Users, on_delete=models.CASCADE)  
    action = models.CharField(
        max_length=60,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Denied", "Denied")
        ],
        default="Pending"
    )
    comments = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.document.title} - {self.action} by {self.approver.name}"


class AdminSignature(models.Model):
    """Model to store admin signatures"""
    admin = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='admin_signatures')
    signature_image = models.ImageField(upload_to='admin_signatures/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Signature for {self.admin.name}"

    class Meta:
        unique_together = ('admin', 'is_active')


class RCEForm(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    exam_date = models.DateField()
    semester = models.CharField(max_length=20)
    comments = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('denied', 'Denied')
        ],
        default='pending'
    )
    decision = models.CharField(
        max_length=10,
        choices=[
            ('Pass', 'Pass'),
            ('Fail', 'Fail')
        ],
        blank=True,
        null=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RCE Form - {self.user.name} - {self.exam_date}"

class SpecialCircumstanceForm(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    degree = models.CharField(max_length=10, choices=[('Master', 'Master'), ('Doctorate', 'Doctorate')])
    graduation_date = models.CharField(max_length=20)
    reason = models.TextField()
    special_request_type = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('denied', 'Denied')
        ],
        default='pending'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Special Circumstance Form for {self.user.name} ({self.user.email})"

