from rest_framework import serializers
from rest_framework.exceptions import NotFound

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializes full order data."""

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Handles order creation from an offer detail snapshot."""

    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        """Returns the offer detail or raises not found."""

        try:
            return OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise NotFound("Offer detail not found.")

    def create(self, validated_data):
        """Creates an order with snapshot data copied from the selected offer detail."""

        offer_detail = validated_data["offer_detail_id"]
        user = self.context["request"].user

        return Order.objects.create(
            customer_user=user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )