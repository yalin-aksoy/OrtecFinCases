from datetime import date
from typing import Dict, List, Optional

from task import Task
from task_analytics import TaskAnalytics


class TaskList:
    _instance: Optional["TaskList"] = None

    def __new__(cls) -> "TaskList":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._tasks: Dict[str, List[Task]] = {}
        self._last_id = 0
        self._analytics = TaskAnalytics()
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "TaskList":
        return cls()

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def list_tasks(self) -> Dict[str, List[Task]]:
        return self._tasks

    def has_project(self, name: str) -> bool:
        return name in self._tasks

    def get_project_tasks(self, name: str) -> Optional[List[Task]]:
        return self._tasks.get(name)

    def add_project(self, name: str) -> None:
        self._tasks[name] = []

    def add_task(self, project: str, description: str) -> bool:
        project_tasks = self._tasks.get(project)
        if project_tasks is None:
            return False

        project_tasks.append(Task(self._next_id(), description, False))
        return True

    def check(self, task_id: int) -> bool:
        return self.set_done(task_id, True)

    def uncheck(self, task_id: int) -> bool:
        return self.set_done(task_id, False)

    def set_done(self, task_id: int, done: bool) -> bool:
        for tasks in self._tasks.values():
            for task in tasks:
                if task.id == task_id:
                    task.done = done
                    return True
        return False

    def add_deadline(self, task_id: int, deadline: date) -> bool:
        for tasks in self._tasks.values():
            for task in tasks:
                if task.id == task_id:
                    task.deadline = deadline
                    return True
        return False

    def get_task(self, task_id: int) -> Optional[Task]:
        for tasks in self._tasks.values():
            for task in tasks:
                if task.id == task_id:
                    return task
        return None

    def get_by_deadline(self) -> Dict[date | None, Dict[str, List[Task]]]:
        deadlines_dict: Dict[date | None, Dict[str, List[Task]]] = {}
        for project_name, tasks in self._tasks.items():
            for task in tasks:
                project_tasks = deadlines_dict.setdefault(task.deadline, {})
                project_tasks.setdefault(project_name, []).append(task)
        return deadlines_dict

    def get_today_tasks(self) -> Dict[str, List[Task]]:
        today = date.today()
        return {
            project_name: [task for task in tasks if task.deadline == today]
            for project_name, tasks in self._tasks.items()
            if any(task.deadline == today for task in tasks)
        }

    def _next_id(self) -> int:
        self._last_id += 1
        return self._last_id
