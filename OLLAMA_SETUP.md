# Ollama Integration Setup Guide

This guide shows you how to integrate Ollama with your Jira Customer Support Chatbot for better local LLM performance.

## 🚀 **What is Ollama?**

Ollama is a tool for running large language models locally. It provides:
- **Better Performance**: Optimized for local inference
- **Easy Model Management**: Simple commands to pull and run models
- **Multiple Models**: Support for Llama, Mistral, CodeLlama, and more
- **REST API**: Easy integration with applications

## 📋 **Prerequisites**

1. **Ollama Installed**: Download from [ollama.ai](https://ollama.ai)
2. **Python Dependencies**: The chatbot with Ollama support
3. **Sufficient RAM**: At least 8GB for smaller models, 16GB+ recommended

## 🔧 **Installation Steps**

### **1. Install Ollama**

**Windows:**
```bash
# Download and install from https://ollama.ai/download
# Or use winget
winget install Ollama.Ollama
```

**macOS:**
```bash
# Download and install from https://ollama.ai/download
# Or use brew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### **2. Start Ollama Service**

```bash
# Start Ollama server
ollama serve
```

Keep this running in a separate terminal.

### **3. Pull a Model**

```bash
# Pull Llama 2 (recommended for general use)
ollama pull llama2

# Or try other models:
ollama pull mistral
ollama pull codellama
ollama pull llama2:13b  # Larger model, requires more RAM
```

### **4. Install Python Dependencies**

```bash
# Install the enhanced chatbot
pip install python-dotenv requests

# The ollama_client.py will handle the rest
```

## 🎯 **Running with Ollama**

### **Option 1: Use the Ollama-Enhanced Version**

```bash
# Run the enhanced version that supports Ollama
python main_ollama.py
```

### **Option 2: Update Your .env File**

Add these settings to your `.env` file:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
USE_OLLAMA=True
```

## 🧪 **Testing Ollama Integration**

### **1. Check Ollama Status**

```bash
# List available models
ollama list

# Test a model
ollama run llama2 "Hello, how are you?"
```

### **2. Test the Chatbot**

```bash
# Start the enhanced chatbot
python main_ollama.py

# Open browser to http://localhost:8000
# You should see "LLM Backend: Ollama" in the interface
```

### **3. API Testing**

```bash
# Test the Ollama models endpoint
curl http://localhost:8000/ollama/models

# Test chat with Ollama
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How do I create an epic in Jira?"}'
```

## 🔄 **Fallback Behavior**

The enhanced chatbot automatically falls back:

1. **Ollama Available** → Uses Ollama (best performance)
2. **Ollama Unavailable** → Falls back to Transformers
3. **Both Unavailable** → Uses rule-based responses

## 📊 **Model Recommendations**

### **For General Use (8GB+ RAM):**
```bash
ollama pull llama2
```

### **For Better Quality (16GB+ RAM):**
```bash
ollama pull llama2:13b
ollama pull mistral
```

### **For Code-Related Queries:**
```bash
ollama pull codellama
```

### **For Smaller Systems (4GB RAM):**
```bash
ollama pull llama2:7b
```

## ⚙️ **Configuration Options**

### **Environment Variables**

```bash
# Ollama server URL
OLLAMA_BASE_URL=http://localhost:11434

# Model to use
OLLAMA_MODEL=llama2

# Enable/disable Ollama
USE_OLLAMA=True
```

### **Model Switching**

You can switch models without restarting:

```bash
# Pull a new model
ollama pull mistral

# Update your .env file
OLLAMA_MODEL=mistral

# Restart the chatbot
python main_ollama.py
```

## 🐛 **Troubleshooting**

### **Ollama Not Starting**

```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

### **Model Not Found**

```bash
# List available models
ollama list

# Pull the model you want
ollama pull llama2
```

### **Memory Issues**

```bash
# Use a smaller model
ollama pull llama2:7b

# Or reduce context length in your .env
MAX_RESPONSE_LENGTH=300
```

### **Connection Errors**

```bash
# Check if Ollama is accessible
curl http://localhost:11434/api/tags

# If not, restart Ollama
ollama serve
```

## 🚀 **Performance Tips**

### **1. Model Selection**
- Use 7B models for faster responses
- Use 13B+ models for better quality
- Use specialized models (CodeLlama) for specific tasks

### **2. System Optimization**
- Close unnecessary applications
- Ensure adequate RAM available
- Use SSD storage for better performance

### **3. Configuration Tuning**
```bash
# In your .env file
MAX_RESPONSE_LENGTH=300  # Shorter responses
TEMPERATURE=0.7          # Balanced creativity
```

## 📈 **Benefits of Ollama Integration**

1. **Better Performance**: Faster inference than Transformers
2. **Model Variety**: Access to many different models
3. **Easy Updates**: Simple model switching
4. **Resource Efficient**: Better memory management
5. **Local Control**: Complete control over your LLM

## 🎉 **Success Indicators**

You'll know Ollama is working when:

1. ✅ Chatbot shows "LLM Backend: Ollama" in the interface
2. ✅ Health check shows "ollama" as the backend
3. ✅ Responses are more natural and contextual
4. ✅ `/ollama/models` endpoint returns your models

## 🔗 **Useful Commands**

```bash
# Start Ollama
ollama serve

# List models
ollama list

# Pull a model
ollama pull llama2

# Run a model interactively
ollama run llama2

# Remove a model
ollama rm llama2

# Update Ollama
ollama update
```

Your Jira Customer Support Chatbot is now enhanced with Ollama support! 🎊
