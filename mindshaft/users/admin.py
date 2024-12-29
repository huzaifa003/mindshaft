from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_premium', 'daily_limit', 'credits_used_today', 'total_credits_used', 'last_reset_date', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_premium')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('last_reset_date', 'date_joined', 'total_credits_used')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Subscription Details', {
            'fields': ('is_premium', 'daily_limit', 'credits_used_today', 'total_credits_used', 'last_reset_date')
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
