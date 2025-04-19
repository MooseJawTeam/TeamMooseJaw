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
from mptt.models import MPTTModel, TreeForeignKey


class OrganizationalUnit(MPTTModel):
    """Model for organizational units in a hierarchical structure using MPTT for better tree operations"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class MPTTMeta:
        order_insertion_by = ['name']
    
    def __str__(self):
        return self.name

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
    # Add organizational unit relationship
    organizational_units = models.ManyToManyField(OrganizationalUnit, through='UserOrganizationAssignment', related_name='users')

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
    
    def get_assigned_units(self):
        """Get all units this user is assigned to"""
        return self.organizational_units.all()
    

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
    # Add organizational context to approvals
    organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.SET_NULL, null=True, blank=True, 
                                          help_text="The organizational unit context for this approval")
    is_org_level_approval = models.BooleanField(default=False, 
                                            help_text="Whether this is an organizational-level approval")

    def __str__(self):
        org_context = f" for {self.organizational_unit.name}" if self.organizational_unit else ""
        org_level = " (Org-level)" if self.is_org_level_approval else ""
        return f"{self.document.title} - {self.action} by {self.approver.name}{org_context}{org_level}"


class UserOrganizationAssignment(models.Model):
    """Model to track user assignment to organizational units"""
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE)
    is_approver = models.BooleanField(default=False, help_text="Whether the user can approve requests for this unit")
    is_organizational_approver = models.BooleanField(default=False, help_text="Whether the user can approve requests across multiple units")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'organizational_unit')
        ordering = ('organizational_unit__name', 'user__name')

    def __str__(self):
        approver_status = ""
        if self.is_approver:
            approver_status = " (Unit Approver)"
        if self.is_organizational_approver:
            approver_status = " (Organizational Approver)"
        return f"{self.user.name} in {self.organizational_unit.name}{approver_status}"

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
    # Add organizational unit field
    organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.SET_NULL, null=True, 
                                          help_text="The organizational unit this request belongs to")
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
        org_unit = f" ({self.organizational_unit.name})" if self.organizational_unit else ""
        return f"RCE Form - {self.user.name} - {self.exam_date}{org_unit}"

class SpecialCircumstanceForm(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    degree = models.CharField(max_length=10, choices=[('Master', 'Master'), ('Doctorate', 'Doctorate')])
    graduation_date = models.CharField(max_length=20)
    reason = models.TextField()
    special_request_type = models.CharField(max_length=100)
    # Add organizational unit field
    organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.SET_NULL, null=True, 
                                          help_text="The organizational unit this request belongs to")
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
        org_unit = f" ({self.organizational_unit.name})" if self.organizational_unit else ""
        return f"Special Circumstance Form for {self.user.name} ({self.user.email}){org_unit}"

