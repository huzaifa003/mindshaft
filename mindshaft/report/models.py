from django.db import models
from users.models import CustomUser
from chats.models import Chat

# Create your models here.
class Report(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)