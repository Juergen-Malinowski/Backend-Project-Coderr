from rest_framework.permissions import BasePermission

from profiles_app.models import Profile


class IsBusinessUser(BasePermission):
    """Allows access only for business users."""

    def has_permission(self, request, view):
        """Checks whether the authenticated user is a business user."""

        return (
            hasattr(request.user, "profile")
            and request.user.profile.type == Profile.BUSINESS
        )