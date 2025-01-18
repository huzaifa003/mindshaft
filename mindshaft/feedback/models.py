from django.db import models
from users.models import CustomUser
# Create your models here.
class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="feedbacks")
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.feedback
    
    