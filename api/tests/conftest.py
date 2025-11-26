"""Test configuration and fixtures."""

import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up test environment variables.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("ERRORBRAIN_OBSIDIAN_ENABLED", "false")
    monkeypatch.setenv("ERRORBRAIN_LLM_PROVIDER", "openai")
    monkeypatch.setenv("ERRORBRAIN_LLM_MODEL", "test-model")
