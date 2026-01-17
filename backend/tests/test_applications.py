"""
Tests for application CRUD endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestCreateApplication:
    """Tests for creating applications."""

    def test_create_individual_application(
        self, client: TestClient, sample_individual_application: dict
    ):
        """Test creating an Individual application."""
        response = client.post("/api/applications", json=sample_individual_application)
        assert response.status_code == 201

        data = response.json()
        assert data["id"] is not None
        assert data["applicant_type"] == "Individual"
        assert data["full_name"] == "John Doe"
        assert data["bond_value"] == 100000
        assert data["payment_status"] == "pending"

    def test_create_joint_application(
        self, client: TestClient, sample_joint_application: dict
    ):
        """Test creating a Joint application."""
        response = client.post("/api/applications", json=sample_joint_application)
        assert response.status_code == 201

        data = response.json()
        assert data["applicant_type"] == "Joint"
        assert data["full_name"] == "John Doe"
        assert data["joint_full_name"] == "Jane Doe"

    def test_create_corporate_application(
        self, client: TestClient, sample_corporate_application: dict
    ):
        """Test creating a Corporate application."""
        response = client.post("/api/applications", json=sample_corporate_application)
        assert response.status_code == 201

        data = response.json()
        assert data["applicant_type"] == "Corporate"
        assert data["company_name"] == "Test Company Ltd"
        assert data["rc_number"] == "RC123456"

    def test_create_application_with_minimum_value(
        self, client: TestClient, sample_individual_application: dict
    ):
        """Test creating application with minimum bond value."""
        sample_individual_application["bond_value"] = 5000
        sample_individual_application["amount_in_words"] = "Five Thousand Naira Only"

        response = client.post("/api/applications", json=sample_individual_application)
        assert response.status_code == 201
        assert response.json()["bond_value"] == 5000

    def test_create_application_with_maximum_value(
        self, client: TestClient, sample_individual_application: dict
    ):
        """Test creating application with maximum bond value."""
        sample_individual_application["bond_value"] = 50000000
        sample_individual_application["amount_in_words"] = "Fifty Million Naira Only"

        response = client.post("/api/applications", json=sample_individual_application)
        assert response.status_code == 201
        assert response.json()["bond_value"] == 50000000

    def test_create_application_invalid_tenor(
        self, client: TestClient, sample_individual_application: dict
    ):
        """Test creating application with invalid tenor fails."""
        sample_individual_application["tenor"] = "5-Year"

        response = client.post("/api/applications", json=sample_individual_application)
        assert response.status_code == 422

    def test_create_application_invalid_email(
        self, client: TestClient, sample_individual_application: dict
    ):
        """Test creating application with invalid email fails."""
        sample_individual_application["email"] = "not-an-email"

        response = client.post("/api/applications", json=sample_individual_application)
        assert response.status_code == 422

    def test_create_application_bond_value_too_low(
        self, client: TestClient, sample_individual_application: dict
    ):
        """Test creating application with bond value below minimum fails."""
        sample_individual_application["bond_value"] = 1000

        response = client.post("/api/applications", json=sample_individual_application)
        assert response.status_code == 422

    def test_create_application_bond_value_too_high(
        self, client: TestClient, sample_individual_application: dict
    ):
        """Test creating application with bond value above maximum fails."""
        sample_individual_application["bond_value"] = 100000000

        response = client.post("/api/applications", json=sample_individual_application)
        assert response.status_code == 422


class TestGetApplication:
    """Tests for retrieving applications."""

    def test_get_application_by_id(self, client: TestClient, created_application: dict):
        """Test retrieving an application by ID."""
        app_id = created_application["id"]

        response = client.get(f"/api/applications/{app_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == app_id
        assert data["full_name"] == created_application["full_name"]

    def test_get_application_not_found(self, client: TestClient):
        """Test retrieving non-existent application returns 404."""
        response = client.get("/api/applications/99999")
        assert response.status_code == 404

    def test_get_application_invalid_id(self, client: TestClient):
        """Test retrieving with invalid ID format."""
        response = client.get("/api/applications/invalid")
        assert response.status_code == 422


class TestDownloadPdf:
    """Tests for PDF download endpoint."""

    def test_download_pdf_success(self, client: TestClient, created_application: dict):
        """Test downloading PDF for an application."""
        app_id = created_application["id"]

        response = client.get(f"/api/applications/{app_id}/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_download_pdf_not_found(self, client: TestClient):
        """Test downloading PDF for non-existent application returns 404."""
        response = client.get("/api/applications/99999/pdf")
        assert response.status_code == 404

    def test_download_pdf_has_filename(
        self, client: TestClient, created_application: dict
    ):
        """Test PDF download has proper filename header."""
        app_id = created_application["id"]

        response = client.get(f"/api/applications/{app_id}/pdf")
        assert response.status_code == 200

        content_disposition = response.headers.get("content-disposition", "")
        assert "filename" in content_disposition
        assert ".pdf" in content_disposition
