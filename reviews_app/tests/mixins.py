from django.contrib.auth.models import User

from profiles_app.models import Profile
from reviews_app.models import Review


class ReviewTestMixin:
    """Provides reusable users, profiles and reviews."""

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


    def create_review(self, business_user, reviewer, rating=4):

        return Review.objects.create(
            business_user=business_user,
            reviewer=reviewer,
            rating=rating,
            description="Great service.",
        )