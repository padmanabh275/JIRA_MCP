# Technical Documentation: Jira Customer Support Chatbot with MCP

## Overview

The Jira Customer Support Chatbot is a sophisticated AI-powered assistant that provides customer support for Jira Software Cloud. It implements the Model Context Protocol (MCP) for direct integration with Jira APIs while maintaining fallback capabilities to documentation when needed.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Chatbot Core   │    │   Local LLM     │
│   (FastAPI)     │◄──►│   (Orchestrator)│◄──►│  (Transformers) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────▼────────┐              │
         │              │                 │              │
         │              ▼                 ▼              │
         │    ┌─────────────────┐ ┌─────────────────┐    │
         │    │   MCP Client    │ │ Documentation   │    │
         │    │  (Jira APIs)    │ │   Scraper       │    │
         │    └─────────────────┘ └─────────────────┘    │
         │              │                 │              │
         │              ▼                 ▼              │
         │    ┌─────────────────┐ ┌─────────────────┐    │
         │    │   Jira Cloud    │ │ Vector Database │    │
         │    │      APIs       │ │   (ChromaDB)    │    │
         │    └─────────────────┘ └─────────────────┘    │
         └─────────────────────────────────────────────────┘
```

### Component Overview

1. **Web Interface** (`main.py`): FastAPI-based REST API with HTML chat interface
2. **Chatbot Core** (`chatbot_core.py`): Main orchestrator handling conversation flow
3. **Local LLM** (`chatbot_core.py`): Open-source language model for response generation
4. **MCP Client** (`mcp_client.py`): Model Context Protocol implementation for Jira APIs
5. **Documentation Scraper** (`documentation_scraper.py`): Web scraper and vector database manager
6. **Configuration** (`config.py`): Centralized configuration management

## Information Retrieval and Prioritization

### Decision Flow

The chatbot follows a sophisticated decision tree for information retrieval:

```
User Query
    │
    ▼
Intent Classification
    │
    ├── Epic-related? ──► MCP Epic API ──► Success? ──► Use MCP Data
    │                              │
    │                              ▼
    │                              Fail ──► Documentation Search ──► Fallback Response
    │
    ├── Sprint-related? ──► MCP Sprint API ──► Success? ──► Use MCP Data
    │                                │
    │                                ▼
    │                                Fail ──► Documentation Search ──► Fallback Response
    │
    └── General Query ──► Documentation Search ──► Generate Response
```

### Priority System

1. **Primary**: MCP APIs (Epic and Sprint)
   - Direct access to live Jira data
   - Real-time information
   - Structured responses

2. **Secondary**: Documentation Search
   - Vector similarity search
   - Cached documentation content
   - Semantic understanding

3. **Tertiary**: Local LLM Knowledge
   - General Jira concepts
   - Fallback responses
   - Rule-based responses

### Information Sources

| Source | Priority | Use Case | Data Type |
|--------|----------|----------|-----------|
| MCP Epic API | 1 | Epic-specific queries | Live Jira data |
| MCP Sprint API | 1 | Sprint-specific queries | Live Jira data |
| Documentation | 2 | General queries, fallback | Scraped web content |
| Local LLM | 3 | General knowledge | Pre-trained knowledge |

## MCP Integration

### Model Context Protocol Implementation

The MCP implementation provides a standardized interface for interacting with Jira APIs:

#### Epic API Integration

```python
class JiraMCPClient:
    def get_epics(self, project_key: Optional[str] = None) -> MCPResponse
    def get_epic(self, epic_key: str) -> MCPResponse
    def create_epic(self, project_key: str, summary: str, description: str) -> MCPResponse
    def update_epic(self, epic_key: str, updates: Dict[str, Any]) -> MCPResponse
```

#### Sprint API Integration

```python
class JiraMCPClient:
    def get_sprints(self, board_id: Optional[int] = None) -> MCPResponse
    def get_sprint(self, sprint_id: int) -> MCPResponse
    def create_sprint(self, name: str, board_id: int, start_date: str, end_date: str) -> MCPResponse
    def update_sprint(self, sprint_id: int, updates: Dict[str, Any]) -> MCPResponse
    def get_sprint_issues(self, sprint_id: int) -> MCPResponse
