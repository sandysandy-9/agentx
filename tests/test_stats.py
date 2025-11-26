import pytest
from tools.task_manager import TaskManager
from models.task import TaskCreate, TaskUpdate

def test_task_stats():
    try:
        tm = TaskManager()
        
        # Create some sample tasks
        t1 = tm.create_task(TaskCreate(title="Task 1", priority="high"))
        
        t2 = tm.create_task(TaskCreate(title="Task 2", priority="medium"))
        tm.update_task(t2.task_id, TaskUpdate(status="completed"))
        
        t3 = tm.create_task(TaskCreate(title="Task 3", priority="low"))
        tm.update_task(t3.task_id, TaskUpdate(status="in_progress"))
        
        stats = tm.get_statistics()
        
        assert "total_tasks" in stats
        assert "by_status" in stats
        assert "by_priority" in stats
        
        assert stats["total_tasks"] >= 3
        assert stats["by_status"]["completed"] >= 1
        assert stats["by_priority"]["high"] >= 1
        
        print("Stats verification successful")
        
    except Exception as e:
        pytest.fail(f"Test failed: {e}")
