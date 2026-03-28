"""Tests for webhook endpoints and signature verification."""

import hashlib
import hmac
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.billing import verify_webhook_signature
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestBillingWebhookSignature:
    def test_valid_signature(self):
        secret = "test-secret"
        payload = b'{"data": "test"}'
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        with patch("app.core.billing.settings") as mock_settings:
            mock_settings.lemon_squeezy_webhook_secret = secret
            assert verify_webhook_signature(payload, expected) is True

    def test_invalid_signature(self):
        with patch("app.core.billing.settings") as mock_settings:
            mock_settings.lemon_squeezy_webhook_secret = "test-secret"
            assert verify_webhook_signature(b"payload", "invalid-sig") is False

    def test_missing_secret(self):
        with patch("app.core.billing.settings") as mock_settings:
            mock_settings.lemon_squeezy_webhook_secret = ""
            assert verify_webhook_signature(b"payload", "any-sig") is False


class TestSentryWebhookEndpoint:
    def test_sentry_webhook_accepts_payload(self, client):
        with patch(
            "app.services.error_analyzer.process_sentry_webhook",
            new_callable=AsyncMock,
        ):
            response = client.post(
                "/webhooks/sentry",
                json={
                    "action": "triggered",
                    "data": {
                        "event": {
                            "title": "ZeroDivisionError",
                            "message": "division by zero",
                            "level": "error",
                            "environment": "production",
                        }
                    },
                },
            )
            assert response.status_code == 200
            assert response.json()["status"] == "accepted"


class TestBillingWebhookEndpoint:
    def test_billing_webhook_accepts_valid_event(self, client):
        with patch(
            "app.core.billing.process_billing_webhook",
            new_callable=AsyncMock,
        ):
            response = client.post(
                "/webhooks/billing",
                json={
                    "meta": {"event_name": "subscription_created"},
                    "data": {
                        "id": "123",
                        "attributes": {
                            "user_email": "test@example.com",
                            "variant_id": "456",
                            "status": "active",
                        },
                    },
                },
            )
            assert response.status_code == 200
            assert response.json()["event"] == "subscription_created"

    def test_billing_webhook_rejects_missing_event(self, client):
        response = client.post("/webhooks/billing", json={"data": {}})
        assert response.status_code == 400

    def test_billing_webhook_rejects_invalid_signature(self, client):
        with patch("app.core.billing.verify_webhook_signature", return_value=False):
            response = client.post(
                "/webhooks/billing",
                json={
                    "meta": {"event_name": "subscription_created"},
                    "data": {},
                },
                headers={"X-Signature": "bad-signature"},
            )
            assert response.status_code == 401
