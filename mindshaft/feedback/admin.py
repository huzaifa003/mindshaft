from django.contrib import admin
from .models import Feedback

# Register the Feedback model
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'feedback', 'created_at')  # Display these fields in the admin panel list view
    search_fields = ('feedback', 'user__username')  # Enable search functionality for feedback text and user username
    list_filter = ('created_at',)  # Add filter by created_at date
    ordering = ('-created_at',)  # Order by created_at in descending order
