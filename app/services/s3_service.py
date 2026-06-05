from typing import BinaryIO


class S3Service:
    def __init__(self, client, bucket_name: str) -> None:
        self._client = client
        self._bucket = bucket_name

    @property
    def bucket_name(self) -> str:
        return self._bucket

    def upload_fileobj(self, fileobj: BinaryIO, key: str, content_type: str) -> None:
        self._client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=self._bucket,
            Key=key,
            ExtraArgs={"ContentType": content_type},
        )

    def get_object_bytes(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)
