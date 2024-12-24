from rest_framework import serializers
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating user profile.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined', 'credits_used_today', 'total_credits_used', 'daily_limit', 'is_premium', 'last_reset_date']
        read_only_fields = ['email', 'date_joined', 'id', 'credits_used_today', 'total_credits_used', 'daily_limit', 'is_premium', 'last_reset_date']


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Generic serializer for the custom user.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'credits_used_today', 'total_credits_used', 'daily_limit', 'is_premium']
