from rest_framework import serializers
from .models import Chat, Message
from django.contrib.auth import get_user_model

User = get_user_model()  # Dynamically fetch the custom user model

from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display owner's email

    class Meta:
        model = Chat
        fields = ['id', 'name', 'user', 'created_at', 'updated_at']




class MessageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display sender's email

    class Meta:
        model = Message
        fields = ['id', 'chat', 'user', 'content', 'created_at', 'is_system_message']
        read_only_fields = ['created_at']



# class CreateChatSerializer(serializers.ModelSerializer):
#     """
#     Serializer to handle chat creation.
#     """
#     participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

#     class Meta:
#         model = Chat
#         fields = ['id', 'name', 'participants']

class CreateChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'name', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']



class AddMessageSerializer(serializers.ModelSerializer):
    """
    Serializer to handle message creation.
    """
    class Meta:
        model = Message
        fields = ['id', 'content', 'chat', 'user', 'created_at']
        read_only_fields = ['chat', 'user', 'created_at']
