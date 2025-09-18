# Jira Customer Support Chatbot - Project Structure

## 📁 **Complete Directory Structure**

```
C:\Users\Padmanabh\OneDrive\Documents\Jira\
├── 📁 __pycache__/                    # Python bytecode cache
├── 📁 cache/                          # Documentation cache (empty)
├── 📁 logs/                           # Application logs (empty)
├── 📁 static/                         # Frontend static files
│   └── 📄 index.html                  # Main web interface
├── 📁 vector_db/                      # ChromaDB vector database
│   └── 📄 chroma.sqlite3             # Vector database file
│
├── 📄 .env                           # Environment variables (not tracked)
├── 📄 main.py                        # Main FastAPI application
├── 📄 main_ollama.py                 # Ollama-enabled main application
├── 📄 main_ollama_clean.py           # Clean Ollama version
├── 📄 main_ollama_old.py             # Old Ollama version (backup)
│
├── 📄 chatbot_core.py                # Core chatbot logic (HuggingFace)
├── 📄 chatbot_core_ollama.py         # Ollama-enabled chatbot core
├── 📄 ollama_client.py               # Ollama API client
├── 📄 mcp_client.py                  # Model Context Protocol client
├── 📄 documentation_scraper.py       # Web scraping and vector DB
├── 📄 config.py                      # Configuration management
│
├── 📄 requirements.txt               # Full Python dependencies
├── 📄 requirements-minimal.txt       # Minimal dependencies
├── 📄 setup.py                       # Automated setup script
├── 📄 quick_setup.py                 # Quick dependency installer
│
├── 📄 Dockerfile                     # Docker containerization
├── 📄 docker-compose.yml             # Docker Compose configuration
├── 📄 env.example                    # Environment variables template
│
├── 📄 test_chatbot.py                # Chatbot testing script
├── 📄 test_epic_creation.py          # Epic creation testing
├── 📄 quick_test.py                  # Quick functionality test
├── 📄 verify_compliance.py           # Restriction compliance checker
│
├── 📄 README.md                      # Project overview and setup
├── 📄 DELIVERABLES.md                # Deliverables documentation
├── 📄 DEPLOYMENT_GUIDE.md            # Deployment instructions
├── 📄 FRONTEND_GUIDE.md              # Frontend documentation
├── 📄 OLLAMA_SETUP.md                # Ollama integration guide
├── 📄 CREATING_EPICS_SPRINTS.md      # Epic/Sprint creation guide
├── 📄 DOCUMENTATION.md               # General documentation
├── 📄 PROJECT_SUMMARY.md             # Project summary
└── 📄 TESTING.md                     # Testing documentation
```

---

## 🎯 **Core Application Files**

### **Main Applications**
| File | Purpose | Usage |
|------|---------|-------|
| `main.py` | Primary FastAPI app with HuggingFace models | `python main.py` |
| `main_ollama.py` | Ollama-enabled FastAPI app | `python main_ollama.py` |
| `main_ollama_clean.py` | Clean Ollama version | Alternative Ollama setup |
| `main_ollama_old.py` | Backup Ollama version | Fallback option |

### **Chatbot Core Logic**
| File | Purpose | Description |
|------|---------|-------------|
| `chatbot_core.py` | Core chatbot with HuggingFace | DialoGPT-medium integration |
| `chatbot_core_ollama.py` | Ollama-enabled chatbot | LLaMA2/smollm2 integration |
| `ollama_client.py` | Ollama API client | Handles Ollama communication |

### **MCP Integration**
| File | Purpose | Description |
|------|---------|-------------|
| `mcp_client.py` | Model Context Protocol | Epic/Sprint/Board API integration |
| `documentation_scraper.py` | Web scraping & vector DB | Documentation fallback system |

### **Configuration**
| File | Purpose | Description |
|------|---------|-------------|
| `config.py` | Configuration management | Environment variables & settings |
| `.env` | Environment variables | Jira credentials & settings |
| `env.example` | Template for .env | Setup guide |

---

## 🚀 **Deployment Files**

### **Dependencies**
| File | Purpose | Usage |
|------|---------|-------|
| `requirements.txt` | Full dependencies | `pip install -r requirements.txt` |
| `requirements-minimal.txt` | Minimal dependencies | Lightweight installation |
| `setup.py` | Automated setup | `python setup.py` |
| `quick_setup.py` | Quick installer | `python quick_setup.py` |

### **Containerization**
| File | Purpose | Usage |
|------|---------|-------|
| `Dockerfile` | Docker container | `docker build -t jira-chatbot .` |
| `docker-compose.yml` | Docker Compose | `docker-compose up` |

---

