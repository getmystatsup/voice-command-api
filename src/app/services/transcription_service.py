from fastapi import HTTPException, status
from groq import Groq

from src.app.core.config import get_settings


def transcribe_audio(
    *,
    filename: str,
    audio_bytes: bytes,
    language: str | None,
) -> str:
    settings = get_settings()
    client = Groq(
        api_key=settings.groq_api_key,
        timeout=settings.request_timeout_seconds,
    )

    request_data: dict[str, object] = {
        "file": (filename, audio_bytes),
        "model": settings.groq_transcription_model,
    }
    if language:
        request_data["language"] = language

    try:
        response = client.audio.transcriptions.create(**request_data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to transcribe audio with Groq.",
        ) from exc

    text = _extract_transcription_text(response)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq returned an empty transcription.",
        )
    return text


def _extract_transcription_text(response: object) -> str:
    if isinstance(response, str):
        return response.strip()

    if hasattr(response, "text") and isinstance(response.text, str):
        return response.text.strip()

    if hasattr(response, "model_dump"):
        data = response.model_dump()
        text = data.get("text")
        if isinstance(text, str):
            return text.strip()

    if isinstance(response, dict):
        text = response.get("text")
        if isinstance(text, str):
            return text.strip()

    return ""