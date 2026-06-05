import time
from typing import Iterable


class TextractService:
    def __init__(self, client) -> None:
        self._client = client

    def extract_text_from_bytes(self, content: bytes) -> str:
        response = self._client.detect_document_text(Document={"Bytes": content})
        return self._collect_lines(response.get("Blocks", []))

    def extract_text_from_s3(self, bucket: str, key: str) -> str:
        response = self._client.start_document_text_detection(
            DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}}
        )
        job_id = response["JobId"]

        for _ in range(60):
            result = self._client.get_document_text_detection(JobId=job_id)
            status = result.get("JobStatus")
            if status == "SUCCEEDED":
                break
            if status in {"FAILED", "PARTIAL_SUCCESS"}:
                raise RuntimeError("Textract job failed")
            time.sleep(2)
        else:
            raise RuntimeError("Textract job timed out")

        pages: list[dict] = []
        next_token: str | None = None
        while True:
            result = self._client.get_document_text_detection(JobId=job_id, NextToken=next_token)
            pages.extend(result.get("Blocks", []))
            next_token = result.get("NextToken")
            if not next_token:
                break

        return self._collect_lines(pages)

    def _collect_lines(self, blocks: Iterable[dict]) -> str:
        lines = [block["Text"] for block in blocks if block.get("BlockType") == "LINE"]
        return "\n".join(lines)
