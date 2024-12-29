from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    CancelSubscriptionView,
    StripeWebhookView,
)

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('cancel-subscription/', CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),

]
