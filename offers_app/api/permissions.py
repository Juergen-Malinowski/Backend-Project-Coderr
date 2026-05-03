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


class IsOfferOwner(BasePermission):
    """Allows access only to the owner of an offer."""

    def has_object_permission(self, request, view, obj):
        """Checks whether the authenticated user owns the offer."""

        return obj.user == request.user