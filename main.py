"""Main application file for the Jira Customer Support Chatbot."""

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

from chatbot_core import ChatbotCore, ChatResponse
from mcp_client import MCPManager
from documentation_scraper import DocumentationManager
from config import config

# Initialize components
app = FastAPI(title="Jira Customer Support Chatbot", version="1.0.0")

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
    print("Starting Jira Customer Support Chatbot...")
    
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
        <head><title>Jira Chatbot</title></head>
        <body>
            <h1>Jira Customer Support Chatbot</h1>
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
                # For successful MCP operations, return the result directly
                if mcp_result.get("type") == "epic_created":
                    epic_data = mcp_result.get("data", {})
                    epic_key = epic_data.get("key", "Unknown")
                    success_message = f"✅ {mcp_result.get('message', 'Epic created successfully')} (Epic: {epic_key})"
                    
                    return ChatResponseModel(
                        response=success_message,
                        confidence=1.0,
                        sources=["mcp_epic_creation"],
                        metadata={"intents": {"epic": 1.0, "create": 1.0}, "has_external_context": False, "mcp_result": mcp_result},
                        timestamp=datetime.now().isoformat()
                    )
                else:
                    # Other MCP operations - pass to LLM with context
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
                # For successful MCP operations, return the result directly
                if mcp_result.get("type") == "sprint_created":
                    sprint_data = mcp_result.get("data", {})
                    sprint_id = sprint_data.get("id", "Unknown")
                    sprint_name = sprint_data.get("name", "Unknown")
                    board_id = sprint_data.get("originBoardId", "Unknown")
                    success_message = f"✅ {mcp_result.get('message', 'Sprint created successfully')} (Sprint ID: {sprint_id}, Board: {board_id})"
                    
                    return ChatResponseModel(
                        response=success_message,
                        confidence=1.0,
                        sources=["mcp_sprint_creation"],
                        metadata={"intents": {"sprint": 1.0, "create": 1.0}, "has_external_context": False, "mcp_result": mcp_result},
                        timestamp=datetime.now().isoformat()
                    )
                else:
                    # Other MCP operations - pass to LLM with context
                    external_context = f"MCP Sprint Data: {mcp_result.get('message', '')}"
                    if mcp_result.get("data"):
                        external_context += f" Data: {str(mcp_result['data'])[:500]}..."
            else:
                # Fallback to documentation
                doc_result = doc_manager.get_sprint_documentation()
                if doc_result.get("source") == "documentation":
                    external_context = f"Documentation: {doc_result.get('message', '')}"
        
        elif any(word in query_lower for word in ["board", "boards"]):
            # Try MCP first for Board queries
            mcp_result = mcp_manager.handle_board_query(request.message)
            
            if mcp_result.get("source") == "mcp":
                # For board listings, return the result directly
                if mcp_result.get("type") == "boards_list":
                    boards_data = mcp_result.get("data", [])
                    boards_text = "\n".join([
                        f"📋 **{board['name']}** (ID: {board['id']}, Type: {board['type']}, Project: {board['location']})"
                        for board in boards_data
                    ])
                    
                    success_message = f"📋 **Available Boards:**\n\n{boards_text}\n\nTotal: {len(boards_data)} boards"
                    
                    return ChatResponseModel(
                        response=success_message,
                        confidence=1.0,
                        sources=["mcp_boards_list"],
                        metadata={"intents": {"board": 1.0, "list": 1.0}, "has_external_context": False, "mcp_result": mcp_result},
                        timestamp=datetime.now().isoformat()
                    )
                else:
                    # Other board operations - pass to LLM with context
                    external_context = f"MCP Board Data: {mcp_result.get('message', '')}"
                    if mcp_result.get("data"):
                        external_context += f" Data: {str(mcp_result['data'])[:500]}..."
            else:
                # Fallback to documentation
                external_context = "Board documentation: Jira boards help you visualize and manage your work. You can create different types of boards like Scrum boards, Kanban boards, etc."
        
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
    
    # Check if LLM is loaded
    if chatbot.llm.pipeline is None:
        components["llm"] = "fallback_mode"
    else:
        components["llm"] = "healthy"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        components=components
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

if __name__ == "__main__":
    print(f"Starting Jira Customer Support Chatbot on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
