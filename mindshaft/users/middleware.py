import logging
from django.utils.timezone import now
from datetime import timedelta
from users.models import CustomUser
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)

class ResetDailyLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()  # Initialize the JWT authenticator

    def __call__(self, request):
        # Attempt JWT authentication to set request.user
        try:
            auth_result = self.jwt_authenticator.authenticate(request)
            if auth_result is not None:
                user, token = auth_result
                request.user = user  # Manually set the user
        except Exception as e:
            logger.error("Error during JWT authentication: %s", str(e))
            # Optionally, you can set request.user to AnonymousUser() here

        # Continue with middleware logic
        user: CustomUser = request.user
        if user and hasattr(user, 'email'):
            logger.info(f"Middleware invoked for {user.email}")
        else:
            logger.info("Middleware invoked for anonymous user")
        
        # print(user)  # Debug print

        if user.is_authenticated:
            # Only apply the logic for non-premium users
            if not user.is_premium:
                user.reset_daily_limit()
                # Check if the user has exceeded their daily limit
                if user.credits_used_today >= user.daily_limit:
                    # Set cooldown if not already set or expired
                    if not user.reset_cooldown or user.reset_cooldown < now():
                        user.reset_cooldown = now() + timedelta(hours=24)
                        logger.info(f"Cooldown set for user {user.email}: {user.reset_cooldown}")
                        user.save()

                logger.info(f"Middleware invoked for user {user.email}")
                print(user.credits_used_today)  # Debug print

                # Reset daily credits if last reset date is not today and no cooldown is set
                if not user.reset_cooldown and user.last_reset_date != now().date():
                    logger.info(f"Resetting daily limit for user {user.email}")
                    user.credits_used_today = 0
                    user.last_reset_date = now().date()
                    user.save()  # Save the changes
        else:
            logger.info("Middleware invoked for anonymous user")
        
        return self.get_response(request)


class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("DebugMiddleware executed!")  # This should print for every request
        return self.get_response(request)
