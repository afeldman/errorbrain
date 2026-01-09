# ErrorBrain Server Architecture

**Version:** v1 (implements spec/v1/)
**Framework:** FastAPI
**Python:** 3.11+

---

## Directory Structure

```
server/
├── src/
│   └── errorbrain_server/
│       ├── __init__.py
│       ├── main.py              # FastAPI app + routes
│       ├── cli.py               # CLI commands
│       ├── v1/
│       │   ├── __init__.py
│       │   ├── routes.py        # /v1/* endpoints
│       │   └── models.py        # Pydantic models from spec/v1/
│       ├── models/
│       │   ├── error_event.py   # ErrorEvent from spec/v1/
│       │   ├── source.py        # Source from spec/v1/
│       │   └── evidence.py      # Evidence from spec/v1/
│       ├── db/
│       │   ├── models.py        # SQLAlchemy ORM
│       │   └── client.py        # Database connection
│       └── llm/
│           └── client.py        # LLM integration
├── tests/
│   ├── test_api_v1.py
│   ├── test_models.py
│   └── conftest.py
├── docs/
│   ├── api.rst
│   └── conf.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── README.md
└── ARCHITECTURE.md
```

---

## API Routes

### v1 Endpoints (implements spec/v1/)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/errors` | Send error for analysis |
| GET | `/v1/errors/{id}` | Get error by ID |
| GET | `/v1/errors` | List errors (with filters) |
| GET | `/healthz` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |

---

## Key Design Principles

1. **Spec-Driven:** All models generated from spec/v1/ JSON Schemas
2. **Versioned API:** v1 namespace allows future v2/ without breaking changes
3. **Async:** Full FastAPI async/await support
4. **Type-Safe:** Pydantic validation on all requests
5. **Testable:** Comprehensive pytest suite

---

## Integration with SDKs

All SDKs post to the same endpoint:

```
POST {baseURL}/v1/errors
Content-Type: application/json

{
  "event": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-09T12:34:56Z",
    "source": {
      "language": "typescript",
      "name": "my-service",
      "version": "1.0.0"
    },
    "message": "Connection timeout",
    "stack_trace": "Error: timeout\n  at fetch()",
    "severity": "error",
    "metadata": {"user_id": "123"}
  },
  "store_in_vault": true
}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "explanation": "Connection timeout occurred due to slow network...",
  "saved_path": "/ErrorBrain/Errors/2024-01-09/550e8400-e29b-41d4-a716-446655440000.md"
}
```

---

## LLM Integration

Server analyzes errors using:

- **Local:** LM Studio on `http://localhost:1234`
- **Cloud:** OpenAI API (requires `OPENAI_API_KEY`)

Environment variables:

```bash
LLM_PROVIDER=lm_studio              # or 'openai'
LLM_BASE_URL=http://localhost:1234  # for LM Studio
OPENAI_API_KEY=sk-...               # for OpenAI
```

---

## Vault Integration

Errors stored in Obsidian vault:

```
<VAULT_PATH>/
├── ErrorBrain/
│   ├── Errors/
│   │   ├── 2024-01-09/
│   │   │   ├── 550e8400-e29b-41d4-a716-446655440000.md
│   │   │   └── ...
│   │   └── 2024-01-10/
│   │       └── ...
│   └── Stats/
│       └── overview.md
```

---

## Development

### Install Dependencies

```bash
cd server
uv sync
```

### Run Server

```bash
fastapi dev src/errorbrain_server/main.py
```

API available at: <http://localhost:8000>

### Run Tests

```bash
pytest tests/ -v
```

### Build Docker Image

```bash
docker build -t errorbrain-server:v1 .
docker run -p 8000:8000 errorbrain-server:v1
```

---

## Dependencies

From `pyproject.toml`:

- **fastapi** - Web framework
- **pydantic** - Data validation
- **sqlalchemy** - ORM
- **requests** - HTTP client
- **python-dotenv** - Environment variables
- **pytest** - Testing
- **pytest-cov** - Coverage reporting

---

## Testing

Test structure:

```python
# test_api_v1.py
def test_post_error():
    """Test POST /v1/errors endpoint"""

def test_get_error():
    """Test GET /v1/errors/{id}"""

def test_health_check():
    """Test GET /healthz"""
```

Run with coverage:

```bash
pytest tests/ --cov=src/errorbrain_server --cov-report=html
```

---

## Migration Notes

- **Before:** API code in `api/` directory
- **After:** Server code in `server/` directory
- **API Spec:** Moved from root-level schemas to `spec/v1/`
- **SDKs:** All SDKs updated to use `/v1/errors` endpoint
- **Compatibility:** Breaking change - requires SDK updates
