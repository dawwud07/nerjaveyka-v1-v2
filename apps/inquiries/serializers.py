from rest_framework import serializers

from .models import ContactRequest, Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'name', 'email', 'message', 'created_at')
        read_only_fields = ('id', 'created_at')


class ContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = ('id', 'name', 'phone', 'email', 'message', 'created_at')
        read_only_fields = ('id', 'created_at')
