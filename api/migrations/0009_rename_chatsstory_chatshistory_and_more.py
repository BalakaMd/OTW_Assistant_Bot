# Generated by Django 5.0.6 on 2024-06-07 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_contact'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ChatsStory',
            new_name='ChatsHistory',
        ),
        migrations.RenameModel(
            old_name='Context',
            new_name='CustomerContext',
        ),
    ]
