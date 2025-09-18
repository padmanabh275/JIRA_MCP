#!/usr/bin/env python3
"""Quick test for epic creation functionality."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def quick_test():
    """Quick test of epic creation."""
    print("🔍 Quick Epic Creation Test")
    print("=" * 40)
    
    # Check environment variables
    jira_url = os.getenv('JIRA_BASE_URL')
    jira_email = os.getenv('JIRA_EMAIL')
    jira_token = os.getenv('JIRA_API_TOKEN')
    
    print(f"JIRA_BASE_URL: {jira_url}")
    print(f"JIRA_EMAIL: {jira_email}")
    print(f"JIRA_API_TOKEN: {'***' if jira_token else 'NOT SET'}")
    
    if not all([jira_url, jira_email, jira_token]):
        print("\n❌ Missing Jira credentials in .env file")
        print("Please check your .env file has:")
        print("JIRA_BASE_URL=https://your-domain.atlassian.net")
        print("JIRA_EMAIL=your-email@example.com")
        print("JIRA_API_TOKEN=your-api-token")
        return
    
    try:
        from mcp_client import MCPManager
        mcp_manager = MCPManager()
        
        # Test epic creation query
        test_query = "Create epic in DEMO with title Test Epic"
        print(f"\nTesting query: '{test_query}'")
        
        result = mcp_manager.handle_epic_query(test_query)
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()
