from django.contrib.auth.models import User


class AuthTestMixin:
    """Provides reusable authentication test data and users."""

    def get_registration_data(self):
        return {
            "username": "customer_user",
            "email": "customer@example.com",
            "password": "Testpass123",
            "repeated_password": "Testpass123",
            "type": "customer",
        }


    def create_customer_user(self):
        return User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="Testpass123",
        )