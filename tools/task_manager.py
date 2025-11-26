from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from models.task import Task, TaskCreate, TaskUpdate
from config import settings
import logging

logger = logging.getLogger(__name__)


class TaskManager:
    """Task management system with CRUD operations"""
    
    def __init__(self):
        try:
            self.client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=2000)
            # Test connection
            self.client.server_info()
            self.db = self.client[settings.mongodb_db_name]
            self.collection = self.db["tasks"]
            # Create indexes for better query performance
            self.collection.create_index("task_id", unique=True)
            self.collection.create_index("status")
            self.collection.create_index("deadline")
            self.available = True
            self.fallback_tasks = [] # In-memory fallback
            logger.info("TaskManager connected to MongoDB")
        except Exception as e:
            self.available = False
            self.collection = None
            self.fallback_tasks = []
            logger.warning(f"TaskManager: MongoDB not available - Using in-memory fallback - {e}")
        
    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task"""
        task = Task(**task_data.model_dump())
        
        if not self.available:
            self.fallback_tasks.append(task.model_dump())
            logger.info(f"Created task (local): {task.task_id} - {task.title}")
            return task
        
        self.collection.insert_one(task.model_dump())
        logger.info(f"Created task: {task.task_id} - {task.title}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        if not self.available:
            for t in self.fallback_tasks:
                if t["task_id"] == task_id:
                    return Task(**t)
            return None
        
        task_dict = self.collection.find_one({"task_id": task_id}, {"_id": 0})
        if task_dict:
            return Task(**task_dict)
        return None
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        deadline_before: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Task]:
        """List tasks with optional filters"""
        if not self.available:
            filtered = self.fallback_tasks
            if status:
                filtered = [t for t in filtered if t.get("status") == status]
            if priority:
                filtered = [t for t in filtered if t.get("priority") == priority]
            if category:
                filtered = [t for t in filtered if t.get("category") == category]
            if deadline_before:
                filtered = [t for t in filtered if t.get("deadline") and datetime.fromisoformat(str(t["deadline"])) <= deadline_before]
            return [Task(**t) for t in filtered[:limit]]

        query: Dict[str, Any] = {}
        
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        if category:
            query["category"] = category
        if deadline_before:
            query["deadline"] = {"$lte": deadline_before}
        
        tasks = self.collection.find(query, {"_id": 0}).limit(limit)
        return [Task(**task) for task in tasks]
    
    def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update an existing task"""
        update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
        
        if not update_data:
            return self.get_task(task_id)
            
        update_data["updated_at"] = datetime.utcnow()
        
        if not self.available:
            for i, t in enumerate(self.fallback_tasks):
                if t["task_id"] == task_id:
                    # Update fields
                    t.update(update_data)
                    # Handle datetime serialization if needed, though dict update is fine for in-memory
                    self.fallback_tasks[i] = t
                    logger.info(f"Updated task (local): {task_id}")
                    return Task(**t)
            return None
        
        result = self.collection.update_one(
            {"task_id": task_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated task: {task_id}")
            return self.get_task(task_id)
        return None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if not self.available:
            initial_len = len(self.fallback_tasks)
            self.fallback_tasks = [t for t in self.fallback_tasks if t["task_id"] != task_id]
            if len(self.fallback_tasks) < initial_len:
                logger.info(f"Deleted task (local): {task_id}")
                return True
            return False

        result = self.collection.delete_one({"task_id": task_id})
        if result.deleted_count > 0:
            logger.info(f"Deleted task: {task_id}")
            return True
        return False
    
    def get_upcoming_tasks(self, days: int = 7) -> List[Task]:
        """Get tasks due within specified days"""
        from datetime import timedelta
        deadline = datetime.utcnow() + timedelta(days=days)
        
        if not self.available:
            tasks = [
                t for t in self.fallback_tasks 
                if t.get("deadline") and 
                datetime.fromisoformat(str(t["deadline"])) <= deadline and 
                t.get("status") != "completed"
            ]
            tasks.sort(key=lambda x: x.get("deadline") or datetime.max)
            return [Task(**t) for t in tasks]

        tasks = self.collection.find(
            {
                "deadline": {"$lte": deadline},
                "status": {"$ne": "completed"}
            },
            {"_id": 0}
        ).sort("deadline", 1)
        
        return [Task(**task) for task in tasks]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        if not self.available:
            total = len(self.fallback_tasks)
            by_status = {}
            by_priority = {}
            
            for t in self.fallback_tasks:
                s = t.get("status", "unknown")
                p = t.get("priority", "unknown")
                by_status[s] = by_status.get(s, 0) + 1
                by_priority[p] = by_priority.get(p, 0) + 1
            
            return {
                "total_tasks": total,
                "by_status": by_status,
                "by_priority": by_priority,
                "pending": by_status.get("pending", 0),
                "in_progress": by_status.get("in_progress", 0),
                "completed": by_status.get("completed", 0)
            }

        status_pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        priority_pipeline = [
            {
                "$group": {
                    "_id": "$priority",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_counts = {item["_id"]: item["count"] for item in self.collection.aggregate(status_pipeline)}
        priority_counts = {item["_id"]: item["count"] for item in self.collection.aggregate(priority_pipeline)}
        
        return {
            "total_tasks": self.collection.count_documents({}),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "pending": status_counts.get("pending", 0),
            "in_progress": status_counts.get("in_progress", 0),
            "completed": status_counts.get("completed", 0)
        }
