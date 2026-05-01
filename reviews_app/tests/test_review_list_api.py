from time import sleep
from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from reviews_app.tests.mixins import ReviewTestMixin


class TestReviewListAPI(APITestCase, ReviewTestMixin):
    """Tests the review list endpoint."""

    def setUp(self):

        self.customer_user = self.create_user_with_profile(
            "customer_user",
            "customer@example.com",
            Profile.CUSTOMER,
        )

        self.other_customer_user = self.create_user_with_profile(
            "other_customer",
            "other_customer@example.com",
            Profile.CUSTOMER,
        )

        self.business_user = self.create_user_with_profile(
            "business_user",
            "business@example.com",
            Profile.BUSINESS,
        )

        self.other_business_user = self.create_user_with_profile(
            "other_business",
            "other_business@example.com",
            Profile.BUSINESS,
        )

        self.review = self.create_review(
            self.business_user,
            self.customer_user,
            rating=4,
        )

        self.other_review = self.create_review(
            self.other_business_user,
            self.other_customer_user,
            rating=5,
        )

        self.url = reverse("review-list-create")

        self.review.description = "Older review."
        self.review.save()

        sleep(0.01)

        self.other_review.description = "Latest review."
        self.other_review.save()


    def test_get_reviews_returns_200(self):
        """Ensures authenticated users can list reviews."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_reviews_without_auth_returns_401(self):
        """Ensures unauthenticated review list access returns HTTP 401."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_reviews_returns_required_fields(self):
        """Ensures review list response contains required fields."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        review_data = response.data[0]

        assert "id" in review_data
        assert "business_user" in review_data
        assert "reviewer" in review_data
        assert "rating" in review_data
        assert "description" in review_data
        assert "created_at" in review_data
        assert "updated_at" in review_data


    def test_get_reviews_filters_by_business_user_id(self):
        """Ensures reviews can be filtered by business user id."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(
            self.url,
            {"business_user_id": self.business_user.id},
        )

        assert len(response.data) == 1
        assert response.data[0]["business_user"] == self.business_user.id


    def test_get_reviews_filters_by_reviewer_id(self):
        """Ensures reviews can be filtered by reviewer id."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(
            self.url,
            {"reviewer_id": self.customer_user.id},
        )

        assert len(response.data) == 1
        assert response.data[0]["reviewer"] == self.customer_user.id


    def test_get_reviews_orders_by_rating(self):
        """Ensures reviews can be ordered by rating in descending order."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(
            self.url,
            {"ordering": "-rating"},
        )

        assert response.data[0]["rating"] == 5
        assert response.data[1]["rating"] == 4


    def test_get_reviews_orders_by_updated_at(self):
        """Ensures reviews can be ordered by latest updated date first."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(
            self.url,
            {"ordering": "-updated_at"},
        )

        assert response.data[0]["id"] == self.other_review.id
        assert response.data[1]["id"] == self.review.id


    @patch("reviews_app.models.Review.objects.all")
    def test_get_reviews_internal_error_returns_500(self, mock_all):
        """Ensures review list returns HTTP 500 on errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_all.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR