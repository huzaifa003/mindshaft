# rag/models.py

from django.db import models

class Document(models.Model):
    """
    Model to store uploaded documents.
    """
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/', max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class IngestionStatus(models.Model):
    is_ingesting = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ingestion in progress: {self.is_ingesting}"

    def save(self, *args, **kwargs):
        self.pk = 1  # Ensure singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_status(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj