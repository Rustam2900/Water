# Generated by Django 4.2 on 2024-11-28 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0026_order_is_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='amount',
            field=models.IntegerField(default=0, max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.IntegerField(blank=True, default=0, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(max_length=100),
        ),
    ]
