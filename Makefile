# GitIngest MCP Server Makefile

.PHONY: help install test build run clean docker-build docker-run docker-stop docker-publish docker-test

# Default target
help:
	@echo "GitIngest MCP Server - Available commands:"
	@echo ""
	@echo "  install        - Install Python dependencies"
	@echo "  test           - Run tests"
	@echo "  build          - Build Docker image locally"
	@echo "  docker-build   - Build Docker image with docker-compose"
	@echo "  docker-run     - Run with Docker Compose"
	@echo "  docker-stop    - Stop Docker containers"
	@echo "  docker-publish - Build and publish Docker image"
	@echo "  docker-test    - Test the built Docker image"
	@echo "  run            - Run the MCP server locally"
	@echo "  clean          - Clean up temporary files"
	@echo ""

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

# Run tests
test:
	@echo "Running MCP server tests..."
	python scripts/test_mcp.py

# Build Docker image locally
build:
	@echo "Building Docker image locally..."
	docker build -t gitingest-mcp:latest .

# Build Docker image with docker-compose
docker-build:
	@echo "Building Docker image with docker-compose..."
	docker-compose build

# Publish Docker image
docker-publish:
	@echo "Building and publishing Docker image..."
	./build_and_publish.sh

# Test Docker image
docker-test:
	@echo "Testing Docker image..."
	docker run --rm gitingest-mcp:latest python -c "import mcp; print('MCP server test successful')"

# Run locally
run:
	@echo "Starting MCP server locally..."
	./scripts/start.sh

# Run with Docker Compose
docker-run:
	@echo "Starting MCP server with Docker Compose..."
	docker-compose up --build

# Stop Docker containers
docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

# Clean up
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from template. Please edit it with your GitHub token."; \
	fi

# Quick test with a public repository
test-public:
	@echo "Testing with public repository..."
	python -c "from gitingest_mcp.mcp_server import GitIngestMCPServer; import asyncio; asyncio.run(GitIngestMCPServer()._ingest_repository({'repository_url': 'https://github.com/octocat/Hello-World', 'include_patterns': ['*.md']}))"

# Check if GitHub token is set
check-token:
	@if [ -z "$$GITHUB_TOKEN" ]; then \
		echo "Warning: GITHUB_TOKEN environment variable is not set."; \
		echo "Private repositories may not be accessible."; \
	else \
		echo "GitHub token is configured."; \
	fi
