from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

import pytest
import requests

from errorbrain.client import (
    ErrorBrainClient,
    ErrorEvent,
    ExplainResponse,
    Source,
    Verdict,
)


class StubResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any]):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")


def _sample_verdict(event_id: str) -> Dict[str, Any]:
    return {
        "id": str(uuid4()),
        "event_id": event_id,
        "hypothesis": {
            "title": "Issue observed",
            "description": "Something happened",
            "confidence": 0.7,
        },
        "impact": {
            "severity": "warning",
            "affected_components": ["svc"],
        },
        "recommended_actions": [
            {"title": "Check logs", "description": "Inspect logs", "urgency": "medium"}
        ],
        "evidence_refs": [],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


def _sample_event(event_id: str) -> ErrorEvent:
    return ErrorEvent(
        id=event_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        source=Source(language="python", name="svc"),
        message="boom",
        severity="error",
    )


def test_health_check(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, timeout: int) -> StubResponse:  # type: ignore[override]
        return StubResponse(200, {"status": "ok"})

    monkeypatch.setattr("errorbrain.client.requests.get", fake_get)
    client = ErrorBrainClient(base_url="http://example.com/api")

    result = client.health_check()
    assert result["status"] == "ok"


def test_get_verdict_uses_analysis_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}
    event_id = str(uuid4())

    def fake_get(url: str, timeout: int) -> StubResponse:  # type: ignore[override]
        captured["url"] = url
        return StubResponse(200, _sample_verdict(event_id))

    monkeypatch.setattr("errorbrain.client.requests.get", fake_get)
    client = ErrorBrainClient(base_url="http://example.com")

    verdict = client.get_verdict(event_id)

    assert captured["url"] == f"http://example.com/analysis/{event_id}"
    assert verdict.event_id == event_id


def test_submit_event_builds_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}
    event = _sample_event(str(uuid4()))

    def fake_post(url: str, json: Dict[str, Any], timeout: int) -> StubResponse:  # type: ignore[override]
        captured["url"] = url
        captured["json"] = json
        return StubResponse(200, _sample_verdict(event.id))

    monkeypatch.setattr("errorbrain.client.requests.post", fake_post)
    client = ErrorBrainClient(base_url="http://example.com")

    verdict = client.submit_event(event)

    assert captured["url"] == "http://example.com/events"
    assert captured["json"]["id"] == event.id
    assert verdict.event_id == event.id


def test_explain_parses_response(monkeypatch: pytest.MonkeyPatch) -> None:
    event_id = str(uuid4())
    captured: Dict[str, Any] = {}

    def fake_get(url: str, timeout: int) -> StubResponse:  # type: ignore[override]
        captured["url"] = url
        payload = {
            "event_id": event_id,
            "verdict_id": str(uuid4()),
            "summary": "Issue observed",
            "details": "Something happened",
            "actions": ["do X"],
        }
        return StubResponse(200, payload)

    monkeypatch.setattr("errorbrain.client.requests.get", fake_get)
    client = ErrorBrainClient(base_url="http://example.com")

    explanation = client.explain(event_id)

    assert isinstance(explanation, ExplainResponse)
    assert captured["url"] == f"http://example.com/explain/{event_id}"


def test_env_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ERRORBRAIN_API_URL", "http://env-url")
    client = ErrorBrainClient()
    assert client.base_url == "http://env-url"


@pytest.mark.asyncio
async def test_get_verdict_async(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}
    event_id = str(uuid4())

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any):
            captured["init_kwargs"] = kwargs

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
            return None

        async def get(self, url: str):  # type: ignore[override]
            captured["url"] = url

            class Resp:
                status_code = 200

                def raise_for_status(self) -> None:
                    return None

                def json(self) -> Dict[str, Any]:
                    return _sample_verdict(event_id)

            return Resp()

    monkeypatch.setattr("errorbrain.client.httpx.AsyncClient", FakeAsyncClient)
    client = ErrorBrainClient(base_url="http://example.com")

    verdict = await client.get_verdict_async(event_id)

    assert captured["url"] == f"http://example.com/analysis/{event_id}"
    assert isinstance(verdict, Verdict)
