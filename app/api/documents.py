import logging
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, HTTPException, File
from fastapi import status
from fastapi.concurrency import run_in_threadpool

from app.api.deps import (
    get_bedrock_service,
    get_dynamodb_service,
    get_s3_service,
    get_textract_service,
)
from app.auth.dependencies import get_current_user
from app.auth.models import UserContext
from app.models.audit import AuditRecord
from app.models.document import DocumentRecord
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services.bedrock_service import BedrockService
from app.services.dynamodb_service import DynamoDBService
from app.services.s3_service import S3Service
from app.services.textract_service import TextractService
from app.utils.files import validate_upload_file
from app.utils.time import now_utc_iso

logger = logging.getLogger(__name__)

router = APIRouter()

STATUS_UPLOADED = "UPLOADED"
STATUS_PROCESSING = "PROCESSING"
STATUS_READY = "READY"
STATUS_FAILED = "FAILED"


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


def _process_document(
    document_id: str,
    s3_key: str,
    content_type: str,
    s3_service: S3Service,
    textract_service: TextractService,
    bedrock_service: BedrockService,
    dynamodb_service: DynamoDBService,
    bucket_name: str,
) -> None:
    try:
        dynamodb_service.update_document_fields(
            document_id, {"status": STATUS_PROCESSING}
        )
        if content_type == "application/pdf":
            extracted_text = textract_service.extract_text_from_s3(bucket_name, s3_key)
        else:
            content = s3_service.get_object_bytes(s3_key)
            extracted_text = textract_service.extract_text_from_bytes(content)

        dynamodb_service.update_document_fields(
            document_id, {"extracted_text": extracted_text}
        )
        summary_source = extracted_text[:12000]
        summary = bedrock_service.generate_summary(summary_source)
        dynamodb_service.update_document_fields(
            document_id, {"summary": summary, "status": STATUS_READY}
        )
    except Exception:
        logger.exception("document_processing_failed", extra={"document_id": document_id})
        dynamodb_service.update_document_fields(
            document_id, {"status": STATUS_FAILED}
        )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: UserContext = Depends(get_current_user),
    s3_service: S3Service = Depends(get_s3_service),
    textract_service: TextractService = Depends(get_textract_service),
    bedrock_service: BedrockService = Depends(get_bedrock_service),
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service),
) -> DocumentResponse:
    validate_upload_file(file)

    document_id = str(uuid.uuid4())
    s3_key = f"documents/{document_id}/{file.filename}"
    content_type = file.content_type or "application/octet-stream"

    await run_in_threadpool(s3_service.upload_fileobj, file.file, s3_key, content_type)

    record = DocumentRecord(
        document_id=document_id,
        filename=file.filename or "",
        uploaded_by=current_user.user_id,
        upload_timestamp=now_utc_iso(),
        s3_key=s3_key,
        status=STATUS_UPLOADED,
        summary="",
        extracted_text="",
        content_type=content_type,
    )
    await run_in_threadpool(dynamodb_service.put_document, record)
    await run_in_threadpool(
        _audit,
        dynamodb_service,
        "upload",
        current_user.user_id,
        document_id,
        {"filename": file.filename},
    )

    background_tasks.add_task(
        _process_document,
        document_id,
        s3_key,
        content_type,
        s3_service,
        textract_service,
        bedrock_service,
        dynamodb_service,
        s3_service.bucket_name,
    )

    return DocumentResponse(
        document_id=document_id,
        filename=file.filename or "",
        uploaded_by=current_user.user_id,
        upload_timestamp=record.upload_timestamp,
        s3_key=s3_key,
        status=STATUS_UPLOADED,
        summary=record.summary,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    current_user: UserContext = Depends(get_current_user),
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service),
) -> DocumentListResponse:
    items = await run_in_threadpool(dynamodb_service.list_documents)
    documents = [DocumentResponse(**item) for item in items]
    await run_in_threadpool(
        _audit,
        dynamodb_service,
        "list",
        current_user.user_id,
        None,
        {"count": len(documents)},
    )
    return DocumentListResponse(documents=documents)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: UserContext = Depends(get_current_user),
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service),
) -> DocumentResponse:
    item = await run_in_threadpool(dynamodb_service.get_document, document_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await run_in_threadpool(
        _audit,
        dynamodb_service,
        "get",
        current_user.user_id,
        document_id,
        None,
    )
    return DocumentResponse(**item)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: UserContext = Depends(get_current_user),
    s3_service: S3Service = Depends(get_s3_service),
    dynamodb_service: DynamoDBService = Depends(get_dynamodb_service),
) -> dict:
    item = await run_in_threadpool(dynamodb_service.get_document, document_id)
    if item:
        await run_in_threadpool(s3_service.delete_object, item["s3_key"])
        await run_in_threadpool(dynamodb_service.delete_document, document_id)

    await run_in_threadpool(
        _audit,
        dynamodb_service,
        "delete",
        current_user.user_id,
        document_id,
        None,
    )
    return {"message": "Deleted"}
