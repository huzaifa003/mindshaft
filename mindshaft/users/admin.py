import csv
from django.urls import path
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

from django.contrib.auth.forms import UserChangeForm, UserCreationForm

# Function to export selected emails
def export_user_emails_to_csv(modeladmin, request, queryset):
    """
    Export selected user emails to a CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="selected_user_emails.csv"'

    writer = csv.writer(response)
    # Write the header row
    writer.writerow(['Email', 'First Name', 'Last Name'])

    # Write data rows for selected users
    for user in queryset:
        writer.writerow([user.email, user.first_name, user.last_name])

    return response


export_user_emails_to_csv.short_description = "Export Selected Emails to CSV"


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'email', 'first_name', 'last_name', 'is_staff', 'is_active', 
        'is_premium', 'daily_limit', 'credits_used_today', 'total_credits_used', 
        'last_reset_date', 'date_joined', 'subscription_type', 'reset_cooldown'  # Added here
    )
    list_filter = ('is_staff', 'is_active', 'is_premium', 'subscription_type')  # Added subscription_type to filters
    search_fields = ('email', 'first_name', 'last_name', 'subscription_type')  # Allow searching by subscription type
    ordering = ('email',)
    readonly_fields = ('last_reset_date', 'date_joined', 'total_credits_used')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Subscription', {'fields': ('is_premium', 'subscription_type', 'daily_limit', 'credits_used_today', 'total_credits_used', 'last_reset_date')}),  # Added subscription_type
        ('Timestamps', {'fields': ('date_joined',)}),
        ('Misc', {'fields': ('reset_cooldown',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    actions = [export_user_emails_to_csv]

    def get_urls(self):
        """
        Add custom URLs for the admin.
        """
        urls = super().get_urls()
        custom_urls = [
            path('export-all-emails/', self.admin_site.admin_view(self.export_all_emails_to_csv), name='export_all_emails'),
        ]
        return custom_urls + urls

    def export_all_emails_to_csv(self, request):
        """
        Custom view to export all user emails to a CSV file without requiring selection.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="all_user_emails.csv"'

        writer = csv.writer(response)
        writer.writerow(['Email', 'First Name', 'Last Name', 'Subscription Type'])  # Added Subscription Type

        users = CustomUser.objects.all()

        for user in users:
            writer.writerow([user.email, user.first_name, user.last_name, user.subscription_type])  # Added subscription_type

        return response


admin.site.register(CustomUser, CustomUserAdmin)
