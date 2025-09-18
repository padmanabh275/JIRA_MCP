#!/usr/bin/env python3
"""Simple test script for the Jira Customer Support Chatbot."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test an endpoint and return the response."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        response.raise_for_status()
        return response.json()
    
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")
        return None

def main():
    """Run all tests."""
    print("Testing Jira Customer Support Chatbot...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    health = test_endpoint("/health")
    if health:
        print(f"✅ Health check passed: {health['status']}")
    else:
        print("❌ Health check failed")
    
    # Test 2: Basic chat
    print("\n2. Testing basic chat...")
    chat_response = test_endpoint("/chat", "POST", {"message": "Hello!"})
    if chat_response:
        print(f"✅ Chat response: {chat_response['response'][:100]}...")
    else:
        print("❌ Chat test failed")
    
    # Test 3: Epic query
    print("\n3. Testing epic query...")
    epic_response = test_endpoint("/chat", "POST", {"message": "How do I create an epic?"})
    if epic_response:
        print(f"✅ Epic response: {epic_response['response'][:100]}...")
        print(f"   Sources: {epic_response['sources']}")
    else:
        print("❌ Epic query test failed")
    
    # Test 4: Sprint query
    print("\n4. Testing sprint query...")
    sprint_response = test_endpoint("/chat", "POST", {"message": "Show me all sprints"})
    if sprint_response:
        print(f"✅ Sprint response: {sprint_response['response'][:100]}...")
        print(f"   Sources: {sprint_response['sources']}")
    else:
        print("❌ Sprint query test failed")
    
    # Test 5: MCP endpoints
    print("\n5. Testing MCP endpoints...")
    epic_list = test_endpoint("/mcp/epic/list")
    if epic_list:
        print(f"✅ Epic MCP: {epic_list.get('message', 'No message')}")
    else:
        print("❌ Epic MCP test failed")
    
    sprint_list = test_endpoint("/mcp/sprint/list")
    if sprint_list:
        print(f"✅ Sprint MCP: {sprint_list.get('message', 'No message')}")
    else:
        print("❌ Sprint MCP test failed")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
