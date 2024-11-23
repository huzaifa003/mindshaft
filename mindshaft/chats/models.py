from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    """
    Represents a chat session or thread.
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_all_messages(self):
        """
        Retrieve all messages in this chat.
        """
        return self.messages.all()

    def __str__(self):
        return self.name or f"Chat {self.id}"


class Message(models.Model):
    """
    Represents individual messages within a chat.
    """
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="messages", on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_system_message = models.BooleanField(default=False)

    def __str__(self):
        return f"Message by {self.user or 'System'} in Chat {self.chat.id}"


class ChatParticipant(models.Model):
    """
    Represents users participating in a chat session.
    """
    chat = models.ForeignKey(Chat, related_name="participants", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="chats", on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat', 'user')  # Prevent duplicate user entries for the same chat

    def __str__(self):
        return f"{self.user.username} in Chat {self.chat.id}"


# Add a method to the User model using a mixin
def get_all_user_chats(self):
    """
    Retrieve all chats related to this user.
    """
    return Chat.objects.filter(participants__user=self).distinct()


# Attach the method to the User model dynamically
User.add_to_class("get_all_user_chats", get_all_user_chats)
