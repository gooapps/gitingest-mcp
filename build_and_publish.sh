#!/bin/bash

# GitIngest MCP Server - Build and Publish Script

set -e

# Configuration
IMAGE_NAME="gitingest-mcp"
REGISTRY="docker.io"  # Using Docker Hub for public access
USERNAME="develgooapps"  # Organization or username owning the container registry namespace
FULL_IMAGE_NAME="${REGISTRY}/${USERNAME}/${IMAGE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}GitIngest MCP Server - Build and Publish${NC}"
echo "=============================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if user is logged in to Docker Hub
if ! docker info | grep -q "docker.io"; then
    print_warning "You may need to login to Docker Hub:"
    echo "  docker login"
    echo "  Use your Docker Hub username and password"
    echo ""
fi

# Build the Docker image
print_status "Building Docker image: ${FULL_IMAGE_NAME}"
docker build -t "${FULL_IMAGE_NAME}:latest" .

# Tag with version
VERSION=$(date +%Y%m%d-%H%M%S)
docker tag "${FULL_IMAGE_NAME}:latest" "${FULL_IMAGE_NAME}:${VERSION}"

print_status "Image built successfully!"
print_status "Tags created:"
echo "  - ${FULL_IMAGE_NAME}:latest"
echo "  - ${FULL_IMAGE_NAME}:${VERSION}"

# Ask if user wants to push to registry
read -p "Do you want to push the image to Docker Hub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Pushing image to Docker Hub..."
    
    # Push latest tag
    docker push "${FULL_IMAGE_NAME}:latest"
    
    # Push version tag
    docker push "${FULL_IMAGE_NAME}:${VERSION}"
    
    print_status "Image pushed successfully to Docker Hub!"
    echo ""
    echo -e "${GREEN}Your MCP server is now publicly available at:${NC}"
    echo "  ${FULL_IMAGE_NAME}:latest"
    echo ""
    echo -e "${BLUE}Usage in Claude Desktop:${NC}"
    echo "Add this to your claude_desktop_config.json:"
    echo ""
    cat << EOF
{
  "mcpServers": {
    "gitingest": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "GITHUB_TOKEN",
        "docker.io/${USERNAME}/gitingest-mcp:latest"
      ],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
EOF
else
    print_warning "Image not pushed to registry."
    print_status "You can push it later with:"
    echo "  docker push ${FULL_IMAGE_NAME}:latest"
    echo "  docker push ${FULL_IMAGE_NAME}:${VERSION}"
fi

# Test the image locally
print_status "Testing the built image..."
if docker run --rm "${FULL_IMAGE_NAME}:latest" python -c "import mcp; print('MCP server test successful')"; then
    print_status "Image test passed!"
else
    print_error "Image test failed!"
    exit 1
fi

echo ""
print_status "Build and publish process completed!"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Set your GITHUB_TOKEN environment variable"
echo "2. Configure your MCP client with the provided configuration"
echo "3. Start using the GitIngest MCP server!"
