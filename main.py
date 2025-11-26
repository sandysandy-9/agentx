from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import logging
import uuid
from datetime import datetime

from agent.orchestrator import AgentOrchestrator
from tools.task_manager import TaskManager
from tools.document_search import DocumentSearchEngine
from tools.web_search import WebSearchTool
from tools.memory import MemoryModule
from tools.llm import GeminiLLM
from tools.visualizer_enhanced import EnhancedVisualizer
from models.task import TaskCreate, TaskUpdate
from config import settings
import pandas as pd

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgentX API",
    description="General-Purpose AI Agent with Tool Intelligence",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for visualizations
import os
static_dir = "static/visualizations"
os.makedirs(static_dir, exist_ok=True)
app.mount("/visualizations", StaticFiles(directory=static_dir), name="visualizations")

# Initialize tools
task_manager = TaskManager()
# Initialize web search (optional)
try:
    web_search = WebSearchTool()
except ValueError:
    web_search = None
    logger.warning("Web search tool not configured (missing API key)")

# Initialize enhanced visualizer
visualizer = EnhancedVisualizer()

# Initialize other tools
document_search = DocumentSearchEngine()
memory = MemoryModule()
try:
    llm = GeminiLLM()
except ValueError:
    llm = None
    logger.warning("Gemini LLM not configured (missing API key)")

# Initialize agent orchestrator
agent = AgentOrchestrator(
    task_manager=task_manager,
    document_search=document_search,
    web_search=web_search,
    memory=memory,
    llm=llm,
    visualizer=visualizer
)

# ============== Request/Response Models ==============

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: str = "default_user"
    csv_data: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime

# ============== Health Check ==============

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "AgentX",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    redis_healthy = memory.health_check()
    
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "services": {
            "redis": redis_healthy,
            "task_manager": True,
            "document_search": True,
            "web_search": web_search is not None
        }
    }

# ============== Chat Endpoint ==============

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint - handles all user interactions
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Run agent
        response = agent.run(
            user_input=request.message,
            session_id=session_id,
            user_id=request.user_id,
            csv_data=request.csv_data
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== Task Management Endpoints ==============

@app.post("/tasks")
def create_task(task: TaskCreate):
    """Create a new task"""
    try:
        created_task = task_manager.create_task(task)
        return created_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None
):
    """List tasks with optional filters"""
    try:
        tasks = task_manager.list_tasks(
            status=status,
            priority=priority,
            category=category
        )
        return {"tasks": tasks, "count": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    """Get a specific task"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}")
def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    updated_task = task_manager.update_task(task_id, task_update)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    """Delete a task"""
    success = task_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted", "task_id": task_id}

@app.get("/tasks/stats")
def get_task_statistics():
    """Get task statistics"""
    return task_manager.get_statistics()

# ============== Document Management Endpoints ==============

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    if not document_search:
        raise HTTPException(status_code=503, detail="Document search not available. Install pytorch/transformers for RAG features.")
    
    try:
        # Save file temporarily
        import os
        temp_dir = "./data/uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Add to vector store
        chunks_added = document_search.add_document(file_path)
        
        return {
            "filename": file.filename,
            "chunks_added": chunks_added,
            "status": "processed"
        }
    
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
def list_documents():
    """List all uploaded documents"""
    if not document_search:
        raise HTTPException(status_code=503, detail="Document search not available")
    documents = document_search.list_documents()
    return {"documents": documents, "count": len(documents)}

@app.delete("/documents/{filename}")
def delete_document(filename: str):
    """Delete a document"""
    if not document_search:
        raise HTTPException(status_code=503, detail="Document search not available")
    success = document_search.delete_document(filename)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "filename": filename}

@app.post("/documents/search")
def search_documents(query: str, top_k: int = 4):
    """Search documents"""
    if not document_search:
        raise HTTPException(status_code=503, detail="Document search not available")
    results = document_search.search(query, top_k=top_k)
    return {"query": query, "results": results, "count": len(results)}

# ============== Memory Endpoints ==============

@app.get("/memory/conversation/{session_id}")
def get_conversation_history(session_id: str, limit: int = 50):
    """Get conversation history"""
    history = memory.get_conversation(session_id, limit=limit)
    return {"session_id": session_id, "messages": history, "count": len(history)}

@app.delete("/memory/conversation/{session_id}")
def clear_conversation(session_id: str):
    """Clear conversation history"""
    memory.clear_conversation(session_id)
    return {"status": "cleared", "session_id": session_id}

@app.get("/memory/preferences/{user_id}")
def get_user_preferences(user_id: str):
    """Get user preferences"""
    preferences = memory.get_all_preferences(user_id)
    return {"user_id": user_id, "preferences": preferences}

# ============== Visualization Endpoints ==============

class VisualizationRequest(BaseModel):
    message: str
    csv_data: Optional[str] = None
    chart_type: Optional[str] = None
    analyze: bool = True

@app.post("/visualize")
def create_visualization(request: VisualizationRequest):
    """Create visualization from request"""
    try:
        # Parse CSV if provided
        custom_data = None
        if request.csv_data:
            custom_data = visualizer.parse_csv_data(request.csv_data)
        
        # Detect visualization request
        viz_request = visualizer.detect_visualization_request(request.message)
        if not viz_request:
            return {"success": False, "error": "Could not detect visualization type"}
        
        # Override with explicit chart type if provided
        if request.chart_type:
            viz_request['type'] = request.chart_type
        
        # Set analyze flag
        viz_request['analyze'] = request.analyze
        
        # Generate visualization
        result = visualizer.generate_visualization(request.message, viz_request, custom_data)
        return result
        
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file for visualization"""
    try:
        content = await file.read()
        csv_data = content.decode('utf-8')
        
        # Parse CSV
        df = visualizer.parse_csv_data(csv_data)
        
        return {
            "success": True,
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(5).to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== Run Server ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
