from django.contrib import admin

from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """
    Displays related OfferDetail entries directly inside the Offer admin page.

    TabularInline provides a compact table-based layout for editing
    multiple offer packages within the parent offer view.

    The related OfferDetail objects are automatically linked through
    the ForeignKey relation to Offer.

    extra = 0 prevents Django from showing additional empty input rows.
    """

    model = OfferDetail
    extra = 0


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin configuration for offers."""

    list_display = [
        "id",
        "title",
        "user",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "title",
        "description",
        "user__username",
    ]
    inlines = [
        OfferDetailInline,
    ]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin configuration for offer details."""

    list_display = [
        "id",
        "offer",
        "offer_type",
        "title",
        "price",
        "delivery_time_in_days",
    ]
    list_filter = [
        "offer_type",
    ]
    search_fields = [
        "title",
        "offer__title",
    ]
