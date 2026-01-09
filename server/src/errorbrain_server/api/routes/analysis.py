"""Analysis/verdict retrieval route: GET /analysis/{event_id}."""

from fastapi import HTTPException

from errorbrain_server.api.app import app
from errorbrain_server.api.mapping import core_verdict_to_spec
from errorbrain_server.api.spec_models import SpecVerdict
from errorbrain_server.ports import QueryPort


# This will be injected by the main app setup
_query_port: QueryPort | None = None


def set_query_port(port: QueryPort) -> None:
    """Inject the query port."""
    global _query_port
    _query_port = port


@app.get("/analysis/{event_id}", response_model=SpecVerdict)
def get_analysis(event_id: str) -> SpecVerdict:
    """Retrieve the verdict for an event."""
    if _query_port is None:
        raise HTTPException(status_code=500, detail="Query port not initialized")

    verdict = _query_port.get_verdict(event_id)
    if verdict is None:
        raise HTTPException(status_code=404, detail="Verdict not found")

    spec_verdict = core_verdict_to_spec(verdict)
    return spec_verdict
