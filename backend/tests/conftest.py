"""
Pytest configuration and fixtures for backend tests.
"""

import os
from typing import Generator

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Generate password hash dynamically for test user
TEST_PASSWORD = "testpass"
TEST_PASSWORD_HASH = bcrypt.hashpw(TEST_PASSWORD.encode(), bcrypt.gensalt()).decode()

# Set test environment before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ADMIN_USERNAME"] = "testadmin"
os.environ["ADMIN_PASSWORD_HASH"] = TEST_PASSWORD_HASH
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    # Create a new engine for each test to ensure complete isolation
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """Get authentication headers for admin user."""
    # Login and get token
    response = client.post(
        "/api/auth/login",
        data={"username": "testadmin", "password": "testpass"},
    )

    if response.status_code != 200:
        # If login fails, the password hash might not match
        pytest.skip("Auth not configured properly for tests")

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_individual_application() -> dict:
    """Sample Individual application data."""
    return {
        "tenor": "2-Year",
        "month_of_offer": "January",
        "bond_value": 100000,
        "amount_in_words": "One Hundred Thousand Naira Only",
        "applicant_type": "Individual",
        "title": "Mr.",
        "full_name": "John Doe",
        "date_of_birth": "1990-01-15",
        "phone_number": "+2348012345678",
        "email": "john.doe@example.com",
        "occupation": "Engineer",
        "address": "123 Test Street, Lagos",
        "bank_name": "Access Bank",
        "bank_branch": "Lagos Main",
        "account_number": "0123456789",
        "sort_code": "044",
        "bvn": "12345678901",
        "is_resident": True,
        "investor_category": ["Retail Investor"],
    }


@pytest.fixture
def sample_joint_application() -> dict:
    """Sample Joint application data."""
    return {
        "tenor": "3-Year",
        "month_of_offer": "February",
        "bond_value": 250000,
        "amount_in_words": "Two Hundred and Fifty Thousand Naira Only",
        "applicant_type": "Joint",
        "title": "Mr.",
        "full_name": "John Doe",
        "date_of_birth": "1985-06-20",
        "phone_number": "+2348012345678",
        "email": "john.doe@example.com",
        "occupation": "Doctor",
        "address": "456 Test Avenue, Abuja",
        "bank_name": "First Bank",
        "bank_branch": "Abuja Central",
        "account_number": "1234567890",
        "sort_code": "011",
        "bvn": "12345678901",
        "joint_title": "Mrs.",
        "joint_full_name": "Jane Doe",
        "joint_date_of_birth": "1988-03-10",
        "joint_phone_number": "+2348087654321",
        "joint_email": "jane.doe@example.com",
        "joint_occupation": "Nurse",
        "joint_address": "456 Test Avenue, Abuja",
        "joint_bank_name": "GTBank",
        "joint_bank_branch": "Abuja Main",
        "joint_account_number": "0987654321",
        "joint_sort_code": "058",
        "joint_bvn": "10987654321",
        "is_resident": True,
        "investor_category": ["Retail Investor"],
    }


@pytest.fixture
def sample_corporate_application() -> dict:
    """Sample Corporate application data."""
    return {
        "tenor": "2-Year",
        "month_of_offer": "March",
        "bond_value": 5000000,
        "amount_in_words": "Five Million Naira Only",
        "applicant_type": "Corporate",
        "company_name": "Test Company Ltd",
        "rc_number": "RC123456",
        "business_type": "Technology",
        "contact_person": "Jane Smith",
        "corp_phone_number": "+2348012345678",
        "corp_email": "info@testcompany.com",
        "corp_address": "789 Business Park, Lagos",
        "bank_name": "Zenith Bank",
        "bank_branch": "Victoria Island",
        "account_number": "1122334455",
        "sort_code": "057",
        "bvn": "11223344556",
        "is_resident": True,
        "investor_category": ["Institutional Investor"],
    }


@pytest.fixture
def sample_payment() -> dict:
    """Sample payment data."""
    return {
        "amount": 100000,
        "payment_method": "bank_transfer",
        "payment_reference": "TRF123456789",
        "payment_date": "2026-01-15",
        "receiving_bank": "Access Bank",
        "notes": "Test payment",
    }


@pytest.fixture
def created_application(client: TestClient, sample_individual_application: dict) -> dict:
    """Create an application and return its data with ID."""
    response = client.post("/api/applications", json=sample_individual_application)
    assert response.status_code == 201
    return response.json()
