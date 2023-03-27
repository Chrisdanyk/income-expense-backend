from rest_framework import serializers
from authentication.models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'is_staff')

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError('Username must be alphanumeric')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'A user with this email already exists')
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class VerifyEmailSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ('token')


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    username = serializers.EmailField(max_length=255, min_length=3,
                                      read_only=True)
    password = serializers.CharField(
        max_length=128, min_length=6, write_only=True)
    tokens = serializers.CharField(
        max_length=128, min_length=6, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'tokens')

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid Credentials')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, Contact Admin')
        if not user.email_verified:
            raise AuthenticationFailed('Email not verified')

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }
        return super().validate(attrs)
