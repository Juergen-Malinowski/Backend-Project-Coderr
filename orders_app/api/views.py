from django.db.models import Q

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.models import Order
from profiles_app.models import Profile

from .permissions import IsCustomerUser
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


class OrderListCreateView(APIView):
    """
    API view for listing orders and creating orders by copying
    immutable snapshot data from offer details.
    """

    def get_permissions(self):
        """Returns permissions based on request method."""

        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerUser()]

        return [IsAuthenticated()]

    def get(self, request):
        """Returns orders related to the authenticated user."""

        try:
            queryset = Order.objects.filter(
                Q(customer_user=request.user)
                | Q(business_user=request.user)
            )

            serializer = OrderSerializer(queryset, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """Creates a new order by copying snapshot data from an offer detail."""

        try:
            serializer = OrderCreateSerializer(
                data=request.data,
                context={"request": request},
            )

            serializer.is_valid(raise_exception=True)
            order = serializer.save()

            response_serializer = OrderSerializer(order)

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )

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


class OrderDetailView(APIView):
    """API view for updating and deleting a specific order."""

    permission_classes = [IsAuthenticated]


    def get_object(self, pk):
        """Returns order or raises not found."""

        try:
            return Order.objects.get(id=pk)
        except Order.DoesNotExist:
            raise NotFound("Order not found.")


    def validate_patch_request(self, request, order):
        """Validates permission, fields and status for order updates."""

        valid_statuses = [
            Order.IN_PROGRESS,
            Order.COMPLETED,
            Order.CANCELLED,
        ]

        if not hasattr(request.user, "profile"):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.user.profile.type != Profile.BUSINESS:
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if order.business_user != request.user:
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if set(request.data.keys()) != {"status"}:
            return Response(
                {"detail": "Only status can be updated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.data["status"] not in valid_statuses:
            return Response(
                {"detail": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return None


    def patch(self, request, pk):
        """Updates order status for the related business user."""

        try:
            order = self.get_object(pk)

            if not self.can_update_order(request, order):
                return Response(
                    {"detail": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = OrderStatusUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            order.status = serializer.validated_data["status"]
            order.save()

            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

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


    def can_update_order(self, request, order):
        """
        Ensures that only the related business user is allowed
        to update the order status.
        """

        return (
            hasattr(request.user, "profile")
            and request.user.profile.type == Profile.BUSINESS
            and order.business_user == request.user
        )


    def delete(self, request, pk):
        """Deletes an order for staff users only."""

        try:
            order = self.get_object(pk)

            if not request.user.is_staff:
                return Response(
                    {"detail": "Permission denied."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            order.delete()

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


class OrderCountView(APIView):
    """API view for counting the total business user orders."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Returns in-progress order count for a business user."""

        try:
            if not Order.objects.filter(
                business_user_id=business_user_id
            ).exists():
                raise NotFound("Business user not found.")

            count = Order.objects.filter(
                business_user_id=business_user_id,
                status=Order.IN_PROGRESS,
            ).count()

            return Response(
                {"order_count": count},
                status=status.HTTP_200_OK,
            )

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


class CompletedOrderCountView(APIView):
    """API view for counting the completed business user orders."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Returns completed order count for a business user."""

        try:
            if not Order.objects.filter(
                business_user_id=business_user_id
            ).exists():
                raise NotFound("Business user not found.")

            count = Order.objects.filter(
                business_user_id=business_user_id,
                status=Order.COMPLETED,
            ).count()

            return Response(
                {"completed_order_count": count},
                status=status.HTTP_200_OK,
            )

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