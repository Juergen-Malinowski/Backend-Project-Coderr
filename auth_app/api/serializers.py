from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import serializers

from profiles_app.models import Profile


class RegistrationSerializer(serializers.Serializer):
    """Handles user registration validation and creation."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=Profile.TYPE_CHOICES)

    def validate_username(self, value):
        """Ensures the username is unique."""

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value


    def validate_email(self, value):
        """Ensures the email address is unique."""

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email address is already registered."
            )

        return value


    def validate(self, attrs):
        """Ensures both password fields match."""

        password = attrs.get("password")
        repeated_password = attrs.get("repeated_password")

        if password != repeated_password:
            raise serializers.ValidationError(
                {
                    "password": "Passwords do not match."
                }
            )

        return attrs


    def create(self, validated_data):
        """Creates a new user account with profile."""

        validated_data.pop("repeated_password")

        profile_type = validated_data.pop("type")

        user = User.objects.create_user(**validated_data)

        self._create_profile(user, profile_type)

        return user


    def _create_profile(self, user, profile_type):
        """Creates the matching user profile."""

        Profile.objects.create(
            user=user,
            type=profile_type,
        )


class LoginSerializer(serializers.Serializer):
    """Handles user login validation and authentication."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticates the user credentials."""

        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            username=username,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        attrs["user"] = user

        return attrs