// Package errorbrain provides a Go client for the ErrorBrain API.
//
// ErrorBrain is an error tracking system that captures errors,
// analyzes them with AI (LLM), and stores them in an Obsidian vault
// for searchable engineering knowledge.
//
// This SDK strictly follows the spec defined in spec/error_event.schema.json.
// SDKs in other languages implement the same contract.
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
	"crypto/rand"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/afeldman/errorbrain/sdk/go/types"
)

// ErrorReport represents a simple error to be sent to ErrorBrain.
//
// The client converts this to a spec-compliant ErrorEvent.
// All fields except Language, Project, and Message are optional.
// StoreInVault defaults to true.
type ErrorReport struct {
	Language     string                 `json:"language"`             // Programming language (e.g., "go", "python")
	Project      string                 `json:"project"`              // Project or service name
	Message      string                 `json:"message"`              // Error message
	ErrorType    string                 `json:"error_type,omitempty"` // Error/exception type
	Severity     string                 `json:"severity,omitempty"`   // debug, info, warning, error, critical
	Traceback    string                 `json:"traceback,omitempty"`  // Optional stack trace
	Tags         []string               `json:"tags,omitempty"`       // Tags for categorization
	Metadata     map[string]interface{} `json:"metadata,omitempty"`   // Additional context
	StoreInVault bool                   `json:"store_in_vault"`       // Whether to save in Obsidian vault
}

// ErrorResponse represents the response from ErrorBrain API.
//
// Contains the error analysis, AI-generated explanation, and storage information.
type ErrorResponse struct {
	ID          string    `json:"id"`          // Unique error identifier
	Project     string    `json:"project"`     // Project name
	Language    string    `json:"language"`    // Programming language
	Tags        []string  `json:"tags"`        // Tags
	CreatedAt   time.Time `json:"created_at"`  // Timestamp of error
	Explanation string    `json:"explanation"` // AI-generated explanation
	SavedPath   *string   `json:"saved_path"`  // Path where error was saved in Obsidian
}

// HealthResponse represents the API health status.
type HealthResponse struct {
	Status          string `json:"status"`
	LLMConfigured   bool   `json:"llm_configured"`
	VaultConfigured bool   `json:"vault_configured"`
	VaultPath       string `json:"vault_path,omitempty"`
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

	// Strip trailing slash
	baseURL = strings.TrimSuffix(baseURL, "/")

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
//	fmt.Printf("Status: %v\n", health.Status)
func (c *Client) HealthCheck() (*HealthResponse, error) {
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

	var result HealthResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode health check response: %w", err)
	}

	return &result, nil
}

// SendError sends an error report to ErrorBrain for AI analysis.
//
// The error will be analyzed by the LLM and optionally stored in
// the Obsidian vault if StoreInVault is true.
//
// This method converts ErrorReport to the spec-compliant ErrorEvent format.
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
	errorEvent := c.buildErrorEvent(report)

	payload := map[string]interface{}{
		"event":          errorEvent,
		"store_in_vault": report.StoreInVault || true,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal error event: %w", err)
	}

	resp, err := c.HTTPClient.Post(
		c.BaseURL+"/v1/errors",
		"application/json",
		bytes.NewBuffer(body),
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

// buildErrorEvent converts a simple ErrorReport to a spec-compliant ErrorEvent.
//
// This is where we construct the canonical format defined in spec/error_event.schema.json.
func (c *Client) buildErrorEvent(report *ErrorReport) *types.ErrorEvent {
	id := generateUUID()
	timestamp := time.Now().UTC()

	source := types.Source{
		Language: report.Language,
		Name:     report.Project,
		Tags:     report.Tags,
	}

	severity := report.Severity
	if severity == "" {
		severity = "error"
	}

	return &types.ErrorEvent{
		ID:         id,
		Timestamp:  timestamp,
		Source:     source,
		Message:    report.Message,
		StackTrace: report.Traceback,
		ErrorType:  report.ErrorType,
		Severity:   severity,
		Metadata:   report.Metadata,
		Evidence:   []types.Evidence{},
	}
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

// generateUUID generates a UUID v4.
func generateUUID() string {
	b := make([]byte, 16)
	_, err := rand.Read(b)
	if err != nil {
		panic(fmt.Sprintf("failed to generate UUID: %v", err))
	}

	// Set version (4) and variant bits
	b[6] = (b[6] & 0x0f) | 0x40
	b[8] = (b[8] & 0x3f) | 0x80

	return fmt.Sprintf("%x-%x-%x-%x-%x", b[0:4], b[4:6], b[6:8], b[8:10], b[10:])
}
