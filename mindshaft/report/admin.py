from django.contrib import admin
from .models import Report

# Register the Report model
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat', 'reason', 'created_at')  # Display these fields in the admin list view
    search_fields = ('user__username', 'chat__id', 'reason')  # Enable search functionality for user, chat, and reason
    list_filter = ('created_at',)  # Add filter for created_at
    ordering = ('-created_at',)  # Order by created_at in descending order
