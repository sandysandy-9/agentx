# AgentX Development & Setup Guide

## Quick Start Commands

### Environment Setup
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env
```

### Database Setup

#### MongoDB (Option 1: Docker)
```powershell
# Pull and run MongoDB
docker pull mongo:latest
docker run -d --name agentx-mongo -p 27017:27017 mongo:latest

# Check if running
docker ps | findstr mongo
```

#### MongoDB (Option 2: Windows Installation)
```powershell
# Download from: https://www.mongodb.com/try/download/community
# Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas
```

#### Redis (Option 1: Docker)
```powershell
# Pull and run Redis
docker pull redis:latest
docker run -d --name agentx-redis -p 6379:6379 redis:latest

# Check if running
docker ps | findstr redis
```

#### Redis (Option 2: WSL)
```powershell
# Install via WSL
wsl --install
wsl -d Ubuntu
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Running the Application

#### Backend
```powershell
# Make sure you're in the project directory
cd C:\agentx

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the server
python main.py

# Or with auto-reload for development
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```powershell
# Option 1: Direct file opening
start frontend\index.html

# Option 2: Using Python HTTP server
cd frontend
python -m http.server 8080
# Then open: http://localhost:8080

# Option 3: Using Node.js http-server
npm install -g http-server
cd frontend
http-server -p 8080
```

### Testing

#### Manual Testing
```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"Hello AgentX\", \"user_id\": \"test_user\"}'

# Test task creation
curl -X POST http://localhost:8000/tasks `
  -H "Content-Type: application/json" `
  -d '{\"title\": \"Test Task\", \"priority\": \"high\"}'
```

#### Automated Tests
```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_tasks.py
```

## Development Workflow

### 1. Environment Configuration

Create `.env` file with your credentials:
```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Tavily (optional for web search)
TAVILY_API_KEY=tvly-your-key-here

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=agentx

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Vector Store
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### 2. Database Initialization

The application auto-creates necessary collections and indexes on first run. No manual setup needed.

### 3. Adding Sample Data

```python
# Run this in Python console after starting the app
import requests

# Create sample tasks
tasks = [
    {"title": "Complete project documentation", "priority": "high"},
    {"title": "Review code changes", "priority": "medium"},
    {"title": "Update README", "priority": "low"}
]

for task in tasks:
    requests.post("http://localhost:8000/tasks", json=task)
```

## Project Structure Explained

```
agentx/
├── agent/                   # Agent orchestration logic
│   ├── orchestrator.py     # Main Think-Act-Observe-Answer loop
│   └── __init__.py
│
├── tools/                   # Individual tool implementations
│   ├── task_manager.py     # MongoDB-based task management
│   ├── document_search.py  # ChromaDB RAG engine
│   ├── web_search.py       # Tavily web search integration
│   ├── memory.py           # Redis-based user memory
│   └── __init__.py
│
├── models/                  # Pydantic data models
│   ├── task.py             # Task schemas
│   └── __init__.py
│
├── frontend/                # Web interface
│   └── index.html          # Single-page application
│
├── data/                    # Runtime data (auto-created)
│   ├── chroma/             # Vector embeddings
│   └── uploads/            # User-uploaded documents
│
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # Main documentation
```

## API Endpoint Reference

### Chat API
- `POST /chat` - Send message to agent
  - Request: `{"message": str, "session_id": str, "user_id": str}`
  - Response: `{"response": str, "session_id": str, "timestamp": datetime}`

### Task Management
- `POST /tasks` - Create task
- `GET /tasks` - List tasks (with filters: status, priority, category)
- `GET /tasks/{task_id}` - Get specific task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task
- `GET /tasks/stats` - Get statistics

### Document Management
- `POST /documents/upload` - Upload file (multipart/form-data)
- `GET /documents` - List all documents
- `POST /documents/search` - Semantic search
- `DELETE /documents/{filename}` - Remove document

### Memory & Preferences
- `GET /memory/conversation/{session_id}` - Get chat history
- `DELETE /memory/conversation/{session_id}` - Clear conversation
- `GET /memory/preferences/{user_id}` - Get user preferences

## Common Development Tasks

### Adding a New Tool

1. **Create tool file** in `tools/`:
```python
# tools/my_tool.py
from typing import Any
import logging

logger = logging.getLogger(__name__)

class MyTool:
    def __init__(self):
        # Initialization
        pass
    
    def execute(self, query: str) -> Any:
        """Execute tool logic"""
        logger.info(f"Executing MyTool with query: {query}")
        # Your logic here
        return {"result": "data"}
```

2. **Register in orchestrator** (`agent/orchestrator.py`):
```python
# In __init__
self.my_tool = MyTool()
self.tool_registry["my_tool"] = self.my_tool

# In _select_tools
if "keyword" in user_input:
    return ["my_tool"]
```

3. **Add endpoint** in `main.py`:
```python
@app.post("/mytool/action")
def my_tool_action(param: str):
    result = my_tool.execute(param)
    return result
```

### Modifying the Frontend

The frontend is a single HTML file with inline CSS and JavaScript:

- **Styling**: Edit `<style>` section
- **Layout**: Modify HTML structure in `<body>`
- **Logic**: Update `<script>` section

To add a new view:
1. Add navigation item in sidebar
2. Create view container div
3. Add JavaScript to handle view switching
4. Implement API calls for data loading

### Database Schema Changes

#### For Tasks
Edit `models/task.py` and add fields to `Task` class:
```python
class Task(BaseModel):
    # Existing fields...
    new_field: Optional[str] = None
```

MongoDB is schemaless, so changes take effect immediately.

#### For Vector Store
Modify `tools/document_search.py` to change:
- Chunk size: `chunk_size` in `config.py`
- Embedding model: Change in `DocumentSearchEngine.__init__`
- Similarity threshold: `similarity_threshold` in `config.py`

## Performance Optimization

### Vector Search
```python
# Batch document additions
documents = [doc1, doc2, doc3]
for doc in documents:
    document_search.add_document(doc)

# Adjust chunk size for better performance
# config.py
chunk_size = 256  # Smaller = more granular, slower
chunk_size = 1024  # Larger = less granular, faster
```

### Task Queries
```python
# Use indexes (auto-created in TaskManager.__init__)
# Add custom indexes as needed
self.collection.create_index("category")
self.collection.create_index([("status", 1), ("priority", -1)])
```

### Caching
```python
# Use memory.cache_set/get for expensive operations
result = memory.cache_get("expensive_query")
if not result:
    result = expensive_operation()
    memory.cache_set("expensive_query", result, ttl=3600)
```

## Debugging Tips

### Enable Debug Logging
```python
# main.py
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Check Tool Execution
```python
# agent/orchestrator.py - Add in act() method
logger.debug(f"Tool output: {result}")
logger.debug(f"State: {state.model_dump()}")
```

### Monitor Database Operations
```python
# tools/task_manager.py - Add before operations
logger.debug(f"Query: {query}")
logger.debug(f"Update data: {update_data}")
```

### Frontend Debugging
Open browser console (F12) and check:
- Network tab for API calls
- Console for JavaScript errors
- Add `console.log()` statements in functions

## Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong database credentials
- [ ] Configure CORS properly in `main.py`
- [ ] Set up HTTPS/SSL
- [ ] Enable rate limiting
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Configure backup for MongoDB
- [ ] Use environment variables for all secrets
- [ ] Set up proper logging aggregation
- [ ] Test with production data

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **LangChain Docs**: https://python.langchain.com/
- **ChromaDB Guide**: https://docs.trychroma.com/
- **MongoDB Tutorial**: https://www.mongodb.com/docs/manual/
- **Redis Commands**: https://redis.io/commands/

## Support

For issues during development:
1. Check logs in console
2. Verify all services are running (`docker ps`)
3. Confirm environment variables are set
4. Test individual components separately
5. Review API documentation at `/docs`

---

**Happy Coding! 🚀**
