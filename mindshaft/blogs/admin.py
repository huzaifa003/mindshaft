from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from .models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'updated_at', 'view_image', 'blog_actions')
    search_fields = ('title', 'content')
    list_filter = ('uploaded_at', 'updated_at')
    readonly_fields = ('uploaded_at', 'updated_at', 'display_image')

    def view_image(self, obj):
        """
        Displays a clickable thumbnail of the image in the admin panel.
        """
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height: 50px; width: 50px; object-fit: cover;" /></a>',
                obj.image.url,
                obj.image.url,
            )
        return "No Image"
    view_image.short_description = "Image"

    def display_image(self, obj):
        """
        Displays the full-sized image in the detailed admin view.
        """
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100%; height: auto;" />', obj.image.url)
        return "No Image Uploaded"
    display_image.short_description = "Image Preview"

    def blog_actions(self, obj):
        """
        Provides admin actions for update and delete.
        """
        update_url = reverse('admin:blogs_blog_change', args=[obj.id])  # Uses the correct change URL
        delete_url = reverse('admin:blogs_blog_delete', args=[obj.id])  # Uses the correct delete URL
        return format_html(
            '<a href="{}" style="color: blue; margin-right: 10px;">Update</a>'
            '<a href="{}" style="color: red;">Delete</a>',
            update_url, delete_url
        )
    blog_actions.short_description = "Actions"

    def save_model(self, request, obj, form, change):
        """
        Custom save method to add admin feedback messages.
        """
        if not obj.id:
            self.message_user(request, "Blog added successfully!", level='success')
        else:
            self.message_user(request, "Blog updated successfully!", level='info')
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Custom delete method to add admin feedback messages.
        """
        self.message_user(request, f"Blog '{obj.title}' deleted successfully!", level='warning')
        super().delete_model(request, obj)

    def get_queryset(self, request):
        """
        Customize the queryset to add any filters if required.
        """
        queryset = super().get_queryset(request)
        return queryset
