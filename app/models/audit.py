from pydantic import BaseModel


class AuditRecord(BaseModel):
    audit_id: str
    event_type: str
    timestamp: str
    user_id: str
    document_id: str | None = None
    metadata: dict | None = None
