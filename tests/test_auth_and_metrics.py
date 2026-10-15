import pytest
from fastapi.testclient import TestClient
from main import app
from services.keyGenerator import keyGenerator
from repository.database import get_connection, init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_key_generation_and_verification():
    tenant_name = "test_tenant_xyz"
    raw_key = keyGenerator.generate_key(tenant=tenant_name)
    assert raw_key.startswith("sk-")

    # Verify valid key returns tenant
    verified_tenant = keyGenerator.verify_key(raw_key)
    assert verified_tenant == tenant_name

    # Verify invalid key returns None
    assert keyGenerator.verify_key("sk-invalidkey123") is None


def test_chat_completion_unauthorized():
    client = TestClient(app)
    # Request without auth header
    response = client.post(
        "/v1/chat/completions",
        json={"model": "fake-1", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert response.status_code == 401
    assert "Missing API Key" in response.json()["detail"]


def test_chat_completion_invalid_key():
    client = TestClient(app)
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer sk-nonexistent"},
        json={"model": "fake-1", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert response.status_code == 401
    assert "Invalid or revoked API Key" in response.json()["detail"]


def test_chat_completion_authorized_and_metric_tenant():
    tenant_name = "tenant_metrics_check"
    raw_key = keyGenerator.generate_key(tenant=tenant_name)

    client = TestClient(app)
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {raw_key}"},
        json={"model": "fake-1", "messages": [{"role": "user", "content": "hello"}]},
    )

    # Regardless of provider response (success or fakeProvider1 error/delay), verify metric was recorded with actual tenant
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tenant FROM provider_metrics WHERE tenant = ? ORDER BY id DESC LIMIT 1",
            (tenant_name,),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["tenant"] == tenant_name
