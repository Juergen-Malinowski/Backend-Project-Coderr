from django.contrib.auth.models import User

from profiles_app.models import Profile


class ProfileTestMixin:
    """Provides reusable users and profile test data."""

    def create_user_with_profile(self, username, email, profile_type):

        user = User.objects.create_user(
            username=username,
            email=email,
            password="Testpass123",
        )

        Profile.objects.create(
            user=user,
            type=profile_type,
        )

        return user