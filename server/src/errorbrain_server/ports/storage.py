"""In-memory storage implementation of ports.

For production, replace with database backend.
"""

from __future__ import annotations

from errorbrain_server.core.models import ErrorEvent, Verdict
from errorbrain_server.core import analyze
from errorbrain_server.ports.base import IngestPort, QueryPort


class InMemoryStorage(IngestPort, QueryPort):
    """Simple in-memory storage for events and verdicts."""

    def __init__(self) -> None:
        self._events: dict[str, ErrorEvent] = {}
        self._verdicts: dict[str, Verdict] = {}

    def ingest(self, event: ErrorEvent) -> Verdict:
        """Ingest event, generate verdict, store both."""
        self._events[event.id] = event
        verdict = analyze(event)
        self._verdicts[event.id] = verdict
        return verdict

    def get_verdict(self, event_id: str) -> Verdict | None:
        """Retrieve stored verdict."""
        return self._verdicts.get(event_id)
