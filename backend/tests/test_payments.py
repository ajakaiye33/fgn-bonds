"""
Tests for payment management endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestRecordPayment:
    """Tests for recording payments."""

    def test_record_payment_success(
        self,
        client: TestClient,
        auth_headers: dict,
        created_application: dict,
        sample_payment: dict,
    ):
        """Test recording a payment for an application."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]
        response = client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == sample_payment["amount"]
        assert data["payment_method"] == sample_payment["payment_method"]
        assert data["payment_reference"] == sample_payment["payment_reference"]
        assert data["status"] == "pending"

    def test_record_payment_requires_auth(
        self, client: TestClient, created_application: dict, sample_payment: dict
    ):
        """Test recording payment requires authentication."""
        app_id = created_application["id"]
        response = client.post(
            f"/api/admin/applications/{app_id}/payment", json=sample_payment
        )
        assert response.status_code == 401

    def test_record_duplicate_payment_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        created_application: dict,
        sample_payment: dict,
    ):
        """Test recording duplicate payment for same application fails."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]

        # First payment
        response1 = client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )
        assert response1.status_code == 200

        # Second payment should fail
        response2 = client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )
        assert response2.status_code in [400, 409]

    def test_record_payment_for_nonexistent_application(
        self, client: TestClient, auth_headers: dict, sample_payment: dict
    ):
        """Test recording payment for non-existent application fails."""
        if not auth_headers:
            pytest.skip("Auth not available")

        response = client.post(
            "/api/admin/applications/99999/payment",
            json=sample_payment,
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestGetPayment:
    """Tests for retrieving payment information."""

    def test_get_payment_success(
        self,
        client: TestClient,
        auth_headers: dict,
        created_application: dict,
        sample_payment: dict,
    ):
        """Test getting payment details for an application."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]

        # Record a payment first
        client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )

        # Get payment
        response = client.get(
            f"/api/admin/applications/{app_id}/payment", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == sample_payment["amount"]

    def test_get_payment_not_found(
        self, client: TestClient, auth_headers: dict, created_application: dict
    ):
        """Test getting payment for application without payment."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]
        response = client.get(
            f"/api/admin/applications/{app_id}/payment", headers=auth_headers
        )
        assert response.status_code == 404


class TestVerifyPayment:
    """Tests for payment verification workflow."""

    def test_verify_payment_success(
        self,
        client: TestClient,
        auth_headers: dict,
        created_application: dict,
        sample_payment: dict,
    ):
        """Test verifying a payment."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]

        # Record payment
        payment_response = client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )
        payment_id = payment_response.json()["id"]

        # Verify payment
        response = client.post(
            f"/api/admin/payments/{payment_id}/verify",
            json={"action": "verify"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "verified"

    def test_reject_payment_success(
        self,
        client: TestClient,
        auth_headers: dict,
        created_application: dict,
        sample_payment: dict,
    ):
        """Test rejecting a payment with reason."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]

        # Record payment
        payment_response = client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )
        payment_id = payment_response.json()["id"]

        # Reject payment
        response = client.post(
            f"/api/admin/payments/{payment_id}/verify",
            json={"action": "reject", "rejection_reason": "Invalid reference number"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert "Invalid reference" in data.get("rejection_reason", "")

    def test_reject_payment_requires_reason(
        self,
        client: TestClient,
        auth_headers: dict,
        created_application: dict,
        sample_payment: dict,
    ):
        """Test rejecting payment without reason fails."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]

        # Record payment
        payment_response = client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )
        payment_id = payment_response.json()["id"]

        # Reject without reason
        response = client.post(
            f"/api/admin/payments/{payment_id}/verify",
            json={"action": "reject"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestUpdatePayment:
    """Tests for updating payments."""

    def test_update_pending_payment(
        self,
        client: TestClient,
        auth_headers: dict,
        created_application: dict,
        sample_payment: dict,
    ):
        """Test updating a pending payment."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]

        # Record payment
        payment_response = client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )
        payment_id = payment_response.json()["id"]

        # Update payment
        update_data = {"amount": 150000, "notes": "Updated payment"}
        response = client.patch(
            f"/api/admin/payments/{payment_id}",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 150000
        assert data["notes"] == "Updated payment"


class TestDeletePayment:
    """Tests for deleting payments."""

    def test_delete_pending_payment(
        self,
        client: TestClient,
        auth_headers: dict,
        created_application: dict,
        sample_payment: dict,
    ):
        """Test deleting a pending payment."""
        if not auth_headers:
            pytest.skip("Auth not available")

        app_id = created_application["id"]

        # Record payment
        payment_response = client.post(
            f"/api/admin/applications/{app_id}/payment",
            json=sample_payment,
            headers=auth_headers,
        )
        payment_id = payment_response.json()["id"]

        # Delete payment
        response = client.delete(
            f"/api/admin/payments/{payment_id}", headers=auth_headers
        )
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/admin/applications/{app_id}/payment", headers=auth_headers
        )
        assert get_response.status_code == 404
