# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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
        ('admin', 'Admin'),
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
