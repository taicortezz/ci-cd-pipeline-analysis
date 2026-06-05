from app.models import TaskCreate, TaskPriority, TaskStatus
from app.services import TaskService


def make_task(title="Study metrics", priority=TaskPriority.MEDIUM):
    return TaskCreate(
        title=title,
        description="Analyze GitHub Actions runs",
        priority=priority,
    )


def test_service_creates_task_with_incremental_id():
    service = TaskService()

    first = service.create_task(make_task("First"))
    second = service.create_task(make_task("Second"))

    assert first.id == 1
    assert second.id == 2


def test_service_creates_task_as_pending():
    service = TaskService()

    task = service.create_task(make_task())

    assert task.status == TaskStatus.PENDING


def test_service_lists_all_tasks():
    service = TaskService()
    service.create_task(make_task("First"))
    service.create_task(make_task("Second"))

    tasks = service.list_tasks()

    assert len(tasks) == 2


def test_service_gets_existing_task():
    service = TaskService()
    task = service.create_task(make_task())

    found = service.get_task(task.id)

    assert found == task


def test_service_returns_none_for_missing_task():
    service = TaskService()

    assert service.get_task(123) is None


def test_service_completes_existing_task():
    service = TaskService()
    task = service.create_task(make_task())

    completed = service.complete_task(task.id)

    assert completed is not None
    assert completed.status == TaskStatus.COMPLETED


def test_service_returns_none_when_completing_missing_task():
    service = TaskService()

    assert service.complete_task(123) is None


def test_service_deletes_existing_task():
    service = TaskService()
    task = service.create_task(make_task())

    deleted = service.delete_task(task.id)

    assert deleted is True
    assert service.get_task(task.id) is None


def test_service_returns_false_when_deleting_missing_task():
    service = TaskService()

    assert service.delete_task(123) is False


def test_service_calculates_stats():
    service = TaskService()
    first = service.create_task(make_task("First"))
    service.create_task(make_task("Second"))
    service.complete_task(first.id)

    stats = service.get_stats()

    assert stats.total_tasks == 2
    assert stats.completed_tasks == 1
    assert stats.pending_tasks == 1
