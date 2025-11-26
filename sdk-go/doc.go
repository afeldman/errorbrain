// Package errorbrain provides a Go client for the ErrorBrain API.
//
// ErrorBrain is an error tracking system that captures errors from your applications,
// analyzes them with AI (LLM), and stores them in an Obsidian vault for searchable
// engineering knowledge.
//
// # Installation
//
//	go get github.com/afeldman/errorbrain/sdk-go
//
// # Basic Usage
//
// Create a client and send a simple error:
//
//	client := errorbrain.NewClient("")
//	response, err := client.SendErrorSimple("go", "my-service", "connection timeout", "stack trace...")
//	if err != nil {
//	    log.Fatal(err)
//	}
//	fmt.Printf("Error ID: %s\n", response.ID)
//	fmt.Printf("Explanation: %s\n", response.Explanation)
//
// # Advanced Usage
//
// Send a detailed error report with tags and metadata:
//
//	report := &errorbrain.ErrorReport{
//	    Language:     "go",
//	    Project:      "billing-service",
//	    Message:      "database connection pool exhausted",
//	    Traceback:    "goroutine 42 [running]:\n...",
//	    Tags:         []string{"prod", "critical", "database"},
//	    Metadata: map[string]interface{}{
//	        "host":     "prod-server-01",
//	        "user_id":  12345,
//	        "endpoint": "/api/v1/payment",
//	    },
//	    StoreInVault: true,
//	}
//	response, err := client.SendError(report)
//
// # Configuration
//
// The client reads the API URL from the ERRORBRAIN_API_URL environment variable.
// If not set, it defaults to http://localhost:8000.
//
//	export ERRORBRAIN_API_URL=https://errors.example.com
//
// # Health Check
//
// Check if the ErrorBrain API is available:
//
//	ok := client.HealthCheck()
//	if !ok {
//	    log.Println("ErrorBrain API is not available")
//	}
//
// For more information, see https://github.com/afeldman/errorbrain
package errorbrain
