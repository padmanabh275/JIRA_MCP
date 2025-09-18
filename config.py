"""Configuration settings for the Jira Customer Support Chatbot."""

import os
from typing import Optional

class Config:
    """Configuration class for the chatbot."""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Jira API settings
    JIRA_BASE_URL: str = os.getenv("JIRA_BASE_URL", "https://your-domain.atlassian.net")
    JIRA_API_TOKEN: Optional[str] = os.getenv("JIRA_API_TOKEN")
    JIRA_EMAIL: Optional[str] = os.getenv("JIRA_EMAIL")
    
    # MCP settings
    MCP_EPIC_API_URL: str = "https://developer.atlassian.com/server/jira/platform/rest/v11000/api-group-epic"
    MCP_SPRINT_API_URL: str = "https://developer.atlassian.com/server/jira/platform/rest/v11000/api-group-sprint"
    
    # Documentation settings
    JIRA_DOCS_URL: str = "https://support.atlassian.com/jira-software-cloud/resources/"
    
    # LLM settings
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "microsoft/DialoGPT-medium")
    MAX_RESPONSE_LENGTH: int = int(os.getenv("MAX_RESPONSE_LENGTH", "500"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    USE_OLLAMA: bool = os.getenv("USE_OLLAMA", "True").lower() == "true"
    
    # Vector database settings
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./vector_db")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Cache settings
    CACHE_DOCS: bool = os.getenv("CACHE_DOCS", "True").lower() == "true"
    CACHE_PATH: str = os.getenv("CACHE_PATH", "./cache")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        if not cls.JIRA_API_TOKEN and not cls.JIRA_EMAIL:
            print("Warning: JIRA_API_TOKEN and JIRA_EMAIL not set. MCP features will be limited.")
        return True

config = Config()
config.validate()
