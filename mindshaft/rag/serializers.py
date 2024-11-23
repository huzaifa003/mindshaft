from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = Document
        fields = ['id', 'title', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at', 'title']
