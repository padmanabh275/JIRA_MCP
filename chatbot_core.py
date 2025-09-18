"""Chatbot core with local LLM integration."""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config import config

@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChatResponse:
    """Represents a chatbot response."""
    message: str
    confidence: float
    sources: List[str]
    metadata: Optional[Dict[str, Any]] = None

class LocalLLM:
    """Local language model wrapper."""
    
    def __init__(self):
        self.model_name = config.LLM_MODEL_NAME
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the local language model."""
        try:
            print(f"Loading local model: {self.model_name}")
            
            # Use a lightweight model for local inference
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=config.MAX_RESPONSE_LENGTH,
                temperature=config.TEMPERATURE,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print("Local model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading local model: {e}")
            print("Falling back to simple rule-based responses...")
            self.pipeline = None
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate a response using the local model."""
        if not self.pipeline:
            return self._generate_fallback_response(prompt)
        
        try:
            # Format the prompt for the model
            full_prompt = self._format_prompt(prompt, context)
            
            # Generate response
            response = self.pipeline(
                full_prompt,
                max_length=len(self.tokenizer.encode(full_prompt)) + 150,
                num_return_sequences=1,
                temperature=config.TEMPERATURE,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = response[0]["generated_text"]
            
            # Remove the original prompt from the response
            if generated_text.startswith(full_prompt):
                response_text = generated_text[len(full_prompt):].strip()
            else:
                response_text = generated_text.strip()
            
            # Clean up the response
            response_text = self._clean_response(response_text)
            
            return response_text if response_text else self._generate_fallback_response(prompt)
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._generate_fallback_response(prompt)
    
    def _format_prompt(self, user_input: str, context: str = "") -> str:
        """Format the prompt for the model."""
        if context:
            prompt = f"""You are a helpful Jira customer support chatbot. Use the following context to answer the user's question:

Context: {context}

User: {user_input}

Assistant:"""
        else:
            prompt = f"""You are a helpful Jira customer support chatbot. Answer the user's question about Jira Software Cloud:

User: {user_input}

Assistant:"""
        
        return prompt
    
    def _clean_response(self, response: str) -> str:
        """Clean up the generated response."""
        # Remove any incomplete sentences at the end
        sentences = response.split('. ')
        if sentences and not sentences[-1].endswith('.'):
            sentences = sentences[:-1]
        
        # Join sentences back
        cleaned = '. '.join(sentences)
        if cleaned and not cleaned.endswith('.'):
            cleaned += '.'
        
        # Remove any unwanted patterns
        cleaned = re.sub(r'\n+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when the model is not available."""
        prompt_lower = prompt.lower()
        
        # Simple rule-based responses for common queries
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

class IntentClassifier:
    """Classifies user intents for routing to appropriate handlers."""
    
    def __init__(self):
        self.intent_keywords = {
            "epic": ["epic", "epics", "epic-", "large story", "feature"],
            "sprint": ["sprint", "sprints", "iteration", "sprint planning", "agile"],
            "issue": ["issue", "issues", "task", "story", "bug", "ticket"],
            "create": ["create", "add", "new", "make", "generate"],
            "list": ["list", "show", "display", "get all", "find all"],
            "get": ["get", "find", "search", "retrieve", "fetch"],
            "update": ["update", "modify", "change", "edit", "alter"],
            "delete": ["delete", "remove", "cancel", "archive"],
            "help": ["help", "how", "what", "explain", "guide", "tutorial"]
        }
    
    def classify_intent(self, query: str) -> Dict[str, float]:
        """Classify the intent of a user query."""
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            
            if score > 0:
                intent_scores[intent] = score / len(keywords)
        
        return intent_scores

class ChatbotCore:
    """Main chatbot core that orchestrates all components."""
    
    def __init__(self):
        self.llm = LocalLLM()
        self.intent_classifier = IntentClassifier()
        self.conversation_history: List[ChatMessage] = []
        self.max_history = 10  # Keep last 10 messages
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to conversation history."""
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=timestamp,
            metadata=metadata
        )
        
        self.conversation_history.append(message)
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_conversation_context(self) -> str:
        """Get recent conversation context."""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for message in self.conversation_history[-5:]:  # Last 5 messages
            context_parts.append(f"{message.role}: {message.content}")
        
        return "\n".join(context_parts)
    
    def process_query(self, user_input: str, external_context: Optional[str] = None) -> ChatResponse:
        """Process a user query and generate a response."""
        # Add user message to history
        self.add_message("user", user_input)
        
        # Classify intent
        intents = self.intent_classifier.classify_intent(user_input)
        
        # Prepare context
        conversation_context = self.get_conversation_context()
        full_context = conversation_context
        
        if external_context:
            full_context += f"\n\nAdditional Context: {external_context}"
        
        # Generate response
        response_text = self.llm.generate_response(user_input, full_context)
        
        # Determine confidence based on intent classification
        confidence = max(intents.values()) if intents else 0.5
        
        # Determine sources
        sources = []
        if external_context:
            sources.append("external_data")
        if intents:
            sources.extend([f"intent_{intent}" for intent in intents.keys()])
        
        # Create response
        response = ChatResponse(
            message=response_text,
            confidence=confidence,
            sources=sources,
            metadata={
                "intents": intents,
                "has_external_context": external_context is not None
            }
        )
        
        # Add assistant message to history
        self.add_message("assistant", response_text, response.metadata)
        
        return response
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        return {
            "message_count": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m.role == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m.role == "assistant"]),
            "recent_topics": self._extract_recent_topics()
        }
    
    def _extract_recent_topics(self) -> List[str]:
        """Extract recent topics from conversation."""
        topics = []
        for message in self.conversation_history[-5:]:
            intents = self.intent_classifier.classify_intent(message.content)
            if intents:
                topics.extend(intents.keys())
        
        return list(set(topics))  # Remove duplicates
