# Generated by Django 4.2 on 2024-11-28 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0027_alter_cartitem_amount_alter_order_total_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(),
        ),
    ]