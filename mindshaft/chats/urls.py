from django.urls import path
from .views import (
    CreateChatView,
    UserChatsView,
    ChatMessagesView,
    AddMessageView,
    DeleteChatView,
)

urlpatterns = [
    path('create/', CreateChatView.as_view(), name='create-chat'),
    path('delete/', DeleteChatView.as_view(), name='delete-chat'),
    path('user/', UserChatsView.as_view(), name='user-chats'),
    path('<int:chat_id>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
    path('<int:chat_id>/messages/add/', AddMessageView.as_view(), name='add-message'),
]
