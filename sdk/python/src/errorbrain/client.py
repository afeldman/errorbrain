"""ErrorBrain Python SDK - spec-first client.

Provides thin, typed access to the ErrorBrain server for:
- Health checks
- Verdict retrieval (/analysis)
- Explanation retrieval (/explain)
- Optional event submission (/events) using spec/v1/error_event
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import requests

from errorbrain.model import ErrorEvent, Verdict, ExplainResponse

class ErrorBrainClient:
    """Thin HTTP client for the ErrorBrain API (spec/v1)."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (
            base_url or os.getenv("ERRORBRAIN_API_URL", "http://localhost:8000")
        ).rstrip("/")

    def health_check(self) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/healthz", timeout=5)
        response.raise_for_status()
        return response.json()

    def submit_event(self, event: ErrorEvent) -> Verdict:
        response = requests.post(
            f"{self.base_url}/events",
            json=event.model_dump(mode="json"),
            timeout=10,
        )
        response.raise_for_status()
        return Verdict.model_validate(response.json())

    async def submit_event_async(self, event: ErrorEvent) -> Verdict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{self.base_url}/events",
                json=event.model_dump(mode="json"),
            )
            response.raise_for_status()
            return Verdict.model_validate(response.json())

    def get_verdict(self, event_id: str) -> Verdict:
        response = requests.get(f"{self.base_url}/analysis/{event_id}", timeout=5)
        response.raise_for_status()
        return Verdict.model_validate(response.json())

    def get_analysis(self, event_id: str) -> Verdict:
        return self.get_verdict(event_id)

    def explain(self, event_id: str) -> ExplainResponse:
        response = requests.get(f"{self.base_url}/explain/{event_id}", timeout=5)
        response.raise_for_status()
        return ExplainResponse.model_validate(response.json())

    async def get_verdict_async(self, event_id: str) -> Verdict:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{self.base_url}/analysis/{event_id}")
            response.raise_for_status()
            return Verdict.model_validate(response.json())

    async def explain_async(self, event_id: str) -> ExplainResponse:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{self.base_url}/explain/{event_id}")
            response.raise_for_status()
            return ExplainResponse.model_validate(response.json())

    def _normalize_context(context: dict[str, Any] | None) -> dict[str, Any]:
        if not context:
            return {}

        annotation = context.pop("_errorbrain_annotation", None)

        return {
            "context": context,
            "annotations": annotation,
        }

def send_to_errorbrain(event):
    client = ErrorBrainClient()
    return client.verdict(event)

__all__ = [
    "ErrorBrainClient",
    "ErrorEvent",
    "Verdict",
    "ExplainResponse",
    "Source",
    "Evidence",
    "Impact",
    "Hypothesis",
    "RecommendedAction",
]
