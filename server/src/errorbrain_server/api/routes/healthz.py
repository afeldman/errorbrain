"""Health check route."""

from typing import Any

from errorbrain_server.api.app import app


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "spec_version": "v1",
        "schemas": ["error_event", "verdict"],
    }
