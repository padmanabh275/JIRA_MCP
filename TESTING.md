# Testing Guide for Jira Customer Support Chatbot

This document provides comprehensive testing instructions and examples for the Jira Customer Support Chatbot with MCP integration.

## Prerequisites

1. **Python Environment**: Python 3.8 or higher
2. **Dependencies**: Install all requirements from `requirements.txt`
3. **Jira Credentials** (Optional): For full MCP functionality
   - Jira instance URL
   - API token or email/password

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Create a `.env` file in the project root:

```bash
# Jira Configuration (Optional - for MCP features)
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### 3. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:8000`

## Testing Scenarios

### 1. Basic Functionality Tests

#### Test 1: Web Interface
1. Open browser to `http://localhost:8000`
2. Verify the chat interface loads correctly
3. Check that example questions are displayed

**Expected Result**: Clean, responsive web interface with chat input and example questions.

#### Test 2: Health Check
```bash
curl http://localhost:8000/health
```

**Expected Result**: JSON response showing all components as "healthy" or "fallback_mode".

### 2. Chatbot Core Tests

#### Test 3: Basic Conversation
Send a POST request to `/chat`:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, what can you help me with?"}'
```

**Expected Result**: Friendly greeting response from the chatbot.

#### Test 4: Intent Classification
Test various intents:

```bash
# Epic intent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I create an epic?"}'

# Sprint intent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me all sprints"}'

# Help intent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Jira?"}'
```

**Expected Result**: Responses should be relevant to the detected intent with appropriate confidence scores.

### 3. MCP Integration Tests

#### Test 5: Epic MCP Operations
```bash
# List epics
curl "http://localhost:8000/mcp/epic/list"

# Chat about epics
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "List all epics in my project"}'
```

**Expected Result**: 
- If Jira credentials are configured: Returns actual epic data
- If not configured: Returns appropriate error message or falls back to documentation

#### Test 6: Sprint MCP Operations
```bash
# List sprints
curl "http://localhost:8000/mcp/sprint/list"

# Chat about sprints
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I create a new sprint?"}'
```

**Expected Result**: Similar to epic tests - either real data or fallback to documentation.

### 4. Documentation Fallback Tests

#### Test 7: Documentation Search
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I manage issues in Jira?"}'
```

**Expected Result**: Response should include information from Jira documentation.

#### Test 8: General Knowledge Questions
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Agile methodology?"}'
```

**Expected Result**: Helpful response about Agile, possibly with references to Jira features.

### 5. Conversation Management Tests

#### Test 9: Conversation History
```bash
# Send multiple messages
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'

curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Tell me about epics"}'

# Get conversation summary
curl "http://localhost:8000/conversation/summary"
```

**Expected Result**: Summary shows message count and recent topics.

#### Test 10: Reset Conversation
```bash
curl -X POST "http://localhost:8000/conversation/reset"
```

**Expected Result**: Success message, conversation history cleared.

### 6. Error Handling Tests

#### Test 11: Invalid Input
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": ""}'
```

**Expected Result**: Graceful handling of empty messages.

#### Test 12: Malformed Requests
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"invalid": "data"}'
```

**Expected Result**: Proper error response with validation details.

## Sample Test Script

Create a file called `test_chatbot.py`:

```python
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
```

Run the test script:
```bash
python test_chatbot.py
```

## Performance Testing

### Load Testing
Use a tool like `wrk` or `ab` to test the API under load:

```bash
# Install wrk (if available)
# Test with 10 concurrent users for 30 seconds
wrk -t10 -c10 -d30s -s test_script.lua http://localhost:8000/chat

# Or use Apache Bench
ab -n 100 -c 10 -p chat_request.json -T application/json http://localhost:8000/chat
```

### Memory Usage
Monitor memory usage during operation:
```bash
# On Linux/Mac
top -p $(pgrep -f "python main.py")

# Or use htop for better visualization
htop
```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - **Symptom**: LLM fails to load, falls back to rule-based responses
   - **Solution**: Check internet connection for model download, ensure sufficient disk space

2. **MCP Authentication Errors**
   - **Symptom**: MCP endpoints return authentication errors
   - **Solution**: Verify Jira credentials in `.env` file or environment variables

3. **Documentation Scraping Issues**
   - **Symptom**: Documentation search returns no results
   - **Solution**: Check internet connection, verify Atlassian documentation URLs are accessible

4. **Port Already in Use**
   - **Symptom**: Application fails to start
   - **Solution**: Change port in `config.py` or kill existing process

### Debug Mode

Enable debug logging by setting `DEBUG=True` in `config.py` or running:
```bash
DEBUG=True python main.py
```

### Log Files

The application logs to console by default. For production, consider redirecting to files:
```bash
python main.py > chatbot.log 2>&1
```

## Success Criteria

A successful test should demonstrate:

1. ✅ **Web Interface**: Clean, responsive chat interface
2. ✅ **Basic Chat**: Bot responds appropriately to greetings and general questions
3. ✅ **Intent Recognition**: Correctly identifies Epic, Sprint, and other intents
4. ✅ **MCP Integration**: Either returns real Jira data or gracefully falls back
5. ✅ **Documentation Fallback**: Provides helpful information from Jira docs
6. ✅ **Error Handling**: Gracefully handles invalid inputs and edge cases
7. ✅ **Conversation Flow**: Maintains context across multiple messages
8. ✅ **Performance**: Responds within reasonable time (< 5 seconds for most queries)

## Test Data Examples

### Epic-Related Queries
- "How do I create an epic?"
- "List all epics in my project"
- "What is an epic in Jira?"
- "Show me epic EPIC-123"
- "How do I manage epics?"

### Sprint-Related Queries
- "How do I create a sprint?"
- "Show me all sprints"
- "What is a sprint?"
- "How do I manage sprint 123?"
- "Tell me about sprint planning"

### General Jira Queries
- "What is Jira Software Cloud?"
- "How do I create an issue?"
- "What is Agile methodology?"
- "How do I track project progress?"
- "What are Jira workflows?"

This comprehensive testing approach ensures the chatbot works correctly across all its features and gracefully handles various scenarios.
