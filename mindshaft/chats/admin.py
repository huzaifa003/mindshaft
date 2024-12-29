from django.contrib import admin
from .models import Chat, Message, ChatParticipant

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1  # Number of empty fields to display for new messages
    fields = ('user', 'content', 'created_at', 'is_system_message')
    readonly_fields = ('created_at',)

class ChatParticipantInline(admin.TabularInline):
    model = ChatParticipant
    extra = 1  # Number of empty fields to display for new participants
    fields = ('user', 'joined_at')
    readonly_fields = ('joined_at',)

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'created_at', 'updated_at')
    search_fields = ('name', 'user__username')  # Assuming 'username' exists in your user model
    list_filter = ('created_at', 'updated_at')
    inlines = [MessageInline, ChatParticipantInline]
    ordering = ('-created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'created_at', 'is_system_message')
    search_fields = ('content', 'user__username', 'chat__name')
    list_filter = ('created_at', 'is_system_message')
    ordering = ('-created_at',)

@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'joined_at')
    search_fields = ('chat__name', 'user__username')
    list_filter = ('joined_at',)
    ordering = ('-joined_at',)
