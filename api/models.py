from django.db import models


class ChatsHistory(models.Model):
    chat_id = models.CharField(max_length=255, unique=True)
    messages = models.JSONField(default=list)

    class Meta:
        verbose_name_plural = 'chat histories'

    def __str__(self):
        return self.chat_id


class CustomerContext(models.Model):
    customer_id = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255, blank=True)
    data = models.JSONField(default=list)

    def __str__(self):
        return f"Context for customer {self.customer_name}, Customer ID:{self.customer_id}"


class Contact(models.Model):
    contact_id = models.CharField(max_length=255, unique=True)
    contact_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    drive_folder_id = models.CharField(max_length=255, blank=True, null=True)
    related_accounts = models.CharField(max_length=255, blank=True, null=True)
    related_deal = models.CharField(max_length=255, blank=True, null=True)
    design_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    development_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    marketing = models.CharField(max_length=255, blank=True, null=True)
    client_satisfaction = models.CharField(max_length=255, blank=True, null=True)
    client_activity = models.CharField(max_length=255, blank=True, null=True)
    client_type = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Contact ID:{self.contact_id}, Contact Name: {self.contact_name}"


class ModelSettings(models.Model):
    MODEL_CHOICES = [
        ('gpt-3.5-turbo', 'GPT-3.5-turbo',),
        ('gpt-4o', 'GPT-4o'),
        ('gpt-4-turbo', 'GPT-4'),
        ('gemini-pro', 'Gemini Pro'),
        ('claude-3-haiku-20240307', 'Claude 3 Haiku'),
    ]
    settings_id = models.CharField(max_length=255, primary_key=True)
    model_name = models.CharField(max_length=255, choices=MODEL_CHOICES, unique=True, default='gpt-3.5-turbo')
    system_prompt = models.TextField()
    number_of_chunks = models.IntegerField(default=5)
    number_of_QA_history = models.IntegerField(default=5)
    temperature = models.FloatField(default=0.5)

    def __str__(self):
        return "Settings for ID: " + self.settings_id

    class Meta:
        verbose_name_plural = 'LLM Settings'
