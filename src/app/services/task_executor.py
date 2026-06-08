import re
from typing import Any

from fastapi import HTTPException, status

from src.app.schemas.voice import InstructionPayload
from src.app.services import task_store

_TASK_ENDPOINT = re.compile(r"^/tasks(?:/(\d+))?$")


def execute_instruction(
    instruction: InstructionPayload,
    *,
    transcription: str | None = None,
) -> Any:
    match = _TASK_ENDPOINT.fullmatch(instruction.endpoint)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Instruction endpoint is invalid.",
        )

    task_id_raw = match.group(1)
    method = instruction.method.upper()
    params = instruction.params

    if task_id_raw is None:
        return _execute_collection_instruction(
            method,
            params,
            transcription=transcription,
        )

    task_id = int(task_id_raw)
    return _execute_item_instruction(method, task_id, params)


def _execute_collection_instruction(
    method: str,
    params: dict[str, Any],
    *,
    transcription: str | None,
) -> Any:
    if method == "GET":
        return task_store.list_tasks()

    if method == "POST":
        title = _coerce_non_empty_string(params.get("title"))
        if title is None and transcription:
            # Voice-first fallback: when the model omits title, use what user said.
            title = transcription.strip()
        if not title:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="POST /tasks requires a non-empty 'title'.",
            )

        done = params.get("done", False)
        if not isinstance(done, bool):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'done' must be a boolean when provided.",
            )

        return task_store.create_task(title=title, done=done)

    if method == "PATCH":
        task_id = _resolve_task_id_from_params(params, transcription=transcription)
        return _execute_item_instruction(method, task_id, params)

    if method == "DELETE":
        task_id = _resolve_task_id_from_params(params, transcription=transcription)
        return _execute_item_instruction(method, task_id, params)

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Method {method} is not supported for /tasks.",
    )


def _execute_item_instruction(method: str, task_id: int, params: dict[str, Any]) -> Any:
    if method == "PUT":
        title = params.get("title")
        done = params.get("done")
        if not isinstance(title, str) or not title.strip() or not isinstance(done, bool):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="PUT /tasks/{id} requires 'title' (non-empty string) and 'done' (boolean).",
            )
        task = task_store.replace_task(task_id=task_id, title=title.strip(), done=done)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        return task

    if method == "PATCH":
        title_raw = params.get("title") if "title" in params else None
        done_raw = params.get("done") if "done" in params else None

        if title_raw is None and done_raw is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="PATCH /tasks/{id} requires at least one of 'title' or 'done'.",
            )

        if title_raw is not None and (not isinstance(title_raw, str) or not title_raw.strip()):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'title' must be a non-empty string when provided.",
            )

        if done_raw is not None and not isinstance(done_raw, bool):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="'done' must be a boolean when provided.",
            )

        task = task_store.update_task(
            task_id=task_id,
            title=title_raw.strip() if isinstance(title_raw, str) and title_raw.strip() else None,
            done=done_raw if isinstance(done_raw, bool) else None,
        )
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        return task

    if method == "DELETE":
        deleted = task_store.delete_task(task_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found.",
            )
        return {"message": f"Task {task_id} deleted."}

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Method {method} is not supported for /tasks/{{id}}.",
    )


def _coerce_non_empty_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _resolve_task_id_from_params(
    params: dict[str, Any],
    *,
    transcription: str | None,
) -> int:
    raw_task_id = params.get("task_id")
    if isinstance(raw_task_id, int):
        return raw_task_id

    selector = (
        _coerce_non_empty_string(params.get("task_title"))
        or _coerce_non_empty_string(params.get("target_title"))
        or _coerce_non_empty_string(params.get("task"))
    )
    selector_from_transcription = _extract_selector_from_transcription(transcription) if transcription else None
    if selector is None and selector_from_transcription:
        selector = selector_from_transcription
    if selector is None:
        selector = _coerce_non_empty_string(params.get("title"))

    if selector is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task selector missing. Provide task_id or task title.",
        )

    matches = task_store.find_tasks_by_title(selector)
    if not matches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found for title '{selector}'.",
        )
    if len(matches) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Multiple tasks match title '{selector}'. Use task ID.",
        )
    return int(matches[0]["id"])


def _extract_selector_from_transcription(transcription: str) -> str | None:
    candidate = transcription.strip()
    if not candidate:
        return None

    lowered = candidate.lower()
    prefixes = (
        "delete ",
        "remove ",
        "complete ",
        "finish ",
        "mark ",
        "set ",
        "update ",
        "rename ",
    )
    for prefix in prefixes:
        if lowered.startswith(prefix):
            candidate = candidate[len(prefix) :].strip()
            break

    if " to " in candidate.lower():
        candidate = candidate.split(" to ", 1)[0].strip()

    lowered = candidate.lower()
    suffixes = (" as done", " done", " as complete", " complete")
    for suffix in suffixes:
        if lowered.endswith(suffix):
            candidate = candidate[: -len(suffix)].strip()
            break

    if candidate.lower().startswith("task "):
        candidate = candidate[5:].strip()

    return candidate or None