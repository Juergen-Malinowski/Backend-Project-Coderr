from rest_framework import serializers

from profiles_app.models import Profile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializes full review data."""

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Validates review creation data and assigns the authenticated reviewer."""

    class Meta:
        model = Review
        fields = [
            "business_user",
            "rating",
            "description",
        ]

    def validate_business_user(self, value):
        """Ensures that reviews can only be created for business users."""

        if not hasattr(value, "profile"):
            raise serializers.ValidationError(
                "User profile is missing."
            )

        if value.profile.type != Profile.BUSINESS:
            raise serializers.ValidationError(
                "User is not a business user."
            )

        return value

    def validate(self, attrs):
        """Ensures that a reviewer can only review a business user once."""

        request = self.context["request"]
        business_user = attrs["business_user"]

        if Review.objects.filter(
            business_user=business_user,
            reviewer=request.user,
        ).exists():
            raise PermissionError("Review already exists.")

        return attrs

    def create(self, validated_data):
        """Creates a review and assigns the authenticated user as reviewer."""

        request = self.context["request"]

        return Review.objects.create(
            reviewer=request.user,
            **validated_data,
        )