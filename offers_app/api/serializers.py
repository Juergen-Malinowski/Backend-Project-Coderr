from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Nested serializer for full offer detail data."""

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Helper serializer for offer detail link responses."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "url",
        ]

    def get_url(self, obj):
        """Returns the offer detail API path."""

        return f"/api/offerdetails/{obj.id}/"


class OfferListSerializer(serializers.ModelSerializer):
    """Serializes offer list data with summary fields."""

    user = serializers.IntegerField(source="user.id", read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_user_details(self, obj):
        """Returns compact data of the offer owner."""

        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username,
        }


class OfferCreateSerializer(serializers.ModelSerializer):
    """Handles offer creation with required basic, standard and premium details."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]

    def validate_details(self, value):
        """Ensures all required offer detail types are provided."""

        offer_types = self._get_offer_types(value)
        required_types = self._get_required_offer_types()

        if offer_types != required_types:
            raise serializers.ValidationError(
                "Details must include basic, standard and premium."
            )

        return value

    def _get_offer_types(self, details):
        """Returns all submitted offer detail types."""

        return {
            detail["offer_type"]
            for detail in details
        }

    def _get_required_offer_types(self):
        """Returns all required offer detail types."""

        return {
            OfferDetail.BASIC,
            OfferDetail.STANDARD,
            OfferDetail.PREMIUM,
        }

    def create(self, validated_data):
        """Creates an offer with nested offer details."""

        details_data = validated_data.pop("details")
        user = self.context["request"].user

        offer = Offer.objects.create(
            user=user,
            **validated_data,
        )

        self._create_offer_details(offer, details_data)

        return offer

    def _create_offer_details(self, offer, details_data):
        """Creates all nested offer details."""

        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail_data,
            )