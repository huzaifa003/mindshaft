import logging
from django.utils.timezone import now

logger = logging.getLogger(__name__)

class ResetDailyLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
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
