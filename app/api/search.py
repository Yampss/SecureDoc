from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_dynamodb_service
from app.auth.dependencies import get_current_user
from app.auth.models import UserContext
from app.models.audit import AuditRecord
from app.schemas.document import DocumentResponse
from app.schemas.search import SearchResponse
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


@router.get("/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=1),
    current_user: UserContext = Depends(get_current_user),
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service),
) -> SearchResponse:
    results = await run_in_threadpool(dynamodb_service.search_documents, q)
    documents = [DocumentResponse(**item) for item in results]

    await run_in_threadpool(
        _audit,
        dynamodb_service,
        "search",
        current_user.user_id,
        None,
        {"query": q, "count": len(documents)},
    )
    return SearchResponse(query=q, results=documents)
