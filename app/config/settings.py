from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, case_sensitive=True)

    app_name: str = "Secure Document Intelligence Platform"
    app_version: str = "1.0.0"
    app_description: str = "Secure document processing and intelligence APIs."

    aws_region: str
    s3_bucket_name: str
    dynamodb_table_name: str
    audit_table_name: str
    bedrock_model_id: str

    jwt_secret: str
    jwt_expiration: int

    log_level: str = "INFO"

    cognito_username_header: str = "x-cognito-username"
    cognito_role_header: str = "x-cognito-role"


@lru_cache
def get_settings() -> Settings:
    return Settings()
