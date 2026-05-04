from rest_framework.permissions import BasePermission

from profiles_app.models import Profile


class IsCustomerUser(BasePermission):
    """Allows access only for customer users."""

    def has_permission(self, request, view):
        """Checks whether the authenticated user is a customer user."""

        return (
            hasattr(request.user, "profile")
            and request.user.profile.type == Profile.CUSTOMER
        )