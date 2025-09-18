# Jira Customer Support Chatbot with MCP

A chatbot that acts as a customer service agent for Jira Software Cloud, with Model Context Protocol (MCP) integration for Epic and Sprint APIs.

## Features

- **Local LLM Integration**: Uses open-source models (no proprietary APIs)
- **MCP Protocol**: Implements Model Context Protocol for Jira Epic and Sprint APIs
- **Documentation Fallback**: Falls back to Jira help documentation when MCP APIs don't have the answer
- **Web Interface**: Simple web interface for testing the chatbot
- **Offline Capable**: Can run without internet access to proprietary LLM services

## Architecture

The chatbot follows a layered architecture:

1. **Web Interface**: FastAPI-based web server for user interaction
2. **Chatbot Core**: Manages conversation flow and decision making
3. **MCP Layer**: Handles communication with Jira APIs
4. **Documentation Layer**: Retrieves information from Jira help docs
5. **LLM Layer**: Local language model for generating responses

## Quick Start

### Option 1: Automated Setup
```bash
python setup.py
```

### Option 2: Manual Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy environment file: `cp env.example .env`
3. Edit `.env` with your Jira credentials (optional)
4. Run the application: `python main.py`
5. Open your browser to `http://localhost:8000`

### Option 3: Docker Deployment
```bash
docker-compose up --build
```

## Configuration

### Jira Credentials (Optional)
To enable MCP features, add your Jira credentials to `.env`:
```bash
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### Environment Variables
- `JIRA_BASE_URL`: Your Jira instance URL
- `JIRA_EMAIL`: Your Jira email address
- `JIRA_API_TOKEN`: Your Jira API token
- `DEBUG`: Enable debug mode (True/False)
- `PORT`: Server port (default: 8000)

## Testing

### Run Tests
```bash
python test_chatbot.py
```

### Test Examples
- Open `http://localhost:8000` in your browser
- Try asking: "How do I create an epic?"
- Try asking: "Show me all sprints"
- Try asking: "What is Jira Software Cloud?"

### Creating Epics and Sprints
With proper Jira credentials configured, you can create epics and sprints:

**Create Epic:**
```
"Create epic in PROJ with title My New Epic"
```

**Create Sprint:**
```
"Create sprint in board 123 named Sprint 1"
```

See `CREATING_EPICS_SPRINTS.md` for detailed instructions.

See `TESTING.md` for comprehensive testing instructions.

## Troubleshooting

### Installation Issues

If you encounter dependency installation problems:

1. **Try minimal installation first:**
   ```bash
   pip install -r requirements-minimal.txt
   ```

2. **For PyTorch issues, install separately:**
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Use conda for better dependency management:**
   ```bash
   conda install pytorch transformers -c pytorch -c huggingface
   pip install -r requirements-minimal.txt
   ```

4. **Install system dependencies (Linux):**
   ```bash
   sudo apt-get install python3-dev build-essential
   ```

### Common Issues

- **PyTorch version conflicts**: Use the latest compatible version
- **Memory issues**: The chatbot will fall back to rule-based responses if LLM fails to load
- **Network issues**: Documentation scraping requires internet access initially

## Documentation

See `DOCUMENTATION.md` for technical details about the implementation.
