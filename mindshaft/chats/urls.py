from django.urls import path
from .views import (
    CreateChatView,
    UserChatsView,
    ChatMessagesView,
    AddMessageView
)

urlpatterns = [
    path('chats/create/', CreateChatView.as_view(), name='create-chat'),
    path('chats/user/', UserChatsView.as_view(), name='user-chats'),
    path('chats/<int:chat_id>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
    path('chats/<int:chat_id>/messages/add/', AddMessageView.as_view(), name='add-message'),
]
