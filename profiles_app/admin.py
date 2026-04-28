from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for user profiles."""

    list_display = [
        "id",
        "user",
        "type",
        "location",
        "tel",
        "created_at",
    ]
    list_filter = [
        "type",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "location",
    ]
