import json
import re
from urllib.parse import urlparse

from fastapi import HTTPException, status
from groq import Groq

from src.app.core.config import get_settings
from src.app.schemas.voice import InstructionPayload

ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
ALLOWED_ENDPOINT_PATTERN = re.compile(r"^/tasks(?:/\d+)?$")

SYSTEM_PROMPT = """
You convert natural-language transcriptions into API instructions.

Return only a JSON object in this exact shape:
{
  "endpoint": "/tasks",
  "method": "POST",
  "params": {"title": "Buy groceries"}
}

Rules:
- Output must be valid JSON only. No markdown. No code fences. No explanations.
- endpoint must be either /tasks or /tasks/{id}.
- method must be one of GET, POST, PUT, PATCH, DELETE.
- params must always be a JSON object (use {} when empty).
- For create commands, use POST /tasks and include params.title.
- For mark-done commands, prefer PATCH and include params.done=true.
- For update/rename commands, use PATCH and include params.title for the updated title.
- For delete commands, use DELETE.
- If task id is unknown, include a selector in params.task_title.
""".strip()


def build_instruction(transcription: str) -> InstructionPayload:
    settings = get_settings()
    client = Groq(
        api_key=settings.groq_api_key,
        timeout=settings.request_timeout_seconds,
    )

    try:
        completion = client.chat.completions.create(
            model=settings.groq_model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Transcription: {transcription}",
                },
            ],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to get instruction from Groq.",
        ) from exc

    content = completion.choices[0].message.content if completion.choices else None
    if not content or not isinstance(content, str):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq returned an empty instruction response.",
        )

    return _validate_instruction_content(content)


def _validate_instruction_content(content: str) -> InstructionPayload:
    normalized = _strip_markdown_fence(content)
    try:
        data = json.loads(normalized)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq returned invalid JSON for instruction.",
        ) from exc

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Instruction payload must be a JSON object.",
        )

    endpoint = data.get("endpoint")
    method = data.get("method")
    params = data.get("params", {})

    if isinstance(endpoint, str):
        endpoint, method, params = _normalize_instruction(endpoint, method, params)

    if isinstance(method, str):
        method, params = _normalize_method(method, params)

    if not isinstance(endpoint, str) or not ALLOWED_ENDPOINT_PATTERN.fullmatch(endpoint):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Instruction endpoint is invalid.",
        )

    if not isinstance(method, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Instruction method is invalid.",
        )
    normalized_method = method.upper()
    if normalized_method not in ALLOWED_METHODS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Instruction method is not allowed.",
        )

    if not isinstance(params, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Instruction params must be an object.",
        )

    return InstructionPayload(
        endpoint=endpoint,
        method=normalized_method,
        params=params,
    )


def _normalize_instruction(
    endpoint: str,
    method: object,
    params: object,
) -> tuple[str, object, object]:
    normalized_endpoint = endpoint.strip()
    if normalized_endpoint.startswith("http://") or normalized_endpoint.startswith("https://"):
        normalized_endpoint = urlparse(normalized_endpoint).path

    if not normalized_endpoint.startswith("/"):
        normalized_endpoint = "/" + normalized_endpoint

    normalized_endpoint = re.sub(r"/+", "/", normalized_endpoint).rstrip("/") or "/"
    if normalized_endpoint == "/task":
        normalized_endpoint = "/tasks"
    elif normalized_endpoint.startswith("/task/"):
        normalized_endpoint = "/tasks/" + normalized_endpoint[len("/task/") :]

    if re.fullmatch(r"/tasks/\d+/done", normalized_endpoint):
        normalized_endpoint = normalized_endpoint.rsplit("/", 1)[0]
        method = "PATCH"
        if isinstance(params, dict) and "done" not in params:
            params = {**params, "done": True}

    if not ALLOWED_ENDPOINT_PATTERN.fullmatch(normalized_endpoint):
        lowered = normalized_endpoint.lower()
        if "task" in lowered:
            id_match = re.search(r"(\d+)", lowered)
            normalized_endpoint = f"/tasks/{id_match.group(1)}" if id_match else "/tasks"

    return normalized_endpoint, method, params


def _normalize_method(method: str, params: object) -> tuple[str, object]:
    normalized = method.strip().upper()
    if normalized in ALLOWED_METHODS:
        return normalized, params

    alias_map = {
        "CREATE": "POST",
        "ADD": "POST",
        "LIST": "GET",
        "FETCH": "GET",
        "REMOVE": "DELETE",
        "COMPLETE": "PATCH",
        "DONE": "PATCH",
        "MARK_DONE": "PATCH",
        "UPDATE": "PATCH",
    }
    mapped = alias_map.get(normalized)
    if mapped is None:
        return normalized, params

    if mapped == "PATCH" and isinstance(params, dict) and "done" not in params:
        params = {**params, "done": True}
    return mapped, params


def _strip_markdown_fence(content: str) -> str:
    text = content.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if not lines:
        return text

    # Accept fenced output defensively, even though prompt forbids it.
    first = 1 if lines[0].startswith("```") else 0
    last = len(lines)
    if lines and lines[-1].strip() == "```":
        last -= 1
    return "\n".join(lines[first:last]).strip()