"""
Tests for admin dashboard endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestListApplications:
    """Tests for listing applications with filters."""

    def test_list_applications_empty(self, client: TestClient, auth_headers: dict):
        """Test listing applications when none exist."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get("/api/admin/applications", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_applications_with_data(
        self, client: TestClient, auth_headers: dict, created_application: dict
    ):
        """Test listing applications returns data."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get("/api/admin/applications", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_list_applications_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_individual_application: dict,
    ):
        """Test pagination parameters work correctly."""
        if not auth_headers:
            pytest.skip("Auth not available")

        # Create multiple applications
        for i in range(5):
            app_data = sample_individual_application.copy()
            app_data["email"] = f"test{i}@example.com"
            client.post("/api/applications", json=app_data)

        # Test page size (minimum page_size is 10)
        response = client.get(
            "/api/admin/applications?page=0&page_size=10", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 10
        assert data["page"] == 0
        assert data["page_size"] == 10

    def test_filter_by_applicant_type(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_individual_application: dict,
        sample_corporate_application: dict,
    ):
        """Test filtering by applicant type."""
        if not auth_headers:
            pytest.skip("Auth not available")

        # Create Individual and Corporate applications
        client.post("/api/applications", json=sample_individual_application)
        client.post("/api/applications", json=sample_corporate_application)

        # Filter by Individual
        response = client.get(
            "/api/admin/applications?applicant_types=Individual", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["applicant_type"] == "Individual"

    def test_filter_by_tenor(
        self, client: TestClient, auth_headers: dict, sample_individual_application: dict
    ):
        """Test filtering by tenor."""
        if not auth_headers:
            pytest.skip("Auth not available")

        # Create application with specific tenor
        client.post("/api/applications", json=sample_individual_application)

        response = client.get(
            "/api/admin/applications?tenors=2-Year", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["tenor"] == "2-Year"

    def test_filter_by_payment_status(
        self, client: TestClient, auth_headers: dict, created_application: dict
    ):
        """Test filtering by payment status."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get(
            "/api/admin/applications?payment_status=pending", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["payment_status"] == "pending"

    def test_search_by_name(
        self, client: TestClient, auth_headers: dict, created_application: dict
    ):
        """Test searching by applicant name."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get(
            "/api/admin/applications?search=John", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1


class TestSummary:
    """Tests for dashboard summary endpoint."""

    def test_get_summary_empty(self, client: TestClient, auth_headers: dict):
        """Test summary with no applications."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get("/api/admin/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] == 0
        assert data["total_value"] == 0

    def test_get_summary_with_data(
        self, client: TestClient, auth_headers: dict, created_application: dict
    ):
        """Test summary with application data."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get("/api/admin/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] >= 1
        assert data["total_value"] >= created_application["bond_value"]
        assert "by_applicant_type" in data


class TestAnalytics:
    """Tests for analytics endpoint."""

    def test_get_analytics(
        self, client: TestClient, auth_headers: dict, created_application: dict
    ):
        """Test analytics data retrieval."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get("/api/admin/analytics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "by_applicant_type" in data
        assert "by_month" in data
        assert "by_tenor" in data
        assert "value_distribution" in data


class TestExports:
    """Tests for export endpoints."""

    def test_export_csv(
        self, client: TestClient, auth_headers: dict, created_application: dict
    ):
        """Test CSV export."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get("/api/admin/export/csv", headers=auth_headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_export_excel(
        self, client: TestClient, auth_headers: dict, created_application: dict
    ):
        """Test Excel export."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get("/api/admin/export/excel", headers=auth_headers)
        assert response.status_code == 200
        content_type = response.headers["content-type"]
        assert "spreadsheet" in content_type or "excel" in content_type.lower()

    def test_export_requires_auth(self, client: TestClient):
        """Test exports require authentication."""
        csv_response = client.get("/api/admin/export/csv")
        assert csv_response.status_code == 401

        excel_response = client.get("/api/admin/export/excel")
        assert excel_response.status_code == 401
