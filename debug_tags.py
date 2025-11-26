from tools.task_manager import TaskManager
from models.task import TaskCreate
import sys

try:
    print("Initializing TaskManager...")
    tm = TaskManager()
    print("TaskManager initialized.")
    
    task_data = TaskCreate(
        title="Debug Task",
        tags=["debug"]
    )
    
    print("Creating task...")
    created = tm.create_task(task_data)
    print(f"Task created: {created.task_id} with tags: {created.tags}")
    
    print("Retrieving task...")
    retrieved = tm.get_task(created.task_id)
    print(f"Task retrieved: {retrieved.tags}")
    
    print("Deleting task...")
    tm.delete_task(created.task_id)
    print("Task deleted.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
