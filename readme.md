# Coderr Backend

Backend for the Coderr platform built with Django and Django REST Framework.

This project is part of the Developer Akademie backend course and is designed to work together with a separated frontend repository.

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

# Start development server
python manage.py runserver
```

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

- one package type per offer is allowed per offer

---

### Order Model

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

## Frontend

This backend is designed to work together with the separated Coderr frontend project.

Frontend repository:

[Frontend-Project-Coderr](https://github.com/Juergen-Malinowski/Frontend-Project-Coderr)

Frontend version:

```text
V1.2.0
```

The frontend communicates with the backend through:

```text
http://127.0.0.1:8000/api/
```

---

## Environment Setup

This project uses environment variables to securely manage sensitive data such as the Django SECRET_KEY.

### Setup Instructions

After cloning the repository, create your own `.env` file in the repository root directory.

Use the provided `.env.template` file as a base.

Example:

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

## Guest Login Accounts

The frontend uses predefined guest login accounts.

These users must exist in the backend database.

### Customer Guest Login

```text
username: KarlKalle
password: Dagi1234
```

### Business Guest Login

```text
username: WillWill
password: Dagi1234
```

---

## Project Status

The backend foundation and security setup have been initialized.

Current progress includes:

- backend repository setup
- virtual environment setup
- environment security preparation
- gitignore configuration
- initial README structure
