# context.py
from __future__ import annotations

import traceback
from datetime import datetime, timezone
from uuid import uuid4
from types import TracebackType
from typing import Optional, Type, Any

from .client import ErrorBrainClient
from .model import ErrorEvent, Annotation

ErrorEvent.model_rebuild()

class ErrorContext:
    """
    Controls execution flow and captures exceptions.

    Usage:
        with ErrorContext(source=Source(...), severity="high"):
            do_something()
    """

    def __init__(
        self,
        *,
        source,
        severity: str | None = None,
        annotations: list[Annotation] | None = None,
        client: ErrorBrainClient | None = None,
        reraise: bool = True,
    ):
        self.source = source
        self.severity = severity
        self.annotations = annotations or []
        self.client = client or ErrorBrainClient()
        self.reraise = reraise
        self.last_event_id: str | None = None

    def __enter__(self) -> "ErrorContext":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> bool:
        if exc is None:
            return False

        event = ErrorEvent(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            source=self.source,
            message=str(exc),
            stack_trace="".join(
                traceback.format_exception(exc_type, exc, tb)
            ),
            error_type=exc_type.__name__ if exc_type else None,
            severity=self.severity,
        )

        event_id = event.id

        try:
            verdict = self.client.submit_event(event)
            self.last_event_id = verdict.event_id
        except Exception as send_error:
            print("⚠️ ErrorBrain submission failed:")
            print(send_error)
            self.last_event_id = event_id

        return not self.reraise
