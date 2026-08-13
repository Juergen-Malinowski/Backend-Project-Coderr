# Coderr Backend

[![Live Demo](https://img.shields.io/badge/Live-Demo-168C9D?style=for-the-badge&logo=googlechrome&logoColor=white)](https://coderr.juergen-malinowski.de)

> **Deployment branch:**  
> This branch contains the backend configuration used for the public portfolio demo.  
> The [`main`](https://github.com/Juergen-Malinowski/Backend-Project-Coderr/tree/main) branch preserves the original reviewed project version.

Backend for the Coderr platform built with Django and Django REST Framework.

This project is part of the Developer Akademie backend course and is designed to work together with a separate frontend repository.

---

## Setup / Quick-Start

Run the following commands to set up the project locally.

```bash
# Clone repository
git clone <your-backend-repository-url>

# Open backend folder
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux / Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create local environment file (Windows)
copy .env.template .env

# Create local environment file (Linux / Mac)
cp .env.template .env

# Generate a Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Insert SECRET_KEY into .env

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Optional: Load demo data for frontend testing
python manage.py shell -c "exec(open('scripts/seed_coderr_demo_data.py', encoding='utf-8').read())"

# Start development server
python manage.py runserver
```

---

## Table of Contents

- [Project Structure](#project-structure)
- [Database Models](#database-models)
  - [Profile Model](#profile-model)
  - [Offer Model](#offer-model)
  - [OfferDetail Model](#offerdetail-model)
  - [Order Model](#order-model)
  - [Review Model](#review-model)
- [API Overview](#api-overview)
- [Frontend](#frontend)
- [Environment Setup](#environment-setup)
- [Authentication](#authentication)
- [Django Admin](#django-admin)
- [Guest Login Accounts](#guest-login-accounts)
- [Project Status](#project-status)
- [Testing](#testing)
  - [Test Structure](#test-structure)
  - [Tested Apps](#tested-apps)
  - [Test File Locations](#test-file-locations)
  - [Running Tests](#running-tests)
- [Current Test Counts - 167 Tests](#current-test-counts---167-tests)
  - [Test Coverage Focus](#test-coverage-focus)
- [Demo Seed Data](#demo-seed-data)

---

## Project Structure

Recommended local project structure:

```text
project_coderr/
├── frontend/
└── backend/
```

Frontend and backend are maintained in separate repositories.

---

### Apps

```text
auth_app
profiles_app
offers_app
orders_app
reviews_app
base_info_app
```

---

## Database Models

### Profile Model

Purpose:

- extends the Django default user model
- stores customer and business profile information
- separates platform roles between `customer` and `business`

Fields:

- user (OneToOneField → User)
- file
- location
- tel
- description
- working_hours
- type
- created_at

Role choices:

```text
customer
business
```

---

### Offer Model

Purpose:

- stores service offers created by business users

Additional notes:

- offers are limited to business users
- related pricing packages are managed through OfferDetail objects
- the Django admin supports inline editing of related offer packages

Fields:

- user (ForeignKey → User)
- title
- image
- description
- created_at
- updated_at

---

### OfferDetail Model

Purpose:

- stores pricing packages for an offer

Fields:

- offer (ForeignKey → Offer)
- title
- revisions
- delivery_time_in_days
- price
- features
- offer_type

Offer type choices:

```text
basic
standard
premium
```

Constraints:

- each offer can contain only one package per offer_type

Admin integration:

- OfferDetail objects can be managed directly inside the related Offer admin page through Django admin inlines

---

### Order Model

Important behavior:

- orders store snapshot data from OfferDetail objects
- later offer changes do not affect already created orders

Purpose:

- stores customer orders for offer packages
- preserves snapshot data from offers at purchase time

Fields:

- customer_user (ForeignKey → User)
- business_user (ForeignKey → User)
- title
- revisions
- delivery_time_in_days
- price
- features
- offer_type
- status
- created_at
- updated_at

Status choices:

```text
in_progress
completed
cancelled
```

---

### Review Model

Purpose:

- stores customer reviews for business users
- allows editable user-based business ratings

Fields:

- business_user (ForeignKey → User)
- reviewer (ForeignKey → User)
- rating
- description
- created_at
- updated_at

Rules:

- one review per reviewer and business user combination
- ratings are limited to values between 1 and 5
- reviews can be updated by their creator

---

## Frontend

This backend works together with the separate Coderr frontend project.

Frontend repository:

[Frontend-Project-Coderr](https://github.com/Juergen-Malinowski/Frontend-Project-Coderr)

Frontend version:

```text
V1.2.0
```

### Live Deployment

The public portfolio demo is available at:

[Open the Coderr Live Demo](https://coderr.juergen-malinowski.de)

The deployed frontend communicates with this backend through:

```text
https://api.coderr.juergen-malinowski.de/api/
```

### Local Development

For local development, the frontend communicates with the backend through:

```text
http://127.0.0.1:8000/api/
```

The Django development server must be running locally for API-dependent frontend functionality.

---

## Environment Setup

This project uses environment variables to securely manage sensitive data such as the Django SECRET_KEY.

### Setup Instructions

After cloning the repository, create your own `.env` file in the repository root directory.

Use the provided `.env.template` file as a base.

Generate a SECRET_KEY using:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then insert it into your `.env` file:

```env
SECRET_KEY="your_secret_key_here"
```

### Important

- The `.env` file must never be committed
- Every developer must generate their own SECRET_KEY
- Exposed SECRET_KEY values must be replaced immediately

---

## Authentication

The backend uses token authentication via Django REST Framework.

Authentication header format:

```text
Authorization: Token <token>
```

---

## Django Admin

The project includes a configured Django admin interface for managing platform data.

Available admin areas include:

- Profiles
- Offers
- OfferDetails
- Orders
- Reviews

Admin interface URL:

```text
http://127.0.0.1:8000/admin/
```

A superuser account is required to access the admin interface.

---

## Guest Login Accounts

The deployed frontend provides predefined guest login accounts for demonstration and testing.

These accounts are created through the backend demo seed data.

### Customer Guest Login

```text
username: CreativeCat
password: Testpass123
```

### Business Guest Login

```text
username: PixelForge
password: Testpass123
```

These accounts are intended exclusively for the non-commercial portfolio demo and testing.

---

## API Overview

Available API endpoint groups:

```text
/api/registration/
/api/login/

/api/profile/<pk>/
/api/profiles/business/
/api/profiles/customer/

/api/offers/
/api/offers/<pk>/
/api/offerdetails/<pk>/

/api/orders/
/api/orders/<pk>/
/api/order-count/<business_user_id>/
/api/completed-order-count/<business_user_id>/

/api/reviews/
/api/reviews/<pk>/

/api/base-info/
```

---

## Project Status

The backend is fully implemented and deployed as part of the public Coderr portfolio demo.

Current state includes:

- all API endpoints implemented
- full test suite passing (167 tests)
- TDD-based architecture completed
- frontend and backend integration completed
- deployed behind Nginx and Gunicorn on a Hetzner VM

---

## Testing

This project follows a strong test-driven development (TDD) approach.

The goal of the testing architecture is to validate backend behavior before endpoint implementation is completed. Each endpoint receives dedicated API tests to verify permissions, validation logic, filtering behavior, aggregation logic, ordering behavior and expected HTTP responses.

---

### Test Structure

The test suite is organized by app and endpoint responsibility.

Each endpoint has its own dedicated test file to keep tests isolated, maintainable and easier to debug.

Reusable setup logic is extracted into `mixins.py` files where appropriate.

Example structure:

```text
app_name/tests/
├── mixins.py
├── test_endpoint_list_api.py
├── test_endpoint_create_api.py
├── test_endpoint_detail_api.py
```

---

### Tested Apps

The following apps currently contain dedicated API test coverage:

```text
auth_app
profiles_app
offers_app
orders_app
reviews_app
base_info_app
```

---

### Test File Locations

#### auth_app

```text
auth_app/tests/
├── mixins.py
├── test_login_api.py
└── test_registration_api.py
```

#### profiles_app

```text
profiles_app/tests/
├── mixins.py
├── test_business_profile_list_api.py
├── test_customer_profile_list_api.py
└── test_profile_detail_api.py
```

#### offers_app

```text
offers_app/tests/
├── mixins.py
├── test_offer_create_api.py
├── test_offer_detail_api.py
├── test_offer_detail_retrieve_api.py
└── test_offer_list_api.py
```

#### orders_app

```text
orders_app/tests/
├── mixins.py
├── test_completed_order_count_api.py
├── test_order_count_api.py
├── test_order_create_api.py
├── test_order_detail_api.py
└── test_order_list_api.py
```

#### reviews_app

```text
reviews_app/tests/
├── mixins.py
├── test_review_create_api.py
├── test_review_detail_api.py
└── test_review_list_api.py
```

#### base_info_app

```text
base_info_app/tests/
└── test_base_info_platform_statistics_api.py
```

---

### Running Tests

Run all tests:

```bash
pytest
```

Run tests for a specific app:

```bash
pytest reviews_app/tests/
```

Run a single endpoint test file:

```bash
pytest reviews_app/tests/test_review_create_api.py
```

Run a single test method:

```bash
pytest reviews_app/tests/test_review_create_api.py::TestReviewCreateAPI::test_create_review_returns_201
```

This allows every endpoint test suite to be executed independently during development and debugging.

---

### Current Test Counts - 167 Tests

| App           | Test Count |
| ------------- | ---------: |
| auth_app      |         19 |
| profiles_app  |         22 |
| offers_app    |         45 |
| orders_app    |         38 |
| reviews_app   |         35 |
| base_info_app |          8 |

---

### Test Coverage Focus

The test suite validates:

- authentication and permissions
- ownership protection
- serializer validation
- required fields
- filtering and ordering behavior
- aggregation and statistics endpoints
- pagination responses
- snapshot data integrity
- invalid input handling
- HTTP status code correctness
- internal error handling
- object deletion behavior

All tests are designed to validate backend behavior independently from frontend validation logic.

---

## Demo Seed Data

This project includes a demo data script to quickly populate the database with realistic example data for frontend and backend testing.

The demo seed data includes:

- 3 business users
- 3 customer users
- profiles for all users
- offers with basic, standard and premium variants
- completed and in-progress orders
- reviews and ratings

The deployed frontend guest login accounts are part of this demo seed data and provide direct access to the portfolio demo.

### Run Demo Seed Script

Run the following command inside the `backend` directory:

```cmd
python manage.py shell -c "exec(open('scripts/seed_coderr_demo_data.py', encoding='utf-8').read())"
```

### Repeated Execution

The demo seed script is designed to be safely executable multiple times.

Existing demo users, profiles, offers, orders and reviews are reused or updated automatically to prevent duplicate or inconsistent demo data.

### Demo Business Users

| Username | Specialization |
| --- | --- |
| PixelForge | Frontend Development |
| APIBuilder | Backend Development |
| CodeCraftStudio | Fullstack Development |

### Demo Customer Users

| Username |
| --- |
| CreativeCat |
| StartupVision |
| DigitalWave |

### Default Password

All demo users use the following password:

```text
Testpass123
```

### Successful Execution Output

After successful execution, the terminal displays all created demo users and the shared password.

Example output:

```text
Coderr demo data created successfully.
Business users: PixelForge, APIBuilder, CodeCraftStudio
Customer users: CreativeCat, StartupVision, DigitalWave
Default password for all demo users: Testpass123
```
