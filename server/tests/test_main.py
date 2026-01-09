"""Tests for ErrorBrain Server API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from errorbrain_server.main import app, build_error_prompt
from errorbrain_server.main import ErrorReport


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API.

    Returns:
        FastAPI test client.
    """
    return TestClient(app)


def test_healthz(client: TestClient) -> None:
    """Test health check endpoint.

    Args:
        client: FastAPI test client.
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "llm_provider" in data
    assert "obsidian_enabled" in data


def test_build_error_prompt() -> None:
    """Test error prompt building."""
    report = ErrorReport(
        language="python",
        project="test-service",
        message="Test error",
        traceback="Line 1\nLine 2",
        tags=["test", "prod"],
        metadata={"user_id": "123"},
    )

    prompt = build_error_prompt(report)

    assert "python" in prompt
    assert "test-service" in prompt
    assert "Test error" in prompt
    assert "Line 1" in prompt
    assert "test, prod" in prompt


def test_error_report_validation() -> None:
    """Test ErrorReport model validation."""
    # Valid report
    report = ErrorReport(
        language="go",
        project="payment-service",
        message="Connection failed",
    )
    assert report.language == "go"
    assert report.tags == []
    assert report.store_in_vault is True

    # Missing required fields should fail
    with pytest.raises(Exception):
        ErrorReport(language="python")  # type: ignore


@pytest.mark.asyncio
async def test_create_error_endpoint_structure(client: TestClient) -> None:
    """Test error creation endpoint structure (without actual LLM call).

    Args:
        client: FastAPI test client.
    """
    payload = {
        "language": "python",
        "project": "test-project",
        "message": "Test error message",
        "traceback": "Traceback...",
        "tags": ["test"],
        "store_in_vault": False,  # Don't actually save during tests
    }

    # Note: This will fail without a real LLM, but tests the structure
    response = client.post("/v1/errors", json=payload)

    # We expect either 200 (success) or 502 (LLM failure)
    assert response.status_code in [200, 502]

    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "explanation" in data
        assert data["project"] == "test-project"
        assert data["language"] == "python"
