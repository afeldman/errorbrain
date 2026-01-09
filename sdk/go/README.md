# ErrorBrain Go SDK

Go client library for the ErrorBrain API.

**Spec-driven:** This SDK strictly follows [spec/error_event.schema.json](../../spec/error_event.schema.json) to ensure consistency across all language SDKs.

## Installation

```bash
go get github.com/afeldman/errorbrain/sdk/go
```

## Usage

```go
package main

import (
 "fmt"
 "log"

 errorbrain "github.com/afeldman/errorbrain/sdk/go"
)

func main() {
 // Create client (uses ERRORBRAIN_API_URL env var or defaults to localhost:8000)
 client := errorbrain.NewClient("")

 // Check health
 health, err := client.HealthCheck()
 if err != nil {
  log.Fatal(err)
 }
 fmt.Printf("API Status: %v\n", health.Status)

 // Send an error
 report := &errorbrain.ErrorReport{
  Language:     "go",
  Project:      "my-service",
  Message:      "database connection failed",
  Traceback:    "panic: runtime error...",
  Tags:         []string{"prod", "database"},
  StoreInVault: true,
 }

 response, err := client.SendError(report)
 if err != nil {
  log.Fatal(err)
 }

 fmt.Printf("Error ID: %s\n", response.ID)
 fmt.Printf("Explanation: %s\n", response.Explanation)
 if response.SavedPath != nil {
  fmt.Printf("Saved to: %s\n", *response.SavedPath)
 }
}
```

## API Reference

### `NewClient(baseURL string) *Client`

Creates a new ErrorBrain client.

- If `baseURL` is empty, uses `ERRORBRAIN_API_URL` env var or defaults to `http://localhost:8000`
- Strips trailing slashes from the URL

```go
client := errorbrain.NewClient("")
client := errorbrain.NewClient("https://errorbrain.example.com")
```

### `HealthCheck() (*HealthResponse, error)`

Checks if the API is healthy.

```go
health, err := client.HealthCheck()
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Status: %s\n", health.Status)
fmt.Printf("LLM Configured: %v\n", health.LLMConfigured)
```

### `SendError(report *ErrorReport) (*ErrorResponse, error)`

Sends an error report for AI analysis.

Converts the `ErrorReport` to a spec-compliant `ErrorEvent` before sending.

```go
report := &errorbrain.ErrorReport{
    Language:     "go",
    Project:      "billing-service",
    Message:      "payment failed",
    ErrorType:    "PaymentError",
    Severity:     "error",
    Traceback:    "stack trace...",
    Tags:         []string{"prod", "payment"},
    Metadata:     map[string]interface{}{"user_id": "123"},
    StoreInVault: true,
}

response, err := client.SendError(report)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("Error ID: %s\n", response.ID)
fmt.Printf("Explanation: %s\n", response.Explanation)
```

### `SendErrorSimple(language, project, message, traceback string) (*ErrorResponse, error)`

Convenience method for sending an error with minimal configuration.

```go
response, err := client.SendErrorSimple(
    "go",
    "my-service",
    "connection timeout",
    "goroutine 1:\nmain.go:42",
)
```

## Types

### ErrorReport

Simple error representation that gets converted to the spec-compliant format.

```go
type ErrorReport struct {
    Language     string                 // Required: e.g., "go", "python"
    Project      string                 // Required: e.g., "billing-service"
    Message      string                 // Required: error message
    ErrorType    string                 // Optional: exception/error class
    Severity     string                 // Optional: debug, info, warning, error, critical
    Traceback    string                 // Optional: stack trace
    Tags         []string               // Optional: categorization tags
    Metadata     map[string]interface{} // Optional: additional context
    StoreInVault bool                   // Whether to save in Obsidian vault
}
```

### ErrorResponse

Response from the ErrorBrain API.

```go
type ErrorResponse struct {
    ID          string    // Unique error identifier
    Project     string    // Project name
    Language    string    // Programming language
    Tags        []string  // Tags
    CreatedAt   time.Time // Error creation timestamp
    Explanation string    // AI-generated explanation
    SavedPath   *string   // Path in Obsidian vault (if saved)
}
```

### ErrorEvent (Spec-defined)

Canonical error event format (generated from spec/).

```go
type ErrorEvent struct {
    ID         string                 // UUID
    Timestamp  time.Time              // ISO 8601
    Source     Source                 // Language, service info
    Message    string                 // Error message
    StackTrace string                 // Stack trace
    ErrorType  string                 // Exception class
    Severity   string                 // debug, info, warning, error, critical
    Metadata   map[string]interface{} // Custom context
    Evidence   []Evidence             // Logs, metrics, HTTP, etc.
}
```

See [types/types.go](./types/types.go) and [spec/error_event.schema.json](../../spec/error_event.schema.json).

## Environment Variables

- `ERRORBRAIN_API_URL` - Base URL of the ErrorBrain API (default: `http://localhost:8000`)

## Testing

```bash
# Run tests
go test ./...

# With coverage
go test -cover ./...

# Verbose output
go test -v ./...
```

## Architecture

This SDK strictly follows the [spec/](../../spec/) - the canonical source of truth:

- **Types generated from** `spec/error_event.schema.json`
- **No server-code imports** - SDKs are independent
- **Simple conversion** - `ErrorReport` → `ErrorEvent` (spec-compliant)

See [sdk/README.md](../README.md) for multi-language SDK details.

## License

MIT

## Links

- [ErrorBrain Main Repository](https://github.com/afeldman/errorbrain)
- [Specification](../../spec/)
- [SDK Overview](../README.md)
