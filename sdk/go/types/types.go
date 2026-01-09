// Package types contains type definitions generated from spec/v1/error_event.schema.json
//
// These are the canonical types that all ErrorBrain SDKs must follow.
// This ensures consistency across all languages and runtimes.
package types

import "time"

// Source represents the origin of an error.
//
// This identifies which application, service, or system produced the error.
type Source struct {
	Language    string   `json:"language"`              // Programming language (python, go, typescript, etc.)
	Name        string   `json:"name"`                  // Application or service name
	Version     string   `json:"version,omitempty"`     // Application version (semver recommended)
	Environment string   `json:"environment,omitempty"` // local, development, staging, production
	Hostname    string   `json:"hostname,omitempty"`    // Hostname or pod name
	Tags        []string `json:"tags,omitempty"`        // Arbitrary tags for filtering
}

// Evidence represents additional context for an error.
//
// Examples: log lines, metrics, HTTP requests/responses, database queries
type Evidence struct {
	Type      string                 `json:"type"`                // log_line, metric, http_request, etc.
	Data      map[string]interface{} `json:"data"`                // Evidence payload
	Timestamp *time.Time             `json:"timestamp,omitempty"` // ISO 8601 timestamp
}

// ErrorEvent is the canonical error event format for ErrorBrain.
//
// This is the standardized format that all SDKs must produce,
// regardless of the language they're written in.
type ErrorEvent struct {
	ID         string                 `json:"id"`                    // UUID
	Timestamp  time.Time              `json:"timestamp"`             // ISO 8601
	Source     Source                 `json:"source"`                // Origin information
	Message    string                 `json:"message"`               // Error message
	StackTrace string                 `json:"stack_trace,omitempty"` // Stack trace
	ErrorType  string                 `json:"error_type,omitempty"`  // Exception class
	Severity   string                 `json:"severity,omitempty"`    // debug, info, warning, error, critical
	Metadata   map[string]interface{} `json:"metadata,omitempty"`    // Custom context
	Evidence   []Evidence             `json:"evidence,omitempty"`    // Additional evidence
}
