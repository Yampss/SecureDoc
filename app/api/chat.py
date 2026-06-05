from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_bedrock_service, get_dynamodb_service
from app.auth.dependencies import get_current_user
from app.auth.models import UserContext
from app.models.audit import AuditRecord
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.bedrock_service import BedrockService
from app.services.dynamodb_service import DynamoDBService
from app.utils.time import now_utc_iso
import uuid

router = APIRouter()


def _audit(
    dynamodb_service: DynamoDBService,
    event_type: str,
    user_id: str,
    document_id: str | None = None,
    metadata: dict | None = None,
) -> None:
    record = AuditRecord(
        audit_id=str(uuid.uuid4()),
        event_type=event_type,
        timestamp=now_utc_iso(),
        user_id=user_id,
        document_id=document_id,
        metadata=metadata,
    )
    dynamodb_service.put_audit_log(record)


@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
    document_id: str,
    request: ChatRequest,
    current_user: UserContext = Depends(get_current_user),
    bedrock_service: BedrockService = Depends(get_bedrock_service),
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service),
) -> ChatResponse:
    item = await run_in_threadpool(dynamodb_service.get_document, document_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    extracted_text = item.get("extracted_text", "")
    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text is not available yet.",
        )

    answer = await run_in_threadpool(
        bedrock_service.answer_question, extracted_text[:12000], request.question
    )

    await run_in_threadpool(
        _audit,
        dynamodb_service,
        "chat",
        current_user.user_id,
        document_id,
        {"question": request.question},
    )
    return ChatResponse(answer=answer)
