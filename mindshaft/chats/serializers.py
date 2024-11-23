from rest_framework import serializers
from .models import Chat, Message
from django.contrib.auth.models import User


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for Chat model.
    """
    class Meta:
        model = Chat
        fields = ['id', 'name', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    """
    user = serializers.StringRelatedField()  # Display the username instead of ID

    class Meta:
        model = Message
        fields = ['id', 'content', 'user', 'is_system_message', 'created_at']


class CreateChatSerializer(serializers.ModelSerializer):
    """
    Serializer to handle chat creation.
    """
    participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Chat
        fields = ['id', 'name', 'participants']


class AddMessageSerializer(serializers.ModelSerializer):
    """
    Serializer to handle message creation.
    """
    class Meta:
        model = Message
        fields = ['id', 'content', 'chat', 'user', 'created_at']
        read_only_fields = ['chat', 'user', 'created_at']
