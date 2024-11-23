from django.urls import path
from .views import UserChatsView, ChatMessagesView, CreateChatView, AddMessageView

urlpatterns = [
    path('user/chats/', UserChatsView.as_view(), name='user-chats'),
    path('chats/<int:chat_id>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
    path('chats/create/', CreateChatView.as_view(), name='create-chat'),
    path('chats/<int:chat_id>/messages/add/', AddMessageView.as_view(), name='add-message'),
]
