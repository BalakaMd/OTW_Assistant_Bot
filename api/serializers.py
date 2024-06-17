from datetime import datetime

import requests
from rest_framework import serializers

from api.tools.main_tools import create_document
from api.tools.db_templates import end_conference, start_conference

from .models import ChatsHistory, Contact, CustomerContext


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
    client_email_1 = serializers.EmailField(required=False)
    client_email_2 = serializers.EmailField(required=False, allow_blank=True)
    client_email_3 = serializers.EmailField(required=False, allow_blank=True)
    transcript_url = serializers.URLField(required=False)
    audio_url = serializers.URLField(required=False)
    video_url = serializers.URLField(required=False)
    transcript = serializers.CharField(required=False, allow_blank=True)

    def save(self, context_id):
        metadata = {
            'context_id': context_id,
            'title': self.validated_data.get('title', ''),
            'date': self.validated_data.get('date', datetime.now()),
            'client_email_1': self.validated_data.get('client_email_1', ''),
            'client_email_2': self.validated_data.get('client_email_2', ''),
            'client_email_3': self.validated_data.get('client_email_3', ''),
            'transcript_url': self.validated_data.get('transcript_url', ''),
            'audio_url': self.validated_data.get('audio_url', ''),
            'video_url': self.validated_data.get('video_url', ''),
        }
        transcript = self.validated_data.get('transcript', '')

        content = (
            f"Title: {metadata['title']}\n"
            f"Date: {metadata['date']}\n"
            f"Client Email 1: {metadata['client_email_1']}\n"
            f"Client Email 2: {metadata['client_email_2']}\n"
            f"Client Email 3: {metadata['client_email_3']}\n"
            f"Transcript URL: {metadata['transcript_url']}\n"
            f"Audio URL: {metadata['audio_url']}\n"
            f"Video URL: {metadata['video_url']}\n"
            f"Transcript: {start_conference}{transcript}{end_conference}\n"
        )

        document = create_document(content, metadata)
        return document

    def create(self, validated_data):
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
