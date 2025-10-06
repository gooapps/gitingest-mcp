"""
Configuration settings for GitIngest MCP Server
"""

import os
from typing import Optional


class Config:
    """Configuration class for GitIngest MCP Server."""
    
    # GitHub Configuration
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # GitIngest Configuration
    GITINGEST_MAX_FILE_SIZE: int = int(os.getenv("GITINGEST_MAX_FILE_SIZE", "1048576"))  # 1MB
    GITINGEST_TIMEOUT: int = int(os.getenv("GITINGEST_TIMEOUT", "300"))  # 5 minutes
    
    # MCP Server Configuration
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "gitingest-mcp")
    MCP_SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    
    # Default patterns for common exclusions
    DEFAULT_EXCLUDE_PATTERNS: list = [
        "node_modules/*",
        "*.lock",
        "dist/*",
        "build/*",
        "*.min.js",
        "*.log",
        ".git/*",
        ".DS_Store",
        "*.pyc",
        "__pycache__/*",
        ".pytest_cache/*",
        "*.egg-info/*",
        ".coverage",
        "coverage.xml",
        "*.so",
        "*.dylib",
        "*.dll"
    ]
    
    # Default patterns for common inclusions
    DEFAULT_INCLUDE_PATTERNS: list = [
        "*.py",
        "*.js",
        "*.ts",
        "*.jsx",
        "*.tsx",
        "*.go",
        "*.rs",
        "*.java",
        "*.cpp",
        "*.c",
        "*.h",
        "*.hpp",
        "*.cs",
        "*.php",
        "*.rb",
        "*.swift",
        "*.kt",
        "*.scala",
        "*.md",
        "*.txt",
        "*.json",
        "*.yaml",
        "*.yml",
        "*.xml",
        "*.toml",
        "*.ini",
        "*.cfg",
        "*.conf",
        "Dockerfile",
        "docker-compose.yml",
        "Makefile",
        "CMakeLists.txt",
        "package.json",
        "requirements.txt",
        "Pipfile",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
        "composer.json",
        "Gemfile"
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        # GitHub token is optional but recommended for private repos
        if not cls.GITHUB_TOKEN:
            print("Warning: GITHUB_TOKEN not set. Private repositories may not be accessible.")
        
        # Validate numeric values
        if cls.GITINGEST_MAX_FILE_SIZE <= 0:
            raise ValueError("GITINGEST_MAX_FILE_SIZE must be positive")
        
        if cls.GITINGEST_TIMEOUT <= 0:
            raise ValueError("GITINGEST_TIMEOUT must be positive")
        
        return True
    
    @classmethod
    def get_github_token(cls) -> Optional[str]:
        """Get GitHub token with validation."""
        return cls.GITHUB_TOKEN
    
    @classmethod
    def get_default_exclude_patterns(cls) -> list:
        """Get default exclude patterns."""
        return cls.DEFAULT_EXCLUDE_PATTERNS.copy()
    
    @classmethod
    def get_default_include_patterns(cls) -> list:
        """Get default include patterns."""
        return cls.DEFAULT_INCLUDE_PATTERNS.copy()
