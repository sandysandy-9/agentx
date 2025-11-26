import requests
import json
import os
import time
import uuid

API_BASE = "http://localhost:8000"
SESSION_ID = f"test_session_{int(time.time())}"
USER_ID = "test_user"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def log(message, success=True):
    icon = "✅" if success else "❌"
    color = GREEN if success else RED
    print(f"{color}{icon} {message}{RESET}")

def test_health():
    print("\n--- Testing Health Endpoints ---")
    try:
        # Root
        resp = requests.get(f"{API_BASE}/")
        if resp.status_code == 200:
            log("Root endpoint is accessible")
        else:
            log(f"Root endpoint failed: {resp.status_code}", False)

        # Health
        resp = requests.get(f"{API_BASE}/health")
        if resp.status_code == 200:
            data = resp.json()
            log(f"Health check passed (Status: {data.get('status')})")
        else:
            log(f"Health check failed: {resp.status_code}", False)
    except Exception as e:
        log(f"Health check exception: {e}", False)

def test_chat():
    print("\n--- Testing Chat Endpoint ---")
    payload = {
        "message": "Hello, are you working?",
        "session_id": SESSION_ID,
        "user_id": USER_ID
    }
    try:
        resp = requests.post(f"{API_BASE}/chat", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("response"):
                log("Chat response received")
            else:
                log("Chat response empty", False)
        else:
            log(f"Chat request failed: {resp.status_code}", False)
    except Exception as e:
        log(f"Chat exception: {e}", False)

def test_tasks():
    print("\n--- Testing Task Management ---")
    task_id = None
    
    # 1. Create Task
    try:
        payload = {
            "title": "Test Task",
            "priority": "high",
            "status": "pending",
            "tags": ["test", "automated"]
        }
        resp = requests.post(f"{API_BASE}/tasks", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            task_id = data.get("id") or data.get("_id")
            log(f"Task created (ID: {task_id})")
        else:
            log(f"Create task failed: {resp.status_code}", False)
            return
    except Exception as e:
        log(f"Create task exception: {e}", False)
        return

    # 2. List Tasks
    try:
        resp = requests.get(f"{API_BASE}/tasks")
        if resp.status_code == 200:
            data = resp.json()
            tasks = data.get("tasks", [])
            if any(t.get("id") == task_id or t.get("_id") == task_id for t in tasks):
                log("Task found in list")
            else:
                log("Task NOT found in list", False)
        else:
            log(f"List tasks failed: {resp.status_code}", False)
    except Exception as e:
        log(f"List tasks exception: {e}", False)

    # 3. Update Task
    if task_id:
        try:
            payload = {"status": "in_progress"}
            resp = requests.put(f"{API_BASE}/tasks/{task_id}", json=payload)
            if resp.status_code == 200:
                log("Task updated successfully")
            else:
                log(f"Update task failed: {resp.status_code}", False)
        except Exception as e:
            log(f"Update task exception: {e}", False)

    # 4. Delete Task
    if task_id:
        try:
            resp = requests.delete(f"{API_BASE}/tasks/{task_id}")
            if resp.status_code == 200:
                log("Task deleted successfully")
            else:
                log(f"Delete task failed: {resp.status_code}", False)
        except Exception as e:
            log(f"Delete task exception: {e}", False)

def test_visualization():
    print("\n--- Testing Visualization ---")
    csv_content = "Category,Value\nA,10\nB,20\nC,30"
    payload = {
        "message": "visualize this data",
        "csv_data": csv_content,
        "chart_type": "bar_chart"
    }
    try:
        resp = requests.post(f"{API_BASE}/visualize", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                log("Visualization generated")
            else:
                log(f"Visualization failed: {data.get('error')}", False)
        else:
            log(f"Visualization request failed: {resp.status_code}", False)
    except Exception as e:
        log(f"Visualization exception: {e}", False)

def test_memory():
    print("\n--- Testing Memory ---")
    try:
        # Get history
        resp = requests.get(f"{API_BASE}/memory/conversation/{SESSION_ID}")
        if resp.status_code == 200:
            log("Conversation history retrieved")
        else:
            log(f"Get history failed: {resp.status_code}", False)

        # Clear history
        resp = requests.delete(f"{API_BASE}/memory/conversation/{SESSION_ID}")
        if resp.status_code == 200:
            log("Conversation history cleared")
        else:
            log(f"Clear history failed: {resp.status_code}", False)
    except Exception as e:
        log(f"Memory exception: {e}", False)

def run_all_tests():
    print("🚀 Starting Comprehensive System Test...")
    print(f"Target: {API_BASE}")
    
    test_health()
    test_chat()
    test_tasks()
    test_visualization()
    test_memory()
    
    print("\n🏁 Test Suite Completed")

if __name__ == "__main__":
    run_all_tests()
