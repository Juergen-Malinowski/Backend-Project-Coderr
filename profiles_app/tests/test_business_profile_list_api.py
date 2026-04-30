from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from profiles_app.tests.mixins import ProfileTestMixin


class TestBusinessProfileListAPI(APITestCase, ProfileTestMixin):
    """Tests the business user profile list endpoint."""

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

        self.url = reverse("business-profile-list")


    def test_get_business_profiles_returns_200(self):
        """Ensures authenticated users can list business user profiles."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_business_profiles_returns_only_business_profiles(self):
        """Ensures the response only contains business user profiles."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        assert len(response.data) == 1
        assert response.data[0]["type"] == Profile.BUSINESS
        assert response.data[0]["username"] == "business_user"


    def test_get_business_profiles_without_auth_returns_401(self):
        """Ensures unauthenticated business user list access returns HTTP 401."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_business_profiles_string_fields_are_not_null(self):
        """Ensures business user profile string fields are returned as strings."""

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        profile_data = response.data[0]

        assert profile_data["first_name"] == ""
        assert profile_data["last_name"] == ""
        assert profile_data["location"] == ""
        assert profile_data["tel"] == ""
        assert profile_data["description"] == ""
        assert profile_data["working_hours"] == ""


    @patch("profiles_app.models.Profile.objects.filter")
    def test_get_business_profiles_internal_error_returns_500(self, mock_filter):
        """Ensures business user profile list returns HTTP 500 on errors."""

        self.client.force_authenticate(user=self.customer_user)
        mock_filter.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR