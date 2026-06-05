from pydantic import BaseModel


class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    uploaded_by: str
    upload_timestamp: str
    s3_key: str
    status: str
    summary: str = ""
    extracted_text: str = ""
    content_type: str | None = None
