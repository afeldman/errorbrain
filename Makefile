# Makefile for ErrorBrain Project

.PHONY: help install test lint format clean dev-api

help: ## Show this help message
	@echo "ErrorBrain - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "Installing API dependencies..."
	cd api && uv sync --all-extras
	@echo "Installing SDK dependencies..."
	cd sdk-python && uv sync --all-extras
	@echo "Installing Go dependencies..."
	cd sdk-go && go mod download
	cd terraform-provider && go mod download

test: ## Run all tests
	@echo "Testing API..."
	cd api && uv run pytest tests/ -v
	@echo "Testing Go SDK..."
	cd sdk-go && go test -v ./...
	@echo "All tests passed!"

lint: ## Run linters on all code
	@echo "Linting API..."
	cd api && uv run ruff check src/
	@echo "Linting Python SDK..."
	cd sdk-python && uv run ruff check src/
	@echo "Linting Go SDK..."
	cd sdk-go && golangci-lint run
	@echo "All lints passed!"

format: ## Format all code
	@echo "Formatting Python code..."
	cd api && uv run ruff format src/ tests/
	cd sdk-python && uv run ruff format src/
	@echo "Formatting Go code..."
	cd sdk-go && go fmt ./...
	cd terraform-provider && go fmt ./...
	@echo "Formatting complete!"

clean: ## Clean build artifacts
	@echo "Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	@echo "Clean complete!"

dev-api: ## Start API development server
	cd api && uv run errorbrain-server-dev

build-terraform: ## Build Terraform provider
	cd terraform-provider && go build -o terraform-errorbrain

setup-git-hooks: ## Install pre-commit hooks
	pip install pre-commit
	pre-commit install
	@echo "Git hooks installed!"

docs: ## Build documentation (Sphinx + godoc)
	@echo "Building Python API docs..."
	cd api/docs && uv run sphinx-build -b html . _build/html
	@echo "Building Python SDK docs..."
	cd sdk-python/docs && uv run sphinx-build -b html . _build/html
	@echo "Generating Go SDK docs..."
	cd sdk-go && godoc -http=:6060 &
	@echo "Docs built! API: api/docs/_build/html/index.html"
	@echo "           SDK: sdk-python/docs/_build/html/index.html"
	@echo "           Go:  http://localhost:6060/pkg/github.com/afeldman/errorbrain/sdk-go/"

check-all: format lint test ## Format, lint, and test everything
	@echo "All checks passed! ✨"
