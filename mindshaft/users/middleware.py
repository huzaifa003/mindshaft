import logging
from django.utils.timezone import now
from datetime import timedelta  # Import timedelta
from users.models import CustomUser
logger = logging.getLogger(__name__)

class ResetDailyLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user : CustomUser = request.user 
        if user.is_authenticated:
             # If the user is not a premium user
            if not user.is_premium:
                user.reset_daily_limit()
                # Check if the user has exceeded their daily limit
                if user.credits_used_today >= user.daily_limit:
                    # If the reset cooldown has not already been set
                    if not user.reset_cooldown or user.reset_cooldown < now():
                        # Set reset cooldown to 24 hours from now
                        user.reset_cooldown = now() + timedelta(hours=24)
                        logger.info(f"Cooldown set for user {user.email}: {user.reset_cooldown}")
                        user.save()

            logger.info(f"Middleware invoked for user {request.user.email}")
            print(request.user.credits_used_today)
            if request.user.last_reset_date != now().date():
                logger.info(f"Resetting daily limit for user {request.user.email}")
                request.user.credits_used_today = 0
                request.user.last_reset_date = now().date()
                request.user.save()  # Save the changes

        else: 
            logger.info("Middleware invoked for anonymous user")
        return self.get_response(request)



class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("DebugMiddleware executed!")  # This should print for every request
        return self.get_response(request)
