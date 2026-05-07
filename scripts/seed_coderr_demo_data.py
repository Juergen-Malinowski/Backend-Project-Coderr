from decimal import Decimal

from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from profiles_app.models import Profile
from reviews_app.models import Review


def create_business_user(
    username,
    email,
    first_name,
    last_name,
    location,
    tel,
    working_hours,
    description,
):
    """Creates or updates a business user with profile."""

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    if created:
        user.set_password("Testpass123")
        user.save()

    Profile.objects.update_or_create(
        user=user,
        defaults={
            "type": Profile.BUSINESS,
            "location": location,
            "tel": tel,
            "working_hours": working_hours,
            "description": description,
        },
    )

    return user


def create_customer_user(
    username,
    email,
    first_name,
    last_name,
):
    """Creates or updates a customer user with profile."""

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    if created:
        user.set_password("Testpass123")
        user.save()

    Profile.objects.update_or_create(
        user=user,
        defaults={
            "type": Profile.CUSTOMER,
        },
    )

    return user


def create_offer_with_details(user, title, description, details):
    """Creates or updates one offer with its three offer details."""

    offer, created = Offer.objects.update_or_create(
        user=user,
        title=title,
        defaults={
            "description": description,
        },
    )

    for detail_data in details:
        OfferDetail.objects.update_or_create(
            offer=offer,
            offer_type=detail_data["offer_type"],
            defaults={
                "title": detail_data["title"],
                "revisions": detail_data["revisions"],
                "delivery_time_in_days": detail_data[
                    "delivery_time_in_days"
                ],
                "price": detail_data["price"],
                "features": detail_data["features"],
            },
        )

    return offer


def create_order(customer_user, offer_detail, status_value):
    """Creates or updates an order using offer detail snapshot data."""

    order, created = Order.objects.update_or_create(
        customer_user=customer_user,
        business_user=offer_detail.offer.user,
        title=offer_detail.title,
        offer_type=offer_detail.offer_type,
        defaults={
            "revisions": offer_detail.revisions,
            "delivery_time_in_days": offer_detail.delivery_time_in_days,
            "price": offer_detail.price,
            "features": offer_detail.features,
            "status": status_value,
        },
    )

    return order


def create_review(business_user, reviewer, rating, description):
    """Creates or updates one review for a business user."""

    review, created = Review.objects.update_or_create(
        business_user=business_user,
        reviewer=reviewer,
        defaults={
            "rating": rating,
            "description": description,
        },
    )

    return review


