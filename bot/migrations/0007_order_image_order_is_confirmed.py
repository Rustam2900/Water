# Generated by Django 4.2 on 2024-11-15 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_remove_order_items_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='orders/images/', verbose_name='Order Image'),
        ),
        migrations.AddField(
            model_name='order',
            name='is_confirmed',
            field=models.BooleanField(default=False, verbose_name='Is Confirmed'),
        ),
    ]