from typing import Dict, Any, Optional
from redis import Redis
from config import settings
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryModule:
    """Persistent user memory and preferences"""
    
    def __init__(self):
        try:
            self.redis_client = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
            self.fallback_memory = {}  # In-memory fallback
            logger.info("MemoryModule connected to Redis")
        except Exception as e:
            self.available = False
            self.redis_client = None
            self.fallback_memory = {}  # Dictionary to store conversations in memory
            logger.warning(f"MemoryModule: Redis not available - Using in-memory fallback - {e}")
    
    # ============== User Preferences ==============
    
    def set_preference(self, user_id: str, key: str, value: Any) -> None:
        """Set a user preference"""
        if not self.available:
            logger.warning("Redis not available, preference not saved")
            return
        
        pref_key = f"user:{user_id}:pref:{key}"
        self.redis_client.set(pref_key, json.dumps(value))
        logger.info(f"Set preference for user {user_id}: {key}={value}")
    
    def get_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        if not self.available:
            return default
        
        pref_key = f"user:{user_id}:pref:{key}"
        value = self.redis_client.get(pref_key)
        return json.loads(value) if value else default
    
    def get_all_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get all preferences for a user"""
        if not self.available:
            return {}
        
        pattern = f"user:{user_id}:pref:*"
        keys = self.redis_client.keys(pattern)
        
        preferences = {}
        for key in keys:
            pref_name = key.split(":")[-1]
            value = self.redis_client.get(key)
            preferences[pref_name] = json.loads(value) if value else None
        
        return preferences
    
    # ============== Conversation History ==============
    
    def save_conversation(self, session_id: str, message: Dict[str, Any]) -> None:
        """Save a conversation message"""
        if not self.available:
            # Use in-memory fallback
            if session_id not in self.fallback_memory:
                self.fallback_memory[session_id] = []
            message["timestamp"] = datetime.utcnow().isoformat()
            self.fallback_memory[session_id].append(message)
            # Keep only last 100 messages
            self.fallback_memory[session_id] = self.fallback_memory[session_id][-100:]
            return
            
        conv_key = f"session:{session_id}:conversation"
        message["timestamp"] = datetime.utcnow().isoformat()
        self.redis_client.rpush(conv_key, json.dumps(message))
        # Keep only last 100 messages
        self.redis_client.ltrim(conv_key, -100, -1)
    
    def get_conversation(self, session_id: str, limit: int = 50) -> list:
        """Get conversation history"""
        if not self.available:
            # Use in-memory fallback
            messages = self.fallback_memory.get(session_id, [])
            return messages[-limit:] if messages else []
            
        conv_key = f"session:{session_id}:conversation"
        messages = self.redis_client.lrange(conv_key, -limit, -1)
        return [json.loads(msg) for msg in messages]
    
    def clear_conversation(self, session_id: str) -> None:
        """Clear conversation history"""
        if not self.available:
            if session_id in self.fallback_memory:
                del self.fallback_memory[session_id]
            return
            
        conv_key = f"session:{session_id}:conversation"
        self.redis_client.delete(conv_key)
        logger.info(f"Cleared conversation for session {session_id}")
    
    # ============== User Context ==============
    
    def set_user_context(self, user_id: str, context_data: Dict[str, Any]) -> None:
        """Set user context (skills, interests, goals, etc.)"""
        if not self.available:
            return
            
        context_key = f"user:{user_id}:context"
        current_context = self.get_user_context(user_id)
        current_context.update(context_data)
        self.redis_client.set(context_key, json.dumps(current_context))
        logger.info(f"Updated context for user {user_id}")
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context"""
        if not self.available:
            return {}
            
        context_key = f"user:{user_id}:context"
        context = self.redis_client.get(context_key)
        return json.loads(context) if context else {}
    
    # ============== Recent Actions ==============
    
    def log_action(self, user_id: str, action: str, details: Optional[Dict] = None) -> None:
        """Log user action"""
        if not self.available:
            return
        action_key = f"user:{user_id}:actions"
        action_data = {
            "action": action,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis_client.rpush(action_key, json.dumps(action_data))
        # Keep only last 50 actions
        self.redis_client.ltrim(action_key, -50, -1)
    
    def get_recent_actions(self, user_id: str, limit: int = 10) -> list:
        """Get recent user actions"""
        if not self.available:
            return []
            
        action_key = f"user:{user_id}:actions"
        actions = self.redis_client.lrange(action_key, -limit, -1)
        return [json.loads(action) for action in actions]
    
    # ============== Cache Management ==============
    
    def cache_set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set cache with TTL (time to live in seconds)"""
        if not self.available:
            return
        self.redis_client.setex(f"cache:{key}", ttl, json.dumps(value))
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.available:
            return None
        value = self.redis_client.get(f"cache:{key}")
        return json.loads(value) if value else None
    
    def cache_delete(self, key: str) -> None:
        """Delete cached value"""
        if not self.available:
            return
        self.redis_client.delete(f"cache:{key}")
    
    # ============== Utility ==============
    
    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        if not self.available:
            return True  # In-memory fallback is considered healthy for dev
            
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