def run_seed():
    """Creates demo users, profiles, offers, orders and reviews."""

    frontend_business = create_business_user(
        username="PixelForge",
        email="frontend@coderr.dev",
        first_name="Lena",
        last_name="Hartmann",
        location="Hamburg, Deutschland",
        tel="+49 157 84561230",
        working_hours="Mo - Fr | 09:00 - 17:00",
        description=(
            "Frontend-Entwicklerin mit Fokus auf responsive Benutzeroberflächen, "
            "moderne JavaScript-Anwendungen und saubere UI/UX-Umsetzung. "
            "Spezialisiert auf Performance, Accessibility und pixelgenaue Designs."
        ),
    )

    backend_business = create_business_user(
        username="APIBuilder",
        email="backend@coderr.dev",
        first_name="David",
        last_name="Krüger",
        location="Berlin, Deutschland",
        tel="+49 176 44219873",
        working_hours="Mo - Sa | 10:00 - 19:00",
        description=(
            "Backend-Entwickler mit Schwerpunkt auf Django REST Framework, "
            "API-Architektur, Datenbankoptimierung und Authentifizierungssystemen. "
            "Erfahren in skalierbaren Backend-Lösungen und sicherem API-Design."
        ),
    )

    fullstack_business = create_business_user(
        username="CodeCraftStudio",
        email="fullstack@coderr.dev",
        first_name="Mika",
        last_name="Schneider",
        location="München, Deutschland",
        tel="+49 151 77234491",
        working_hours="Flexible Zeiten | Remote und Vor-Ort",
        description=(
            "Fullstack-Entwickler für komplette Weblösungen von der "
            "Frontend-Gestaltung bis zur Backend-Architektur. "
            "Spezialisiert auf Django, REST APIs, JavaScript "
            "und responsive Webanwendungen."
        ),
    )


    customer_one = create_customer_user(
        username="CreativeCat",
        email="creativecat@example.com",
        first_name="Sophie",
        last_name="Neumann",
    )

    customer_two = create_customer_user(
        username="StartupVision",
        email="startupvision@example.com",
        first_name="Jonas",
        last_name="Becker",
    )

    customer_three = create_customer_user(
        username="DigitalWave",
        email="digitalwave@example.com",
        first_name="Emily",
        last_name="Wagner",
    )


    frontend_offer = create_offer_with_details(
        user=frontend_business,
        title="Modernes Frontend Design und UI Umsetzung",
        description=(
            "Entwicklung moderner und responsiver Benutzeroberflächen "
            "mit Fokus auf Performance, Accessibility und sauberem UI Design."
        ),
        details=[
            {
                "title": "Basic Frontend Paket",
                "revisions": 1,
                "delivery_time_in_days": 5,
                "price": Decimal("249.00"),
                "features": [
                    "Responsive Design",
                    "Landingpage Umsetzung",
                    "Mobile Optimierung",
                ],
                "offer_type": "basic",
            },
            {
                "title": "Standard Frontend Paket",
                "revisions": 3,
                "delivery_time_in_days": 10,
                "price": Decimal("599.00"),
                "features": [
                    "Mehrseitige Umsetzung",
                    "Responsive Design",
                    "Animationen",
                    "Performance Optimierung",
                ],
                "offer_type": "standard",
            },
            {
                "title": "Premium Frontend Paket",
                "revisions": 5,
                "delivery_time_in_days": 14,
                "price": Decimal("1199.00"),
                "features": [
                    "Komplette UI Entwicklung",
                    "Custom Animationen",
                    "Accessibility Optimierung",
                    "High-End Responsive Design",
                    "Performance Analyse",
                ],
                "offer_type": "premium",
            },
        ],
    )


    backend_offer = create_offer_with_details(
        user=backend_business,
        title="Django Backend und REST API Entwicklung",
        description=(
            "Entwicklung sicherer und skalierbarer Backend-Systeme "
            "mit Django und Django REST Framework."
        ),
        details=[
            {
                "title": "Basic Backend Paket",
                "revisions": 1,
                "delivery_time_in_days": 7,
                "price": Decimal("349.00"),
                "features": [
                    "REST API Grundstruktur",
                    "CRUD Endpunkte",
                    "Datenbankanbindung",
                ],
                "offer_type": "basic",
            },
            {
                "title": "Standard Backend Paket",
                "revisions": 3,
                "delivery_time_in_days": 14,
                "price": Decimal("899.00"),
                "features": [
                    "Authentifizierung",
                    "Permissions",
                    "API Validierung",
                    "Optimierte Datenbankabfragen",
                ],
                "offer_type": "standard",
            },
            {
                "title": "Premium Backend Paket",
                "revisions": 5,
                "delivery_time_in_days": 21,
                "price": Decimal("1799.00"),
                "features": [
                    "Komplette API Architektur",
                    "Token Authentication",
                    "Custom Permissions",
                    "Performance Optimierung",
                    "Erweiterte Sicherheitslogik",
                ],
                "offer_type": "premium",
            },
        ],
    )


    fullstack_offer = create_offer_with_details(
        user=fullstack_business,
        title="Fullstack Webentwicklung für moderne Plattformen",
        description=(
            "Komplette Entwicklung moderner Webplattformen "
            "inklusive Frontend, Backend und API-Anbindung."
        ),
        details=[
            {
                "title": "Basic Fullstack Paket",
                "revisions": 2,
                "delivery_time_in_days": 10,
                "price": Decimal("599.00"),
                "features": [
                    "Frontend und Backend Basis",
                    "Responsive Umsetzung",
                    "API Integration",
                ],
                "offer_type": "basic",
            },
            {
                "title": "Standard Fullstack Paket",
                "revisions": 4,
                "delivery_time_in_days": 18,
                "price": Decimal("1399.00"),
                "features": [
                    "Komplette Plattformstruktur",
                    "Authentifizierung",
                    "Datenbankdesign",
                    "Responsive Frontend",
                ],
                "offer_type": "standard",
            },
            {
                "title": "Premium Fullstack Paket",
                "revisions": 6,
                "delivery_time_in_days": 30,
                "price": Decimal("2499.00"),
                "features": [
                    "Individuelle Plattformlösung",
                    "Frontend und Backend Entwicklung",
                    "REST API Architektur",
                    "Deployment Vorbereitung",
                    "Performance Optimierung",
                ],
                "offer_type": "premium",
            },
        ],
    )


    frontend_basic = frontend_offer.details.get(offer_type="basic")
    backend_standard = backend_offer.details.get(
        offer_type="standard"
    )
    fullstack_premium = fullstack_offer.details.get(
        offer_type="premium"
    )

    create_order(
        customer_user=customer_one,
        offer_detail=frontend_basic,
        status_value="completed",
    )

    create_order(
        customer_user=customer_one,
        offer_detail=backend_standard,
        status_value="in_progress",
    )

    create_order(
        customer_user=customer_two,
        offer_detail=backend_standard,
        status_value="completed",
    )

    create_order(
        customer_user=customer_two,
        offer_detail=fullstack_premium,
        status_value="in_progress",
    )

    create_order(
        customer_user=customer_three,
        offer_detail=frontend_basic,
        status_value="completed",
    )

    create_order(
        customer_user=customer_three,
        offer_detail=fullstack_premium,
        status_value="in_progress",
    )


    create_review(
        business_user=frontend_business,
        reviewer=customer_one,
        rating=5,
        description=(
            "Sehr professionelle Umsetzung. Die Oberfläche ist modern, "
            "übersichtlich und funktioniert auch mobil sehr gut."
        ),
    )

    create_review(
        business_user=backend_business,
        reviewer=customer_two,
        rating=4,
        description=(
            "Die API wurde sauber aufgebaut und gut dokumentiert. "
            "Besonders die Authentifizierung funktioniert zuverlässig."
        ),
    )

    create_review(
        business_user=fullstack_business,
        reviewer=customer_three,
        rating=5,
        description=(
            "Komplette Umsetzung aus einer Hand. Frontend, Backend "
            "und API-Anbindung passen sehr gut zusammen."
        ),
    )


    print("Coderr demo data created successfully.")
    print("Business users: PixelForge, APIBuilder, CodeCraftStudio")
    print("Customer users: CreativeCat, StartupVision, DigitalWave")
    print("Default password for all demo users: Testpass123")


run_seed()