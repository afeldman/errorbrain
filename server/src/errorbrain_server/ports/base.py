"""Ports: stable interfaces for the core system.

The core does not know HTTP or any framework. These ports define
how external systems interact with the core.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from errorbrain_server.core.models import ErrorEvent, Verdict


class IngestPort(ABC):
    """Port for ingesting error events and receiving verdicts.

    Implementers (API, CLI, queue consumers) use this port.
    The core produces Verdicts; the port is responsible for persistence.
    """

    @abstractmethod
    def ingest(self, event: ErrorEvent) -> Verdict:
        """Ingest an error event and return a verdict.

        Args:
            event: Normalized error event.

        Returns:
            Generated verdict.
        """
        ...


class QueryPort(ABC):
    """Port for retrieving stored verdicts."""

    @abstractmethod
    def get_verdict(self, event_id: str) -> Verdict | None:
        """Retrieve a verdict by event ID.

        Args:
            event_id: The event ID.

        Returns:
            Verdict if found, None otherwise.
        """
        ...
