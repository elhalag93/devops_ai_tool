from typing import Dict, List, Any
from datetime import datetime
import uuid

class Task:
    def __init__(self, name: str, description: str, task_type: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.type = task_type
        self.status = 'pending'
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, task_details: Dict[str, str]) -> Task:
        task = Task(
            name=task_details['name'],
            description=task_details['description'],
            task_type=task_details['type']
        )
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def update_task_status(self, task_id: str, status: str) -> Task:
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.now()
        return task 