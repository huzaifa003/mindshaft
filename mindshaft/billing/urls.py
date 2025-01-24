from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    CreateYearlyCheckoutSessionView,
    CancelSubscriptionView,
    StripeWebhookView,
)

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('create-yearly-checkout-session/', CreateYearlyCheckoutSessionView.as_view(), name='create_yearly_checkout_session'),
    
    path('cancel-subscription/', CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),

]
