import stripe
from datetime import datetime
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
        try:
            # Create a Stripe customer if not already exists
            if created or not stripe_customer.stripe_customer_id:
                customer = stripe.Customer.create(email=user.email)
                stripe_customer.stripe_customer_id = customer['id']
                stripe_customer.save()

            # Create a Stripe Checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=stripe_customer.stripe_customer_id,
                payment_method_types=['card'],
                # line_items=[{'price': 'price_1QZSQqKbqgiOLixUfdRFtnW6', 'quantity': 1}],
                line_items=[{'price': 'price_1QrNaXKbqgiOLixUwPpvrcLb', 'quantity': 1}],
                mode='subscription',
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL
            )
            return Response({'url': checkout_session.url})
        except Exception as e:
            stripe_customer.delete()
            return Response({'error': str(e)}, status=400)

class RenewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            stripe_customer = StripeCustomer.objects.get(user=user)
            
            if not stripe_customer.stripe_subscription_id:
                return Response({'error': 'User not subscribed'}, status=400)

            # Retrieve the current subscription details from Stripe
            subscription = stripe.Subscription.retrieve(
                stripe_customer.stripe_subscription_id
            )

            # Check if the subscription is set to cancel at period end
            if not subscription.cancel_at_period_end:
                return Response(
                    {'message': 'Subscription is already active'},
                    status=400
                )

            # Remove the cancellation flag to renew the subscription
            subscription = stripe.Subscription.modify(
                stripe_customer.stripe_subscription_id,
                cancel_at_period_end=False
            )

            # Optionally update local records if you are storing cancellation info
            stripe_customer.subscription_end_date = None
            user.subscription_end_date = None
            user.save()
            stripe_customer.save()

            return Response({'message': 'Subscription renewed successfully'})
        except StripeCustomer.DoesNotExist:
            return Response({'error': 'User not subscribed'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

            
class CreateYearlyCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        user = request.user
        stripe_customer, created = StripeCustomer.objects.get_or_create(user=user)
        try:
            # Create a Stripe customer if not already exists
            if created or not stripe_customer.stripe_customer_id:
                customer = stripe.Customer.create(email=user.email)
                stripe_customer.stripe_customer_id = customer['id']
                stripe_customer.save()

            # Create a Stripe Checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=stripe_customer.stripe_customer_id,
                payment_method_types=['card'],
                # line_items=[{'price': 'price_1QidIRKbqgiOLixU11MRxyRV', 'quantity': 1}],
                line_items=[{'price': 'price_1QrNaRKbqgiOLixUSi9N6hX3', 'quantity': 1}],
                mode='subscription',
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL
            )
            return Response({'url': checkout_session.url})
        except Exception as e:
            stripe_customer.delete()
            return Response({'error': str(e)}, status=400)
        

class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            stripe_customer = StripeCustomer.objects.get(user=user)
            
            if not stripe_customer.stripe_subscription_id:
                return Response({'error': 'User not subscribed'}, status=400)

            # Set subscription to cancel at the end of the current period
            subscription = stripe.Subscription.modify(
                stripe_customer.stripe_subscription_id,
                cancel_at_period_end=True
            )

            # Optionally, you could store the cancellation time if you need to notify the user
            stripe_customer.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
            user.subscription_end_date = stripe_customer.subscription_end_date
            user.save()
            stripe_customer.save()

            # Do not immediately change the premium status. The user remains premium until the period ends.
            return Response({'message': 'Subscription will be cancelled at the end of the billing period'})
        except StripeCustomer.DoesNotExist:
            return Response({'error': 'User not subscribed'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = []  # No authentication required for Stripe webhooks

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        event = None

        try:
            # Verify the event's signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.error("Invalid payload received in webhook.")
            return Response({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in webhook.")
            return Response({"error": "Invalid signature"}, status=400)

        # Process the event based on its type
        try:
            if event['type'] == 'checkout.session.completed':
                self.handle_checkout_session_completed(event)
            elif event['type'] == 'invoice.payment_failed':
                self.handle_payment_failed(event)
            elif event['type'] == 'customer.subscription.deleted':
                self.handle_subscription_deleted(event)
            else:
                logger.warning(f"Unhandled event type: {event['type']}")
        except Exception as e:
            # Log unexpected errors during processing
            logger.error(f"Error handling event {event['type']}: {str(e)}")
            return Response({"error": "Internal server error"}, status=500)

        return Response(status=200)

    def handle_checkout_session_completed(self, event):
        """
        Handle checkout.session.completed events.
        """
        session = event['data']['object']
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')

        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription['items']['data'][0]['price']['id']  # Retrieve the price ID
        
        subscription_type = "monthly"
        if price_id == 'price_1QrNaXKbqgiOLixUwPpvrcLb':  # Monthly price ID
            subscription_type = 'monthly'
        elif price_id == 'price_1QrNaRKbqgiOLixUSi9N6hX3':  # Yearly price ID
            subscription_type = 'yearly'
        else:
            logger.error(f"Unknown price ID: {price_id}")
        
        
        if not customer_id or not subscription_id:
            logger.error("Missing customer_id or subscription_id in event data.")
            return

        try:
            stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
            stripe_customer.stripe_subscription_id = subscription_id
            stripe_customer.save()

            # Update user's premium status
            user = stripe_customer.user
            user.subscription_type = subscription_type
            user.is_premium = True
            user.save()
        except StripeCustomer.DoesNotExist:
            logger.error(f"StripeCustomer not found for customer_id: {customer_id}")

    def handle_payment_failed(self, event):
        """
        Handle invoice.payment_failed events.
        """
        invoice = event['data']['object']
        customer_id = invoice.get('customer')

        if not customer_id:
            logger.error("Missing customer_id in payment failed event.")
            return

        try:
            stripe_customer = StripeCustomer.objects.get(stripe_customer_id=customer_id)
            user = stripe_customer.user

            # Notify the user about the failed payment (e.g., via email)
            logger.info(f"Payment failed for user {user.email}.")
        except StripeCustomer.DoesNotExist:
            logger.error(f"StripeCustomer not found for customer_id: {customer_id}")

    def handle_subscription_deleted(self, event):
        """
        Handle customer.subscription.deleted events.
        """
        subscription = event['data']['object']
        subscription_id = subscription.get('id')

        if not subscription_id:
            logger.error("Missing subscription_id in subscription deleted event.")
            return

        try:
            stripe_customer = StripeCustomer.objects.get(stripe_subscription_id=subscription_id)
            stripe_customer.stripe_subscription_id = None
            stripe_customer.save()

            # Update user's premium status
            user = stripe_customer.user
            user.is_premium = False
            user.subscription_end_date = None
            user.save()
        except StripeCustomer.DoesNotExist:
            logger.error(f"StripeCustomer not found for subscription_id: {subscription_id}")

