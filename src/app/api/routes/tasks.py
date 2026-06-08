from fastapi import APIRouter, HTTPException, status

from src.app.schemas.voice import Task, TaskCreate, TaskReplace, TaskUpdate
from src.app.services import task_store

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[Task])
def get_tasks() -> list[Task]:
    return [Task.model_validate(task) for task in task_store.list_tasks()]


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    task = task_store.create_task(title=payload.title, done=payload.done)
    return Task.model_validate(task)


@router.put("/{task_id}", response_model=Task)
def replace_task(
    task_id: int,
    payload: TaskReplace,
) -> Task:
    task = task_store.replace_task(
        task_id=task_id,
        title=payload.title,
        done=payload.done,
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )
    return Task.model_validate(task)


@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    payload: TaskUpdate,
) -> Task:
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided to update the task.",
        )

    task = task_store.update_task(
        task_id=task_id,
        title=payload.title,
        done=payload.done,
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )
    return Task.model_validate(task)


@router.delete("/{task_id}")
def delete_task(task_id: int) -> dict[str, str]:
    deleted = task_store.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )
    return {"message": f"Task {task_id} deleted."}
