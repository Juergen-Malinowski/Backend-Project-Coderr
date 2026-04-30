from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tests.mixins import AuthTestMixin


class TestLoginAPI(APITestCase, AuthTestMixin):
    """Tests the login endpoint."""

    def setUp(self):
        self.url = reverse("login")
        self.user = self.create_customer_user()


    def test_login_returns_200(self):
        """Ensures successful login returns HTTP 200."""

        data = {
            "username": "customer_user",
            "password": "Testpass123",
        }

        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK


    def test_login_returns_token_and_user_data(self):
        """
        Ensures the response includes a token and the expected
        authenticated user data.
        """

        data = {
            "username": "customer_user",
            "password": "Testpass123",
        }

        response = self.client.post(self.url, data)

        assert "token" in response.data
        assert response.data["username"] == "customer_user"
        assert response.data["email"] == "customer@example.com"
        assert response.data["user_id"] == self.user.id


    def test_login_with_invalid_password_returns_400(self):
        """Ensures login fails with an invalid password."""

        data = {
            "username": "customer_user",
            "password": "WrongPass123",
        }

        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_login_without_username_returns_400(self):
        """Ensures login fails when username is missing."""

        data = {
            "password": "Testpass123",
        }

        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_login_without_password_returns_400(self):
        """Ensures login fails when password is missing."""

        data = {
            "username": "customer_user",
        }

        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_login_with_unknown_username_returns_400(self):
        """Ensures login fails with an unknown username."""

        data = {
            "username": "unknown_user",
            "password": "Testpass123",
        }

        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    @patch("auth_app.api.views.authenticate")
    def test_login_internal_error_returns_500(self, mock_authenticate):
        """Ensures login returns HTTP 500 on internal errors."""

        mock_authenticate.side_effect = Exception("Internal error")

        data = {
            "username": "customer_user",
            "password": "Testpass123",
        }

        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR