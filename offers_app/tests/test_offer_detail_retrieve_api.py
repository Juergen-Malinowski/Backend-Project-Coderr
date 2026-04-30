from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.tests.mixins import OfferTestMixin
from profiles_app.models import Profile


class TestOfferDetailRetrieveAPI(APITestCase, OfferTestMixin):
    """Tests the single offer detail retrieve endpoint."""

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

        self.offer = self.create_offer(self.business_user)

        self.offer_detail = self.offer.details.first()

        self.url = reverse(
            "offer-detail-retrieve",
            kwargs={"pk": self.offer_detail.id},
        )


    def test_get_offer_detail_object_returns_200(self):
        """Ensures authenticated users can retrieve an offer detail."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_offer_detail_object_returns_required_fields(self):
        """Ensures offer detail response contains package fields."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        assert response.data["id"] == self.offer_detail.id
        assert response.data["title"] == self.offer_detail.title
        assert "revisions" in response.data
        assert "delivery_time_in_days" in response.data
        assert "price" in response.data
        assert "features" in response.data
        assert "offer_type" in response.data


    def test_get_offer_detail_object_without_auth_returns_401(self):
        """Ensures unauthenticated offer detail access returns HTTP 401."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_unknown_offer_detail_object_returns_404(self):
        """Ensures unknown offer details return HTTP 404."""

        self.client.force_authenticate(user=self.customer_user)

        url = reverse("offer-detail-retrieve", kwargs={"pk": 9999})

        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch("offers_app.models.OfferDetail.objects.get")
    def test_get_offer_detail_object_internal_error_returns_500(self, mock_get):
        """Ensures offer detail retrieval returns HTTP 500 on errors."""

        self.client.force_authenticate(user=self.customer_user)

        mock_get.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR