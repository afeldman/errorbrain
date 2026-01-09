"""FastAPI application setup."""

from fastapi import FastAPI

app = FastAPI(
    title="ErrorBrain Server",
    description="Verdict-first analysis API (spec/v1)",
    version="0.2.0",
)
