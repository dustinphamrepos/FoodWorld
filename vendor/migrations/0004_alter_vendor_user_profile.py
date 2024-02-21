# Generated by Django 5.0.1 on 2024-02-21 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_userprofile_district'),
        ('vendor', '0003_alter_vendor_vendor_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='user_profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_by_user_profile', to='accounts.userprofile'),
        ),
    ]
