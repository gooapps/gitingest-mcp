# Use Python 3.11 slim image for optimal size and performance
FROM python:3.11-slim

# Set metadata
LABEL maintainer="GitIngest MCP Server"
LABEL description="MCP Server for GitIngest integration with GitHub repositories"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the MCP server code
COPY mcp_server.py config.py .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash mcpuser && \
    chown -R mcpuser:mcpuser /app
USER mcpuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import mcp; print('MCP server is healthy')" || exit 1

# Default command
CMD ["python", "mcp_server.py"]
