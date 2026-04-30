from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order
from orders_app.tests.mixins import OrderTestMixin
from profiles_app.models import Profile


class TestOrderCountAPI(APITestCase, OrderTestMixin):
    """Tests the in-progress order count endpoint."""

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

        self.create_order(
            self.customer_user,
            self.business_user,
            status=Order.IN_PROGRESS,
        )

        self.create_order(
            self.customer_user,
            self.business_user,
            status=Order.IN_PROGRESS,
        )

        self.create_order(
            self.customer_user,
            self.business_user,
            status=Order.COMPLETED,
        )

        self.create_order(
            self.customer_user,
            self.other_business_user,
            status=Order.IN_PROGRESS,
        )

        self.url = reverse(
            "order-count",
            kwargs={"business_user_id": self.business_user.id},
        )


    def test_get_order_count_returns_200(self):
        """Ensures authenticated users can retrieve order counts."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_order_count_returns_in_progress_count(self):
        """
        Ensures only in-progress orders for the requested business
        user are counted.
        """

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        assert response.data["order_count"] == 2


    def test_get_order_count_without_auth_returns_401(self):
        """Ensures unauthenticated order count access returns HTTP 401."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_order_count_unknown_business_user_returns_404(self):
        """Ensures unknown business users return HTTP 404."""

        self.client.force_authenticate(user=self.customer_user)

        url = reverse("order-count", kwargs={"business_user_id": 9999})

        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch("orders_app.models.Order.objects.filter")
    def test_get_order_count_internal_error_returns_500(self, mock_filter):
        """Ensures order count returns HTTP 500 on errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_filter.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR