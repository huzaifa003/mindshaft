from django.contrib import admin
from .models import StripeCustomer

@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_customer_id', 'stripe_subscription_id')
    search_fields = ('user__email', 'stripe_customer_id', 'stripe_subscription_id')