```

### MCP Request/Response Format

#### Request Structure
```python
@dataclass
class MCPRequest:
    method: str                    # HTTP method (GET, POST, PUT)
    url: str                      # API endpoint URL
    headers: Dict[str, str]       # HTTP headers
    data: Optional[Dict[str, Any]] # Request body (for POST/PUT)
```

#### Response Structure
```python
@dataclass
class MCPResponse:
    success: bool                 # Request success status
    data: Optional[Dict[str, Any]] # Response data
    error: Optional[str]          # Error message if failed
```

### Authentication

The MCP client supports multiple authentication methods:

1. **API Token Authentication** (Recommended)
   ```python
   headers["Authorization"] = f"Basic {base64_encode(email:token)}"
   ```

2. **Username/Password Authentication**
   ```python
   headers["Authorization"] = f"Basic {base64_encode(username:password)}"
   ```

## Documentation System

### Web Scraping Architecture

The documentation system uses a multi-layered approach:

1. **Discovery**: Automatically finds documentation pages from the main resources URL
2. **Scraping**: Extracts structured content using BeautifulSoup
3. **Processing**: Chunks content for optimal vector search
4. **Indexing**: Stores embeddings in ChromaDB vector database

### Vector Database Integration

```python
# ChromaDB Collection Structure
collection = {
    "name": "jira_docs",
    "documents": [chunked_text],
    "embeddings": [sentence_transformer_embeddings],
    "metadatas": [{
        "url": "original_page_url",
        "title": "page_title",
        "chunk_index": 0,
        "total_chunks": N
    }],
    "ids": ["unique_document_ids"]
}
```

### Search Algorithm

1. **Query Processing**: Convert user query to embedding using SentenceTransformer
2. **Similarity Search**: Find most similar document chunks using cosine similarity
3. **Ranking**: Rank results by similarity score
4. **Context Extraction**: Extract relevant context for LLM generation

## Local LLM Integration

### Model Selection

The system uses `microsoft/DialoGPT-medium` as the primary local model:

- **Size**: ~345MB (suitable for local deployment)
- **Performance**: Good for conversational AI
- **Requirements**: Minimal computational resources
- **License**: Open source (MIT)

### Response Generation Pipeline

```python
def generate_response(self, prompt: str, context: str = "") -> str:
    # 1. Format prompt with context
    formatted_prompt = self._format_prompt(prompt, context)
    
    # 2. Generate using local model
    response = self.pipeline(formatted_prompt, ...)
    
    # 3. Clean and format response
    cleaned_response = self._clean_response(response)
    
    # 4. Return final response
    return cleaned_response
```

### Fallback System

When the local LLM is unavailable:

1. **Rule-based Responses**: Pre-defined responses for common intents
2. **Template Matching**: Pattern-based response generation
3. **Context-aware Fallbacks**: Responses based on detected intent

## API Endpoints

### Core Chat Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main chat interface (HTML) |
| `/chat` | POST | Process chat messages |
| `/health` | GET | System health check |

### MCP Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp/epic/list` | GET | List all epics via MCP |
| `/mcp/sprint/list` | GET | List all sprints via MCP |

### Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/conversation/summary` | GET | Get conversation summary |
| `/conversation/reset` | POST | Reset conversation history |

### Request/Response Examples

#### Chat Request
```json
{
    "message": "How do I create an epic?",
    "user_id": "optional_user_id"
}
```

