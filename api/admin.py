from django.contrib import admin
from .models import ChatsHistory, CustomerContext, Contact


@admin.register(ChatsHistory)
class ChatsHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomerContext)
class CustomerContextAdmin(admin.ModelAdmin):
    readonly_fields = ('customer_id', 'data', 'customer_name')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    readonly_fields = ["contact_id", "contact_name", "email", "drive_folder_id", "related_accounts", "related_deal",
                       "design_hourly_rate", "development_hourly_rate", "marketing", "client_satisfaction",
                       "client_activity", "client_type"]
