from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """
    Stores a customer review for a business user.

    The rating field is limited to values between 1 and 5
    because the frontend uses a five-star rating system.

    Validators prevent invalid rating values from being
    stored through direct API requests.
    """

    business_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='received_reviews'
    )

    reviewer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='written_reviews'
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['business_user', 'reviewer'],
                name='unique_review_per_business_user'
            ),
        ]

    def __str__(self):
        return (
            f"Review #{self.id} - {self.rating} stars - "
            f"{self.reviewer.username} for "
            f"{self.business_user.username} "
        )