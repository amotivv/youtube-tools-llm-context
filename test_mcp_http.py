#!/usr/bin/env python3
"""
Test script for HTTP MCP Server
"""

import requests
import json
import sys

# Base URL for the server
BASE_URL = "http://localhost:8080"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_mcp_health():
    """Test the MCP health endpoint"""
    print("Testing MCP health endpoint...")
    response = requests.get(f"{BASE_URL}/mcp/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_initialize():
    """Test MCP initialization"""
    print("Testing MCP initialization...")
    data = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "clientInfo": {
                "name": "test-client",
                "version": "1.0"
            }
        },
        "id": 1
    }
    response = requests.post(f"{BASE_URL}/mcp/initialize", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    return response.json().get('result', {}).get('sessionId')

def test_list_tools():
    """Test listing tools"""
    print("Testing list tools...")
    data = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    response = requests.post(f"{BASE_URL}/mcp/list_tools", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_get_info():
    """Test getting video info"""
    print("Testing get video info...")
    data = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "youtube_get_info",
            "arguments": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        },
        "id": 3
    }
    response = requests.post(f"{BASE_URL}/mcp/call_tool", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    if 'result' in result:
        # Parse the nested JSON in the text content
        content = json.loads(result['result']['content'][0]['text'])
        print(f"Video Info: {json.dumps(content, indent=2)}")
    else:
        print(f"Response: {json.dumps(result, indent=2)}")
    print()

def main():
    """Run all tests"""
    print("YouTube MCP HTTP Server Test Suite")
    print("=" * 50)
    
    try:
        test_health()
        test_mcp_health()
        session_id = test_initialize()
        test_list_tools()
        test_get_info()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server at", BASE_URL)
        print("Make sure the server is running with: docker-compose up")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
