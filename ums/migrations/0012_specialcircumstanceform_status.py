# Generated by Django 5.1.6 on 2025-04-03 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ums', '0011_rceform_status_alter_rceform_decision'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialcircumstanceform',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending', max_length=20),
        ),
    ]
