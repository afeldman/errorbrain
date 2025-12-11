"""ErrorBrain Server - CLI commands.

This module provides command-line interface for ErrorBrain server operations.
Uses Typer for modern CLI with type hints.

Example:
    Run development server:
        errorbrain-server dev

    Run production server:
        errorbrain-server run

    Check API health:
        errorbrain-server health
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import uvicorn

app = typer.Typer(help="ErrorBrain Server CLI")


@app.command()
def run(
    host: str = typer.Option("0.0.0.0", help="Server host"),
    port: int = typer.Option(8000, help="Server port"),
    workers: int = typer.Option(1, help="Number of worker processes"),
) -> None:
    """Run production server.

    Args:
        host: Server bind address.
        port: Server port.
        workers: Number of worker processes.
    """
    typer.echo(f"🚀 Starting ErrorBrain server on {host}:{port}...")
    uvicorn.run(
        "errorbrain_server.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        log_level="info",
    )


@app.command()
def dev(
    host: str = typer.Option("127.0.0.1", help="Server host"),
    port: int = typer.Option(8000, help="Server port"),
) -> None:
    """Run development server with auto-reload.

    Args:
        host: Server bind address.
        port: Server port.
    """
    typer.echo(f"🔄 Starting ErrorBrain development server on {host}:{port}...")
    typer.echo("ℹ️  Auto-reload enabled. Press Ctrl+C to stop.")
    uvicorn.run(
        "errorbrain_server.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="debug",
    )


@app.command()
def health(api_url: str = typer.Option("http://localhost:8000", help="API base URL")) -> None:
    """Check API health.

    Args:
        api_url: Base URL of the ErrorBrain API.
    """
    import asyncio

    async def check_health() -> None:
        """Async health check."""
        import httpx

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{api_url}/healthz", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    typer.echo("✅ API is healthy")
                    typer.echo(f"  Status: {data.get('status')}")
                    typer.echo(f"  LLM Configured: {data.get('llm_configured')}")
                    typer.echo(f"  Vault Configured: {data.get('vault_configured')}")
                else:
                    typer.echo(f"❌ API returned {response.status_code}")
            except Exception as e:
                typer.echo(f"❌ Health check failed: {e}", err=True)

    asyncio.run(check_health())


@app.command()
def config(
    format: str = typer.Option("text", help="Output format (text, json)"),
) -> None:
    """Show current configuration.

    Args:
        format: Output format.
    """
    from decouple import config as get_env

    settings = {
        "APP_NAME": get_env("ERRORBRAIN_APP_NAME", default="errorbrain-server"),
        "LLM_PROVIDER": get_env("ERRORBRAIN_LLM_PROVIDER", default="openai"),
        "LLM_MODEL": get_env("ERRORBRAIN_LLM_MODEL", default="local-model"),
        "LLM_BASE_URL": get_env("ERRORBRAIN_LLM_BASE_URL", default="http://localhost:1234/v1"),
        "OBSIDIAN_ENABLED": get_env("ERRORBRAIN_OBSIDIAN_ENABLED", default="true"),
        "OBSIDIAN_PATH": get_env("ERRORBRAIN_OBSIDIAN_PATH", default="/vault/errors"),
    }

    if format == "json":
        import json
        typer.echo(json.dumps(settings, indent=2))
    else:
        typer.echo("📋 ErrorBrain Configuration")
        typer.echo("=" * 50)
        for key, value in settings.items():
            typer.echo(f"  {key}: {value}")


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
