from datetime import datetime

from rest_framework import serializers

from .models import ChatsHistory, Contact, CustomerContext, Lead


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatsHistory
        fields = ['chat_id', 'messages']


class QuestionSerializer(serializers.Serializer):
    chat_id = serializers.CharField(max_length=255)
    question = serializers.CharField(max_length=1024)
    customer_id = serializers.IntegerField(required=False)


class AddDataSerializer(serializers.Serializer):
    class Meta:
        model = CustomerContext
        fields = '__all__'

    title = serializers.CharField(max_length=255, required=False)
    date = serializers.DateTimeField(required=False)
    client_email_1 = serializers.EmailField(required=False, allow_blank=True)
    client_email_2 = serializers.EmailField(required=False, allow_blank=True)
    client_email_3 = serializers.EmailField(required=False, allow_blank=True)
    transcript_url = serializers.CharField(required=False, allow_blank=True)
    audio_url = serializers.CharField(required=False, allow_blank=True)
    video_url = serializers.CharField(required=False, allow_blank=True)
    transcript = serializers.CharField(required=False, allow_blank=True)

    def get_contact_id_by_emails(self, emails):
        for email in emails:
            try:
                contact = Contact.objects.get(email=email)
                return contact.contact_id
            except Contact.DoesNotExist:
                try:
                    lead = Lead.objects.get(email=email)
                    return lead.lead_id
                except Lead.DoesNotExist:
                    continue
        return ''

    def create(self, validated_data):
        client_email_1 = self.validated_data.get('client_email_1', '')
        client_email_2 = self.validated_data.get('client_email_2', '')
        client_email_3 = self.validated_data.get('client_email_3', '')
        validated_data['client_id'] = self.get_contact_id_by_emails([client_email_1, client_email_2, client_email_3])
        return CustomerContext.objects.create(**validated_data)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "contact_id", "contact_name", "email", "drive_folder_id",
            "related_accounts", "related_deal", "design_hourly_rate",
            "development_hourly_rate", "marketing", "client_satisfaction",
            "client_activity", "client_type"
        ]

    def create(self, validated_data):
        return Contact.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.contact_id = validated_data.get('contact_id', instance.contact_id)
        instance.contact_name = validated_data.get('contact_name', instance.contact_name)
        instance.email = validated_data.get('email', instance.email)
        instance.drive_folder_id = validated_data.get('drive_folder_id', instance.drive_folder_id)
        instance.related_accounts = validated_data.get('related_accounts', instance.related_accounts)
        instance.related_deal = validated_data.get('related_deal', instance.related_deal)
        instance.design_hourly_rate = validated_data.get('design_hourly_rate', instance.design_hourly_rate)
        instance.development_hourly_rate = validated_data.get('development_hourly_rate',
                                                              instance.development_hourly_rate)
        instance.marketing = validated_data.get('marketing', instance.marketing)
        instance.client_satisfaction = validated_data.get('client_satisfaction', instance.client_satisfaction)
        instance.client_activity = validated_data.get('client_activity', instance.client_activity)
        instance.client_type = validated_data.get('client_type', instance.client_type)
        instance.save()
        return instance


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'
