# Generated by Django 5.0.6 on 2024-06-13 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_modelsettings_model_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatshistory',
            name='whatsapp_chat_history',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='modelsettings',
            name='model_name',
            field=models.CharField(choices=[('gpt-3.5-turbo', 'GPT-3.5-turbo'), ('gpt-4o', 'GPT-4o'), ('gpt-4-turbo', 'GPT-4'), ('gemini-pro', 'Gemini Pro'), ('claude-3-haiku-20240307', 'Claude 3 Haiku')], default='gpt-3.5-turbo', max_length=255, unique=True),
        ),
    ]
