#!/usr/bin/env python3
"""
GitIngest MCP Server

An MCP server that integrates with GitIngest to generate repository context files
for private GitHub repositories, designed for LLM task resolution nodes.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict
from urllib.parse import urlparse

from mcp.server import Server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import gitingest, fallback to subprocess if not available
try:
    from gitingest import ingest, ingest_async
    GITINGEST_AVAILABLE = True
except ImportError:
    GITINGEST_AVAILABLE = False
    logger.warning("GitIngest package not found. Will use subprocess fallback.")


class GitIngestMCPServer:
    """MCP Server for GitIngest integration."""

    def __init__(self):
        self.server = Server("gitingest-mcp")
        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP server handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="ingest_repository",
                        description="Generate a text digest of a GitHub repository using GitIngest. Returns structured plain-text optimized for LLM consumption.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "repository_url": {
                                    "type": "string",
                                    "description": "GitHub repository URL (e.g., https://github.com/user/repo)",
                                },
                                "github_token": {
                                    "type": "string",
                                    "description": "GitHub personal access token for private repositories (optional if GITHUB_TOKEN env var is set)",
                                },
                                "branch": {
                                    "type": "string",
                                    "description": "Specific branch to analyze (defaults to repository's default branch)",
                                    "default": None,
                                },
                                "include_patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Include files matching Unix shell-style wildcards (e.g., ['*.py', '*.js'])",
                                    "default": [],
                                },
                                "exclude_patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Exclude files matching Unix shell-style wildcards (e.g., ['node_modules/*', '*.log'])",
                                    "default": [],
                                },
                                "max_file_size": {
                                    "type": "integer",
                                    "description": "Maximum file size in bytes to process (default: no limit)",
                                    "default": None,
                                },
                            },
                            "required": ["repository_url"],
                        },
                    ),
                    Tool(
                        name="ingest_repository_async",
                        description="Asynchronously generate a text digest of a GitHub repository. Better for batch processing multiple repositories.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "repository_url": {
                                    "type": "string",
                                    "description": "GitHub repository URL (e.g., https://github.com/user/repo)",
                                },
                                "github_token": {
                                    "type": "string",
                                    "description": "GitHub personal access token for private repositories (optional if GITHUB_TOKEN env var is set)",
                                },
                                "branch": {
                                    "type": "string",
                                    "description": "Specific branch to analyze (defaults to repository's default branch)",
                                    "default": None,
                                },
                                "include_patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Include files matching Unix shell-style wildcards",
                                    "default": [],
                                },
                                "exclude_patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Exclude files matching Unix shell-style wildcards",
                                    "default": [],
                                },
                                "max_file_size": {
                                    "type": "integer",
                                    "description": "Maximum file size in bytes to process",
                                    "default": None,
                                },
                            },
                            "required": ["repository_url"],
                        },
                    ),
                    Tool(
                        name="validate_repository_url",
                        description="Validate if a URL is a valid GitHub repository URL",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "repository_url": {
                                    "type": "string",
                                    "description": "Repository URL to validate",
                                }
                            },
                            "required": ["repository_url"],
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""

            if name == "ingest_repository":
                return await self._ingest_repository(arguments, sync=True)
            elif name == "ingest_repository_async":
                return await self._ingest_repository(arguments, sync=False)
            elif name == "validate_repository_url":
                return await self._validate_repository_url(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _validate_repository_url(self, arguments: Dict[str, Any]):
        """Validate GitHub repository URL."""
        repository_url = arguments.get("repository_url")

        if not repository_url:
            return self._create_text_result(json.dumps({
                "valid": False,
                "error": "Repository URL is required"
            }, indent=2))

        try:
            parsed = urlparse(repository_url)

            # Check if it's a GitHub URL
            if parsed.netloc not in ["github.com", "www.github.com"]:
                return self._create_text_result(json.dumps({
                    "valid": False,
                    "error": "URL must be a GitHub repository URL"
                }, indent=2))

            # Check if it has the right path structure
            path_parts = [p for p in parsed.path.split("/") if p]
            if len(path_parts) < 2:
                return self._create_text_result(json.dumps({
                    "valid": False,
                    "error": "URL must include owner and repository name"
                }, indent=2))

            owner, repo = path_parts[0], path_parts[1]

            return self._create_text_result(json.dumps({
                "valid": True,
                "owner": owner,
                "repository": repo,
                "full_name": f"{owner}/{repo}"
            }, indent=2))

        except Exception as e:
            return self._create_text_result(json.dumps({
                "valid": False,
                "error": f"Invalid URL format: {str(e)}"
            }, indent=2))

    async def _ingest_repository(self, arguments: Dict[str, Any], sync: bool = True):
        """Ingest repository using GitIngest."""
        repository_url = arguments.get("repository_url")
        github_token = arguments.get("github_token") or os.getenv("GITHUB_TOKEN")
        branch = arguments.get("branch")
        include_patterns = arguments.get("include_patterns", [])
        exclude_patterns = arguments.get("exclude_patterns", [])
        max_file_size = arguments.get("max_file_size")

        if not repository_url:
            return self._create_text_result("Error: Repository URL is required")

        # Validate URL first
        validation_result = await self._validate_repository_url({"repository_url": repository_url})
        validation_text = self._get_text_from_result(validation_result)
        validation_data = json.loads(validation_text)

        if not validation_data.get("valid"):
            return self._create_text_result(f"Error: {validation_data.get('error')}")

        try:
            logger.info(f"Starting repository ingestion for: {repository_url}")

            # Prepare GitIngest parameters
            ingest_kwargs = {}
            if github_token:
                ingest_kwargs["token"] = github_token
            if branch:
                ingest_kwargs["branch"] = branch
            if include_patterns:
                ingest_kwargs["include_patterns"] = include_patterns
            if exclude_patterns:
                ingest_kwargs["exclude_patterns"] = exclude_patterns
            if max_file_size:
                ingest_kwargs["max_file_size"] = max_file_size

            if GITINGEST_AVAILABLE:
                # Use GitIngest Python package
                if sync:
                    summary, tree, content = ingest(repository_url, **ingest_kwargs)
                else:
                    summary, tree, content = await ingest_async(repository_url, **ingest_kwargs)
            else:
                # Fallback to subprocess
                summary, tree, content = await self._ingest_via_subprocess(
                    repository_url, ingest_kwargs
                )

            # Combine all sections for LLM consumption
            full_context = f"{summary}\n\n{tree}\n\n{content}"

            logger.info(f"Successfully ingested repository: {repository_url}")

            return self._create_text_result(full_context)

        except Exception as e:
            error_msg = f"Error ingesting repository {repository_url}: {str(e)}"
            logger.error(error_msg)
            return self._create_text_result(error_msg)

    @staticmethod
    def _create_text_result(text: str):
        """Create a text-only result helper."""
        return {
            "content": [
                {
                    "type": "text",
                    "text": str(text)
                }
            ],
            "isError": False
        }

    @staticmethod
    def _get_text_from_result(result) -> str:
        """Extract the first text content entry from a result."""
        if isinstance(result, dict):
            content = result.get("content", [])
            if content and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict) and first_item.get("type") == "text":
                    return first_item.get("text", "")

        # Fallback for CallToolResult objects
        if hasattr(result, 'content') and result.content:
            for item in result.content:
                if isinstance(item, TextContent):
                    return item.text
                elif isinstance(item, dict) and item.get("type") == "text":
                    return item.get("text", "")

        raise ValueError("Expected text content in result")

    async def _ingest_via_subprocess(self, repository_url: str, ingest_kwargs: Dict[str, Any]) -> tuple:
        """Fallback method using subprocess to call gitingest CLI."""
        import subprocess

        # Build gitingest command
        cmd = ["gitingest", repository_url, "-o", "-"]

        # Add parameters
        if ingest_kwargs.get("token"):
            cmd.extend(["-t", ingest_kwargs["token"]])
        if ingest_kwargs.get("branch"):
            cmd.extend(["-b", ingest_kwargs["branch"]])
        if ingest_kwargs.get("include_patterns"):
            for pattern in ingest_kwargs["include_patterns"]:
                cmd.extend(["-i", pattern])
        if ingest_kwargs.get("exclude_patterns"):
            for pattern in ingest_kwargs["exclude_patterns"]:
                cmd.extend(["-e", pattern])
        if ingest_kwargs.get("max_file_size"):
            cmd.extend(["-s", str(ingest_kwargs["max_file_size"])])

        try:
            # Run gitingest command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"GitIngest CLI failed: {stderr.decode()}")

            # Parse the output (GitIngest CLI returns combined output)
            output = stdout.decode()

            # Split into sections (this is a simplified parser)
            lines = output.split('\n')
            summary_lines = []
            tree_lines = []
            content_lines = []

            current_section = "summary"
            for line in lines:
                if line.startswith("Directory structure:"):
                    current_section = "tree"
                    tree_lines.append(line)
                elif line.startswith("================================================"):
                    current_section = "content"
                    content_lines.append(line)
                else:
                    if current_section == "summary":
                        summary_lines.append(line)
                    elif current_section == "tree":
                        tree_lines.append(line)
                    elif current_section == "content":
                        content_lines.append(line)

            summary = '\n'.join(summary_lines).strip()
            tree = '\n'.join(tree_lines).strip()
            content = '\n'.join(content_lines).strip()

            return summary, tree, content

        except FileNotFoundError:
            raise Exception("GitIngest CLI not found. Please install gitingest package or ensure gitingest command is available.")
        except Exception as e:
            raise Exception(f"Subprocess execution failed: {str(e)}")

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="gitingest-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities=None,
                    ),
                ),
            )


async def main():
    """Main entry point."""
    server = GitIngestMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
