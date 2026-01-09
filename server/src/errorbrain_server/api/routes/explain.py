"""Explain route: GET /explain/{event_id}.

Provides human-readable explanation derived from the canonical verdict.
"""

from fastapi import HTTPException

from errorbrain_server.api.app import app
from errorbrain_server.api.mapping import core_verdict_to_explain
from errorbrain_server.api.spec_models import SpecExplainResponse
from errorbrain_server.ports import QueryPort


# This will be injected by the main app setup
_query_port: QueryPort | None = None


def set_query_port(port: QueryPort) -> None:
    """Inject the query port."""
    global _query_port
    _query_port = port


@app.get("/explain/{event_id}", response_model=SpecExplainResponse)
def explain(event_id: str) -> SpecExplainResponse:
    """Get human-readable explanation for an error.

    Explanation is always derived from the verdict (the source of truth),
    never computed separately.
    """
    if _query_port is None:
        raise HTTPException(status_code=500, detail="Query port not initialized")

    verdict = _query_port.get_verdict(event_id)
    if verdict is None:
        raise HTTPException(status_code=404, detail="Verdict not found")

    explain = core_verdict_to_explain(verdict)
    return explain
