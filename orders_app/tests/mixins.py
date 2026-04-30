from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from profiles_app.models import Profile


class OrderTestMixin:
    """Provides reusable users, offers, offer details and orders."""

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


    def create_offer_with_detail(self, business_user):

        offer = Offer.objects.create(
            user=business_user,
            title="Logo Design",
            description="Professional logo design.",
        )

        return OfferDetail.objects.create(
            offer=offer,
            title="Basic Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design", "Business Card"],
            offer_type=OfferDetail.BASIC,
        )


    def create_order(self, customer_user, business_user, status=None):

        order_status = status or Order.IN_PROGRESS

        return Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo Design", "Business Card"],
            offer_type=OfferDetail.BASIC,
            status=order_status,
        )