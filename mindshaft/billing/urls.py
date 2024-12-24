from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    CancelSubscriptionView,
    StripeWebhookView,
    SubscriptionSuccessView,
    SubscriptionCancelView,
    SubscriptionCancelledView,
)

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('cancel-subscription/', CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('subscription-success/', SubscriptionSuccessView.as_view(), name='subscription_success'),
    path('subscription-cancel/', SubscriptionCancelView.as_view(), name='subscription_cancel'),
    path('subscription-cancelled/', SubscriptionCancelledView.as_view(), name='subscription_cancelled'),
]
