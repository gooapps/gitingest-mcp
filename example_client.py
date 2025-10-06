#!/usr/bin/env python3
"""
Example client for GitIngest MCP Server

This demonstrates how to connect to and use the MCP server
from another Python application.
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any


class GitIngestMCPClient:
    """Simple client for GitIngest MCP Server."""
    
    def __init__(self, server_command: str = "python mcp_server.py"):
        self.server_command = server_command
        self.process = None
    
    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command.split(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request to the MCP server."""
        if not self.process:
            await self.start_server()
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())
        
        return response
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return await self.send_request("tools/list")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool."""
        return await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
    
    async def ingest_repository(self, repository_url: str, **kwargs) -> str:
        """Ingest a repository and return the content."""
        response = await self.call_tool("ingest_repository", {
            "repository_url": repository_url,
            **kwargs
        })
        
        if "error" in response:
            raise Exception(f"MCP Error: {response['error']}")
        
        # Extract content from the response
        result = response.get("result", {})
        content = result.get("content", [])
        
        if content and len(content) > 0:
            return content[0].get("text", "")
        else:
            return ""


async def main():
    """Example usage of the MCP client."""
    print("GitIngest MCP Client Example")
    print("=" * 40)
    
    client = GitIngestMCPClient()
    
    try:
        # Start the server
        print("Starting MCP server...")
        await client.start_server()
        
        # List available tools
        print("\n1. Listing available tools...")
        tools_response = await client.list_tools()
        print(f"Response: {json.dumps(tools_response, indent=2)}")
        
        # Validate a repository URL
        print("\n2. Validating repository URL...")
        validation_response = await client.call_tool("validate_repository_url", {
            "repository_url": "https://github.com/octocat/Hello-World"
        })
        print(f"Validation result: {json.dumps(validation_response, indent=2)}")
        
        # Ingest a repository
        print("\n3. Ingesting repository...")
        try:
            content = await client.ingest_repository(
                "https://github.com/octocat/Hello-World",
                include_patterns=["*.md"],
                max_file_size=10240
            )
            print(f"Repository content (first 500 chars):")
            print(content[:500] + "..." if len(content) > 500 else content)
        except Exception as e:
            print(f"Error ingesting repository: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        await client.stop_server()
        print("\nMCP server stopped.")


if __name__ == "__main__":
    asyncio.run(main())
