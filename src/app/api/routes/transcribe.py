from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from src.app.schemas.voice import TranscribeFlowResponse
from src.app.services.instruction_service import build_instruction
from src.app.services.task_executor import execute_instruction
from src.app.services.transcription_service import transcribe_audio
from src.app.utils.language import normalize_transcription_language

router = APIRouter(tags=["transcribe"])


@router.get("/")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/transcribe", response_model=TranscribeFlowResponse)
async def transcribe_and_run_flow(
    request: Request,
    file: UploadFile | None = File(default=None),
    language: str | None = Form(default=None),
) -> TranscribeFlowResponse:
    transcription = await _resolve_transcription(
        request=request,
        file=file,
        language=language,
    )
    instruction = build_instruction(transcription)
    result = execute_instruction(instruction, transcription=transcription)
    return TranscribeFlowResponse(
        transcription=transcription,
        instruction=instruction,
        result=result,
    )


async def _resolve_transcription(
    *,
    request: Request,
    file: UploadFile | None,
    language: str | None,
) -> str:
    if file is not None:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded audio file is empty.",
            )
        normalized_language = normalize_transcription_language(language)
        return transcribe_audio(
            filename=file.filename or "command.webm",
            audio_bytes=audio_bytes,
            language=normalized_language,
        )

    json_payload: object | None = None
    if request.headers.get("content-type", "").lower().startswith("application/json"):
        json_payload = await request.json()

    if isinstance(json_payload, dict):
        manual_transcription = json_payload.get("transcription")
        if isinstance(manual_transcription, str) and manual_transcription.strip():
            return manual_transcription.strip()

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Provide either multipart 'file' audio or JSON body with non-empty 'transcription'.",
    )
