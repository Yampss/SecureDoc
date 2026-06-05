from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    uploaded_by: str
    upload_timestamp: str
    s3_key: str
    status: str
    summary: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
