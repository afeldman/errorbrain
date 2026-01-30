"""Ingest event route: POST /events.

This is a thin adapter:
1. Validate incoming JSON against spec
2. Map to core model
3. Call port
4. Map result back to spec
5. Return
"""

from fastapi import HTTPException

from errorbrain_server.api.app import app
from errorbrain_server.api.mapping import spec_event_to_core, core_verdict_to_spec
from errorbrain_server.api.spec_models import SpecErrorEvent, SpecVerdict
from errorbrain_server.ports import IngestPort


# This will be injected by the main app setup
_ingest_port: IngestPort | None = None


def set_ingest_port(port: IngestPort) -> None:
    """Inject the ingest port."""
    global _ingest_port
    _ingest_port = port


@app.post("/events", response_model=SpecVerdict)
def ingest_event(spec_event: SpecErrorEvent) -> SpecVerdict:
    """Ingest an error event from the spec and return verdict.

    This route is a pure adapter:s
    - Pydantic automatically validates against spec model
    - Convert to core model
    - Call the core (via port)
    - Convert back to spec
    - Return
    """
    if _ingest_port is None:
        raise HTTPException(status_code=500, detail="Ingest port not initialized")

    # Map spec → core
    core_event = spec_event_to_core(spec_event)

    # Call core via port
    core_verdict = _ingest_port.ingest(core_event)

    # Map core → spec
    spec_verdict = core_verdict_to_spec(core_verdict)

    return spec_verdict
