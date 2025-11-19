from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from typing import Any, List, Optional

from decouple import config
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from any_llm import completion


# ============================================================
# Konfiguration
# ============================================================

APP_NAME = config("ERRORBRAIN_APP_NAME", default="errorbrain-api")

# any-llm: Provider & Model
LLM_PROVIDER = config("ERRORBRAIN_LLM_PROVIDER", default="openai")
LLM_MODEL = config("ERRORBRAIN_LLM_MODEL", default="gpt-4.1-mini")

# Obsidian / Second Brain
OBSIDIAN_ENABLED: bool = config("ERRORBRAIN_OBSIDIAN_ENABLED", default="true").lower() == "true"
OBSIDIAN_PATH = Path(config("ERRORBRAIN_OBSIDIAN_PATH", default="data/errors")).expanduser()
if OBSIDIAN_ENABLED:
    OBSIDIAN_PATH.mkdir(parents=True, exist_ok=True)

# ============================================================
# Pydantic Models
# ============================================================

class ErrorReport(BaseModel):
    language: str = Field(..., description="z.B. python, go, terraform")
    project: str = Field(..., description="Service/Projekt-Name, z.B. billing-service")
    message: str = Field(..., description="Fehlermeldung / Exception-Message")
    traceback: Optional[str] = Field(None, description="Optionaler Stacktrace")
    tags: List[str] = Field(default_factory=list, description="z.B. ['cron', 'prod']")
    metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Beliebige Zusatzinfos, z.B. user_id, request_id, version",
    )
    store_in_vault: bool = Field(
        default=True,
        description="Ob der Fehler als Markdown im Obsidian-Vault gespeichert werden soll.",
    )


class ErrorResponse(BaseModel):
    id: str
    project: str
    language: str
    tags: List[str]
    created_at: datetime
    explanation: str
    saved_path: Optional[str]


# ============================================================
# LLM-Hilfsfunktion mit any-llm
# ============================================================

def build_error_prompt(report: ErrorReport) -> str:
    tb = report.traceback or "(kein Traceback übermittelt)"
    tags = ", ".join(report.tags) if report.tags else "-"
    meta = report.metadata or {}

    return (
        "Du bist ein Senior Software Engineer & Debugging-Experte.\n"
        "Analysiere den folgenden Fehler, erkläre ihn verständlich "
        "und gib konkrete nächste Schritte zur Behebung.\n\n"
        f"Sprache: {report.language}\n"
        f"Projekt: {report.project}\n"
        f"Tags: {tags}\n"
        f"Metadata: {meta}\n\n"
        f"Fehlermeldung:\n{report.message}\n\n"
        f"Traceback:\n{tb}\n"
    )


def explain_error_with_llm(report: ErrorReport) -> str:
    prompt = build_error_prompt(report)

    try:
        response = completion(
            model=LLM_MODEL,
            provider=LLM_PROVIDER,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein hilfsbereiter, präziser Debugging-Assistent "
                        "für Backend- und DevOps-Fehler."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as e:
        raise RuntimeError(f"LLM-Call fehlgeschlagen: {e}") from e

    return response.choices[0].message.content


# ============================================================
# Obsidian / Second Brain – Markdown speichern
# ============================================================

def save_markdown_to_obsidian(
    report: ErrorReport,
    explanation: str,
    err_id: str,
) -> str:
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

## Kontext

- Projekt: **{report.project}**
- Sprache: **{report.language}**
- Tags: {", ".join(report.tags) if report.tags else "-"}

## Fehlermeldung

```text
{report.message}
```

## Traceback

```text
{report.traceback or "kein Traceback übermittelt"}
```

## Erklärung (ErrorBrain)

{explanation}
"""

    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


# ============================================================
# FastAPI App + Endpoints
# ============================================================

app = FastAPI(title=APP_NAME, version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    return {
        "status": "ok",
        "app": APP_NAME,
        "llm_provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "obsidian_enabled": OBSIDIAN_ENABLED,
    }


@app.post("/v1/errors", response_model=ErrorResponse)
def create_error(report: ErrorReport) -> ErrorResponse:
    err_id = str(uuid4())

    try:
        explanation = explain_error_with_llm(report)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    saved_path: Optional[str] = None
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

def run_dev():
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)

def run():
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    run()
