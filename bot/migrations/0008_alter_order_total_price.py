# Generated by Django 4.2 on 2024-11-15 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_order_image_order_is_confirmed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
