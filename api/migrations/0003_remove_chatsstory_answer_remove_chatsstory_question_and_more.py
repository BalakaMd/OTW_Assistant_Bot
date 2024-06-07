# Generated by Django 5.0.6 on 2024-06-05 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_user_id_chatsstory_chat_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatsstory',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='chatsstory',
            name='question',
        ),
        migrations.RemoveField(
            model_name='chatsstory',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='chatsstory',
            name='messages',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='chatsstory',
            name='chat_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