## 🧪 **Testing & Verification**

### **Test Scripts**
| File | Purpose | Usage |
|------|---------|-------|
| `test_chatbot.py` | Comprehensive testing | `python test_chatbot.py` |
| `test_epic_creation.py` | Epic creation testing | `python test_epic_creation.py` |
| `quick_test.py` | Quick functionality test | `python quick_test.py` |
| `verify_compliance.py` | Restriction compliance | `python verify_compliance.py` |

---

## 📚 **Documentation Files**

### **Core Documentation**
| File | Purpose | Description |
|------|---------|-------------|
| `README.md` | Project overview | Getting started guide |
| `DELIVERABLES.md` | Deliverables specification | Technical requirements |
| `DEPLOYMENT_GUIDE.md` | Deployment instructions | Local/cloud deployment |
| `FRONTEND_GUIDE.md` | Frontend documentation | UI/UX guide |

### **Feature Documentation**
| File | Purpose | Description |
|------|---------|-------------|
| `OLLAMA_SETUP.md` | Ollama integration | Local LLM setup |
| `CREATING_EPICS_SPRINTS.md` | Epic/Sprint guide | Usage examples |
| `DOCUMENTATION.md` | General docs | System documentation |
| `PROJECT_SUMMARY.md` | Project summary | High-level overview |
| `TESTING.md` | Testing guide | Testing procedures |

---

## 📁 **Data Directories**

### **Runtime Data**
| Directory | Purpose | Contents |
|-----------|---------|----------|
| `cache/` | Documentation cache | Scraped content cache |
| `logs/` | Application logs | Runtime logging |
| `vector_db/` | Vector database | ChromaDB storage |
| `__pycache__/` | Python cache | Bytecode cache |

### **Static Assets**
| Directory | Purpose | Contents |
|-----------|---------|----------|
| `static/` | Frontend files | HTML, CSS, JS assets |

---

## 🔧 **File Relationships**

### **Dependency Chain**
```
main.py/main_ollama.py
├── config.py (configuration)
├── chatbot_core.py/chatbot_core_ollama.py (LLM logic)
├── mcp_client.py (Jira API integration)
├── documentation_scraper.py (fallback system)
└── ollama_client.py (if using Ollama)
```

### **Configuration Flow**
```
.env → config.py → main.py → chatbot components
```

### **Data Flow**
```
User Input → MCP APIs → Documentation Fallback → LLM → Response
```

---

## 🎯 **Quick Start Files**

### **Essential Files for Basic Usage**
1. `main.py` - Main application
2. `config.py` - Configuration
3. `requirements.txt` - Dependencies
4. `.env` - Environment variables
5. `static/index.html` - Frontend

### **Essential Files for Ollama Usage**
1. `main_ollama.py` - Ollama-enabled app
2. `chatbot_core_ollama.py` - Ollama chatbot core
3. `ollama_client.py` - Ollama client
4. Same config and requirements files

### **Testing & Verification**
1. `verify_compliance.py` - Compliance check
2. `test_epic_creation.py` - Epic testing
3. `quick_test.py` - Quick functionality test

---

## 📊 **File Size Summary**

| Category | Count | Key Files |
|----------|-------|-----------|
| **Main Applications** | 4 | main.py, main_ollama.py, etc. |
| **Core Logic** | 4 | chatbot_core.py, mcp_client.py, etc. |
| **Configuration** | 3 | config.py, .env, env.example |
| **Dependencies** | 4 | requirements.txt, setup.py, etc. |
| **Testing** | 4 | test_*.py, verify_compliance.py |
| **Documentation** | 9 | README.md, guides, etc. |
| **Deployment** | 2 | Dockerfile, docker-compose.yml |
| **Data Directories** | 4 | cache/, logs/, vector_db/, static/ |

**Total Files: ~35 files across 8 categories**

---

## 🚀 **Recommended File Usage**

### **For Development**
```bash
# Core development
main.py                    # Primary application
chatbot_core.py           # Core logic
mcp_client.py             # API integration
config.py                 # Configuration

# Testing
verify_compliance.py      # Compliance check
test_epic_creation.py     # Feature testing
```

### **For Production**
```bash
# Production deployment
main.py                   # Main application
requirements.txt          # Dependencies
Dockerfile               # Containerization
.env                     # Environment config
```

### **For Documentation**
```bash
# Key documentation
README.md                # Getting started
DELIVERABLES.md          # Technical specs
DEPLOYMENT_GUIDE.md      # Deployment
FRONTEND_GUIDE.md        # UI guide
```

This structure provides a complete, production-ready Jira Customer Support Chatbot with comprehensive documentation, testing, and deployment capabilities.
