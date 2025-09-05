# Eny Consult AI Chatbot Support Service

**AI-Powered Student Support with RAG and DeepSeek AI Integration**

A comprehensive, production-ready AI microservice that provides intelligent student support using **DeepSeek AI** with Retrieval-Augmented Generation (RAG) capabilities for context-aware responses.


<p align="center">
  <img src="https://res.cloudinary.com/djkrhjgjd/image/upload/v1757062248/chatbot/mermaid-diagram_5_p6v6uc.svg" alt="Logo" width="100%" />
</p>

---

<img 
  src="https://res.cloudinary.com/djkrhjgjd/image/upload/v1757060719/chatbot/swagger_core2_woexij.png" 
  alt="Chatbot core"
  style="width: 100%; height: auto;"
/>
---

## ✨ **Key Features**

### 🤖 **AI Integration**
- **DeepSeek Chat v3.1**: High-quality language model via OpenRouter
- **Multiple API Keys**: Load balancing and automatic fallback
- **Intelligent Escalation**: LLM-generated escalation data for backend processing
- **Confidence Scoring**: Assess response quality and trigger escalation

### 🔍 **RAG (Retrieval-Augmented Generation)**
- **Semantic Search**: Find relevant documents quickly using vector embeddings
- **Context Building**: Intelligent document context assembly
- **Source Attribution**: Track information sources
- **Automatic Fallback**: Graceful degradation when AI unavailable

### 📚 **Document Management**
- **Vector Database**: ChromaDB for efficient storage and retrieval
- **Embedding Models**: SentenceTransformers for semantic search
- **PDF Processing**: Automatic text extraction and processing
- **Bulk Operations**: Upload multiple documents efficiently

### 🏗️ **Architecture**
- **Microservice Design**: FastAPI-based REST API
- **Async Operations**: Non-blocking I/O operations
- **Service Layer**: Clean separation of concerns
- **Health Monitoring**: Real-time service status
- **Graceful Degradation**: Service continues even with partial failures

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Docker & Docker Compose (for ChromaDB)
- DeepSeek API Key via OpenRouter

### **1. Clone & Setup**
```bash
git clone <repository-url>
cd ai-student-support-svc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_URL=https://openrouter.ai/api/v1/chat/completions
DEEPSEEK_MODEL=deepseek/deepseek-chat-v3.1:free
```

### **3. Start Services**
```bash
# Start ChromaDB
docker-compose up -d

# Start the service
python main.py
```

### **4. Verify Installation**
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## 🔑 **API Key Setup**

### **Getting Your DeepSeek API Key**

1. **Visit OpenRouter**: https://openrouter.ai/
2. **Sign In/Sign Up**: Use existing account or create new one
3. **Generate API Key**: Go to "API Keys" section and click "Create Key"
4. **Copy Key**: Key starts with `sk-or-v1-`
5. **Update .env**: Add your key to the `.env` file

### **Multiple API Keys (Recommended)**

For load balancing and fallback capabilities:

```bash
# Primary DeepSeek API Key
DEEPSEEK_API_KEY=your_primary_openrouter_api_key_here

# Secondary DeepSeek API Key (Fallback)
DEEPSEEK_API_KEY_2=your_secondary_openrouter_api_key_here

# Load Balancing Settings
ENABLE_LOAD_BALANCING=true
MAX_RETRIES=3
RETRY_DELAY=1.0
```

**Benefits**:
- ✅ No more rate limit errors
- ✅ Better performance with load distribution
- ✅ Automatic fallback when needed
- ✅ Higher availability and reliability

## 🔧 **Configuration**

### **Environment Variables**

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | Primary DeepSeek API key | Required |
| `DEEPSEEK_API_KEY_2` | Secondary DeepSeek API key | Optional |
| `DEEPSEEK_API_URL` | DeepSeek API endpoint | OpenRouter URL |
| `DEEPSEEK_MODEL` | DeepSeek model name | `deepseek/deepseek-chat-v3.1:free` |
| `CHROMA_HOST` | ChromaDB host | `localhost` |
| `CHROMA_PORT` | ChromaDB port | `8001` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `ENABLE_LOAD_BALANCING` | Enable multi-key load balancing | `true` |

### **AI Provider Priority**
1. **DeepSeek Primary** (if configured)
2. **DeepSeek Secondary** (if primary fails or unavailable)
3. **Fallback** (intelligent responses without AI)

## 📡 **API Endpoints**

### **Chat & AI**
- `POST /api/v1/chat/` - AI-powered chat with RAG
- `GET /api/v1/chat/status` - Chat service status

### **Documents**
- `POST /api/v1/documents/` - Add documents to knowledge base
- `GET /api/v1/documents/` - Get knowledge base information
- `DELETE /api/v1/documents/` - Clear all data from knowledge base

### **Search**
- `POST /api/v1/search/` - Semantic document search

