from pydantic import BaseModel

from app.schemas.document import DocumentResponse


class SearchResponse(BaseModel):
    query: str
    results: list[DocumentResponse]
