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
        "main_ollama_clean:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
