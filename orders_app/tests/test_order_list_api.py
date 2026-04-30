from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.tests.mixins import OrderTestMixin
from profiles_app.models import Profile


class TestOrderListAPI(APITestCase, OrderTestMixin):
    """Tests the order list endpoint."""

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

        self.customer_order = self.create_order(
            self.customer_user,
            self.business_user,
        )

        self.business_order = self.create_order(
            self.other_customer_user,
            self.business_user,
        )

        self.unrelated_order = self.create_order(
            self.other_customer_user,
            self.other_business_user,
        )

        self.url = reverse("order-list-create")


    def test_get_orders_returns_200(self):
        """Ensures authenticated users can list related orders."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_orders_without_auth_returns_401(self):
        """Ensures unauthenticated order list access returns HTTP 401."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_orders_returns_customer_related_orders_only(self):
        """Ensures customers only receive their own customer orders."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        assert len(response.data) == 1
        assert response.data[0]["id"] == self.customer_order.id
        assert response.data[0]["customer_user"] == self.customer_user.id


    def test_get_orders_returns_business_related_orders_only(self):
        """Ensures business users only receive their own business orders."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.get(self.url)

        assert len(response.data) == 2
        assert response.data[0]["business_user"] == self.business_user.id
        assert response.data[1]["business_user"] == self.business_user.id


    def test_get_orders_returns_required_fields(self):
        """Ensures order list response contains required fields."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        order_data = response.data[0]

        assert "id" in order_data
        assert "customer_user" in order_data
        assert "business_user" in order_data
        assert "title" in order_data
        assert "revisions" in order_data
        assert "delivery_time_in_days" in order_data
        assert "price" in order_data
        assert "features" in order_data
        assert "offer_type" in order_data
        assert "status" in order_data
        assert "created_at" in order_data
        assert "updated_at" in order_data


    @patch("orders_app.models.Order.objects.filter")
    def test_get_orders_internal_error_returns_500(self, mock_filter):
        """Ensures order list returns HTTP 500 on internal errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_filter.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR