from django.db.models import Min, Q

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer

from .permissions import IsBusinessUser
from .serializers import OfferCreateSerializer, OfferListSerializer


class OfferPagination(PageNumberPagination):
    """Defines frontend-aligned offer pagination."""

    page_size = 6
    page_size_query_param = "page_size"


class OfferListCreateView(APIView):
    """API view for listing and creating offers."""

    def get_permissions(self):
        """Returns permissions based on request method."""

        if self.request.method == "POST":
            return [IsAuthenticated(), IsBusinessUser()]

        return [AllowAny()]


    def get(self, request):
        """Returns a paginated offer list with filtering and ordering support."""

        try:
            queryset = self._get_offer_queryset(request)
            paginator = OfferPagination()
            page = paginator.paginate_queryset(queryset, request)
            serializer = OfferListSerializer(page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except ValueError:
            return Response(
                {"detail": "Invalid query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def post(self, request):
        """Creates a new offer for a business user."""

        try:
            serializer = OfferCreateSerializer(
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def _get_offer_queryset(self, request):
        """Builds the filtered and ordered offer queryset."""

        queryset = Offer.objects.all()
        queryset = self._add_offer_annotations(queryset)
        queryset = self._apply_offer_filters(queryset, request)
        return self._apply_offer_ordering(queryset, request)


    def _add_offer_annotations(self, queryset):
        """Adds calculated offer summary values."""

        return queryset.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )


    def _apply_offer_filters(self, queryset, request):
        """Applies supported offer query filters."""

        queryset = self._filter_by_creator(queryset, request)
        queryset = self._filter_by_min_price(queryset, request)
        queryset = self._filter_by_max_delivery_time(queryset, request)
        return self._filter_by_search(queryset, request)


    def _filter_by_creator(self, queryset, request):
        """Filters offers by creator id."""

        creator_id = request.query_params.get("creator_id")

        if creator_id:
            queryset = queryset.filter(user_id=int(creator_id))

        return queryset


    def _filter_by_min_price(self, queryset, request):
        """Filters offers by minimum price."""

        min_price = request.query_params.get("min_price")

        if min_price:
            queryset = queryset.filter(min_price__gte=float(min_price))

        return queryset


    def _filter_by_max_delivery_time(self, queryset, request):
        """Filters offers by maximum delivery time."""

        max_delivery_time = request.query_params.get("max_delivery_time")

        if max_delivery_time:
            queryset = queryset.filter(
                min_delivery_time__lte=int(max_delivery_time),
            )

        return queryset


    def _filter_by_search(self, queryset, request):
        """Filters offers by title or description search."""

        search = request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset


    def _apply_offer_ordering(self, queryset, request):
        """Applies supported offer ordering."""

        ordering = request.query_params.get("ordering")

        if ordering in ["updated_at", "-updated_at", "min_price", "-min_price"]:
            return queryset.order_by(ordering)

        return queryset.order_by("id")


class OfferDetailView(APIView):
    """API view for offer details, update and delete."""

    pass


class OfferDetailRetrieveView(APIView):
    """API view for retrieving a single offer detail."""

    pass