#### Chat Response
```json
{
    "response": "To create an epic in Jira Software Cloud...",
    "confidence": 0.85,
    "sources": ["mcp", "intent_epic"],
    "metadata": {
        "intents": {"epic": 0.9, "create": 0.8},
        "has_external_context": true
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Configuration Management

### Environment Variables

```bash
# Jira Configuration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Application Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# LLM Configuration
LLM_MODEL_NAME=microsoft/DialoGPT-medium
MAX_RESPONSE_LENGTH=500
TEMPERATURE=0.7
```

### Configuration Class

The `Config` class centralizes all configuration:

```python
class Config:
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Jira API settings
    JIRA_BASE_URL: str
    JIRA_API_TOKEN: Optional[str]
    
    # MCP settings
    MCP_EPIC_API_URL: str
    MCP_SPRINT_API_URL: str
    
    # Documentation settings
    JIRA_DOCS_URL: str
    
    # LLM settings
    LLM_MODEL_NAME: str
    MAX_RESPONSE_LENGTH: int
    
    # Vector database settings
    VECTOR_DB_PATH: str
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
```

## Error Handling and Resilience

### Error Categories

1. **Network Errors**: API timeouts, connection failures
2. **Authentication Errors**: Invalid credentials, expired tokens
3. **Rate Limiting**: API quota exceeded
4. **Model Errors**: LLM loading failures, generation errors
5. **Data Errors**: Invalid input, parsing failures

### Resilience Strategies

1. **Graceful Degradation**: Fall back to documentation when MCP fails
2. **Retry Logic**: Automatic retry with exponential backoff
3. **Circuit Breaker**: Temporarily disable failing services
4. **Caching**: Cache responses to reduce API calls
5. **Timeout Management**: Prevent hanging requests

### Error Response Format

```json
{
    "error": "error_type",
    "message": "Human-readable error message",
    "details": {
        "component": "mcp_client",
        "operation": "get_epics",
        "timestamp": "2024-01-15T10:30:00Z"
    },
    "fallback_used": true
}
```

## Performance Considerations

### Optimization Strategies

1. **Model Loading**: Load model once at startup
2. **Connection Pooling**: Reuse HTTP connections
3. **Caching**: Cache documentation and API responses
4. **Async Operations**: Use async/await for I/O operations
5. **Resource Management**: Proper cleanup of resources

### Scalability

1. **Horizontal Scaling**: Stateless design allows multiple instances
2. **Load Balancing**: Can be deployed behind a load balancer
3. **Database Scaling**: ChromaDB supports clustering
4. **API Rate Limiting**: Built-in rate limiting for Jira APIs

### Monitoring

1. **Health Checks**: Regular health check endpoints
2. **Metrics**: Response times, error rates, success rates
3. **Logging**: Structured logging for debugging
4. **Alerting**: Alerts for critical failures

## Security Considerations

### Authentication

1. **API Token Security**: Store tokens securely, use environment variables
2. **HTTPS**: Use HTTPS for all communications
3. **Input Validation**: Validate all user inputs
4. **Rate Limiting**: Prevent abuse with rate limiting

### Data Privacy

1. **No Data Storage**: Don't store user conversations permanently
2. **Secure Transmission**: Encrypt data in transit
3. **Access Control**: Implement proper access controls
4. **Audit Logging**: Log access for security auditing

## Deployment Options

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Cloud Deployment

The application can be deployed to:
- **AWS**: EC2, ECS, Lambda
- **Google Cloud**: Compute Engine, Cloud Run
- **Azure**: App Service, Container Instances
- **Heroku**: Direct deployment

## Future Enhancements

### Planned Features

1. **Multi-language Support**: Support for multiple languages
2. **Advanced Analytics**: Conversation analytics and insights
3. **Custom Models**: Fine-tuned models for specific use cases
4. **Integration APIs**: Webhook support for external integrations
5. **Admin Interface**: Web-based administration panel

### Technical Improvements

1. **Model Optimization**: Smaller, faster models
2. **Caching Improvements**: Redis-based caching
3. **Real-time Updates**: WebSocket support for real-time chat
4. **Advanced Search**: Hybrid search (semantic + keyword)
5. **Personalization**: User-specific responses and preferences

This technical documentation provides a comprehensive overview of the Jira Customer Support Chatbot's architecture, implementation, and operational considerations. The system is designed to be robust, scalable, and maintainable while providing excellent user experience through intelligent information retrieval and response generation.
