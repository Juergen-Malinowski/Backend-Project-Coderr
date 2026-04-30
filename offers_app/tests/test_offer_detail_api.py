from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.tests.mixins import OfferTestMixin
from profiles_app.models import Profile


class TestOfferDetailAPI(APITestCase, OfferTestMixin):
    """Tests the offer detail, update and delete endpoint."""

    def setUp(self):

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

        self.customer_user = self.create_user_with_profile(
            "customer_user",
            "customer@example.com",
            Profile.CUSTOMER,
        )

        self.offer = self.create_offer(self.business_user)

        self.url = reverse(
            "offer-detail",
            kwargs={"pk": self.offer.id},
        )


    def test_get_offer_detail_returns_200(self):
        """Ensures authenticated users can retrieve an offer."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_offer_detail_returns_required_fields(self):
        """Ensures offer detail response contains required fields."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        assert response.data["id"] == self.offer.id
        assert response.data["user"] == self.business_user.id
        assert "details" in response.data
        assert "min_price" in response.data
        assert "min_delivery_time" in response.data


    def test_get_offer_detail_without_auth_returns_401(self):
        """Ensures unauthenticated offer detail access returns HTTP 401."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_unknown_offer_returns_404(self):
        """Ensures unknown offers return HTTP 404."""

        self.client.force_authenticate(user=self.customer_user)

        url = reverse(
            "offer-detail",
            kwargs={"pk": 9999},
        )

        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch("offers_app.models.Offer.objects.get")
    def test_get_offer_internal_error_returns_500(self, mock_get):
        """Ensures offer retrieval returns HTTP 500 on internal errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_get.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


    def test_patch_offer_returns_200(self):
        """Ensures offer owners can update their offers."""

        self.client.force_authenticate(user=self.business_user)

        data = {"title": "Updated Design Package"}

        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK


    def test_patch_offer_updates_only_given_fields(self):
        """Ensures partial offer updates preserve unchanged fields."""

        self.client.force_authenticate(user=self.business_user)

        data = {"title": "Updated Design Package"}

        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        assert response.data["title"] == "Updated Design Package"
        assert response.data["description"] == self.offer.description


    def test_patch_offer_detail_by_offer_type_returns_200(self):
        """
        Ensures the correct offer detail is updated by
        offer type while other details remain unchanged.
        """

        self.client.force_authenticate(user=self.business_user)

        data = {
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": ["Logo Design", "Flyer"],
                    "offer_type": "basic",
                }
            ]
        }

        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        self.offer.refresh_from_db()

        basic_detail = self.offer.details.get(offer_type="basic")
        standard_detail = self.offer.details.get(offer_type="standard")
        premium_detail = self.offer.details.get(offer_type="premium")

        assert response.status_code == status.HTTP_200_OK
        assert basic_detail.title == "Basic Design Updated"
        assert basic_detail.revisions == 3
        assert basic_detail.delivery_time_in_days == 6
        assert basic_detail.price == Decimal("120")
        assert basic_detail.features == ["Logo Design", "Flyer"]

        assert standard_detail.title == "Standard Design"
        assert premium_detail.title == "Premium Design"


    def test_patch_offer_without_auth_returns_401(self):
        """Ensures unauthenticated offer updates return HTTP 401."""

        data = {
            "title": "Updated Design Package",
        }

        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_patch_offer_as_non_owner_returns_403(self):
        """Ensures non-owners cannot update offers."""

        self.client.force_authenticate(user=self.other_business_user)

        data = {
            "title": "Updated Design Package",
        }

        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_patch_unknown_offer_returns_404(self):
        """Ensures updating unknown offers returns HTTP 404."""

        self.client.force_authenticate(user=self.business_user)

        url = reverse(
            "offer-detail",
            kwargs={"pk": 9999},
        )

        data = {
            "title": "Updated Design Package",
        }

        response = self.client.patch(
            url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_patch_offer_with_invalid_detail_type_returns_400(self):
        """Ensures invalid offer detail update data returns HTTP 400."""

        self.client.force_authenticate(user=self.business_user)

        data = {
            "details": [
                {
                    "title": "Invalid Detail",
                    "revisions": 1,
                    "delivery_time_in_days": 2,
                    "price": 50,
                    "features": ["Invalid"],
                    "offer_type": "invalid",
                }
            ]
        }

        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    @patch("offers_app.models.Offer.objects.get")
    def test_patch_offer_internal_error_returns_500(self, mock_get):
        """Ensures offer updates return HTTP 500 on internal errors."""

        self.client.force_authenticate(user=self.business_user)
        mock_get.side_effect = Exception("Internal error")
        data = {
            "title": "Updated Design Package",
        }

        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


    def test_delete_offer_returns_204(self):
        """Ensures offer owners can delete their offers."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


    def test_delete_offer_without_auth_returns_401(self):
        """Ensures unauthenticated offer deletion returns HTTP 401."""

        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_delete_offer_as_non_owner_returns_403(self):
        """Ensures non-owners cannot delete offers."""

        self.client.force_authenticate(user=self.other_business_user)

        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_delete_unknown_offer_returns_404(self):
        """Ensures deleting unknown offers returns HTTP 404."""

        self.client.force_authenticate(user=self.business_user)

        url = reverse("offer-detail", kwargs={"pk": 9999})

        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch("offers_app.models.Offer.delete")
    def test_delete_offer_internal_error_returns_500(self, mock_delete):
        """Ensures offer deletion returns HTTP 500 on internal errors."""

        self.client.force_authenticate(user=self.business_user)
        mock_delete.side_effect = Exception("Internal error")

        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR