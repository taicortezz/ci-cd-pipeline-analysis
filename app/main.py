from fastapi import FastAPI, HTTPException, Response, status

from app.models import Task, TaskCreate, TaskStats
from app.services import TaskService

app = FastAPI(title="Task Manager CI Metrics")
task_service = TaskService()


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate) -> Task:
    return task_service.create_task(task)


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    return task_service.list_tasks()


@app.get("/tasks/stats", response_model=TaskStats)
def get_task_stats() -> TaskStats:
    return task_service.get_stats()


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    task = task_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int) -> Task:
    task = task_service.complete_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    deleted = task_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
