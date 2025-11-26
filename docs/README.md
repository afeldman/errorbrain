# ErrorBrain Documentation

Complete documentation for ErrorBrain - an error tracking system with AI analysis.

## Documentation Structure

### Python Documentation (Sphinx)

- **API Server**: `api/docs/`
- **Python SDK**: `sdk-python/docs/`

Both use Sphinx with Google Style docstrings and the Read the Docs theme.

### Go Documentation (godoc)

- **Go SDK**: `sdk-go/`

Uses standard Go documentation format (godoc).

## Building Documentation

### Build All Docs

```bash
make docs
```

This will:

- Build Sphinx HTML docs for API Server → `api/docs/_build/html/`
- Build Sphinx HTML docs for Python SDK → `sdk-python/docs/_build/html/`
- Start godoc server for Go SDK → http://localhost:6060

### Build Individual Docs

#### API Server (Sphinx)

```bash
cd api/docs
uv run sphinx-build -b html . _build/html
open _build/html/index.html
```

#### Python SDK (Sphinx)

```bash
cd sdk-python/docs
uv run sphinx-build -b html . _build/html
open _build/html/index.html
```

#### Go SDK (godoc)

```bash
cd sdk-go
godoc -http=:6060
# Open: http://localhost:6060/pkg/github.com/afeldman/errorbrain/sdk-go/
```

Or view online (after push):

```bash
open https://pkg.go.dev/github.com/afeldman/errorbrain/sdk-go
```

## Documentation Standards

### Python (Google Style)

All Python code uses Google Style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is negative.
    """
```

### Go (godoc)

All Go code uses godoc format:

```go
// FunctionName does something important.
//
// It takes param1 as input and returns result.
// Returns an error if operation fails.
func FunctionName(param1 string) (string, error) {
    // ...
}
```

## Sphinx Configuration

Both Python projects use:

- **Theme**: sphinx_rtd_theme (Read the Docs)
- **Extensions**: autodoc, napoleon, viewcode, intersphinx
- **Napoleon**: Configured for Google Style docstrings
- **Autodoc**: Automatic API documentation generation

## Viewing Documentation

### Local Development

After building, open the HTML files:

```bash
# API Server docs
open api/docs/_build/html/index.html

# Python SDK docs
open sdk-python/docs/_build/html/index.html

# Go SDK docs (via godoc server)
godoc -http=:6060
open http://localhost:6060/pkg/github.com/afeldman/errorbrain/sdk-go/
```

### Online (GitHub Pages - Future)

Documentation can be published to GitHub Pages:

```bash
# Build all docs
make docs

# Deploy to gh-pages branch
# (requires gh-pages setup)
```

## Updating Documentation

### Python

1. Add/update Google Style docstrings in code
2. Rebuild Sphinx docs: `cd api/docs && make html`
3. Check output: `open _build/html/index.html`

### Go

1. Add/update godoc comments in code
2. View with: `godoc -http=:6060`
3. Or push to GitHub and view on pkg.go.dev

## Requirements

### Python Documentation

Install dev dependencies with Sphinx:

```bash
cd api && uv sync --all-extras
cd sdk-python && uv sync --all-extras
```

Includes:

- `sphinx>=7.2.0`
- `sphinx-rtd-theme>=2.0.0`

### Go Documentation

Install godoc:

```bash
go install golang.org/x/tools/cmd/godoc@latest
```

Or use online: https://pkg.go.dev
