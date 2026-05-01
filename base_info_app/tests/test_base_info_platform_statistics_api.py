from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from profiles_app.models import Profile
from reviews_app.models import Review


class TestBaseInfoPlatformStatisticsAPI(APITestCase):
    """Tests the base info platform statistics endpoint."""

    def setUp(self):

        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="Testpass123",
        )

        self.second_customer_user = User.objects.create_user(
            username="second_customer",
            email="second_customer@example.com",
            password="Testpass123",
        )

        self.business_user = User.objects.create_user(
            username="business_user",
            email="business@example.com",
            password="Testpass123",
        )

        self.second_business_user = User.objects.create_user(
            username="second_business",
            email="second_business@example.com",
            password="Testpass123",
        )

        Profile.objects.create(
            user=self.customer_user,
            type=Profile.CUSTOMER,
        )

        Profile.objects.create(
            user=self.second_customer_user,
            type=Profile.CUSTOMER,
        )

        Profile.objects.create(
            user=self.business_user,
            type=Profile.BUSINESS,
        )

        Profile.objects.create(
            user=self.second_business_user,
            type=Profile.BUSINESS,
        )

        Offer.objects.create(
            user=self.business_user,
            title="Logo Design",
            description="Professional logo design.",
        )

        Offer.objects.create(
            user=self.second_business_user,
            title="Website Design",
            description="Professional website design.",
        )

        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Good service.",
        )

        Review.objects.create(
            business_user=self.second_business_user,
            reviewer=self.customer_user,
            rating=5,
            description="Excellent service.",
        )

        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.second_customer_user,
            rating=5,
            description="Okay service.",
        )

        self.url = reverse("base-info")


    def test_get_base_info_returns_200_without_auth(self):
        """Ensures base info can be retrieved without authentication."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_base_info_returns_required_fields(self):
        """Ensures base info response contains required statistic fields."""

        response = self.client.get(self.url)

        assert "review_count" in response.data
        assert "average_rating" in response.data
        assert "business_profile_count" in response.data
        assert "offer_count" in response.data


    def test_get_base_info_returns_review_count(self):
        """Ensures review count is calculated from all reviews."""

        response = self.client.get(self.url)

        assert response.data["review_count"] == 3


    def test_get_base_info_returns_rounded_average_rating(self):
        """Ensures average rating is calculated and rounded to one decimal place."""

        response = self.client.get(self.url)

        assert float(response.data["average_rating"]) == 4.0


    def test_get_base_info_returns_business_profile_count(self):
        """Ensures only business profiles are counted."""

        response = self.client.get(self.url)

        assert response.data["business_profile_count"] == 2


    def test_get_base_info_returns_offer_count(self):
        """Ensures offer count is calculated from all offers."""

        response = self.client.get(self.url)

        assert response.data["offer_count"] == 2


    def test_get_base_info_empty_database_returns_zero_values(self):
        """Ensures empty database statistics return zero values."""

        Review.objects.all().delete()
        Offer.objects.all().delete()
        Profile.objects.all().delete()

        response = self.client.get(self.url)

        assert response.data["review_count"] == 0
        assert float(response.data["average_rating"]) == 0.0
        assert response.data["business_profile_count"] == 0
        assert response.data["offer_count"] == 0


    @patch("reviews_app.models.Review.objects.count")
    def test_get_base_info_internal_error_returns_500(self, mock_count):
        """Ensures base info returns HTTP 500 on internal errors."""

        mock_count.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR