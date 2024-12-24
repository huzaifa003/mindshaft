import stripe
from django.conf import settings
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import StripeCustomer
from .logging_util import getLogger

logger = getLogger()

# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        stripe_customer, created = StripeCustomer.objects.get_or_create(user=user)

        # Create a Stripe customer if not already exists
        if created or not stripe_customer.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            stripe_customer.stripe_customer_id = customer['id']
            stripe_customer.save()

        # Create a Stripe Checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{'price': 'price_1QZSQqKbqgiOLixUfdRFtnW6', 'quantity': 1}],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('subscription_success')),
            cancel_url=request.build_absolute_uri(reverse('subscription_cancel')),
        )
        return Response({'url': checkout_session.url})


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            stripe_customer = StripeCustomer.objects.get(user=user)
            if stripe_customer.stripe_subscription_id:
                stripe.Subscription.delete(stripe_customer.stripe_subscription_id)
                stripe_customer.stripe_subscription_id = None
                stripe_customer.save()

                # Mark the user as non-premium
                user.is_premium = False
                user.save()
            return Response({'message': 'Subscription cancelled successfully'})
        except StripeCustomer.DoesNotExist:
            return Response({'error': 'User not subscribed'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = []  # No authentication required for Stripe webhooks

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response(status=400)  # Invalid payload
        except stripe.error.SignatureVerificationError:
            return Response(status=400)  # Invalid signature

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_id = session.get('customer')
            subscription_id = session.get('subscription')

            try:
                stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
                stripe_customer.stripe_subscription_id = subscription_id
                stripe_customer.save()
                user = stripe_customer.user
                user.is_premium = True
                user.save()
            except StripeCustomer.DoesNotExist:
                logger.error('StripeCustomer not found for customer_id: %s', customer_id)

        return Response(status=200)


class SubscriptionSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Subscription successful!'})


class SubscriptionCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Subscription was cancelled.'})


class SubscriptionCancelledView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({'message': 'Your subscription has been cancelled.'})
