# Generated by Django 4.2 on 2024-11-25 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0025_product_is_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
    ]