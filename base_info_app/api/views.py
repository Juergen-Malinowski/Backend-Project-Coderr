from django.db.models import Avg

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from profiles_app.models import Profile
from reviews_app.models import Review

from .serializers import BaseInfoSerializer


class BaseInfoView(APIView):
    """API view for aggregated platform statistics."""

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Returns aggregated platform statistics
        without authentication.
        """

        try:
            data = {
                "review_count": Review.objects.count(),
                "average_rating": self.get_average_rating(),
                "business_profile_count": Profile.objects.filter(
                    type=Profile.BUSINESS,
                ).count(),
                "offer_count": Offer.objects.count(),
            }

            serializer = BaseInfoSerializer(data)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def get_average_rating(self):
        """Returns average rating rounded to one decimal place."""

        average = Review.objects.aggregate(
            average_rating=Avg("rating"),
        )["average_rating"]

        if average is None:
            return 0.0

        return round(average, 1)