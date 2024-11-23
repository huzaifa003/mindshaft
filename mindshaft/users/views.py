from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
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
from .models import CustomUser


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
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'email': user.email}, status=status.HTTP_200_OK)
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
