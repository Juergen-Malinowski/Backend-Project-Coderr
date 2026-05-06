from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews_app.models import Review

from .permissions import IsCustomerUser
from .serializers import (
    ReviewCreateSerializer, 
    ReviewSerializer, 
    ReviewUpdateSerializer,
)


class ReviewListCreateView(APIView):
    """API view for listing and creating reviews."""


    def get_permissions(self):
        """Returns permissions based on request method."""

        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]

        return [IsAuthenticated()]


    def get(self, request):
        """Returns filtered and ordered reviews."""

        try:
            queryset = Review.objects.all()
            queryset = self.filter_reviews(request, queryset)
            queryset = self.order_reviews(request, queryset)

            serializer = ReviewSerializer(queryset, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def filter_reviews(self, request, queryset):
            """Filters reviews by business user and reviewer query parameters."""

            business_user_id = request.query_params.get("business_user_id")
            reviewer_id = request.query_params.get("reviewer_id")

            if business_user_id:
                queryset = queryset.filter(business_user_id=business_user_id)

            if reviewer_id:
                queryset = queryset.filter(reviewer_id=reviewer_id)

            return queryset


    def order_reviews(self, request, queryset):
        """Orders reviews by allowed ordering query parameters."""

        ordering = request.query_params.get("ordering")
        allowed_orderings = [
            "updated_at",
            "-updated_at",
            "rating",
            "-rating",
        ]

        if ordering in allowed_orderings:
            return queryset.order_by(ordering)

        return queryset


    def post(self, request):
        """
        Creates a review for a business user, assigns the authenticated
        user as reviewer, validates rating and business user, allows only
        customer users to create reviews and ensures that each user can
        review a business user only once.
        """

        try:
            serializer = ReviewCreateSerializer(
                data=request.data,
                context={"request": request},
            )

            serializer.is_valid(raise_exception=True)
            review = serializer.save()

            response_serializer = ReviewSerializer(review)

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        except PermissionError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_403_FORBIDDEN,
            )

        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReviewDetailView(APIView):
    """API view for updating and deleting a review."""

    permission_classes = [IsAuthenticated]


    def get_object(self, pk):
        """Returns review or raises not found."""

        try:
            return Review.objects.get(id=pk)
        except Review.DoesNotExist:
            raise NotFound("Review not found.")


    def patch(self, request, pk):
        """Updates rating and description for the review creator only."""

        try:
            review = self.get_object(pk)

            if review.reviewer != request.user:
                return Response(
                    {"detail": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ReviewUpdateSerializer(
                review,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            review = serializer.save()

            response_serializer = ReviewSerializer(review)

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK,
            )

        except ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)

        except NotFound as error:
            return Response(
                {"detail": str(error.detail)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def delete(self, request, pk):
        """Deletes a review for the review creator only."""

        try:
            review = self.get_object(pk)

            if review.reviewer != request.user:
                return Response(
                    {"detail": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            review.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except NotFound as error:
            return Response(
                {"detail": str(error.detail)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )