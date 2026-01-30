# decorators.py
from __future__ import annotations

from functools import wraps
from typing import Callable, Any

from .context import ErrorContext


def errorbrain(**context_kwargs):
    """
    Decorator wrapper around ErrorContext.

    Usage:
        @errorbrain(
            source=Source(...),
            severity="high",
        )
        def my_function():
            ...
    """

    def decorator(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with ErrorContext(**context_kwargs):
                return fn(*args, **kwargs)

        return wrapper

    return decorator
