from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order
from orders_app.tests.mixins import OrderTestMixin
from profiles_app.models import Profile


class TestOrderCreateAPI(APITestCase, OrderTestMixin):
    """Tests the order create endpoint."""

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

        self.offer_detail = self.create_offer_with_detail(
            self.business_user,
        )

        self.url = reverse("order-list-create")

        self.valid_data = {
            "offer_detail_id": self.offer_detail.id,
        }


    def test_create_order_returns_201(self):
        """Ensures customers can create orders."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED


    def test_create_order_creates_snapshot_data(self):
        """
        Ensures orders keep independent snapshot data by modifying
        the original offer detail after order creation and verifying
        the stored order data remains unchanged.
        """

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        order_id = response.data["id"]

        self.offer_detail.title = "Changed Title"
        self.offer_detail.revisions = 99
        self.offer_detail.delivery_time_in_days = 99
        self.offer_detail.price = 9999
        self.offer_detail.features = ["Changed Feature"]
        self.offer_detail.offer_type = "premium"
        self.offer_detail.save()

        order = Order.objects.get(id=order_id)

        assert order.title == "Basic Logo Design"
        assert order.revisions == 3
        assert order.delivery_time_in_days == 5
        assert order.price == Decimal("150")
        assert order.features == ["Logo Design", "Business Card"]
        assert order.offer_type == "basic"


    def test_create_order_sets_customer_and_business_user(self):
        """Ensures order creation assigns related users correctly."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.data["customer_user"] == self.customer_user.id
        assert response.data["business_user"] == self.business_user.id


    def test_create_order_without_auth_returns_401(self):
        """Ensures unauthenticated order creation returns HTTP 401."""

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_create_order_as_business_user_returns_403(self):
        """Ensures business users cannot create orders."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_create_order_without_offer_detail_id_returns_400(self):
        """Ensures order creation requires offer detail id."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_order_with_unknown_offer_detail_returns_404(self):
        """Ensures unknown offer details return HTTP 404."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            self.url,
            {"offer_detail_id": 9999},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch("orders_app.models.Order.objects.create")
    def test_create_order_internal_error_returns_500(self, mock_create):
        """Ensures order creation returns HTTP 500 on errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_create.side_effect = Exception("Internal error")

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        assert response.status_code == (status.HTTP_500_INTERNAL_SERVER_ERROR)