package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"

	errorbrain "github.com/afeldman/errorbrain/sdk-go"
	"github.com/hashicorp/terraform-plugin-sdk/v2/diag"
	"github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
	"github.com/hashicorp/terraform-plugin-sdk/v2/plugin"
)

// Provider returns the ErrorBrain Terraform provider
func Provider() *schema.Provider {
	return &schema.Provider{
		Schema: map[string]*schema.Schema{
			"api_url": {
				Type:        schema.TypeString,
				Optional:    true,
				DefaultFunc: schema.EnvDefaultFunc("ERRORBRAIN_API_URL", "http://localhost:8000"),
				Description: "The base URL for the ErrorBrain API",
			},
			"project": {
				Type:        schema.TypeString,
				Required:    true,
				Description: "The project name for error tracking",
			},
			"enabled": {
				Type:        schema.TypeBool,
				Optional:    true,
				Default:     true,
				Description: "Enable/disable error tracking",
			},
		},
		ConfigureContextFunc: providerConfigure,
		DataSourcesMap:       map[string]*schema.Resource{},
		ResourcesMap:         map[string]*schema.Resource{},
	}
}

type providerConfig struct {
	client  *errorbrain.Client
	project string
	enabled bool
}

func providerConfigure(ctx context.Context, d *schema.ResourceData) (interface{}, diag.Diagnostics) {
	apiURL := d.Get("api_url").(string)
	project := d.Get("project").(string)
	enabled := d.Get("enabled").(bool)

	client := errorbrain.NewClient(apiURL)

	config := &providerConfig{
		client:  client,
		project: project,
		enabled: enabled,
	}

	return config, nil
}

// TerraformErrorReporter wraps Terraform operations and reports errors
type TerraformErrorReporter struct {
	config *providerConfig
}

// ReportTerraformError captures and reports a Terraform error
func (r *TerraformErrorReporter) ReportTerraformError(operation, resource, message, stderr string) error {
	if !r.config.enabled {
		return nil
	}

	report := &errorbrain.ErrorReport{
		Language:  "terraform",
		Project:   r.config.project,
		Message:   fmt.Sprintf("Terraform %s failed: %s", operation, message),
		Traceback: stderr,
		Tags:      []string{"terraform", operation, resource},
		Metadata: map[string]interface{}{
			"operation": operation,
			"resource":  resource,
		},
		StoreInVault: true,
	}

	_, err := r.config.client.SendError(report)
	return err
}

// WrapTerraformCommand wraps terraform commands to capture errors
func WrapTerraformCommand(args []string, project string) error {
	// Create ErrorBrain client
	client := errorbrain.NewClient("")
	reporter := &TerraformErrorReporter{
		config: &providerConfig{
			client:  client,
			project: project,
			enabled: true,
		},
	}

	// Execute terraform command
	cmd := exec.Command("terraform", args...)
	cmd.Stdout = os.Stdout
	cmd.Stdin = os.Stdin

	var stderrBuf strings.Builder
	cmd.Stderr = &stderrBuf

	err := cmd.Run()
	if err != nil {
		// Extract operation and resource if possible
		operation := "unknown"
		resource := "unknown"

		if len(args) > 0 {
			operation = args[0]
		}

		stderr := stderrBuf.String()

		// Report error to ErrorBrain
		if reportErr := reporter.ReportTerraformError(operation, resource, err.Error(), stderr); reportErr != nil {
			log.Printf("Failed to report error to ErrorBrain: %v", reportErr)
		}

		// Print stderr to console
		fmt.Fprint(os.Stderr, stderr)
		return err
	}

	return nil
}

func main() {
	// Check if running as wrapper or as provider
	if len(os.Args) > 1 && os.Args[1] == "wrap" {
		// Running as CLI wrapper
		project := os.Getenv("ERRORBRAIN_PROJECT")
		if project == "" {
			project = "terraform-project"
		}

		if len(os.Args) < 3 {
			fmt.Println("Usage: terraform-errorbrain wrap <terraform-args>")
			os.Exit(1)
		}

		if err := WrapTerraformCommand(os.Args[2:], project); err != nil {
			os.Exit(1)
		}
	} else {
		// Running as Terraform provider
		plugin.Serve(&plugin.ServeOpts{
			ProviderFunc: Provider,
		})
	}
}
