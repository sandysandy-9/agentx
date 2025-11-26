import pytest
from tools.task_manager import TaskManager
from models.task import TaskCreate

def test_task_tags():
    # Initialize TaskManager
    # Note: This requires MongoDB to be running. 
    # If MongoDB is not running, this test might fail or we should mock it.
    # For now, assuming MongoDB is available as per project setup.
    
    try:
        tm = TaskManager()
        
        # Create task with tags
        task_data = TaskCreate(
            title="Test Task with Tags",
            priority="high",
            tags=["test", "urgent", "feature"]
        )
        
        created_task = tm.create_task(task_data)
        
        assert created_task.tags == ["test", "urgent", "feature"]
        
        # Retrieve task
        retrieved_task = tm.get_task(created_task.task_id)
        assert retrieved_task.tags == ["test", "urgent", "feature"]
        
        # Clean up
        tm.delete_task(created_task.task_id)
        
    except Exception as e:
        pytest.fail(f"Test failed: {e}")
