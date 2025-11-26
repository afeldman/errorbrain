#!/usr/bin/env python3
"""ErrorBrain Python SDK - Example Usage.

This example demonstrates how to use the ErrorBrain Python SDK
to send errors to the ErrorBrain API for AI analysis.
"""

import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk-python" / "src"))

from errorbrain import ErrorBrainClient


def example_basic() -> None:
    """Example 1: Basic error report."""
    print("=" * 60)
    print("Example 1: Basic Error Report")
    print("=" * 60)
    
    client = ErrorBrainClient("http://localhost:8000")
    
    # Health check
    if not client.health_check():
        print("❌ ErrorBrain API is not available")
        return
    
    print("✓ API is healthy\n")
    
    # Send error
    response = client.send_error(
        language="python",
        project="billing-service",
        message="Database connection timeout",
        traceback="Traceback (most recent call last):\n  File 'db.py', line 42\n    conn = pool.get_connection()\n  ConnectionTimeout: timeout after 30s",
        tags=["prod", "database", "critical"],
        metadata={"user_id": "12345", "request_id": "abc-def"},
    )
    
    print(f"Error ID: {response.id}")
    print(f"\nAI Explanation:\n{response.explanation}")
    if response.saved_path:
        print(f"\nSaved to: {response.saved_path}")
    print()


def example_exception() -> None:
    """Example 2: Capture exceptions automatically."""
    print("=" * 60)
    print("Example 2: Exception Handling")
    print("=" * 60)
    
    client = ErrorBrainClient("http://localhost:8000")
    
    try:
        # Provoke an error
        result = 10 / 0  # noqa: F841
    except Exception as exc:
        print(f"Caught exception: {exc}\n")
        
        response = client.send_exception(
            exc=exc,
            language="python",
            project="data-pipeline",
            tags=["cron", "prod"],
        )
        
        print(f"Error ID: {response.id}")
        print(f"\nAI Explanation:\n{response.explanation}")
    print()


def example_with_metadata() -> None:
    """Example 3: Error with rich metadata."""
    print("=" * 60)
    print("Example 3: Error with Rich Metadata")
    print("=" * 60)
    
    client = ErrorBrainClient("http://localhost:8000")
    
    response = client.send_error(
        language="python",
        project="api-gateway",
        message="Rate limit exceeded",
        tags=["api", "rate-limit", "production"],
        metadata={
            "endpoint": "/api/v1/users",
            "method": "POST",
            "client_ip": "203.0.113.42",
            "requests_per_minute": 1200,
            "limit": 1000,
            "user_id": "user_12345",
        },
        store_in_vault=True,
    )
    
    print(f"Error ID: {response.id}")
    print(f"Tags: {', '.join(response.tags)}")
    print(f"\nAI Explanation:\n{response.explanation}")
    print()


def example_batch() -> None:
    """Example 4: Batch error processing."""
    print("=" * 60)
    print("Example 4: Batch Error Processing")
    print("=" * 60)
    
    client = ErrorBrainClient("http://localhost:8000")
    
    errors = [
        {"message": "Redis connection refused", "tags": ["redis", "cache"]},
        {"message": "JWT token expired", "tags": ["auth", "security"]},
        {"message": "S3 upload failed", "tags": ["storage", "aws"]},
    ]
    
    print(f"Processing {len(errors)} errors...\n")
    
    for idx, error in enumerate(errors, 1):
        response = client.send_error(
            language="python",
            project="microservices",
            message=error["message"],
            tags=error["tags"],
        )
        print(f"{idx}. {error['message']} → ID: {response.id}")
    print()


def main() -> None:
    """Run all examples."""
    print("\n" + "=" * 60)
    print("ErrorBrain Python SDK - Examples")
    print("=" * 60)
    print()
    print("Make sure the ErrorBrain API is running:")
    print("  task dev")
    print("  # or: cd api && uv run errorbrain-server-dev")
    print()

    try:
        example_basic()
        example_exception()
        example_with_metadata()
        example_batch()

        print("=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        print()

    except Exception as exc:
        print(f"\n❌ Error running examples: {exc}")
        print("Make sure the ErrorBrain API is running on http://localhost:8000")
        sys.exit(1)


if __name__ == "__main__":
    main()
