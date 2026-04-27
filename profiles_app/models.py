from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Stores additional user profile data."""

    CUSTOMER = "customer"
    BUSINESS = "business"

    TYPE_CHOICES = [
        (CUSTOMER, "Customer"),
        (BUSINESS, "Business"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    file = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=255, blank=True, default="")

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.user.username} ({self.type})"