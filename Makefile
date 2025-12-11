# Makefile for ErrorBrain Project

.PHONY: help install test lint format clean dev-api

help: ## Show this help message
	@echo "ErrorBrain - Development Commands"
	@echo ""
	@echo "⚠️  Use 'task' instead of 'make' for most commands"
	@echo "   Useful make targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Run setup.sh (same as: ./setup.sh)
	./setup.sh

dev: ## Run dev-server.sh (same as: ./dev-server.sh)
	./dev-server.sh

test: ## Run run-tests.sh (same as: ./run-tests.sh)
	./run-tests.sh

health: ## Check API health (same as: ./health-check.sh)
	./health-check.sh

fmt: ## Format all code (same as: ./format-code.sh)
	./format-code.sh
	cd sdk-go && go fmt ./...
	cd terraform-provider && go fmt ./...
	@echo "Formatting TypeScript code..."
	cd sdk-typescript && npm run format
	@echo "Formatting Deno code..."
	cd sdk-deno && deno fmt src/
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
	@echo "Cleaning TypeScript build artifacts..."
	rm -rf sdk-typescript/dist sdk-typescript/node_modules sdk-typescript/coverage
	@echo "Clean complete!"

dev-api: ## Start API development server
	cd api && uv run errorbrain-server-dev

build-terraform: ## Build Terraform provider
	cd terraform-provider && go build -o terraform-errorbrain

setup-git-hooks: ## Install pre-commit hooks
	pip install pre-commit
	pre-commit install
	@echo "Git hooks installed!"

check-all: fmt lint test ## Format, lint, and test everything
	@echo "✨ All checks passed!"

.PHONY: help setup dev test health fmt build-terraform setup-git-hooks check-all
