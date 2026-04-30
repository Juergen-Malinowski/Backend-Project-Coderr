from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order
from orders_app.tests.mixins import OrderTestMixin
from profiles_app.models import Profile


class TestOrderDetailAPI(APITestCase, OrderTestMixin):
    """Tests the order update and delete endpoint."""

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

        self.order = self.create_order(
            self.customer_user,
            self.business_user,
        )

        self.url = reverse(
            "order-detail",
            kwargs={"pk": self.order.id},
        )


    def test_patch_order_status_returns_200(self):
        """Ensures business users can update order status."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.patch(
            self.url,
            {"status": Order.COMPLETED},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK


    def test_patch_order_updates_status(self):
        """Ensures order status updates are stored correctly."""

        self.client.force_authenticate(user=self.business_user)

        self.client.patch(
            self.url,
            {"status": Order.COMPLETED},
            format="json",
        )

        self.order.refresh_from_db()

        assert self.order.status == Order.COMPLETED


    def test_patch_order_without_auth_returns_401(self):
        """Ensures unauthenticated order updates return HTTP 401."""

        response = self.client.patch(
            self.url,
            {"status": Order.COMPLETED},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_patch_order_as_customer_returns_403(self):
        """Ensures customer users cannot update order status."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.patch(
            self.url,
            {"status": Order.COMPLETED},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_patch_order_as_unrelated_business_returns_403(self):
        """Ensures unrelated business users cannot update orders."""

        self.client.force_authenticate(user=self.other_business_user)

        response = self.client.patch(
            self.url,
            {"status": Order.COMPLETED},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_patch_order_with_invalid_status_returns_400(self):
        """Ensures invalid order status values return HTTP 400."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.patch(
            self.url,
            {"status": "invalid"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_patch_unknown_order_returns_404(self):
        """Ensures updating unknown orders returns HTTP 404."""

        self.client.force_authenticate(user=self.business_user)

        url = reverse("order-detail", kwargs={"pk": 9999})

        response = self.client.patch(
            url,
            {"status": Order.COMPLETED},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


    @patch("orders_app.models.Order.objects.get")
    def test_patch_order_internal_error_returns_500(
        self,
        mock_get,
    ):
        """Ensures order updates return HTTP 500 on errors."""

        self.client.force_authenticate(user=self.business_user)

        mock_get.side_effect = Exception("Internal error")

        response = self.client.patch(
            self.url,
            {"status": Order.COMPLETED},
            format="json",
        )

        assert response.status_code == (status.HTTP_500_INTERNAL_SERVER_ERROR)


    def test_delete_order_returns_204(self):
        """Ensures staff users can delete orders."""

        self.business_user.is_staff = True
        self.business_user.save()

        self.client.force_authenticate(user=self.business_user)

        response = self.client.delete(self.url)

        assert response.status_code == (status.HTTP_204_NO_CONTENT)


    def test_delete_order_removes_order(self):
        """Ensures deleted orders are removed from the database."""

        self.business_user.is_staff = True
        self.business_user.save()

        self.client.force_authenticate(user=self.business_user)

        self.client.delete(self.url)

        assert not Order.objects.filter(id=self.order.id).exists()


    def test_delete_order_without_auth_returns_401(self):
        """Ensures unauthenticated order deletion returns HTTP 401."""

        response = self.client.delete(self.url)

        assert response.status_code == (status.HTTP_401_UNAUTHORIZED)


    def test_delete_order_as_non_staff_returns_403(self):
        """Ensures non-staff users cannot delete orders."""

        self.client.force_authenticate(user=self.business_user)

        response = self.client.delete(self.url)

        assert response.status_code == (status.HTTP_403_FORBIDDEN)


    def test_delete_unknown_order_returns_404(self):
        """Ensures deleting unknown orders returns HTTP 404."""

        self.business_user.is_staff = True
        self.business_user.save()

        self.client.force_authenticate(user=self.business_user)

        url = reverse("order-detail", kwargs={"pk": 9999})

        response = self.client.delete(url)

        assert response.status_code == (status.HTTP_404_NOT_FOUND)


    @patch("orders_app.models.Order.delete")
    def test_delete_order_internal_error_returns_500(self, mock_delete):
        """Ensures order deletion returns HTTP 500 on errors."""

        self.business_user.is_staff = True
        self.business_user.save()

        self.client.force_authenticate(user=self.business_user)

        mock_delete.side_effect = Exception("Internal error")

        response = self.client.delete(self.url)

        assert response.status_code == (status.HTTP_500_INTERNAL_SERVER_ERROR)