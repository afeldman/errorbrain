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
	if len(report.Tags) != 2 {
		t.Errorf("Tags length = %v, want 2", len(report.Tags))
	}
	if !report.StoreInVault {
		t.Error("StoreInVault = false, want true")
	}
}

func TestErrorResponse_Structure(t *testing.T) {
	path := "/path/to/file.md"
	response := &ErrorResponse{
		ID:          "123",
		Project:     "test",
		Language:    "go",
		Tags:        []string{"test"},
		Explanation: "test explanation",
		SavedPath:   &path,
	}

	if response.ID != "123" {
		t.Errorf("ID = %v, want 123", response.ID)
	}
	if response.SavedPath == nil {
		t.Error("SavedPath is nil")
	}
	if *response.SavedPath != path {
		t.Errorf("SavedPath = %v, want %v", *response.SavedPath, path)
	}
}
