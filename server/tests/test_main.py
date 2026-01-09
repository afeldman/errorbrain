"""Tests for the verdict-focused ErrorBrain server."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from errorbrain_server.api.spec_models import SpecExplainResponse, SpecVerdict
from errorbrain_server.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _sample_event() -> dict:
    return {
        "id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": {"language": "python", "name": "svc-api", "tags": ["prod"]},
        "message": "Timeout while calling payment provider",
        "severity": "error",
        "metadata": {"component": "payment"},
        "evidence": [
            {"type": "log_line", "data": {"line": "failed to connect"}},
        ],
    }


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "spec_version" in data


def test_ingest_event_returns_verdict(client: TestClient) -> None:
    payload = _sample_event()

    response = client.post("/events", json=payload)
    assert response.status_code == 200

    verdict = SpecVerdict.model_validate(response.json())
    assert verdict.event_id == payload["id"]
    assert verdict.impact.severity == "critical"
    assert verdict.hypothesis.confidence > 0
    assert verdict.evidence_refs == [f"{payload['id']}#e0"]


def test_analysis_endpoint_returns_existing_verdict(client: TestClient) -> None:
    payload = _sample_event()
    post_resp = client.post("/events", json=payload)
    assert post_resp.status_code == 200

    get_resp = client.get(f"/analysis/{payload['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["event_id"] == payload["id"]


def test_explain_endpoint_uses_verdict(client: TestClient) -> None:
    payload = _sample_event()
    post_resp = client.post("/events", json=payload)
    verdict = SpecVerdict.model_validate(post_resp.json())

    explain_resp = client.get(f"/explain/{payload['id']}")
    assert explain_resp.status_code == 200

    explain = SpecExplainResponse.model_validate(explain_resp.json())
    assert explain.event_id == payload["id"]
    assert verdict.hypothesis.title.split()[0] in explain.summary
    assert explain.actions


def test_invalid_event_rejected(client: TestClient) -> None:
    bad_payload = {
        "id": "not-a-uuid",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": {"language": "python", "name": "svc-api"},
        "message": "oops",
    }

    response = client.post("/events", json=bad_payload)
    # FastAPI returns 422 for Pydantic validation errors (not 400)
    assert response.status_code == 422
