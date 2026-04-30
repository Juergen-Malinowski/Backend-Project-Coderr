from unittest.mock import patch

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from profiles_app.tests.mixins import ProfileTestMixin


class TestProfileDetailAPI(APITestCase, ProfileTestMixin):
    """Tests the user profile detail endpoint."""

    def setUp(self):

        self.user = self.create_user_with_profile(
            "customer_user",
            "customer@example.com",
            Profile.CUSTOMER,
        )

        self.other_user = self.create_user_with_profile(
            "other_user",
            "other@example.com",
            Profile.BUSINESS,
        )

        self.url = reverse(
            "profile-detail",
            kwargs={"pk": self.user.id},
        )


    def test_get_profile_returns_200(self):
        """Ensures authenticated users can retrieve user profile data."""

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK


    def test_get_profile_without_auth_returns_401(self):
        """Ensures unauthenticated user profile access returns HTTP 401."""

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_unknown_profile_returns_404(self):
        """Ensures unknown user profiles return HTTP 404."""

        self.client.force_authenticate(user=self.user)
        url = reverse("profile-detail", kwargs={"pk": 9999})

        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_get_profile_string_fields_are_not_null(self):
        """Ensures empty user profile string fields are returned as strings."""

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        assert response.data["first_name"] == ""
        assert response.data["last_name"] == ""
        assert response.data["location"] == ""
        assert response.data["tel"] == ""
        assert response.data["description"] == ""
        assert response.data["working_hours"] == ""


    @patch("profiles_app.models.Profile.objects.get")
    def test_get_profile_internal_error_returns_500(self, mock_get):
        """Ensures user profile retrieval returns HTTP 500 on internal errors."""

        self.client.force_authenticate(user=self.user)
        mock_get.side_effect = Exception("Internal error")

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


    def test_patch_own_profile_returns_200(self):
        """Ensures users can update their own user profile data."""

        self.client.force_authenticate(user=self.user)

        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "123456789",
            "description": "Updated description",
            "working_hours": "9-17",
            "email": "new@example.com",
        }

        response = self.client.patch(self.url, data)
        assert response.status_code == status.HTTP_200_OK


    def test_patch_own_profile_updates_data(self):
        """Ensures user profile updates return the changed user data."""

        self.client.force_authenticate(user=self.user)

        data = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "location": "Berlin",
            "tel": "123456789",
            "description": "Updated description",
            "working_hours": "9-17",
            "email": "new@example.com",
        }

        response = self.client.patch(self.url, data)

        assert response.data["first_name"] == "Max"
        assert response.data["last_name"] == "Mustermann"
        assert response.data["location"] == "Berlin"
        assert response.data["tel"] == "123456789"
        assert response.data["description"] == "Updated description"
        assert response.data["working_hours"] == "9-17"
        assert response.data["email"] == "new@example.com"


    def test_patch_profile_without_auth_returns_401(self):
        """Ensures unauthenticated user profile updates return HTTP 401."""

        data = {"location": "Berlin"}

        response = self.client.patch(self.url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_patch_other_profile_returns_403(self):
        """Ensures users cannot update another user's profile data."""

        self.client.force_authenticate(user=self.other_user)
        data = {"location": "Berlin"}

        response = self.client.patch(self.url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_patch_unknown_profile_returns_404(self):
        """Ensures updating an unknown user profile returns HTTP 404."""

        self.client.force_authenticate(user=self.user)

        url = reverse("profile-detail", kwargs={"pk": 9999})
        data = {"location": "Berlin"}

        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


    def test_patch_profile_string_fields_are_not_null(self):
        """Ensures updated user profile string fields are never returned as null."""

        self.client.force_authenticate(user=self.user)

        data = {
            "location": "",
            "tel": "",
            "description": "",
            "working_hours": "",
        }

        response = self.client.patch(self.url, data)

        assert response.data["first_name"] == ""
        assert response.data["last_name"] == ""
        assert response.data["location"] == ""
        assert response.data["tel"] == ""
        assert response.data["description"] == ""
        assert response.data["working_hours"] == ""


    @patch("profiles_app.models.Profile.objects.get")
    def test_patch_profile_internal_error_returns_500(self, mock_get):
        """Ensures user profile updates return HTTP 500 on internal errors."""

        self.client.force_authenticate(user=self.user)
        mock_get.side_effect = Exception("Internal error")

        data = {"location": "Berlin"}

        response = self.client.patch(self.url, data)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR