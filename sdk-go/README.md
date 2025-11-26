# ErrorBrain Go SDK

Go client library for the ErrorBrain API.

## Installation

```bash
go get github.com/afeldman/errorbrain/sdk-go
```

## Usage

```go
package main

import (
    "fmt"
    "log"

    errorbrain "github.com/afeldman/errorbrain/sdk-go"
)

func main() {
    // Create client (uses ERRORBRAIN_API_URL env var or defaults to localhost:8000)
    client := errorbrain.NewClient("")

    // Check health
    health, err := client.HealthCheck()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("API Status: %v\n", health)

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

## Environment Variables

- `ERRORBRAIN_API_URL` - Base URL of the ErrorBrain API (default: `http://localhost:8000`)

## License

See main repository.
