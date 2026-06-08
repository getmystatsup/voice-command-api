from typing import Any

tasks: list[dict[str, Any]] = []
_next_task_id = 1


def normalize_title(value: str) -> str:
    return " ".join(value.strip().lower().split())


def list_tasks() -> list[dict[str, Any]]:
    return [dict(task) for task in tasks]


def create_task(title: str, done: bool = False) -> dict[str, Any]:
    global _next_task_id
    task = {"id": _next_task_id, "title": title, "done": done}
    tasks.append(task)
    _next_task_id += 1
    return dict(task)


def get_task(task_id: int) -> dict[str, Any] | None:
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def replace_task(task_id: int, title: str, done: bool) -> dict[str, Any] | None:
    task = get_task(task_id)
    if task is None:
        return None
    task["title"] = title
    task["done"] = done
    return dict(task)


def update_task(
    task_id: int,
    *,
    title: str | None = None,
    done: bool | None = None,
) -> dict[str, Any] | None:
    task = get_task(task_id)
    if task is None:
        return None
    if title is not None:
        task["title"] = title
    if done is not None:
        task["done"] = done
    return dict(task)


def delete_task(task_id: int) -> bool:
    for idx, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(idx)
            return True
    return False


def find_tasks_by_title(title: str) -> list[dict[str, Any]]:
    normalized = normalize_title(title)
    return [
        dict(task)
        for task in tasks
        if isinstance(task.get("title"), str)
        and normalize_title(task["title"]) == normalized
    ]