# Generated by Django 4.2 on 2024-11-22 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0017_state_name_ru_state_name_uz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='state',
            options={'verbose_name': 'State', 'verbose_name_plural': 'States'},
        ),
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='name')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='counties', to='bot.state')),
            ],
            options={
                'verbose_name': 'County',
                'verbose_name_plural': 'Counties',
            },
        ),
    ]
