from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.ListField(
        child=serializers.FileField(),
        write_only=True
    )
    title = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )

    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
