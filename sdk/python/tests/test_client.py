import os
from typing import Any, Dict

import pytest
import requests

from errorbrain.client import ErrorBrainClient, ErrorReport


class StubResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any]):
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")


def test_health_check_uses_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}

    def fake_get(url: str, timeout: int) -> StubResponse:
        captured["url"] = url
        captured["timeout"] = timeout
        return StubResponse(200, {"status": "ok", "llm_configured": True})

    monkeypatch.setattr("errorbrain.client.requests.get", fake_get)

    client = ErrorBrainClient(base_url="http://example.com/api")
    result = client.health_check()

    assert result["status"] == "ok"
    assert captured["url"] == "http://example.com/api/healthz"
    assert captured["timeout"] == 5


def test_send_error_builds_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}

    def fake_post(url: str, json: Dict[str, Any], timeout: int) -> StubResponse:  # type: ignore[override]
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return StubResponse(200, {
            "id": "abc-123",
            "project": json["project"],
            "language": json["language"],
            "tags": json.get("tags", []),
            "created_at": "2024-01-01T00:00:00Z",
            "explanation": "ok",
            "saved_path": None,
        })

    monkeypatch.setattr("errorbrain.client.requests.post", fake_post)

    client = ErrorBrainClient(base_url="http://example.com")
    response = client.send_error(
        language="python",
        project="svc",
        message="boom",
        traceback="trace",
        tags=["prod"],
        metadata={"k": "v"},
        store_in_vault=False,
    )

    assert captured["url"] == "http://example.com/v1/errors"
    assert captured["json"]["language"] == "python"
    assert captured["json"]["project"] == "svc"
    assert captured["json"]["traceback"] == "trace"
    assert captured["json"]["tags"] == ["prod"]
    assert captured["json"]["metadata"] == {"k": "v"}
    assert captured["json"]["store_in_vault"] is False
    assert response.id == "abc-123"


def test_send_exception_formats_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}

    def fake_post(url: str, json: Dict[str, Any], timeout: int) -> StubResponse:  # type: ignore[override]
        captured["json"] = json
        return StubResponse(200, {
            "id": "abc-123",
            "project": json["project"],
            "language": json["language"],
            "tags": json.get("tags", []),
            "created_at": "2024-01-01T00:00:00Z",
            "explanation": "ok",
            "saved_path": None,
        })

    monkeypatch.setattr("errorbrain.client.requests.post", fake_post)

    client = ErrorBrainClient(base_url="http://example.com")

    # We need to ensure the traceback is captured; raise inside a helper to make deterministic
    try:
        raise ValueError("example")
    except ValueError as exc:
        _ = client.send_exception(exc, project="svc")

    assert "ValueError" in captured["json"]["traceback"]
    assert captured["json"]["message"] == "example"


def test_env_base_url_is_used(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ERRORBRAIN_API_URL", "http://env-url.local/")
    client = ErrorBrainClient()
    assert client.base_url == "http://env-url.local"


@pytest.mark.asyncio
async def test_send_error_async_builds_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}

    class FakeResponse:
        def __init__(self, status_code: int, payload: Dict[str, Any]):
            self.status_code = status_code
            self._payload = payload

        def json(self) -> Dict[str, Any]:
            return self._payload

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise requests.HTTPError(f"status {self.status_code}")

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any):
            captured["init_kwargs"] = kwargs

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
            return None

        async def post(self, url: str, json: Dict[str, Any]):  # type: ignore[override]
            captured["url"] = url
            captured["json"] = json
            return FakeResponse(200, {
                "id": "xyz",
                "project": json["project"],
                "language": json["language"],
                "tags": json.get("tags", []),
                "created_at": "2024-01-01T00:00:00Z",
                "explanation": "ok",
                "saved_path": None,
            })

    monkeypatch.setattr("errorbrain.client.httpx.AsyncClient", FakeAsyncClient)

    client = ErrorBrainClient(base_url="http://example.com")
    response = await client.send_error_async(
        language="python",
        project="svc",
        message="boom",
        traceback="trace",
        tags=["prod"],
        metadata={"k": "v"},
        store_in_vault=False,
    )

    assert captured["url"] == "http://example.com/v1/errors"
    assert captured["json"]["language"] == "python"
    assert captured["json"]["project"] == "svc"
    assert captured["json"]["traceback"] == "trace"
    assert captured["json"]["tags"] == ["prod"]
    assert captured["json"]["metadata"] == {"k": "v"}
    assert captured["json"]["store_in_vault"] is False
    assert response.id == "xyz"


@pytest.mark.asyncio
async def test_send_exception_async_formats_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: Dict[str, Any] = {}

    class FakeResponse:
        def __init__(self, status_code: int, payload: Dict[str, Any]):
            self.status_code = status_code
            self._payload = payload

        def json(self) -> Dict[str, Any]:
            return self._payload

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise requests.HTTPError(f"status {self.status_code}")

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any):
            captured["init_kwargs"] = kwargs

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
            return None

        async def post(self, url: str, json: Dict[str, Any]):  # type: ignore[override]
            captured["json"] = json
            return FakeResponse(200, {
                "id": "xyz",
                "project": json["project"],
                "language": json["language"],
                "tags": json.get("tags", []),
                "created_at": "2024-01-01T00:00:00Z",
                "explanation": "ok",
                "saved_path": None,
            })

    monkeypatch.setattr("errorbrain.client.httpx.AsyncClient", FakeAsyncClient)

    client = ErrorBrainClient(base_url="http://example.com")

    try:
        raise ValueError("example")
    except ValueError as exc:
        _ = await client.send_exception_async(exc, project="svc")

    assert "ValueError" in captured["json"]["traceback"]
    assert captured["json"]["message"] == "example"


def test_http_errors_propagate(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url: str, json: Dict[str, Any], timeout: int) -> StubResponse:  # type: ignore[override]
        return StubResponse(500, {"error": "fail"})

    monkeypatch.setattr("errorbrain.client.requests.post", fake_post)

    client = ErrorBrainClient(base_url="http://example.com")

    with pytest.raises(requests.HTTPError):
        _ = client.send_error(language="python", project="svc", message="fail")
