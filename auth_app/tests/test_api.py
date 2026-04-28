from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class TestRegistrationAPI(APITestCase):
    """Tests the registration endpoint."""

    def setUp(self):
        self.url = reverse('registration')
        self.valid_data = {
            "username": "customer_user",
            "email": "customer@example.com",
            "password": "Testpass123",
            "repeated_password": "Testpass123",
            "type": "customer",
        }


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

        self.valid_data["repeated_password"] = ("WrongPass123")

        response = self.client.post(self.url, self.valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLoginAPI(APITestCase):
    """Tests the login endpoint."""

    def setUp(self):
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="Testpass123"
        )


    def test_login_returns_200(self):
        """Ensures successful login returns HTTP 200."""

        data = {
            "username": "customer_user",
            "password": "Testpass123"
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
            "password": "Testpass123"
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
            "password": "WrongPass123"
        }

        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST