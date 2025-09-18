"""Ollama client for local LLM integration."""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time

@dataclass
class OllamaMessage:
    """Represents a message in Ollama chat format."""
    role: str  # "user" or "assistant"
    content: str

@dataclass
class OllamaResponse:
    """Represents an Ollama response."""
    message: str
    done: bool
    model: str

class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.conversation_history: List[OllamaMessage] = []
        self.max_history = 10
        
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to Ollama API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ollama API error: {e}")
            return {"error": str(e)}
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate a response using Ollama."""
        # Prepare the prompt with context
        full_prompt = self._prepare_prompt(prompt, context)
        
        # Add user message to history
        self.conversation_history.append(OllamaMessage(role="user", content=prompt))
        
        # Prepare messages for API
        messages = []
        for msg in self.conversation_history[-self.max_history:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Make API request
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 500
            }
        }
        
        response = self._make_request("/api/generate", data)
        
        if "error" in response:
            return self._generate_fallback_response(prompt)
        
        # Extract response message
        if "response" in response:
            assistant_message = response["response"]
            
            # Add assistant response to history
            self.conversation_history.append(OllamaMessage(role="assistant", content=assistant_message))
            
            # Clean up history
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            return assistant_message
        else:
            return self._generate_fallback_response(prompt)
    
    def _prepare_prompt(self, user_input: str, context: str = "") -> str:
        """Prepare the prompt for Ollama."""
        system_prompt = """You are a helpful Jira customer support chatbot. You help users with questions about Jira Software Cloud, including Epics, Sprints, Issues, and other Jira features. Be helpful, accurate, and concise in your responses."""
        
        if context:
            system_prompt += f"\n\nContext: {context}"
        
        return system_prompt
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when Ollama is unavailable."""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["epic", "epics"]):
            return "I can help you with Epic-related questions. Epics are large pieces of work that can be broken down into smaller tasks. You can create, view, and manage epics in Jira Software Cloud."
        
        elif any(word in prompt_lower for word in ["sprint", "sprints"]):
            return "I can help you with Sprint-related questions. Sprints are time-boxed iterations in Agile development, typically lasting 1-4 weeks. You can create, manage, and track sprints in Jira Software Cloud."
        
        elif any(word in prompt_lower for word in ["create", "add", "new"]):
            return "I can help you create new items in Jira. Whether you need to create epics, sprints, or issues, I can guide you through the process."
        
        elif any(word in prompt_lower for word in ["how", "what", "where", "when", "why"]):
            return "I can help you understand how to use Jira Software Cloud. Please ask me a specific question about epics, sprints, or any other Jira features."
        
        else:
            return "I'm here to help you with Jira Software Cloud. I can assist with questions about epics, sprints, issues, and other Jira features. What would you like to know?"
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            models = []
            if "models" in data:
                for model in data["models"]:
                    models.append(model.get("name", ""))
            
            return models
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama."""
        try:
            data = {"name": model_name}
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=data,
                stream=True,
                timeout=300
            )
            
            if response.status_code == 200:
                print(f"Successfully pulled model: {model_name}")
                return True
            else:
                print(f"Failed to pull model: {model_name}")
                return False
                
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            return False
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        return {
            "message_count": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m.role == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m.role == "assistant"]),
            "model": self.model
        }
