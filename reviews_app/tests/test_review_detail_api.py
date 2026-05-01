from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from reviews_app.models import Review
from reviews_app.tests.mixins import ReviewTestMixin


class TestReviewDetailAPI(APITestCase, ReviewTestMixin):
    """Tests the review update and delete endpoint."""

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

        self.review = self.create_review(
            self.business_user,
            self.customer_user,
            rating=4,
        )

        self.url = reverse(
            "review-detail",
            kwargs={"pk": self.review.id},
        )


    def test_patch_review_returns_200(self):
        """Ensures review creators can update their reviews."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.patch(
            self.url,
            {
                "rating": 5,
                "description": "Updated review.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK


    def test_patch_review_updates_allowed_fields(self):
        """Ensures review rating and description are updated."""

        self.client.force_authenticate(user=self.customer_user)

        self.client.patch(
            self.url,
            {
                "rating": 5,
                "description": "Updated review.",
            },
            format="json",
        )

        self.review.refresh_from_db()

        assert self.review.rating == 5
        assert self.review.description == "Updated review."


    def test_patch_review_without_auth_returns_401(self):
        """Ensures unauthenticated review updates return HTTP 401."""

        response = self.client.patch(
            self.url,
            {"rating": 5},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_patch_review_as_non_creator_returns_403(self):
        """Ensures non-creators cannot update reviews."""

        self.client.force_authenticate(user=self.other_customer_user)

        response = self.client.patch(
            self.url,
            {"rating": 5},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_patch_review_with_invalid_rating_returns_400(self):
        """Ensures invalid review ratings return HTTP 400."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.patch(
            self.url,
            {"rating": 6},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_patch_review_with_forbidden_fields_returns_400(self):
        """Ensures forbidden review fields cannot be updated."""

        self.client.force_authenticate(user=self.customer_user)

        forbidden_data = {
            "business_user": self.customer_user.id,
            "reviewer": self.business_user.id,
            "created_at": "2025-01-01T00:00:00Z",
        }

        response = self.client.patch(
            self.url,
            forbidden_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_patch_unknown_review_returns_404(self):
        """Ensures updating unknown reviews returns HTTP 404."""

        self.client.force_authenticate(user=self.customer_user)

        url = reverse("review-detail", kwargs={"pk": 9999})

        response = self.client.patch(
            url,
            {"rating": 5},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch("reviews_app.models.Review.objects.get")
    def test_patch_review_internal_error_returns_500(self, mock_get):
        """Ensures review updates return HTTP 500 on errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_get.side_effect = Exception("Internal error")

        response = self.client.patch(
            self.url,
            {"rating": 5},
            format="json",
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


    def test_delete_review_returns_204(self):
        """Ensures review creators can delete their reviews."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


    def test_delete_review_removes_review(self):
        """Ensures deleted reviews are removed from the database."""

        self.client.force_authenticate(user=self.customer_user)

        self.client.delete(self.url)

        assert not Review.objects.filter(id=self.review.id).exists()


    def test_delete_review_without_auth_returns_401(self):
        """Ensures unauthenticated review deletion returns HTTP 401."""

        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_delete_review_as_non_creator_returns_403(self):
        """Ensures non-creators cannot delete reviews."""

        self.client.force_authenticate(user=self.other_customer_user)

        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_delete_unknown_review_returns_404(self):
        """Ensures deleting unknown reviews returns HTTP 404."""

        self.client.force_authenticate(user=self.customer_user)

        url = reverse("review-detail", kwargs={"pk": 9999})

        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch("reviews_app.models.Review.delete")
    def test_delete_review_internal_error_returns_500(self, mock_delete):
        """Ensures review deletion returns HTTP 500 on errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_delete.side_effect = Exception("Internal error")

        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR