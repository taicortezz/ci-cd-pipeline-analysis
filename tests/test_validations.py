import pytest
from pydantic import ValidationError

from app.models import Task, TaskCreate


def test_task_create_rejects_empty_title():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="",
            description="Invalid task",
            priority="medium",
        )


def test_task_create_rejects_blank_title():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="   ",
            description="Invalid task",
            priority="medium",
        )


def test_task_create_rejects_invalid_priority():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="Study",
            description="Invalid priority",
            priority="urgent",
        )


def test_task_create_accepts_low_priority():
    task = TaskCreate(
        title="Study",
        description="Low priority",
        priority="low",
    )

    assert task.priority == "low"


def test_task_create_accepts_high_priority():
    task = TaskCreate(
        title="Study",
        description="High priority",
        priority="high",
    )

    assert task.priority == "high"


def test_task_rejects_invalid_status():
    with pytest.raises(ValidationError):
        Task(
            id=1,
            title="Study",
            description="Invalid status",
            priority="medium",
            status="archived",
            created_at="2026-06-03T10:00:00Z",
        )


def test_task_create_requires_title():
    with pytest.raises(ValidationError):
        TaskCreate(
            description="Missing title",
            priority="medium",
        )


def test_task_create_requires_description():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="Study",
            priority="medium",
        )


def test_task_uses_medium_priority_by_default():
    task = TaskCreate(
        title="Study",
        description="Default priority",
    )

    assert task.priority == "medium"
