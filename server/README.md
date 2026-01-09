# ErrorBrain API Server

FastAPI server for error tracking, AI analysis, and Obsidian vault storage.

## Features

- **FastAPI** REST API
- **LLM Integration** via any-llm (supports LM Studio, OpenAI, etc.)
- **Obsidian Storage** - Save errors as searchable Markdown
- **Type-Safe** - Full Pydantic models
- **Tested** - Unit tests with pytest
- **Linted** - Ruff + mypy

## Project Structure

```
api/
├── src/
│   └── errorbrain_server/
│       ├── __init__.py
│       └── main.py          # FastAPI app
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   └── test_main.py         # API tests
├── pyproject.toml           # Dependencies & config
└── .env.example             # Environment template
```

## Installation

```bash
# Install with all development dependencies
uv sync --all-extras
```

## Configuration

Create `.env` file:

```bash
# App Name
ERRORBRAIN_APP_NAME=errorbrain-server

# LM Studio Configuration (local)
ERRORBRAIN_LLM_PROVIDER=openai
ERRORBRAIN_LLM_MODEL=local-model
ERRORBRAIN_LLM_BASE_URL=http://localhost:1234/v1
ERRORBRAIN_LLM_API_KEY=lm-studio

# Obsidian Vault Path
ERRORBRAIN_OBSIDIAN_ENABLED=true
ERRORBRAIN_OBSIDIAN_PATH=/Users/anton.feldmann/lynq/errors
```

## Running

### Development Mode (with auto-reload)

```bash
uv run errorbrain-server-dev
```

### Production Mode

```bash
uv run errorbrain-server
```

Server runs on `http://localhost:8000`

## API Endpoints

### `GET /healthz`

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "app": "errorbrain-server",
  "llm_provider": "openai",
  "model": "local-model",
  "llm_base_url": "http://localhost:1234/v1",
  "obsidian_enabled": true,
  "obsidian_path": "/path/to/vault/errors"
}
```

### `POST /v1/errors`

Submit an error for AI analysis.

**Request Body:**

```json
{
  "language": "python",
  "project": "billing-service",
  "message": "Connection timeout",
  "traceback": "Traceback...",
  "tags": ["prod", "database"],
  "metadata": {
    "user_id": "123",
    "request_id": "abc"
  },
  "store_in_vault": true
}
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project": "billing-service",
  "language": "python",
  "tags": ["prod", "database"],
  "created_at": "2024-11-26T10:30:00Z",
  "explanation": "This error occurs when...",
  "saved_path": "/path/to/vault/errors/20241126-103000-billing-service-550e8400.md"
}
```

## Development

### Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ -v --cov

# Coverage report
uv run pytest tests/ --cov --cov-report=html
open htmlcov/index.html
```

### Linting

```bash
# Check code
uv run ruff check src/

# Fix issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/
```

### Type Checking

```bash
uv run mypy src/
```

### All Checks

```bash
# From project root
make check-all
```

## Documentation

Code follows **Google Style** docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When parameter is invalid.
    """
    ...
```

## Dependencies

### Core

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-decouple` - Environment config
- `any-llm-sdk` - LLM integration

### Development

- `pytest` - Testing
- `pytest-cov` - Coverage
- `pytest-asyncio` - Async tests
- `httpx` - HTTP client for tests
- `ruff` - Linting & formatting
- `mypy` - Type checking

## License

MIT - See main repository LICENSE file.
