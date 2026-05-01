from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from reviews_app.tests.mixins import ReviewTestMixin


class TestReviewCreateAPI(APITestCase, ReviewTestMixin):
    """Tests the review create endpoint."""

    def setUp(self):

        self.customer_user = self.create_user_with_profile(
            "customer_user",
            "customer@example.com",
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

        self.url = reverse("review-list-create")

        self.valid_data = {
            "business_user": self.business_user.id,
            "rating": 4,
            "description": "Everything was great.",
        }


    def test_create_review_returns_201(self):
        """Ensures customer users can create reviews."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED


    def test_create_review_sets_reviewer(self):
        """Ensures review creation assigns the authenticated user."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.data["reviewer"] == self.customer_user.id


    def test_create_review_returns_required_fields(self):
        """Ensures created review response contains required fields."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert "id" in response.data
        assert "business_user" in response.data
        assert "reviewer" in response.data
        assert "rating" in response.data
        assert "description" in response.data
        assert "created_at" in response.data
        assert "updated_at" in response.data


    def test_create_review_without_auth_returns_401(self):
        """Ensures unauthenticated review creation returns HTTP 401."""

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_create_review_as_business_user_returns_403(self):
        """Ensures business users cannot create reviews."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_create_duplicate_review_returns_403(self):
        """Ensures users cannot review the same business user twice."""

        self.create_review(
            self.business_user,
            self.customer_user,
            rating=4,
        )

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_create_review_without_business_user_returns_400(self):
        """Ensures review creation requires a business user."""

        self.client.force_authenticate(user=self.customer_user)

        self.valid_data.pop("business_user")

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_review_without_rating_returns_400(self):
        """Ensures review creation requires a rating."""

        self.client.force_authenticate(user=self.customer_user)

        self.valid_data.pop("rating")

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_review_with_rating_below_minimum_returns_400(self):
        """Ensures ratings below the allowed range return HTTP 400."""

        self.client.force_authenticate(user=self.customer_user)

        self.valid_data["rating"] = 0

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_review_with_rating_above_maximum_returns_400(self):
        """Ensures ratings above the allowed range return HTTP 400."""

        self.client.force_authenticate(user=self.customer_user)

        self.valid_data["rating"] = 6

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_review_for_unknown_business_user_returns_400(self):
        """Ensures unknown business users return HTTP 400."""

        self.client.force_authenticate(user=self.customer_user)

        self.valid_data["business_user"] = 9999

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    @patch("reviews_app.models.Review.objects.create")
    def test_create_review_internal_error_returns_500(self, mock_create):
        """Ensures review creation returns HTTP 500 on errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_create.side_effect = Exception("Internal error")

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR