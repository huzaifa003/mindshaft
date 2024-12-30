from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserProfileView, VerifyOTPView, ResendOTPView, ResetPasswordView, RequestPasswordResetView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),

    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("request-password-reset/", RequestPasswordResetView.as_view(), name="request_password_reset"),
    
    path('login/', UserLoginView.as_view(), name='user-login'),
    
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
