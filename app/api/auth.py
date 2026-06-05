import uuid
from fastapi import APIRouter, Depends, status
from fastapi.concurrency import run_in_threadpool

from app.auth.dependencies import get_current_user
from app.auth.models import UserContext
from app.models.audit import AuditRecord
from app.schemas.common import MessageResponse
from app.services.dynamodb_service import DynamoDBService
from app.api.deps import get_dynamodb_service
from app.utils.time import now_utc_iso

router = APIRouter()


@router.post("/login", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def record_login(
    current_user: UserContext = Depends(get_current_user),
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service),
) -> MessageResponse:
    record = AuditRecord(
        audit_id=str(uuid.uuid4()),
        event_type="login",
        timestamp=now_utc_iso(),
        user_id=current_user.user_id,
        document_id=None,
        metadata={"role": current_user.role},
    )
    await run_in_threadpool(dynamodb_service.put_audit_log, record)
    return MessageResponse(message="Login audit recorded")
