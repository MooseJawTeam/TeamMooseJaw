# Generated by Django 5.1.6 on 2025-04-03 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ums', '0008_alter_documentsignature_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='documenttemplate',
            name='file_path',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='documenttemplate',
            name='template_type',
            field=models.CharField(default='latex', max_length=50),
        ),
        migrations.AlterField(
            model_name='documenttemplate',
            name='latex_content',
            field=models.TextField(blank=True),
        ),
    ]
