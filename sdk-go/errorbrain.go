// Package errorbrain provides a Go client for the ErrorBrain API.
//
// ErrorBrain is an error tracking system that captures errors,
// analyzes them with AI (LLM), and stores them in an Obsidian vault
// for searchable engineering knowledge.
//
// Basic usage:
//
//	client := errorbrain.NewClient("")
//	report := &errorbrain.ErrorReport{
//	    Language: "go",
//	    Project:  "my-service",
//	    Message:  "connection failed",
//	    Tags:     []string{"prod"},
//	}
//	response, err := client.SendError(report)
package errorbrain

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

// ErrorReport represents an error to be sent to ErrorBrain.
//
// All fields except Language, Project, and Message are optional.
// StoreInVault defaults to true.
type ErrorReport struct {
	Language     string                 `json:"language"`            // Programming language (e.g., "go", "python")
	Project      string                 `json:"project"`             // Project or service name
	Message      string                 `json:"message"`             // Error message
	Traceback    string                 `json:"traceback,omitempty"` // Optional stack trace
	Tags         []string               `json:"tags,omitempty"`      // Tags for categorization
	Metadata     map[string]interface{} `json:"metadata,omitempty"`  // Additional context
	StoreInVault bool                   `json:"store_in_vault"`      // Whether to save in Obsidian vault
}

// ErrorResponse represents the response from ErrorBrain API.
//
// Contains the error analysis, AI-generated explanation, and
// storage information.
type ErrorResponse struct {
	ID          string    `json:"id"`          // Unique error identifier
	Project     string    `json:"project"`     // Project name
	Language    string    `json:"language"`    // Programming language
	Tags        []string  `json:"tags"`        // Tags
	CreatedAt   time.Time `json:"created_at"`  // Timestamp of error
	Explanation string    `json:"explanation"` // AI-generated explanation
	SavedPath   *string   `json:"saved_path"`  // Path where error was saved in Obsidian
}

// Client is the ErrorBrain API client.
//
// Use NewClient to create a new instance.
type Client struct {
	BaseURL    string       // Base URL of the ErrorBrain API
	HTTPClient *http.Client // HTTP client for making requests
}

// NewClient creates a new ErrorBrain client.
//
// If baseURL is empty, it uses the ERRORBRAIN_API_URL environment variable,
// or defaults to http://localhost:8000.
//
// Example:
//
//	client := errorbrain.NewClient("")
//	client := errorbrain.NewClient("https://errorbrain.example.com")
func NewClient(baseURL string) *Client {
	if baseURL == "" {
		baseURL = os.Getenv("ERRORBRAIN_API_URL")
		if baseURL == "" {
			baseURL = "http://localhost:8000"
		}
	}

	return &Client{
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// HealthCheck checks if the API is healthy.
//
// Returns the API status, configuration, and version information.
//
// Example:
//
//	health, err := client.HealthCheck()
//	if err != nil {
//	    log.Fatal(err)
//	}
//	fmt.Printf("Status: %v\n", health["status"])
func (c *Client) HealthCheck() (map[string]interface{}, error) {
	resp, err := c.HTTPClient.Get(c.BaseURL + "/healthz")
	if err != nil {
		return nil, fmt.Errorf("health check failed: %w", err)
	}
	defer func() {
		_ = resp.Body.Close()
	}()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("health check returned status %d", resp.StatusCode)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode health check response: %w", err)
	}

	return result, nil
}

// SendError sends an error report to ErrorBrain for AI analysis.
//
// The error will be analyzed by the LLM and optionally stored in
// the Obsidian vault if StoreInVault is true.
//
// Example:
//
//	report := &errorbrain.ErrorReport{
//	    Language:     "go",
//	    Project:      "billing-service",
//	    Message:      "database connection failed",
//	    Tags:         []string{"prod", "db"},
//	    StoreInVault: true,
//	}
//	response, err := client.SendError(report)
func (c *Client) SendError(report *ErrorReport) (*ErrorResponse, error) {
	payload, err := json.Marshal(report)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal error report: %w", err)
	}

	resp, err := c.HTTPClient.Post(
		c.BaseURL+"/v1/errors",
		"application/json",
		bytes.NewBuffer(payload),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to send error: %w", err)
	}
	defer func() {
		_ = resp.Body.Close()
	}()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	var result ErrorResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return &result, nil
}

// SendErrorSimple is a convenience method to send an error with minimal configuration.
//
// All tags and metadata are empty, and StoreInVault is set to true.
//
// Example:
//
//	response, err := client.SendErrorSimple(
//	    "go",
//	    "my-service",
//	    "connection timeout",
//	    "goroutine 1:\nmain.go:42",
//	)
func (c *Client) SendErrorSimple(language, project, message, traceback string) (*ErrorResponse, error) {
	report := &ErrorReport{
		Language:     language,
		Project:      project,
		Message:      message,
		Traceback:    traceback,
		Tags:         []string{},
		StoreInVault: true,
	}

	return c.SendError(report)
}
