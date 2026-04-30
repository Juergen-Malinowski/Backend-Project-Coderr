from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.tests.mixins import OfferTestMixin
from profiles_app.models import Profile


class TestOfferCreateAPI(APITestCase, OfferTestMixin):
    """Tests the offer create endpoint."""

    def setUp(self):

        self.business_user = self.create_user_with_profile(
            "business_user",
            "business@example.com",
            Profile.BUSINESS,
        )

        self.customer_user = self.create_user_with_profile(
            "customer_user",
            "customer@example.com",
            Profile.CUSTOMER,
        )

        self.url = reverse("offer-list-create")
        self.valid_data = self.get_valid_offer_data()


    def test_create_offer_returns_201(self):
        """Ensures business users can create offers."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED


    def test_create_offer_creates_three_details(self):
        """Ensures offer creation creates exactly three details."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert len(response.data["details"]) == 3


    def test_create_offer_without_auth_returns_401(self):
        """Ensures unauthenticated offer creation returns HTTP 401."""

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_create_offer_as_customer_returns_403(self):
        """Ensures customer users cannot create offers."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_create_offer_with_missing_title_returns_400(self):
        """Ensures offer creation fails when title is missing."""

        self.client.force_authenticate(user=self.business_user)

        self.valid_data.pop("title")

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_offer_with_less_than_three_details_returns_400(self):
        """Ensures offer creation requires exactly three details."""

        self.client.force_authenticate(user=self.business_user)

        self.valid_data["details"] = self.valid_data["details"][:2]

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_offer_with_more_than_three_details_returns_400(self):
        """Ensures offer creation rejects more than three details."""

        self.client.force_authenticate(user=self.business_user)

        self.valid_data["details"].append(
            {
                "title": "Extra Design",
                "revisions": 1,
                "delivery_time_in_days": 3,
                "price": 50,
                "features": ["Extra"],
                "offer_type": "extra",
            }
        )

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_offer_with_duplicate_detail_type_returns_400(self):
        """Ensures duplicate offer detail types are rejected."""

        self.client.force_authenticate(user=self.business_user)

        self.valid_data["details"][1]["offer_type"] = "basic"

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    @patch("offers_app.models.Offer.objects.create")
    def test_create_offer_internal_error_returns_500(self, mock_create):
        """Ensures offer creation returns HTTP 500 on internal errors."""

        self.client.force_authenticate(user=self.business_user)
        mock_create.side_effect = Exception("Internal error")

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR