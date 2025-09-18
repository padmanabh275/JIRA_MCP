"""Main application file for the Jira Customer Support Chatbot with Ollama support."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import Ollama version first, fallback to regular version
try:
    from chatbot_core_ollama import ChatbotCore, ChatResponse
    print("✅ Using enhanced chatbot core with Ollama support")
    OLLAMA_SUPPORT = True
except ImportError:
    from chatbot_core import ChatbotCore, ChatResponse
    print("⚠️  Using standard chatbot core (Ollama support not available)")
    OLLAMA_SUPPORT = False

from mcp_client import MCPManager
from documentation_scraper import DocumentationManager
from config import config

# Initialize components
app = FastAPI(title="Jira Customer Support Chatbot with Ollama", version="2.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global instances
chatbot = ChatbotCore()
mcp_manager = MCPManager()
doc_manager = DocumentationManager()

# Initialize documentation on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup."""
    print("Starting Jira Customer Support Chatbot with Ollama support...")
    
    # Show LLM backend info
    if hasattr(chatbot.llm, 'ollama_client') and chatbot.llm.ollama_client:
        print(f"🤖 Using Ollama backend with model: {chatbot.llm.ollama_client.model}")
    elif hasattr(chatbot.llm, 'pipeline') and chatbot.llm.pipeline:
        print("🤖 Using Transformers backend")
    else:
        print("🤖 Using fallback rule-based responses")
    
    # Initialize documentation (this might take a while on first run)
    print("Initializing documentation...")
    doc_manager.initialize_documentation()
    
    print("Chatbot ready!")

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    user_id: Optional[str] = None

class ChatResponseModel(BaseModel):
    """Response model for chat endpoint."""
    response: str
    confidence: float
    sources: list
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    components: Dict[str, str]
    llm_backend: str

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main chat interface."""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback to simple HTML if static file not found
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>Jira Chatbot (Ollama)</title></head>
        <body>
            <h1>Jira Customer Support Chatbot (Ollama)</h1>
            <p>Static files not found. Please ensure static/index.html exists.</p>
            <p>You can still use the API endpoints directly.</p>
        </body>
        </html>
        """)
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Jira Customer Support Chatbot (Ollama)</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .chat-container {{
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }}
            .chat-header {{
                background: #0052cc;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin: -20px -20px 20px -20px;
                text-align: center;
            }}
            .llm-info {{
                background: #e3f2fd;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
                text-align: center;
                font-weight: bold;
            }}
            .chat-messages {{
                height: 400px;
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 15px;
                margin-bottom: 15px;
                background: #fafafa;
                border-radius: 5px;
            }}
            .message {{
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 8px;
            }}
            .user-message {{
                background: #e3f2fd;
                margin-left: 20px;
            }}
            .bot-message {{
                background: #f1f8e9;
                margin-right: 20px;
            }}
            .chat-input {{
                display: flex;
                gap: 10px;
            }}
            .chat-input input {{
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }}
            .chat-input button {{
                padding: 12px 20px;
                background: #0052cc;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }}
            .chat-input button:hover {{
                background: #003d99;
            }}
            .examples {{
                margin-top: 20px;
                padding: 15px;
                background: #fff3cd;
                border-radius: 5px;
                border-left: 4px solid #ffc107;
            }}
            .examples h3 {{
                margin-top: 0;
                color: #856404;
            }}
            .examples ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            .examples li {{
                margin: 5px 0;
                color: #856404;
            }}
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>Jira Customer Support Chatbot</h1>
                <p>Ask me anything about Jira Software Cloud - Epics, Sprints, and more!</p>
            </div>
            
            <div class="llm-info">
                🤖 LLM Backend: {llm_info}
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    <strong>Bot:</strong> Hello! I'm your Jira Customer Support assistant. I can help you with questions about Epics, Sprints, and other Jira features. What would you like to know?
                </div>
            </div>
            
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Ask me about Jira..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
            
            <div class="examples">
                <h3>Try asking:</h3>
                <ul>
                    <li>How do I create an epic?</li>
                    <li>Show me all sprints</li>
                    <li>What is a sprint in Jira?</li>
                    <li>How do I manage epics?</li>
                    <li>List all epics in my project</li>
                </ul>
            </div>
        </div>

        <script>
            function handleKeyPress(event) {{
                if (event.key === 'Enter') {{
                    sendMessage();
                }}
            }}

            async function sendMessage() {{
                const input = document.getElementById('messageInput');
                const messages = document.getElementById('chatMessages');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message
                messages.innerHTML += `
                    <div class="message user-message">
                        <strong>You:</strong> ${{message}}
                    </div>
                `;
                
                input.value = '';
                messages.scrollTop = messages.scrollHeight;
                
                // Show typing indicator
                const typingDiv = document.createElement('div');
                typingDiv.className = 'message bot-message';
                typingDiv.innerHTML = '<strong>Bot:</strong> <em>Thinking...</em>';
                messages.appendChild(typingDiv);
                messages.scrollTop = messages.scrollHeight;
                
                try {{
                    const response = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{ message: message }})
                    }});
                    
                    const data = await response.json();
                    
                    // Remove typing indicator
                    messages.removeChild(typingDiv);
                    
                    // Add bot response
                    messages.innerHTML += `
                        <div class="message bot-message">
                            <strong>Bot:</strong> ${{data.response}}
                        </div>
                    `;
                    
                }} catch (error) {{
                    // Remove typing indicator
                    messages.removeChild(typingDiv);
                    
                    // Add error message
                    messages.innerHTML += `
                        <div class="message bot-message">
                            <strong>Bot:</strong> Sorry, I encountered an error. Please try again.
                        </div>
                    `;
                }}
                
                messages.scrollTop = messages.scrollHeight;
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponseModel)
async def chat(request: ChatRequest):
    """Handle chat requests."""
    try:
        # Determine if this is an Epic or Sprint related query
        query_lower = request.message.lower()
        external_context = None
        
        if any(word in query_lower for word in ["epic", "epics"]):
            # Try MCP first for Epic queries
            mcp_result = mcp_manager.handle_epic_query(request.message)
            
            if mcp_result.get("source") == "mcp":
                external_context = f"MCP Epic Data: {mcp_result.get('message', '')}"
                if mcp_result.get("data"):
                    external_context += f" Data: {str(mcp_result['data'])[:500]}..."
            else:
                # Fallback to documentation
                doc_result = doc_manager.get_epic_documentation()
                if doc_result.get("source") == "documentation":
                    external_context = f"Documentation: {doc_result.get('message', '')}"
        
        elif any(word in query_lower for word in ["sprint", "sprints"]):
            # Try MCP first for Sprint queries
            mcp_result = mcp_manager.handle_sprint_query(request.message)
            
            if mcp_result.get("source") == "mcp":
                external_context = f"MCP Sprint Data: {mcp_result.get('message', '')}"
                if mcp_result.get("data"):
                    external_context += f" Data: {str(mcp_result['data'])[:500]}..."
            else:
                # Fallback to documentation
                doc_result = doc_manager.get_sprint_documentation()
                if doc_result.get("source") == "documentation":
                    external_context = f"Documentation: {doc_result.get('message', '')}"
        
        else:
            # For general queries, try documentation search
            doc_result = doc_manager.search(request.message)
            if doc_result.get("source") == "documentation":
                external_context = f"Documentation: {doc_result.get('message', '')}"
        
        # Process the query with the chatbot core
        response = chatbot.process_query(request.message, external_context)
        
        return ChatResponseModel(
            response=response.message,
            confidence=response.confidence,
            sources=response.sources,
            metadata=response.metadata,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    components = {
        "chatbot_core": "healthy",
        "mcp_manager": "healthy",
        "documentation_manager": "healthy"
    }
    
    # Check LLM backend
    if hasattr(chatbot.llm, 'ollama_client') and chatbot.llm.ollama_client:
        llm_backend = "ollama"
        components["llm"] = "healthy (ollama)"
    elif hasattr(chatbot.llm, 'pipeline') and chatbot.llm.pipeline:
        llm_backend = "transformers"
        components["llm"] = "healthy (transformers)"
    else:
        llm_backend = "fallback"
        components["llm"] = "fallback_mode"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        components=components,
        llm_backend=llm_backend
    )

@app.get("/conversation/summary")
async def get_conversation_summary():
    """Get conversation summary."""
    return chatbot.get_conversation_summary()

@app.post("/conversation/reset")
async def reset_conversation():
    """Reset the conversation history."""
    chatbot.reset_conversation()
    return {"message": "Conversation reset successfully"}

@app.get("/mcp/epic/list")
async def list_epics():
    """List all epics via MCP."""
    result = mcp_manager.handle_epic_query("list all epics")
    return result

@app.get("/mcp/sprint/list")
async def list_sprints():
    """List all sprints via MCP."""
    result = mcp_manager.handle_sprint_query("list all sprints")
    return result

@app.get("/ollama/models")
async def list_ollama_models():
    """List available Ollama models."""
    if hasattr(chatbot.llm, 'ollama_client') and chatbot.llm.ollama_client:
        models = chatbot.llm.ollama_client.list_models()
        return {"models": models}
    else:
        return {"error": "Ollama not available"}

if __name__ == "__main__":
    print(f"Starting Jira Customer Support Chatbot with Ollama support on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "main_ollama:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
