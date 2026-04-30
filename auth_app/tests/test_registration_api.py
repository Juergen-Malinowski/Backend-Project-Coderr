from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tests.mixins import AuthTestMixin


class TestRegistrationAPI(APITestCase, AuthTestMixin):
    """Tests the registration endpoint."""

    def setUp(self):
        self.url = reverse("registration")
        self.valid_data = self.get_registration_data()


    def test_registration_returns_201(self):
        """Ensures successful registration returns HTTP 201."""

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_201_CREATED


    def test_registration_creates_user(self):
        """Ensures a new user is created after registration."""

        self.client.post(self.url, self.valid_data)
        assert User.objects.filter(username="customer_user").exists()


    def test_registration_returns_token_and_user_data(self):
        """
        Ensures the response includes a token and the expected
        user information.
        """

        response = self.client.post(self.url, self.valid_data)

        assert "token" in response.data
        assert response.data["username"] == "customer_user"
        assert response.data["email"] == "customer@example.com"
        assert "user_id" in response.data


    def test_registration_with_password_mismatch_returns_400(self):
        """Ensures registration fails when passwords do not match."""

        self.valid_data["repeated_password"] = "WrongPass123"

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_without_username_returns_400(self):
        """Ensures registration fails when username is missing."""

        self.valid_data.pop("username")

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_without_email_returns_400(self):
        """Ensures registration fails when email is missing."""

        self.valid_data.pop("email")

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_without_password_returns_400(self):
        """Ensures registration fails when password is missing."""

        self.valid_data.pop("password")

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_without_type_returns_400(self):
        """Ensures registration fails when type is missing."""

        self.valid_data.pop("type")

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_with_invalid_type_returns_400(self):
        """Ensures registration fails with an invalid profile type."""

        self.valid_data["type"] = "admin"

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_with_duplicate_username_returns_400(self):
        """Ensures registration fails with an existing username."""

        User.objects.create_user(
            username="customer_user",
            email="existing@example.com",
            password="Testpass123",
        )

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_registration_with_duplicate_email_returns_400(self):
        """Ensures registration fails with an existing email address."""

        User.objects.create_user(
            username="existing_user",
            email="customer@example.com",
            password="Testpass123",
        )

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    @patch("django.contrib.auth.models.User.objects.create_user")
    def test_registration_internal_error_returns_500(self, mock_create_user):
        """Ensures registration returns HTTP 500 on internal errors."""

        mock_create_user.side_effect = Exception("Internal error")

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR