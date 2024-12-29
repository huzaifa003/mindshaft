from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def email_verified_required(view_func):
    @wraps(view_func)
    @login_required  # Ensures the user is authenticated before checking email verification
    def _wrapped_view(request, *args, **kwargs):
        print(request.user)
        if not request.user.email_verified:
            return JsonResponse({'error': 'Email not verified. Please verify your email to access this resource.'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
