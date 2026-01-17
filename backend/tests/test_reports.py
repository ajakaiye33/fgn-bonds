"""
Tests for DMO reporting endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestMonthlyReportSummary:
    """Tests for monthly report summary endpoint."""

    def test_get_monthly_summary_empty(self, client: TestClient, auth_headers: dict):
        """Test monthly summary with no data."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get(
            "/api/admin/reports/monthly-summary?month_of_offer=January&year=2026",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["month_of_offer"] == "January"
        assert data["year"] == 2026
        assert data["total_applications"] == 0

    def test_get_monthly_summary_with_data(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_individual_application: dict,
    ):
        """Test monthly summary with application data."""
        if not auth_headers:
            pytest.skip("Auth not available")

        # Create application for January
        sample_individual_application["month_of_offer"] = "January"
        client.post("/api/applications", json=sample_individual_application)

        response = client.get(
            "/api/admin/reports/monthly-summary?month_of_offer=January&year=2026",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] >= 1
        assert data["total_value"] >= 0
        # API returns flat fields for tenor breakdown
        assert "total_2year" in data
        assert "total_3year" in data
        # Applicant type breakdown
        assert "total_individual" in data
        assert "total_joint" in data
        assert "total_corporate" in data
        # Payment status breakdown
        assert "pending_count" in data
        assert "verified_count" in data


class TestDMOReportExport:
    """Tests for DMO report Excel export."""

    def test_export_dmo_report(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_individual_application: dict,
    ):
        """Test exporting DMO report as Excel."""
        if not auth_headers:
            pytest.skip("Auth not available")

        # Create application
        sample_individual_application["month_of_offer"] = "January"
        client.post("/api/applications", json=sample_individual_application)

        response = client.get(
            "/api/admin/reports/export/excel?month_of_offer=January&year=2026",
            headers=auth_headers,
        )
        assert response.status_code == 200
        content_type = response.headers["content-type"]
        assert "spreadsheet" in content_type or "excel" in content_type.lower()

    def test_export_dmo_report_requires_auth(self, client: TestClient):
        """Test DMO report export requires authentication."""
        response = client.get(
            "/api/admin/reports/export/excel?month_of_offer=January&year=2026"
        )
        assert response.status_code == 401


class TestDMOSubmission:
    """Tests for marking reports as submitted to DMO."""

    def test_mark_as_submitted(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_individual_application: dict,
    ):
        """Test marking a month as submitted to DMO."""
        if not auth_headers:
            pytest.skip("Auth not available")

        # Create application
        sample_individual_application["month_of_offer"] = "February"
        client.post("/api/applications", json=sample_individual_application)

        # Mark as submitted
        response = client.post(
            "/api/admin/reports/submit-to-dmo",
            json={"month_of_offer": "February", "year": 2026},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["month_of_offer"] == "February"
        assert data["year"] == 2026
        assert "submitted_at" in data

    def test_prevent_duplicate_submission(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_individual_application: dict,
    ):
        """Test preventing duplicate submission for same period."""
        if not auth_headers:
            pytest.skip("Auth not available")

        # Create application
        sample_individual_application["month_of_offer"] = "March"
        client.post("/api/applications", json=sample_individual_application)

        # First submission
        response1 = client.post(
            "/api/admin/reports/submit-to-dmo",
            json={"month_of_offer": "March", "year": 2026},
            headers=auth_headers,
        )
        assert response1.status_code in [200, 201]

        # Second submission should fail
        response2 = client.post(
            "/api/admin/reports/submit-to-dmo",
            json={"month_of_offer": "March", "year": 2026},
            headers=auth_headers,
        )
        assert response2.status_code in [400, 409]


class TestSubmissionHistory:
    """Tests for DMO submission history."""

    def test_get_submission_history_empty(self, client: TestClient, auth_headers: dict):
        """Test getting submission history when empty."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.get("/api/admin/reports/submissions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_submission_history_with_data(
        self,
        client: TestClient,
        auth_headers: dict,
        sample_individual_application: dict,
    ):
        """Test getting submission history after submissions."""
        if not auth_headers:
            pytest.skip("Auth not available")

        # Create application and submit
        sample_individual_application["month_of_offer"] = "April"
        client.post("/api/applications", json=sample_individual_application)

        client.post(
            "/api/admin/reports/submit-to-dmo",
            json={"month_of_offer": "April", "year": 2026},
            headers=auth_headers,
        )

        # Get history
        response = client.get("/api/admin/reports/submissions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

        # Verify submission details
        submission = data[0]
        assert "month_of_offer" in submission
        assert "year" in submission
        assert "submitted_at" in submission
