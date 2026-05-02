from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles_app.models import Profile

from .permissions import IsProfileOwnerForPatch
from .serializers import ProfileDetailSerializer, ProfileListSerializer


class BusinessProfileListView(APIView):
    """API view for listing business profiles."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Returns all business profiles."""

        try:
            profiles = Profile.objects.filter(type=Profile.BUSINESS)
            serializer = ProfileListSerializer(profiles, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomerProfileListView(APIView):
    """API view for listing customer profiles."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Returns all customer profiles."""

        try:
            profiles = Profile.objects.filter(type=Profile.CUSTOMER)
            serializer = ProfileListSerializer(profiles, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileDetailView(APIView):
    """API view for profile details and updates."""

    permission_classes = [IsAuthenticated, IsProfileOwnerForPatch]

    def get(self, request, pk):
        """Returns user profile detail data."""

        profile, error_response = self._get_profile_or_error(pk)

        if error_response:
            return error_response

        serializer = ProfileDetailSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def patch(self, request, pk):
        """Updates user profile detail data."""

        profile, error_response = self._get_profile_or_error(pk)

        if error_response:
            return error_response

        self.check_object_permissions(request, profile)

        return self._update_profile(request, profile)


    def _get_profile_or_error(self, pk):
        """Returns a profile or an error response."""

        try:
            return Profile.objects.get(user_id=pk), None
        except Profile.DoesNotExist:
            return None, Response(
                {"detail": "Profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return None, Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def _update_profile(self, request, profile):
        """Validates and saves profile update data."""

        try:
            serializer = ProfileDetailSerializer(
                profile,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )