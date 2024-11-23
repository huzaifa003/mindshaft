from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
    View to create a new chat.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateChatSerializer(data=request.data)
        if serializer.is_valid():
            chat = serializer.save()
            
            # Add the authenticated user as a participant if not already included
            participant_ids = request.data.get('participants', [])
            if request.user.id not in participant_ids:
                participant_ids.append(request.user.id)
            
            participants = User.objects.filter(id__in=participant_ids)
            for participant in participants:
                ChatParticipant.objects.create(chat=chat, user=participant)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AddMessageView(APIView):
    """
    View to add a message to a chat.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id, *args, **kwargs):
        chat = get_object_or_404(Chat, id=chat_id)

        # Ensure the user is a participant of the chat
        if not chat.participants.filter(user=request.user).exists():
            return Response({"error": "You are not a participant of this chat."}, status=403)

        serializer = AddMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(chat=chat, user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
