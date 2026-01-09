"""Ingest pipeline: normalize ErrorEvent from spec into core models."""

from __future__ import annotations

from datetime import datetime

from errorbrain_server.core.models import Evidence, ErrorEvent, Source


def ingest(
    event_id: str,
    timestamp: str,
    source: dict,
    message: str,
    stack_trace: str | None = None,
    error_type: str | None = None,
    severity: str | None = None,
    metadata: dict | None = None,
    evidence: list | None = None,
) -> ErrorEvent:
    """Normalize a raw error event into an internal ErrorEvent.

    This module is the only place that understands spec/v1/error_event
    at the core level. It converts incoming data into our internal models.

    Args:
        event_id: UUID string.
        timestamp: ISO 8601 timestamp string.
        source: Source dict with 'language', 'name', etc.
        message: Error message.
        stack_trace: Optional stack trace.
        error_type: Optional error type/class name.
        severity: Optional severity level.
        metadata: Optional metadata dict.
        evidence: Optional evidence list.

    Returns:
        Normalized ErrorEvent model.

    Raises:
        ValueError: If normalization fails.
    """
    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid timestamp: {timestamp}") from exc

    src = Source(
        language=source.get("language"),
        name=source.get("name"),
        version=source.get("version"),
        environment=source.get("environment"),
        hostname=source.get("hostname"),
        tags=source.get("tags"),
    )

    evidence_list = None
    if evidence:
        evidence_list = [
            Evidence(
                type=e.get("type"),
                data=e.get("data", {}),
                timestamp=datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
                if e.get("timestamp")
                else None,
            )
            for e in evidence
        ]

    return ErrorEvent(
        id=event_id,
        timestamp=ts,
        source=src,
        message=message,
        stack_trace=stack_trace,
        error_type=error_type,
        severity=severity,
        metadata=metadata,
        evidence=evidence_list,
    )
