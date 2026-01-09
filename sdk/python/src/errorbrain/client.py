"""ErrorBrain Python SDK - Client for error tracking API.

This module provides a client for communicating with the ErrorBrain API
to submit errors for AI analysis and storage in Obsidian vault, using
spec/v1/error_event.schema.json payloads.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import requests
from pydantic import BaseModel, Field


class ErrorReport(BaseModel):
    """Error report model matching the API schema.

    Attributes:
        language: Programming language (e.g., python, go, terraform).
        project: Project or service name.
        message: Error message or exception message.
        traceback: Optional stack trace.
        tags: List of tags for categorization (e.g., ['prod', 'cron']).
        metadata: Additional metadata dictionary.
        store_in_vault: Whether to save to Obsidian vault.
    """

    language: str = Field(..., description="Programming language")
    project: str = Field(..., description="Project/service name")
    message: str = Field(..., description="Error message")
    traceback: str | None = Field(None, description="Optional stack trace")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")
    store_in_vault: bool = Field(True, description="Save to Obsidian vault")


class ErrorResponse(BaseModel):
    """Response from the ErrorBrain API.

    Attributes:
        id: Unique error identifier.
        project: Project name.
        language: Programming language.
        tags: List of tags.
        created_at: Timestamp of error creation.
        explanation: AI-generated explanation.
        saved_path: Path where error was saved (if applicable).
    """

    id: str
    project: str
    language: str
    tags: list[str]
    created_at: str
    explanation: str
    saved_path: str | None


class ErrorBrainClient:
    """Client for communicating with the ErrorBrain API.

    Attributes:
        base_url: The base URL of the ErrorBrain API server.
    """

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize the ErrorBrain client.

        Args:
            base_url: Base URL of the ErrorBrain API.
                Defaults to ERRORBRAIN_API_URL env var or http://localhost:8000.
        """
        self.base_url = (
            base_url or os.getenv("ERRORBRAIN_API_URL", "http://localhost:8000")
        ).rstrip("/")

    def _build_report(
        self,
        *,
        language: str,
        project: str,
        message: str,
        traceback: str | None,
        tags: list[str] | None,
        metadata: dict[str, Any] | None,
        store_in_vault: bool,
    ) -> ErrorReport:
        return ErrorReport(
            language=language,
            project=project,
            message=message,
            traceback=traceback,
            tags=tags or [],
            metadata=metadata,
            store_in_vault=store_in_vault,
        )

    def health_check(self) -> dict[str, Any]:
        """Check if the API is healthy.

        Returns:
            Health check response with status and configuration.

        Raises:
            requests.HTTPError: If the API is not reachable or returns an error.
        """
        response = requests.get(f"{self.base_url}/healthz", timeout=5)
        response.raise_for_status()
        return response.json()

    def send_error(
        self,
        language: str,
        project: str,
        message: str,
        traceback: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        store_in_vault: bool = True,
    ) -> ErrorResponse:
        """Send an error to ErrorBrain for analysis and storage.

        Args:
            language: Programming language (python, go, terraform).
            project: Project or service name.
            message: Error message.
            traceback: Optional stack trace.
            tags: Optional list of tags.
            metadata: Optional metadata dictionary.
            store_in_vault: Whether to save in Obsidian vault.

        Returns:
            ErrorResponse with explanation and saved path.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        report = ErrorReport(
            language=language,
            project=project,
            message=message,
            traceback=traceback,
            tags=tags or [],
            metadata=metadata,
            store_in_vault=store_in_vault,
        )

        response = requests.post(
            f"{self.base_url}/v1/errors",
            json=report.model_dump(),
            timeout=30,
        )
        response.raise_for_status()
        return ErrorResponse(**response.json())

    async def send_error_async(
        self,
        *,
        language: str,
        project: str,
        message: str,
        traceback: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        store_in_vault: bool = True,
    ) -> ErrorResponse:
        """Async Variante von send_error mit httpx.AsyncClient."""

        report = self._build_report(
            language=language,
            project=project,
            message=message,
            traceback=traceback,
            tags=tags,
            metadata=metadata,
            store_in_vault=store_in_vault,
        )

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v1/errors",
                json=report.model_dump(),
            )
            response.raise_for_status()
            return ErrorResponse(**response.json())

    def send_exception(
        self,
        exc: BaseException,
        project: str,
        language: str = "python",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        store_in_vault: bool = True,
    ) -> ErrorResponse:
        """Send a Python exception to ErrorBrain.

        Args:
            exc: The exception object.
            project: Project or service name.
            language: Programming language (default: python).
            tags: Optional list of tags.
            metadata: Optional metadata dictionary.
            store_in_vault: Whether to save in Obsidian vault.

        Returns:
            ErrorResponse with explanation and saved path.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        import traceback as tb

        traceback_str = "".join(tb.format_exception(type(exc), exc, exc.__traceback__))

        return self.send_error(
            language=language,
            project=project,
            message=str(exc),
            traceback=traceback_str,
            tags=tags,
            metadata=metadata,
            store_in_vault=store_in_vault,
        )

    async def send_exception_async(
        self,
        exc: BaseException,
        project: str,
        language: str = "python",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        store_in_vault: bool = True,
    ) -> ErrorResponse:
        """Async Fehlerversand für Exceptions."""

        import traceback as tb

        traceback_str = "".join(tb.format_exception(type(exc), exc, exc.__traceback__))

        return await self.send_error_async(
            language=language,
            project=project,
            message=str(exc),
            traceback=traceback_str,
            tags=tags,
            metadata=metadata,
            store_in_vault=store_in_vault,
        )


__all__ = [
    "ErrorBrainClient",
    "ErrorReport",
    "ErrorResponse",
]
