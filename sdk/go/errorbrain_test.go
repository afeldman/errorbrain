package errorbrain

import (
	"testing"
)

func TestNewClient(t *testing.T) {
	tests := []struct {
		name    string
		baseURL string
		want    string
	}{
		{
			name:    "default URL",
			baseURL: "",
			want:    "http://localhost:8000",
		},
		{
			name:    "custom URL",
			baseURL: "https://example.com",
			want:    "https://example.com",
		},
		{
			name:    "custom URL with trailing slash",
			baseURL: "https://example.com/",
			want:    "https://example.com",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			client := NewClient(tt.baseURL)
			if client.BaseURL != tt.want {
				t.Errorf("NewClient().BaseURL = %v, want %v", client.BaseURL, tt.want)
			}
			if client.HTTPClient == nil {
				t.Error("NewClient().HTTPClient is nil")
			}
		})
	}
}

func TestErrorReport_Structure(t *testing.T) {
	report := &ErrorReport{
		Language:     "go",
		Project:      "test-project",
		Message:      "test error",
		Traceback:    "line 1\nline 2",
		Tags:         []string{"test", "unit"},
		Metadata:     map[string]interface{}{"key": "value"},
		StoreInVault: true,
	}

	if report.Language != "go" {
		t.Errorf("Language = %v, want go", report.Language)
	}
	if report.Project != "test-project" {
		t.Errorf("Project = %v, want test-project", report.Project)
	}
	if report.Message != "test error" {
		t.Errorf("Message = %v, want test error", report.Message)
	}
	if len(report.Tags) != 2 {
		t.Errorf("Tags length = %v, want 2", len(report.Tags))
	}
	if !report.StoreInVault {
		t.Error("StoreInVault = false, want true")
	}
}

func TestErrorResponse_Structure(t *testing.T) {
	response := &ErrorResponse{
		ID:          "test-id-123",
		Project:     "test-project",
		Language:    "go",
		Tags:        []string{"test"},
		Explanation: "Test explanation",
	}

	if response.ID != "test-id-123" {
		t.Errorf("ID = %v, want test-id-123", response.ID)
	}
	if response.Project != "test-project" {
		t.Errorf("Project = %v, want test-project", response.Project)
	}
	if response.Explanation != "Test explanation" {
		t.Errorf("Explanation = %v, want Test explanation", response.Explanation)
	}
}

func TestGenerateUUID(t *testing.T) {
	uuid1 := generateUUID()
	uuid2 := generateUUID()

	// Basic format check: 8-4-4-4-12
	if len(uuid1) != 36 {
		t.Errorf("UUID length = %d, want 36", len(uuid1))
	}

	// UUIDs should be different
	if uuid1 == uuid2 {
		t.Error("Generated UUIDs are identical")
	}

	// Check version 4 (3rd segment, first digit should be 4)
	if uuid1[14] != '4' {
		t.Errorf("UUID version = %c, want 4", uuid1[14])
	}
}

func TestBuildErrorEvent(t *testing.T) {
	client := NewClient("")

	report := &ErrorReport{
		Language:  "go",
		Project:   "test-service",
		Message:   "test error",
		ErrorType: "TestError",
		Severity:  "error",
		Traceback: "stack trace here",
		Tags:      []string{"test", "unit"},
		Metadata:  map[string]interface{}{"key": "value"},
	}

	event := client.buildErrorEvent(report)

	if event.Source.Language != "go" {
		t.Errorf("event.Source.Language = %v, want go", event.Source.Language)
	}
	if event.Source.Name != "test-service" {
		t.Errorf("event.Source.Name = %v, want test-service", event.Source.Name)
	}
	if event.Message != "test error" {
		t.Errorf("event.Message = %v, want test error", event.Message)
	}
	if event.ErrorType != "TestError" {
		t.Errorf("event.ErrorType = %v, want TestError", event.ErrorType)
	}
	if event.Severity != "error" {
		t.Errorf("event.Severity = %v, want error", event.Severity)
	}
	if event.StackTrace != "stack trace here" {
		t.Errorf("event.StackTrace = %v, want stack trace here", event.StackTrace)
	}
	if len(event.Source.Tags) != 2 {
		t.Errorf("event.Source.Tags length = %d, want 2", len(event.Source.Tags))
	}
	if event.ID == "" {
		t.Error("event.ID is empty")
	}
	if event.Timestamp.IsZero() {
		t.Error("event.Timestamp is zero")
	}
}

func TestBuildErrorEvent_DefaultSeverity(t *testing.T) {
	client := NewClient("")

	report := &ErrorReport{
		Language: "go",
		Project:  "test-service",
		Message:  "test error",
	}

	event := client.buildErrorEvent(report)

	if event.Severity != "error" {
		t.Errorf("event.Severity = %v, want error (default)", event.Severity)
	}
}
