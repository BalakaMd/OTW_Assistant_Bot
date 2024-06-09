import re

import requests
from rest_framework import serializers
from .models import ChatsHistory, Contact
from api.useful_tools import create_document


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatsHistory
        fields = ['chat_id', 'messages']


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1024)
    customer_id = serializers.IntegerField(required=False)


class AddDataSerializer(serializers.Serializer):
    url = serializers.CharField()
    customer_id = serializers.CharField(max_length=255)
    customer_name = serializers.CharField(max_length=255, required=False)

    def save(self):
        url = self.validated_data['url']
        metadata = {'customer_id': self.validated_data['customer_id']}

        export_url = url[:url.find('/edit')] + '/export?format=txt'
        response = requests.get(export_url)
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            document = create_document(content, metadata, is_decorated=True)
            return document
        else:
            return [response.status_code]


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
