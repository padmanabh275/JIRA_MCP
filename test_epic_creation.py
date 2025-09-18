#!/usr/bin/env python3
"""Diagnostic tool for epic creation issues."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_configuration():
    """Test the configuration settings."""
    print("🔧 Testing Configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    print("✅ .env file exists")
    
    # Check environment variables
    required_vars = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var} not set")
        else:
            # Mask sensitive values
            if var == 'JIRA_API_TOKEN':
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                masked_value = value
            print(f"✅ {var}: {masked_value}")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def test_imports():
    """Test if all required modules can be imported."""
    print("\n📦 Testing Imports...")
    
    try:
        from mcp_client import MCPManager
        print("✅ MCPManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MCPManager: {e}")
        return False
    
    try:
        from config import config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    return True

def test_mcp_client():
    """Test MCP client initialization."""
    print("\n🔌 Testing MCP Client...")
    
    try:
        from mcp_client import MCPManager
        mcp_manager = MCPManager()
        print("✅ MCPManager initialized successfully")
        
        # Check if client has authentication
        if hasattr(mcp_manager.client, 'headers') and 'Authorization' in mcp_manager.client.headers:
            print("✅ Authentication headers present")
        else:
            print("❌ No authentication headers found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize MCPManager: {e}")
        return False

def test_query_parsing():
    """Test epic query parsing."""
    print("\n🔍 Testing Query Parsing...")
    
    try:
        from mcp_client import MCPManager
        mcp_manager = MCPManager()
        
        # Test different query formats
        test_queries = [
            "Create epic in PROJ with title Test Epic",
            "Create epic project DEMO title My Epic",
            "How do I create an epic?",
            "Create epic in TEST named Sprint Planning"
        ]
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            result = mcp_manager.handle_epic_query(query)
            print(f"  Source: {result.get('source', 'unknown')}")
            print(f"  Message: {result.get('message', 'No message')}")
            
            if result.get('source') == 'mcp_error':
                print(f"  Error: {result.get('error', 'Unknown error')}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test query parsing: {e}")
        return False

def test_api_connection():
    """Test connection to Jira API."""
    print("\n🌐 Testing API Connection...")
    
    try:
        from mcp_client import MCPManager
        mcp_manager = MCPManager()
        
        # Try to get epics (this will test the connection)
        print("Attempting to connect to Jira API...")
        result = mcp_manager.handle_epic_query("list all epics")
        
        if result.get('source') == 'mcp':
            print("✅ Successfully connected to Jira API")
            return True
        else:
            print(f"❌ Failed to connect to Jira API: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ API connection test failed: {e}")
        return False

def test_epic_creation():
    """Test actual epic creation."""
    print("\n🏗️ Testing Epic Creation...")
    
    try:
        from mcp_client import MCPManager
        mcp_manager = MCPManager()
        
        # Test epic creation with a safe query
        test_query = "Create epic in DEMO with title Test Epic Creation"
        print(f"Testing epic creation with: '{test_query}'")
        
        result = mcp_manager.handle_epic_query(test_query)
        print(f"Result source: {result.get('source', 'unknown')}")
        print(f"Result message: {result.get('message', 'No message')}")
        
        if result.get('source') == 'mcp':
            print("✅ Epic creation successful!")
            return True
        else:
            print(f"❌ Epic creation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Epic creation test failed: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    print("🔍 Jira Epic Creation Diagnostic Tool")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Imports", test_imports),
        ("MCP Client", test_mcp_client),
        ("Query Parsing", test_query_parsing),
        ("API Connection", test_api_connection),
        ("Epic Creation", test_epic_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Epic creation should work.")
    else:
        print("\n💡 Troubleshooting Tips:")
        print("1. Check your .env file has correct Jira credentials")
        print("2. Verify your Jira API token is valid")
        print("3. Ensure you have 'Create Issues' permission in Jira")
        print("4. Make sure your project key exists (e.g., DEMO, PROJ)")
        print("5. Try the query format: 'Create epic in PROJECT_KEY with title Epic Name'")

if __name__ == "__main__":
    main()
