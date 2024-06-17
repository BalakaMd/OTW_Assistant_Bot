from django.contrib import admin

from .models import ChatsHistory, Contact, CustomerContext, ModelSettings


@admin.register(ChatsHistory)
class ChatsHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomerContext)
class CustomerContextAdmin(admin.ModelAdmin):
    search_fields = ['title', 'client_email_1', 'client_email_2', 'client_email_3', 'transcript']
    readonly_fields = ['id', 'title', 'date', 'client_email_1', 'client_email_2', 'client_email_3', 'transcript_url',
                       'audio_url', 'video_url', 'transcript']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    search_fields = ['contact_id', 'contact_name', 'email']
    readonly_fields = ["contact_id", "contact_name", "email", "drive_folder_id", "related_accounts", "related_deal",
                       "design_hourly_rate", "development_hourly_rate", "marketing", "client_satisfaction",
                       "client_activity", "client_type"]


@admin.register(ModelSettings)
class ModelSettingsAdmin(admin.ModelAdmin):
    search_fields = ('model_name',)
