"""ErrorBrain Server - FastAPI application for error tracking and AI analysis.

This module provides a REST API for capturing errors from applications,
analyzing them with LLM (Local or Cloud), and storing them in an Obsidian vault.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from any_llm import completion
from decouple import config
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ============================================================
# Configuration
# ============================================================

APP_NAME = config("ERRORBRAIN_APP_NAME", default="errorbrain-server")

# LLM Configuration (LM Studio or Cloud)
LLM_PROVIDER = config("ERRORBRAIN_LLM_PROVIDER", default="openai")
LLM_MODEL = config("ERRORBRAIN_LLM_MODEL", default="local-model")
LLM_BASE_URL = config("ERRORBRAIN_LLM_BASE_URL", default="http://localhost:1234/v1")
LLM_API_KEY = config("ERRORBRAIN_LLM_API_KEY", default="lm-studio")

# Obsidian / Second Brain Configuration
OBSIDIAN_ENABLED: bool = config("ERRORBRAIN_OBSIDIAN_ENABLED", default="true").lower() == "true"
OBSIDIAN_PATH = Path(
    config("ERRORBRAIN_OBSIDIAN_PATH", default="/Users/anton.feldmann/lynq/errors")
).expanduser()
if OBSIDIAN_ENABLED:
    OBSIDIAN_PATH.mkdir(parents=True, exist_ok=True)

# ============================================================
# Pydantic Models
# ============================================================


class ErrorReport(BaseModel):
    """Error report submitted by client SDKs.

    Attributes:
        language: Programming language (e.g., python, go, terraform).
        project: Service or project name (e.g., billing-service).
        message: Error message or exception message.
        traceback: Optional stack trace or detailed error output.
        tags: List of tags for categorization (e.g., ['cron', 'prod']).
        metadata: Additional context like user_id, request_id, version.
        store_in_vault: Whether to save the error as Markdown in Obsidian.
    """

    language: str = Field(..., description="Programming language (e.g., python, go)")
    project: str = Field(..., description="Service/project name")
    message: str = Field(..., description="Error message or exception")
    traceback: str | None = Field(None, description="Optional stack trace")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")
    store_in_vault: bool = Field(True, description="Save to Obsidian vault")


class ErrorResponse(BaseModel):
    """Response after error analysis.

    Attributes:
        id: Unique error identifier.
        project: Project name.
        language: Programming language.
        tags: List of tags.
        created_at: Timestamp of error creation.
        explanation: AI-generated explanation of the error.
        saved_path: Path where the error was saved (if applicable).
    """

    id: str
    project: str
    language: str
    tags: list[str]
    created_at: datetime
    explanation: str
    saved_path: str | None


# ============================================================
# LLM Helper Functions
# ============================================================


def build_error_prompt(report: ErrorReport) -> str:
    """Build a prompt for the LLM to analyze the error.

    Args:
        report: The error report containing error details.

    Returns:
        A formatted prompt string for LLM analysis.
    """
    tb = report.traceback or "(no traceback provided)"
    tags = ", ".join(report.tags) if report.tags else "-"
    meta = report.metadata or {}

    return (
        "You are a Senior Software Engineer & Debugging Expert.\n"
        "Analyze the following error, explain it clearly, "
        "and provide concrete next steps to fix it.\n\n"
        f"Language: {report.language}\n"
        f"Project: {report.project}\n"
        f"Tags: {tags}\n"
        f"Metadata: {meta}\n\n"
        f"Error Message:\n{report.message}\n\n"
        f"Traceback:\n{tb}\n"
    )


def explain_error_with_llm(report: ErrorReport) -> str:
    """Explain an error using an LLM.

    Args:
        report: The error report to analyze.

    Returns:
        The LLM's explanation of the error.

    Raises:
        RuntimeError: If the LLM call fails.
    """
    prompt = build_error_prompt(report)

    try:
        response = completion(
            model=LLM_MODEL,
            provider=LLM_PROVIDER,
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful, precise debugging assistant "
                        "for backend and DevOps errors."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e

    return response.choices[0].message.content


# ============================================================
# Obsidian / Second Brain - Markdown Storage
# ============================================================


def save_markdown_to_obsidian(
    report: ErrorReport,
    explanation: str,
    err_id: str,
) -> str:
    """Save error report as Markdown in Obsidian vault.

    Args:
        report: The error report to save.
        explanation: The LLM-generated explanation.
        err_id: Unique identifier for the error.

    Returns:
        The file path where the error was saved.
    """
    project_slug = report.project.replace(" ", "-").lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    file_name = f"{timestamp}-{project_slug}-{err_id}.md"
    file_path = OBSIDIAN_PATH / file_name

    content = f"""---
id: {err_id}
project: {report.project}
language: {report.language}
tags: {report.tags}
created_at: {datetime.utcnow().isoformat()}Z
---

# {report.message}

## Context

- Project: **{report.project}**
- Language: **{report.language}**
- Tags: {", ".join(report.tags) if report.tags else "-"}

## Error Message

```text
{report.message}
```

## Traceback

```text
{report.traceback or "no traceback provided"}
```

## Explanation (ErrorBrain)

{explanation}
"""

    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="ErrorBrain Server",
    description="Error tracking and AI analysis API",
    version="0.1.0",
)


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        Dictionary containing server status and configuration.
    """
    return {
        "status": "ok",
        "app": APP_NAME,
        "llm_provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "llm_base_url": LLM_BASE_URL,
        "obsidian_enabled": OBSIDIAN_ENABLED,
        "obsidian_path": str(OBSIDIAN_PATH),
    }


@app.post("/v1/errors", response_model=ErrorResponse)
def create_error(report: ErrorReport) -> ErrorResponse:
    """Process and analyze an error report.

    Args:
        report: The error report submitted by client SDK.

    Returns:
        ErrorResponse containing analysis and storage information.

    Raises:
        HTTPException: If LLM analysis fails (502).
    """
    err_id = str(uuid4())

    try:
        explanation = explain_error_with_llm(report)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    saved_path: str | None = None
    if OBSIDIAN_ENABLED and report.store_in_vault:
        try:
            saved_path = save_markdown_to_obsidian(report, explanation, err_id)
        except Exception:
            saved_path = None

    return ErrorResponse(
        id=err_id,
        project=report.project,
        language=report.language,
        tags=report.tags,
        created_at=datetime.utcnow(),
        explanation=explanation,
        saved_path=saved_path,
    )


# ============================================================
# Server Entry Points
# ============================================================


def run_dev() -> None:
    """Run development server with auto-reload."""
    import uvicorn

    uvicorn.run("errorbrain_server.main:app", host="127.0.0.1", port=8000, reload=True)


def run() -> None:
    """Run production server."""
    import uvicorn

    uvicorn.run("errorbrain_server.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
