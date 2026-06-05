import time

from app.models import TaskCreate, TaskPriority
from app.services import TaskService


def test_bulk_task_workflow_simulates_costly_usage_scenario():
    service = TaskService()
    created_tasks = []

    for index in range(500):
        priority = TaskPriority.HIGH if index % 3 == 0 else TaskPriority.MEDIUM
        task = service.create_task(
            TaskCreate(
                title=f"Task {index}",
                description="Bulk task created for pipeline timing analysis",
                priority=priority,
            )
        )
        created_tasks.append(task)

    for task in created_tasks[:250]:
        completed = service.complete_task(task.id)
        assert completed is not None

    for task in created_tasks:
        found = service.get_task(task.id)
        assert found is not None

    stats = service.get_stats()
    assert stats.total_tasks == 500
    assert stats.completed_tasks == 250
    assert stats.pending_tasks == 250

    for task in created_tasks[250:350]:
        assert service.delete_task(task.id) is True

    updated_stats = service.get_stats()
    assert updated_stats.total_tasks == 400
    assert updated_stats.completed_tasks == 250
    assert updated_stats.pending_tasks == 150

    # Simula uma operacao mais custosa para tornar o impacto visivel no CI.
    time.sleep(3)
