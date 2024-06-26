# Generated by Django 5.0.1 on 2024-02-21 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        ('menu', '0003_alter_fooditem_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='food_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_by_food_item', to='menu.fooditem'),
        ),
    ]
