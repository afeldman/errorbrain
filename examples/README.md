# ErrorBrain Examples

This directory contains comprehensive examples demonstrating how to use ErrorBrain SDKs.

## Prerequisites

1. **Start the ErrorBrain API Server**:
   ```bash
   task dev
   # or
   cd api && uv run errorbrain-server-dev
   ```

2. **Configure Environment** (optional):
   ```bash
   export ERRORBRAIN_LLM_PROVIDER=openai
   export ERRORBRAIN_LLM_MODEL=gpt-4
   export ERRORBRAIN_OBSIDIAN_PATH=~/vault/errors
   ```

## Python SDK Examples

**File**: `python_example.py`

**Run**:
```bash
task examples:python
# or
cd examples && python python_example.py
```

**Examples included**:
1. Basic error report with metadata
2. Automatic exception capture
3. Error with rich metadata
4. Batch error processing

## Go SDK Examples

**File**: `go_example.go`

**Run**:
```bash
task examples:go
# or
cd examples && go run go_example.go
```

**Examples included**:
1. Basic error report
2. Error with stack trace
3. Error with rich metadata
4. Simple convenience method

## Terraform Provider Examples

**File**: `terraform_example.tf`

**View**:
```bash
task examples:terraform
# or
cat examples/terraform_example.tf
```

**Examples included**:
1. Terraform apply failure
2. Plan validation error
3. State lock error
4. Provider authentication error
5. Dependency cycle error

## Integration Patterns

### Python Global Error Handler

```python
from errorbrain import ErrorBrainClient
import sys

client = ErrorBrainClient("http://localhost:8000")

def handle_exception(exc_type, exc_value, exc_traceback):
    if exc_type != KeyboardInterrupt:
        client.send_exception(
            exc=exc_value,
            language="python",
            project="my-app",
            tags=["uncaught"]
        )
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception
```

### Go Defer Pattern

```go
func ProcessRequest() error {
    client := errorbrain.NewClient("")
    defer func() {
        if r := recover(); r != nil {
            client.SendErrorSimple(
                "go",
                "my-service",
                fmt.Sprintf("Panic: %v", r),
                string(debug.Stack()),
            )
        }
    }()
    
    // Your code here
    return nil
}
```

## Documentation

- **Taskfile**: `task --list` for all available commands
- **API Server**: `../api/docs/_build/html/index.html`
- **Python SDK**: `../sdk-python/docs/_build/html/index.html`
- **Go SDK**: https://pkg.go.dev/github.com/afeldman/errorbrain/sdk-go
