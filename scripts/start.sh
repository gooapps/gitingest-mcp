#!/bin/bash

# GitIngest MCP Server Startup Script

set -e

echo "Starting GitIngest MCP Server..."

# Load environment variables if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Validate configuration
echo "Validating configuration..."
python -c "from gitingest_mcp.config import Config; Config.validate(); print('Configuration is valid')"

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Warning: GITHUB_TOKEN environment variable is not set."
    echo "Private repositories may not be accessible."
    echo "Set GITHUB_TOKEN to your GitHub personal access token for full functionality."
fi

# Check if gitingest is available
echo "Checking GitIngest availability..."
python -c "
try:
    from gitingest import ingest
    print('GitIngest Python package is available')
except ImportError:
    print('GitIngest Python package not found, will use CLI fallback')
    import subprocess
    try:
        subprocess.run(['gitingest', '--help'], capture_output=True, check=True)
        print('GitIngest CLI is available')
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('Warning: Neither GitIngest Python package nor CLI found')
        print('Please install gitingest: pip install gitingest')
"

# Start the MCP server
echo "Starting MCP server..."
exec python -m gitingest_mcp.mcp_server
