# AgentX - General-Purpose AI Agent

![AgentX Logo](https://img.shields.io/badge/AgentX-AI%20Agent-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-Latest-orange?style=flat-square)

## 🚀 Overview

AgentX is a production-ready, general-purpose AI agent specialized in personal productivity, knowledge assistance, workflow automation, and intelligent file processing. It implements a sophisticated **Think → Act → Observe → Answer** loop for intelligent task execution.

## ✨ Key Features

### 🧠 Core Capabilities
- **Task Management** - CRUD operations with priority, deadlines, and categories
- **Document Search (RAG)** - Upload and search PDFs/text files with semantic search
- **Web Search Integration** - Real-time information retrieval via Tavily API
- **Memory Module** - Persistent user preferences and conversation history
- **Intelligent Orchestration** - Automatic tool selection and multi-step execution

### 🛠️ Technical Stack
- **Backend**: FastAPI, LangChain, LangGraph
- **Vector DB**: ChromaDB with sentence transformers
- **Database**: MongoDB (tasks), Redis (memory/cache)
- **AI Models**: OpenAI GPT-3.5/4, text-embedding-3-small
- **Frontend**: Vanilla JavaScript with modern UI

## 📁 Project Structure

```
agentx/
├── agent/
│   ├── __init__.py
│   └── orchestrator.py      # Think-Act-Observe-Answer loop
├── tools/
│   ├── __init__.py
│   ├── task_manager.py      # Task CRUD operations
│   ├── document_search.py   # RAG engine
│   ├── web_search.py        # Tavily integration
│   └── memory.py            # Redis-based memory
├── models/
│   ├── __init__.py
│   └── task.py              # Pydantic models
├── frontend/
│   └── index.html           # Web interface
├── data/
│   ├── chroma/              # Vector embeddings
│   └── uploads/             # Uploaded documents
├── main.py                  # FastAPI server
├── config.py                # Settings management
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## 🔧 Installation

### Prerequisites
- Python 3.9+
- MongoDB (local or Atlas)
- Redis (local or cloud)
- OpenAI API key
- Tavily API key (optional, for web search)

### Step 1: Clone and Setup

```powershell
# Create project directory
cd C:\
git clone <your-repo> agentx
cd agentx

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```powershell
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
notepad .env
```

**Required Configuration:**
```env
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb://localhost:27017/
REDIS_HOST=localhost
TAVILY_API_KEY=tvly-...  # Optional
```

### Step 3: Start Services

**Start MongoDB:**
```powershell
# If using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or use MongoDB Atlas (cloud)
```

**Start Redis:**
```powershell
# If using Docker
docker run -d -p 6379:6379 --name redis redis:latest

# Or use Windows Subsystem for Linux (WSL)
wsl -d Ubuntu
sudo service redis-server start
```

### Step 4: Run AgentX

```powershell
# Start the backend server
python main.py
```

The API will be available at `http://localhost:8000`

### Step 5: Open Frontend

```powershell
# Open the frontend in your browser
start frontend/index.html
```

Or use a local server:
```powershell
# Using Python's built-in server
cd frontend
python -m http.server 8080
# Open http://localhost:8080
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Create a task to finish project report",
  "session_id": "optional-session-id",
  "user_id": "demo_user"
}
```

#### Tasks
```http
GET  /tasks                    # List all tasks
POST /tasks                    # Create task
GET  /tasks/{task_id}          # Get specific task
PUT  /tasks/{task_id}          # Update task
DELETE /tasks/{task_id}        # Delete task
GET  /tasks/stats              # Get statistics
```

#### Documents
```http
POST /documents/upload         # Upload document
GET  /documents                # List documents
POST /documents/search         # Search documents
DELETE /documents/{filename}   # Delete document
```

#### Memory
```http
GET  /memory/conversation/{session_id}      # Get chat history
DELETE /memory/conversation/{session_id}    # Clear history
GET  /memory/preferences/{user_id}          # Get user preferences
```

## 🎯 Usage Examples

### 1. Task Management via Chat
```
User: "Create a high-priority task to submit assignment by Friday"
Agent: ✓ Task created: Submit assignment | Priority: high | Deadline: 2025-11-21
```

### 2. Document Q&A
```
User: "What are the key findings in my research PDF?"
Agent: [Searches uploaded PDFs and provides summary with citations]
```

### 3. Web Search
```
User: "What's the latest news about AI developments?"
Agent: [Fetches current information from web and provides summary]
```

### 4. Multi-Step Workflow
```
User: "Remind me to prepare for the presentation tomorrow and search for recent AI trends"
Agent: [Creates task + performs web search + provides consolidated answer]
```

## 🧪 Testing

```powershell
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## 🎨 Customization

### Add New Tools

1. Create tool in `tools/` directory:
```python
# tools/custom_tool.py
class CustomTool:
    def execute(self, query: str):
        # Your logic here
        return result
```

2. Register in orchestrator:
```python
# agent/orchestrator.py
self.tool_registry["custom_tool"] = CustomTool()
```

3. Add intent detection in `_detect_intent()`

### Modify UI

Edit `frontend/index.html` to customize the interface. The frontend uses vanilla JavaScript for simplicity.

## 🔒 Security Considerations

- **API Keys**: Never commit `.env` file to version control
- **Input Validation**: All user inputs are validated via Pydantic models
- **CORS**: Configure appropriately for production (currently set to allow all origins)
- **Rate Limiting**: Implement rate limiting in production (use Redis)

## 📊 Production Deployment

### Using Docker

```dockerfile
# Dockerfile (create this)
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```powershell
# Build and run
docker build -t agentx .
docker run -p 8000:8000 --env-file .env agentx
```

### Environment Variables for Production
```env
DEBUG=False
LOG_LEVEL=WARNING
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/agentx
REDIS_HOST=redis.cloud.com
```

## 🐛 Troubleshooting

### Common Issues

**"Import could not be resolved"** (VS Code)
- These are linting warnings. Install packages: `pip install -r requirements.txt`

**MongoDB connection failed**
- Check if MongoDB is running: `docker ps` or check service status
- Verify `MONGODB_URI` in `.env`

**Redis connection failed**
- Start Redis: `docker start redis` or `wsl sudo service redis-server start`
- Check `REDIS_HOST` and `REDIS_PORT` in `.env`

**Document upload fails**
- Ensure `./data/uploads` directory exists (auto-created)
- Check file format (.pdf, .txt, .md only)

## 🤝 Contributing

This is a B.Tech project. For suggestions:
1. Fork the repository
2. Create feature branch
3. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Built as a B.Tech final year project demonstrating:
- AI agent architecture
- RAG implementation
- Tool orchestration
- Production-ready API design
- Modern web development

## 🙏 Acknowledgments

- LangChain framework for agent tools
- OpenAI for LLM capabilities
- FastAPI for excellent documentation
- ChromaDB for vector storage

---

**Project Status**: ✅ Production Ready

For questions or issues, please open a GitHub issue or contact the maintainer.
