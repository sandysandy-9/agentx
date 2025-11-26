import requests
import json
import time
import uuid

API_BASE = "http://localhost:8000"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def log(message, success=True):
    icon = "✅" if success else "❌"
    color = GREEN if success else RED
    print(f"{color}{icon} {message}{RESET}")

def test_input_validation():
    print("\n--- Testing Input Validation ---")
    
    # 1. Chat: Empty Message
    try:
        resp = requests.post(f"{API_BASE}/chat", json={"message": ""})
        # Should handle gracefully (200 OK with "I didn't hear you" or 422 Validation Error)
        if resp.status_code in [200, 422]:
            log("Chat handled empty message gracefully")
        else:
            log(f"Chat empty message failed: {resp.status_code}", False)
    except Exception as e:
        log(f"Chat exception: {e}", False)

    # 2. Tasks: Invalid Priority
    try:
        payload = {"title": "Bad Task", "priority": "super_urgent_mega_high"}
        resp = requests.post(f"{API_BASE}/tasks", json=payload)
        # Expect 422 Unprocessable Entity due to strict Literal validation
        if resp.status_code == 422:
             log("Task creation correctly rejected invalid priority (422)")
        else:
             log(f"Task creation with invalid priority gave unexpected status: {resp.status_code}", False)
    except Exception as e:
        log(f"Task exception: {e}", False)

def test_error_handling():
    print("\n--- Testing Error Handling ---")
    
    # 1. 404 Non-existent Task
    try:
        fake_id = str(uuid.uuid4())
        resp = requests.get(f"{API_BASE}/tasks/{fake_id}")
        if resp.status_code == 404:
            log("Correctly returned 404 for non-existent task")
        else:
            log(f"Incorrect status for non-existent task: {resp.status_code}", False)
    except Exception as e:
        log(f"404 check exception: {e}", False)

    # 2. 404 Non-existent Document
    try:
        resp = requests.delete(f"{API_BASE}/documents/fake_file.pdf")
        # 503 if doc search not init, 404 if init but not found
        if resp.status_code in [404, 503]: 
            log("Correctly returned 404/503 for non-existent document")
        else:
            log(f"Incorrect status for non-existent document: {resp.status_code}", False)
    except Exception as e:
        log(f"Doc 404 check exception: {e}", False)

def test_complex_workflow():
    print("\n--- Testing Complex Workflows ---")
    
    # Task Lifecycle
    task_id = None
    try:
        # Create
        resp = requests.post(f"{API_BASE}/tasks", json={"title": "Lifecycle Task", "status": "pending"})
        if resp.status_code == 200:
            task_id = resp.json().get("id") or resp.json().get("_id")
            log("Step 1: Task Created")
        else:
            log("Step 1 Failed", False)
            return

        # Update
        if task_id:
            resp = requests.put(f"{API_BASE}/tasks/{task_id}", json={"status": "completed"})
            if resp.status_code == 200 and resp.json().get("status") == "completed":
                log("Step 2: Task Updated")
            else:
                log("Step 2 Failed", False)

        # Delete
        if task_id:
            resp = requests.delete(f"{API_BASE}/tasks/{task_id}")
            if resp.status_code == 200:
                log("Step 3: Task Deleted")
            else:
                log("Step 3 Failed", False)

        # Verify Gone
        if task_id:
            resp = requests.get(f"{API_BASE}/tasks/{task_id}")
            if resp.status_code == 404:
                log("Step 4: Task Verified Gone")
            else:
                log(f"Step 4 Failed: Got {resp.status_code}", False)

    except Exception as e:
        log(f"Lifecycle exception: {e}", False)

def test_visualization_robustness():
    print("\n--- Testing Visualization Robustness ---")
    
    # 1. Malformed CSV
    try:
        payload = {
            "message": "visualize this",
            "csv_data": "Column1,Column2\nA,1\nB,MissingValue\nC,3",
            "chart_type": "bar_chart"
        }
        resp = requests.post(f"{API_BASE}/visualize", json=payload)
        # Should handle gracefully
        if resp.status_code == 200:
            log("Server handled malformed CSV without crashing")
        else:
            log(f"Server crashed on malformed CSV: {resp.status_code}", False)
    except Exception as e:
        log(f"Viz exception: {e}", False)

if __name__ == "__main__":
    print(f"🚀 Starting Deep System Test against {API_BASE}")
    test_input_validation()
    test_error_handling()
    test_complex_workflow()
    test_visualization_robustness()
    print("\n🏁 Deep Test Completed")
