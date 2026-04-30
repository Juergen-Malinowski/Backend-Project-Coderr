from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from profiles_app.models import Profile


class OfferTestMixin:
    """Provides reusable users, profiles, offers and payloads."""

    def create_user_with_profile(self, username, email, profile_type):

        user = User.objects.create_user(
            username=username,
            email=email,
            password="Testpass123",
        )

        Profile.objects.create(
            user=user,
            type=profile_type,
        )
        return user


    def create_offer(self, user, title="Website Design"):

        offer = Offer.objects.create(
            user=user,
            title=title,
            description="Professional website design.",
        )
        self.create_offer_details(offer)
        return offer


    def create_offer_details(self, offer):

        OfferDetail.objects.create(
            offer=offer,
            title="Basic Design",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Logo Design", "Business Card"],
            offer_type=OfferDetail.BASIC,
        )

        OfferDetail.objects.create(
            offer=offer,
            title="Standard Design",
            revisions=5,
            delivery_time_in_days=7,
            price=200,
            features=["Logo Design", "Business Card", "Letterhead"],
            offer_type=OfferDetail.STANDARD,
        )

        OfferDetail.objects.create(
            offer=offer,
            title="Premium Design",
            revisions=10,
            delivery_time_in_days=10,
            price=500,
            features=["Logo Design", "Business Card", "Flyer"],
            offer_type=OfferDetail.PREMIUM,
        )


    def get_valid_offer_data(self):
        return {
            "title": "Graphic Design Package",
            "image": None,
            "description": "Complete graphic design package.",
            "details": [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo Design", "Business Card"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": [
                        "Logo Design",
                        "Business Card",
                        "Letterhead",
                    ],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": [
                        "Logo Design",
                        "Business Card",
                        "Letterhead",
                        "Flyer",
                    ],
                    "offer_type": "premium",
                },
            ],
        }