### **Status & Health**
- `GET /api/v1/status/` - Service status monitoring
- `GET /health` - Comprehensive health check
- `GET /` - Service information and endpoints

## 🧠 **Embedding Model Management**

### **Automatic Model Management**
The service includes a robust model management system that ensures embedding models are always available:

- **Strategy 1**: Load cached model (fastest)
- **Strategy 2**: Download model (reliable)
- **Strategy 3**: Fallback embeddings (always works)

### **Model Options**
- **`all-MiniLM-L6-v2`** (default): Fast, 384 dimensions, ~90MB
- **`all-mpnet-base-v2`**: Better quality, 768 dimensions, ~420MB
- **`all-MiniLM-L12-v2`**: Balanced, 384 dimensions, ~120MB

### **Cache Management**
```bash
# Local project cache
./model_cache/

# Global HuggingFace cache
~/.cache/huggingface/hub/
```

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   AI Service    │    │  DeepSeek API   │
│                 │    │                 │    │                 │
│  - Chat API     │◄──►│  - DeepSeek     │◄──►│  - Chat v3.1    │
│  - Documents    │    │  - Load Balance │    │  - Free Tier    │
│  - Search       │    │  - Fallback     │    │                 │
│  - Status       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   RAG Service   │    │  ChromaDB       │
│                 │    │                 │
│  - Context      │    │  - Vector DB    │
│  - Retrieval    │◄──►│  - Embeddings   │
│  - Processing   │    │  - Documents    │
└─────────────────┘    └─────────────────┘
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **DeepSeek API Errors**
```bash
# Check API key
echo $DEEPSEEK_API_KEY

# Test connection
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek/deepseek-chat-v3.1:free","messages":[{"role":"user","content":"Hello"}]}' \
     https://openrouter.ai/api/v1/chat/completions
```

#### **ChromaDB Issues**
```bash
# Check Docker containers
docker ps

# Restart ChromaDB
docker-compose restart chromadb

# Check logs
docker-compose logs chromadb
```

#### **Embedding Model Issues**
```bash
# Ensure model availability
python ensure_model.py

# Check disk space
python -c "from app.utils.model_manager import ModelManager; print(ModelManager().get_disk_usage())"
```

### **Service Status**
```bash
# Check all services
curl http://localhost:8000/api/v1/status/

# Health check
curl http://localhost:8000/health
```

## 📚 **Development**

### **Project Structure**
```
ai-student-support-svc/
├── app/
│   ├── api/           # API endpoints
│   ├── config/        # Configuration
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   ├── prompts/       # AI prompts
│   └── utils/         # Utilities
├── tests/             # Test files
├── main.py            # Application entry point
├── requirements.txt   # Dependencies
└── docker-compose.yml # ChromaDB setup
```

### **Code Style**
- **Professional**: Clean, concise code
- **Documentation**: Clear docstrings and comments
- **Error Handling**: Comprehensive error handling and logging
- **Testing**: Comprehensive test coverage
- **Type Annotations**: Full type hints throughout

### **Adding New Features**
1. Create models in `app/models/`
2. Add services in `app/services/`
3. Create API endpoints in `app/api/`
4. Add tests in test scripts
5. Update documentation

## 🐳 **Docker Support**

### **Start with Docker Compose**
```bash
docker-compose up -d
```

### **Build and Run**
```bash
docker build -t ai-student-support .
docker run -p 8000:8000 ai-student-support
```

## 📊 **Monitoring & Debugging**

### **Service Status**
```bash
curl http://localhost:8000/api/v1/chat/status
```

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Logs**
The service uses a centralized logging system with:
- **Colored Output**: Different log levels in distinct colors
- **Service Prefixing**: All logs include `[ai-service]` prefix
- **Consistent Format**: Standardized timestamp and formatting
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🎯 **Expected Behavior**

### **✅ What Works**
1. **Service starts** even if ChromaDB is down
2. **RAG provides real AI responses** with context
3. **All endpoints respond** with proper error handling
4. **Graceful fallbacks** when services unavailable
5. **Real-time health monitoring** of all services
6. **Proper async handling** without blocking
7. **Load balancing** between multiple API keys

### **⚠️ What to Expect**
1. **First request** might be slower (lazy initialization)
2. **Service status** shows real availability
3. **Error messages** are helpful and actionable
4. **Fallback responses** when LLM unavailable

## 🚀 **Production Deployment**

### **Environment Setup**
```bash
# Set production environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

### **Security Considerations**
- Use environment variables for all sensitive data
- Configure proper CORS settings
- Set up proper logging and monitoring
- Configure ChromaDB for production use
- Use HTTPS in production

### **Performance Optimization**
- Pre-download embedding models during build
- Use model health checks in monitoring
- Monitor API rate limits and usage
- Implement caching for frequently requested data
