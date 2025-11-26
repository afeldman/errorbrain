# ErrorBrain Terraform Provider Example
#
# This example demonstrates how to use the ErrorBrain Terraform provider
# to send infrastructure errors to ErrorBrain for AI analysis.

terraform {
  required_providers {
    errorbrain = {
      source  = "afeldman/errorbrain"
      version = "~> 0.1.0"
    }
  }
}

# Configure the ErrorBrain provider
provider "errorbrain" {
  # API URL (defaults to http://localhost:8000)
  api_url = "http://localhost:8000"
}

# Example 1: Simple error report
resource "errorbrain_error" "terraform_apply_failed" {
  language = "terraform"
  project  = "infrastructure"
  message  = "Failed to apply Terraform configuration"

  traceback = <<-EOT
    Error: Error creating AWS EC2 instance
    
    on main.tf line 42, in resource "aws_instance" "web":
    42: resource "aws_instance" "web" {
    
    Provider produced inconsistent result after apply
    
    When applying changes to aws_instance.web, provider "aws" produced an
    unexpected new value: .id: was null, but now "i-0123456789abcdef0".
  EOT

  tags = ["terraform", "aws", "ec2", "production"]

  metadata = {
    "terraform_version" = "1.6.0"
    "provider"          = "aws"
    "resource_type"     = "aws_instance"
    "workspace"         = "production"
  }

  store_in_vault = true
}

# Example 2: Plan failure
resource "errorbrain_error" "plan_failure" {
  language = "terraform"
  project  = "infrastructure"
  message  = "Terraform plan failed: Invalid configuration"

  traceback = <<-EOT
    Error: Unsupported argument
    
    on main.tf line 15, in resource "aws_s3_bucket" "data":
    15:   region = "us-east-1"
    
    An argument named "region" is not expected here. Did you mean to define a
    block of type "region"?
  EOT

  tags = ["terraform", "validation", "s3"]

  metadata = {
    "command"     = "terraform plan"
    "working_dir" = "/infrastructure/aws"
    "module"      = "storage"
  }

  store_in_vault = true
}

# Example 3: State lock error
resource "errorbrain_error" "state_lock_error" {
  language = "terraform"
  project  = "infrastructure"
  message  = "Failed to acquire state lock"

  traceback = <<-EOT
    Error: Error acquiring the state lock
    
    Error message: ConditionalCheckFailedException: The conditional request
    failed
    Lock Info:
      ID:        abc123-def456-789012
      Path:      terraform-state/production.tfstate
      Operation: OperationTypeApply
      Who:       user@example.com
      Version:   1.6.0
      Created:   2025-11-26 10:30:00 UTC
      Info:
    
    Terraform acquires a state lock to protect the state from being written
    by multiple users at the same time. Please resolve the issue above and try
    again.
  EOT

  tags = ["terraform", "state", "locking", "critical"]

  metadata = {
    "backend"    = "s3"
    "lock_table" = "terraform-state-lock"
    "lock_id"    = "abc123-def456-789012"
  }

  store_in_vault = true
}

# Example 4: Provider configuration error
resource "errorbrain_error" "provider_config_error" {
  language = "terraform"
  project  = "infrastructure"
  message  = "Provider authentication failed"

  traceback = <<-EOT
    Error: error configuring Terraform AWS Provider: failed to get shared
    config profile, production
    
    with provider["registry.terraform.io/hashicorp/aws"],
    on providers.tf line 10, in provider "aws":
    10: provider "aws" {
  EOT

  tags = ["terraform", "aws", "authentication", "provider"]

  metadata = {
    "provider" = "aws"
    "profile"  = "production"
    "region"   = "eu-central-1"
  }

  store_in_vault = true
}

# Example 5: Dependency error
resource "errorbrain_error" "dependency_error" {
  language = "terraform"
  project  = "infrastructure"
  message  = "Resource dependency cycle detected"

  traceback = <<-EOT
    Error: Cycle: aws_security_group.app, aws_instance.web,
    aws_security_group_rule.app_ingress
    
    Terraform detected a dependency cycle between resources. This usually
    indicates a configuration error.
  EOT

  tags = ["terraform", "dependencies", "cycle", "configuration"]

  metadata = {
    "affected_resources" = "aws_security_group.app,aws_instance.web,aws_security_group_rule.app_ingress"
  }

  store_in_vault = true
}

# Output the error IDs
output "error_ids" {
  description = "ErrorBrain error IDs"
  value = {
    apply_failed     = errorbrain_error.terraform_apply_failed.id
    plan_failure     = errorbrain_error.plan_failure.id
    state_lock       = errorbrain_error.state_lock_error.id
    provider_config  = errorbrain_error.provider_config_error.id
    dependency_cycle = errorbrain_error.dependency_error.id
  }
}
