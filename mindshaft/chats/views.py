from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Chat, Message, ChatParticipant
from .serializers import ChatSerializer, MessageSerializer, CreateChatSerializer, AddMessageSerializer
from django.contrib.auth.models import User


class UserChatsView(APIView):
    """
    View to list all chats related to the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        chats = user.get_all_user_chats()
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)


class ChatMessagesView(APIView):
    """
    View to list all messages of a specific chat.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id, *args, **kwargs):
        chat = get_object_or_404(Chat, id=chat_id)

        # Ensure the user is a participant of the chat
        if not chat.participants.filter(user=request.user).exists():
            return Response({"error": "You are not a participant of this chat."}, status=403)

        messages = chat.get_all_messages()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class CreateChatView(APIView):
    """
    View to create a new chat with the logged-in user as the owner.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Add the logged-in user as the owner of the chat
        chat_data = request.data.copy()
        chat_data['user'] = request.user.id  # Set the logged-in user as the chat owner
        print(chat_data)
        serializer = CreateChatSerializer(data=chat_data)
        if serializer.is_valid():
            chat = serializer.save(user=request.user)

            # Automatically add the logged-in user as a participant
            ChatParticipant.objects.create(chat=chat, user=request.user)

            return Response({
                'id': chat.id,
                'name': chat.name,
                'owner': request.user.email,
                'participants': [request.user.email]  # Default participant list with the owner
            }, status=201)
        return Response(serializer.errors, status=400)


class AddMessageView(APIView):
    """
    View to add a message to a chat owned by the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id, *args, **kwargs):
        try:
            chat = Chat.objects.get(id=chat_id, user=request.user)
        except Chat.DoesNotExist:
            raise PermissionDenied("You do not have permission to add messages to this chat.")

        # Add the message to the chat
        message_data = request.data.copy()
        message_data['chat'] = chat.id
        message_data['user'] = request.user.id

        serializer = MessageSerializer(data=message_data)
        if serializer.is_valid():
            message = serializer.save()
            return Response({
                'id': message.id,
                'chat': chat.id,
                'user': request.user.email,
                'content': message.content,
                'created_at': message.created_at
            }, status=201)
        return Response(serializer.errors, status=400)