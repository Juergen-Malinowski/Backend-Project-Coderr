from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsProfileOwnerForPatch(BasePermission):
    """Allows profile updates only for the profile owner."""

    def has_object_permission(self, request, view, obj):
        """Checks profile ownership for unsafe requests."""

        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user