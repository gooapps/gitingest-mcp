#!/usr/bin/env python3
"""
Test script for GitIngest MCP Server
"""

import asyncio
import json
import sys
from mcp_server import GitIngestMCPServer


async def test_mcp_server():
    """Test the MCP server functionality."""
    print("Testing GitIngest MCP Server...")
    
    # Create server instance
    server = GitIngestMCPServer()
    
    # Test 1: List tools
    print("\n1. Testing list_tools...")
    try:
        tools = await server.server.list_tools()
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"✗ Error listing tools: {e}")
        return False
    
    # Test 2: Validate repository URL
    print("\n2. Testing validate_repository_url...")
    test_urls = [
        "https://github.com/octocat/Hello-World",
        "https://github.com/microsoft/vscode",
        "https://invalid-url.com/repo",
        "not-a-url"
    ]
    
    for url in test_urls:
        try:
            result = await server._validate_repository_url({"repository_url": url})
            data = json.loads(result[0].text)
            status = "✓" if data.get("valid") else "✗"
            print(f"  {status} {url}: {data.get('error', 'Valid')}")
        except Exception as e:
            print(f"  ✗ {url}: Error - {e}")
    
    # Test 3: Test repository ingestion (if GitHub token is available)
    print("\n3. Testing repository ingestion...")
    test_repo = "https://github.com/octocat/Hello-World"
    
    try:
        result = await server._ingest_repository({
            "repository_url": test_repo,
            "include_patterns": ["*.md"],
            "max_file_size": 10240
        })
        
        if result and len(result) > 0:
            content = result[0].text
            if "Repository:" in content and "Files analyzed:" in content:
                print(f"✓ Successfully ingested {test_repo}")
                print(f"  Content length: {len(content)} characters")
                print(f"  Preview: {content[:200]}...")
            else:
                print(f"✗ Unexpected content format: {content[:100]}...")
        else:
            print("✗ No content returned")
            
    except Exception as e:
        print(f"✗ Error ingesting repository: {e}")
        print("  This might be due to missing GitHub token or network issues")
    
    print("\n✓ MCP Server tests completed!")
    return True


async def main():
    """Main test function."""
    try:
        await test_mcp_server()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
