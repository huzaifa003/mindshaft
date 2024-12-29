from django.contrib import admin
from .models import Document, IngestionStatus

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'file', 'uploaded_at')
    search_fields = ('title',)
    list_filter = ('uploaded_at',)
    ordering = ('-uploaded_at',)

@admin.register(IngestionStatus)
class IngestionStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_ingesting', 'last_updated')
    readonly_fields = ('id', 'last_updated')

    def has_add_permission(self, request):
        """Prevent adding new IngestionStatus objects."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the IngestionStatus object."""
        return False
