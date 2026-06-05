from datetime import datetime, timezone

from app.models import Task, TaskCreate, TaskStats, TaskStatus


class TaskService:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def create_task(self, data: TaskCreate) -> Task:
        task = Task(
            id=self._next_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def complete_task(self, task_id: int) -> Task | None:
        task = self.get_task(task_id)
        if task is None:
            return None

        updated_task = task.model_copy(update={"status": TaskStatus.COMPLETED})
        self._tasks[task_id] = updated_task
        return updated_task

    def delete_task(self, task_id: int) -> bool:
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        return True

    def get_stats(self) -> TaskStats:
        total_tasks = len(self._tasks)
        completed_tasks = sum(
            task.status == TaskStatus.COMPLETED
            for task in self._tasks.values()
        )

        return TaskStats(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=total_tasks - completed_tasks,
        )

    def clear(self) -> None:
        self._tasks.clear()
        self._next_id = 1
