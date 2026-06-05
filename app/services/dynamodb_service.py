from typing import Any
from boto3.dynamodb.conditions import Attr

from app.models.document import DocumentRecord
from app.models.audit import AuditRecord


class DynamoDBService:
    def __init__(self, resource, table_name: str, audit_table_name: str) -> None:
        self._table = resource.Table(table_name)
        self._audit_table = resource.Table(audit_table_name)

    def put_document(self, record: DocumentRecord) -> None:
        self._table.put_item(Item=record.model_dump())

    def get_document(self, document_id: str) -> dict | None:
        response = self._table.get_item(Key={"document_id": document_id})
        return response.get("Item")

    def list_documents(self, limit: int = 100) -> list[dict]:
        response = self._table.scan(Limit=limit)
        return response.get("Items", [])

    def delete_document(self, document_id: str) -> None:
        self._table.delete_item(Key={"document_id": document_id})

    def update_document_fields(self, document_id: str, fields: dict[str, Any]) -> None:
        if not fields:
            return
        update_parts = []
        values: dict[str, Any] = {}
        names: dict[str, str] = {}
        for idx, (key, value) in enumerate(fields.items()):
            name_key = f"#field{idx}"
            value_key = f":value{idx}"
            update_parts.append(f"{name_key} = {value_key}")
            names[name_key] = key
            values[value_key] = value
        update_expression = "SET " + ", ".join(update_parts)
        self._table.update_item(
            Key={"document_id": document_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
        )

    def search_documents(self, keyword: str, limit: int = 100) -> list[dict]:
        filter_expression = (
            Attr("filename").contains(keyword)
            | Attr("extracted_text").contains(keyword)
            | Attr("summary").contains(keyword)
        )
        response = self._table.scan(FilterExpression=filter_expression, Limit=limit)
        return response.get("Items", [])

    def put_audit_log(self, record: AuditRecord) -> None:
        self._audit_table.put_item(Item=record.model_dump())
