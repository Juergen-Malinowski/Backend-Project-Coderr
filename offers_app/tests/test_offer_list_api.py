from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import OfferDetail
from offers_app.tests.mixins import OfferTestMixin
from profiles_app.models import Profile


class TestOfferListAPI(APITestCase, OfferTestMixin):
    """Tests the offer list endpoint."""

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
        self.url = reverse("offer-list-create")


    def test_get_offers_returns_200(self):
        """Ensures all users can list offers without authentication."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_offers_returns_paginated_response(self):
        """Ensures the offer list uses pagination response structure."""

        response = self.client.get(self.url)

        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data


    def test_get_offers_returns_offer_summary_fields(self):
        """Ensures the offer list response contains required fields."""

        response = self.client.get(self.url)
        offer_data = response.data["results"][0]

        assert "id" in offer_data
        assert "user" in offer_data
        assert "title" in offer_data
        assert "details" in offer_data
        assert "min_price" in offer_data
        assert "min_delivery_time" in offer_data
        assert "user_details" in offer_data


    def test_get_offers_filters_by_creator_id(self):
        """Ensures offers can be filtered by creator id."""

        self.create_offer(
            self.other_business_user,
            title="Logo Design",
        )

        response = self.client.get(self.url, {"creator_id": self.business_user.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["user"] == self.business_user.id


    def test_get_offers_filters_by_min_price(self):
        """Ensures offers can be filtered by minimum price."""

        expensive_offer = self.create_offer(
            self.other_business_user,
            title="Expensive Design",
        )

        expensive_offer.details.all().update(price=1000)

        response = self.client.get(self.url, {"min_price": 500})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Expensive Design"


    def test_get_offers_filters_by_max_delivery_time(self):
        """Ensures offers can be filtered by maximum delivery time."""

        slow_offer = self.create_offer(
            self.other_business_user,
            title="Slow Design",
        )

        slow_offer.details.all().update(
            delivery_time_in_days=20,
        )

        response = self.client.get(self.url, {"max_delivery_time": 7})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Website Design"


    def test_get_offers_searches_title_and_description(self):
        """Ensures offers can be searched by title and description."""

        response = self.client.get(self.url, {"search": "Website"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Website Design"


    def test_get_offers_orders_by_min_price(self):
        """Ensures offers can be ordered by minimum price."""

        cheap_offer = self.offer

        expensive_offer = self.create_offer(
            self.other_business_user,
            title="Expensive Design",
        )

        cheap_offer.details.all().update(price=100)
        expensive_offer.details.all().update(price=1000)

        response = self.client.get(self.url, {"ordering": "min_price"})
        results = response.data["results"]

        assert response.status_code == status.HTTP_200_OK
        assert results[0]["title"] == "Website Design"
        assert results[1]["title"] == "Expensive Design"


    def test_get_offers_with_invalid_parameter_returns_400(self):
        """Ensures invalid offer query parameters return HTTP 400."""

        response = self.client.get(
            self.url,
            {"min_price": "invalid"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    @patch("offers_app.models.Offer.objects.all")
    def test_get_offers_internal_error_returns_500(self, mock_all):
        """Ensures offer list returns HTTP 500 on internal errors."""

        mock_all.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR