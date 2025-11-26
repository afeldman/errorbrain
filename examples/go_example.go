package main

import (
"fmt"
"log"
"runtime"
"strings"

"github.com/afeldman/errorbrain/sdk-go"
)

func main() {
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("ErrorBrain Go SDK - Examples")
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println()
	fmt.Println("Make sure the ErrorBrain API is running:")
	fmt.Println("  task dev")
	fmt.Println("  # or: cd api && uv run errorbrain-server-dev")
	fmt.Println()

	// Create client
	client := errorbrain.NewClient("")

	// Check API health
	if !client.HealthCheck() {
		log.Fatal("❌ ErrorBrain API is not available")
	}
	fmt.Println("✓ API is healthy\n")

	// Run examples
	example1Basic(client)
	example2WithTraceback(client)
	example3WithMetadata(client)
	example4Simple(client)

	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("✓ All examples completed successfully!")
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println()
}

func example1Basic(client *errorbrain.Client) {
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("Example 1: Basic Error Report")
	fmt.Println(strings.Repeat("=", 60))

	report := &errorbrain.ErrorReport{
		Language:     "go",
		Project:      "billing-service",
		Message:      "Database connection failed",
		Traceback:    "connection refused on postgres://db:5432",
		Tags:         []string{"production", "database"},
		StoreInVault: true,
	}

	response, err := client.SendError(report)
	if err != nil {
		log.Fatalf("Failed to send error: %v", err)
	}

	fmt.Printf("Error ID: %s\n", response.ID)
	fmt.Printf("Project: %s\n", response.Project)
	fmt.Printf("\nAI Explanation:\n%s\n", response.Explanation)
	if response.SavedPath != "" {
		fmt.Printf("\nSaved to: %s\n", response.SavedPath)
	}
	fmt.Println()
}

func example2WithTraceback(client *errorbrain.Client) {
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("Example 2: Error with Stack Trace")
	fmt.Println(strings.Repeat("=", 60))

	// Get stack trace
	_, file, line, _ := runtime.Caller(0)
	stackTrace := fmt.Sprintf(
"goroutine 1 [running]:\nmain.example2WithTraceback\n\t%s:%d\nmain.main\n\t%s:25",
file, line, file,
)

	report := &errorbrain.ErrorReport{
		Language:     "go",
		Project:      "api-gateway",
		Message:      "Panic: nil pointer dereference",
		Traceback:    stackTrace,
		Tags:         []string{"panic", "runtime-error", "critical"},
		StoreInVault: true,
	}

	response, err := client.SendError(report)
	if err != nil {
		log.Fatalf("Failed to send error: %v", err)
	}

	fmt.Printf("Error ID: %s\n", response.ID)
	fmt.Printf("\nAI Explanation:\n%s\n", response.Explanation)
	fmt.Println()
}

func example3WithMetadata(client *errorbrain.Client) {
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("Example 3: Error with Rich Metadata")
	fmt.Println(strings.Repeat("=", 60))

	report := &errorbrain.ErrorReport{
		Language: "go",
		Project:  "monitoring-service",
		Message:  "High memory usage detected",
		Tags:     []string{"monitoring", "performance", "memory"},
		Metadata: map[string]interface{}{
			"memory_usage_mb": 1024,
			"threshold_mb":    512,
			"num_goroutines":  150,
			"uptime_hours":    72,
			"host":            "prod-server-03",
			"environment":     "production",
		},
		StoreInVault: true,
	}

	response, err := client.SendError(report)
	if err != nil {
		log.Fatalf("Failed to send error: %v", err)
	}

	fmt.Printf("Error ID: %s\n", response.ID)
	fmt.Printf("Tags: %v\n", response.Tags)
	fmt.Printf("\nAI Explanation:\n%s\n", response.Explanation)
	fmt.Println()
}

func example4Simple(client *errorbrain.Client) {
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("Example 4: Simple Error Report (Convenience Method)")
	fmt.Println(strings.Repeat("=", 60))

	// Using the convenience method
	response, err := client.SendErrorSimple(
"go",
"config-service",
"Configuration file not found",
"error reading config.yaml: file does not exist at /etc/app/config.yaml",
)
	if err != nil {
		log.Fatalf("Failed to send error: %v", err)
	}

	fmt.Printf("Error ID: %s\n", response.ID)
	fmt.Printf("\nAI Explanation:\n%s\n", response.Explanation)
	fmt.Println()
}
