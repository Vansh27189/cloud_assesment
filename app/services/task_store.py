"""Thread-safe distributed task repository."""

import threading
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.models import TaskCreateRequest, TaskItem


class TaskStore:
    """In-memory thread-safe task store simulating distributed work queue."""

    def __init__(self):
        self._tasks: List[TaskItem] = []
        self._lock = threading.Lock()

    def create_task(self, req: TaskCreateRequest, instance_id: str) -> TaskItem:
        """Create and store a new task."""
        with self._lock:
            task = TaskItem(
                id=f"tsk-{uuid.uuid4().hex[:8]}",
                title=req.title,
                description=req.description or "",
                priority=req.priority,
                status="queued",
                created_at=datetime.now(timezone.utc).isoformat(),
                processed_by=instance_id,
            )
            self._tasks.insert(0, task)
            # Cap maximum tasks in memory to avoid unlimited growth
            if len(self._tasks) > 200:
                self._tasks.pop()
            return task

    def get_all(self, limit: int = 50) -> List[TaskItem]:
        """Retrieve recent tasks."""
        with self._lock:
            return list(self._tasks[:limit])

    def get_by_id(self, task_id: str) -> Optional[TaskItem]:
        """Find a single task by ID."""
        with self._lock:
            for t in self._tasks:
                if t.id == task_id:
                    return t
            return None

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        with self._lock:
            for idx, t in enumerate(self._tasks):
                if t.id == task_id:
                    self._tasks.pop(idx)
                    return True
            return False

    def count(self) -> int:
        """Return total number of active tasks."""
        with self._lock:
            return len(self._tasks)

    def clear(self) -> None:
        """Clear all tasks (used in test resets)."""
        with self._lock:
            self._tasks.clear()


# Global singleton instance
task_store = TaskStore()
