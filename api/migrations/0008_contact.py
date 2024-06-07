# Generated by Django 5.0.6 on 2024-06-07 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_context_customer_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_id', models.CharField(max_length=255, unique=True)),
                ('contact_name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('drive_folder_id', models.CharField(blank=True, max_length=255, null=True)),
                ('related_accounts', models.CharField(blank=True, max_length=255, null=True)),
                ('related_deal', models.CharField(blank=True, max_length=255, null=True)),
                ('design_hourly_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('development_hourly_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('marketing', models.CharField(blank=True, max_length=255, null=True)),
                ('client_satisfaction', models.CharField(blank=True, max_length=255, null=True)),
                ('client_activity', models.CharField(blank=True, max_length=255, null=True)),
                ('client_type', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
