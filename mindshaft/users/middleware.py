from django.utils.timezone import now

class ResetDailyLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user.reset_daily_limit()
        return self.get_response(request)
