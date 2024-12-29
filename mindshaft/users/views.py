from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token

from django.conf import settings
from .serializers import (
    CustomUserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
)

from .utils import generate_otp, send_otp_email, send_email_verification_email, create_and_send_password_reset_otp, send_password_reset_confirmation_email
from users.models import CustomUser, OTP, PasswordResetOTP

from django_ratelimit.decorators import ratelimit 
from django.utils.decorators import method_decorator

from django.utils.timezone import now
from datetime import timedelta


class UserRegistrationView(CreateAPIView):
    """
    Handles user registration.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer


class UserLoginView(APIView):
    """
    Handles user login and provides an authentication token.
    """
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                
                return Response(
                    {
                        "user": serializer.data,
                        "refresh": refresh_token,
                        "access": access_token,
                    },
                    status=status.HTTP_200_OK,
                    
                )
                
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    Handles user logout and deletes the authentication token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except AttributeError:
            pass
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class UserProfileView(RetrieveUpdateAPIView):
    """
    Handles retrieving and updating the user's profile.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user






class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp_value = request.data.get("otp")

        if not email or not otp_value:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            if user.email_verified:
                return Response({"error": "Email already verified."}, status=status.HTTP_400_BAD_REQUEST)
            otp = OTP.objects.filter(user=user, otp=otp_value, purpose="email_verification").first()

            if not otp or not otp.is_valid():
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

            user.email_verified = True
            user.save()
            otp.delete()

            send_email_verification_email(user)
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "CustomUser does not exist."}, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    @method_decorator(ratelimit(key="ip", rate="5/m", block=True))
    def post(self, request):
        email = request.data.get("email")
        print(email)

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            otp_value = generate_otp()
            otp_expiry = now() + timedelta(minutes=10)

            OTP.objects.filter(user=user, purpose="email_verification").delete()  # Remove old OTPs
            OTP.objects.create(user=user, otp=otp_value, purpose="email_verification", expires_at=otp_expiry)

            send_otp_email(email, otp_value)
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "CustomUser does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            create_and_send_password_reset_otp(user)
            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "CustomUser with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
class ResetPasswordView(APIView):
    @method_decorator(ratelimit(key="ip", rate="5/m", block=True))
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP, and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            reset_otp = PasswordResetOTP.objects.filter(user=user, otp=otp).first()

            if not reset_otp:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

            if not reset_otp.is_valid():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Update the password
            user.set_password(new_password)
            user.save()

            # Delete the OTP after successful reset
            reset_otp.delete()
            send_password_reset_confirmation_email(user)
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "CustomUser with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        

