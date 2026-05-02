from rest_framework import serializers

from profiles_app.models import Profile


class ProfileDetailSerializer(serializers.ModelSerializer):
    """Handles user and profile detail serialization and updates."""

    user = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True,
    )
    email = serializers.EmailField(
        source="user.email",
        required=False,
    )

    class Meta:
        model = Profile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "username",
            "type",
            "created_at",
        ]

    def update(self, instance, validated_data):
        """Updates user and profile fields."""

        user_data = validated_data.pop("user", {})

        self._update_user(instance.user, user_data)

        return super().update(instance, validated_data)

    def _update_user(self, user, user_data):
        """Updates related user fields."""

        for field, value in user_data.items():
            setattr(user, field, value)

        user.save()