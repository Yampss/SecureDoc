from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.services.bedrock_service import BedrockService
from app.services.dynamodb_service import DynamoDBService
from app.services.s3_service import S3Service
from app.services.textract_service import TextractService
from app.services.secrets_manager_service import SecretsManagerService
from app.services import dependencies as aws_deps


def get_settings_dep() -> Settings:
    return get_settings()


def get_s3_service(
    settings: Settings = Depends(get_settings_dep),
) -> S3Service:
    client = aws_deps.get_s3_client(settings)
    return S3Service(client=client, bucket_name=settings.s3_bucket_name)


def get_textract_service(
    settings: Settings = Depends(get_settings_dep),
) -> TextractService:
    client = aws_deps.get_textract_client(settings)
    return TextractService(client=client)


def get_bedrock_service(
    settings: Settings = Depends(get_settings_dep),
) -> BedrockService:
    client = aws_deps.get_bedrock_client(settings)
    return BedrockService(client=client, model_id=settings.bedrock_model_id)


def get_dynamodb_service(
    settings: Settings = Depends(get_settings_dep),
) -> DynamoDBService:
    resource = aws_deps.get_dynamodb_resource(settings)
    return DynamoDBService(
        resource=resource,
        table_name=settings.dynamodb_table_name,
        audit_table_name=settings.audit_table_name,
    )


def get_secrets_manager_service(
    settings: Settings = Depends(get_settings_dep),
) -> SecretsManagerService:
    client = aws_deps.get_secrets_manager_client(settings)
    return SecretsManagerService(client=client)
