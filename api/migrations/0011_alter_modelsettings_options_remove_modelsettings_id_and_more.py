# Generated by Django 5.0.6 on 2024-06-08 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_modelsettings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modelsettings',
            options={'verbose_name_plural': 'LLM Settings'},
        ),
        migrations.RemoveField(
            model_name='modelsettings',
            name='id',
        ),
        migrations.AddField(
            model_name='modelsettings',
            name='settings_id',
            field=models.CharField(default=1, max_length=255, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]