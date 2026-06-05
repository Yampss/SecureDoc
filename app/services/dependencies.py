from functools import lru_cache
import boto3
from botocore.config import Config

from app.config.settings import Settings


def _client_config(settings: Settings) -> Config:
    return Config(region_name=settings.aws_region)


@lru_cache
def get_boto3_session() -> boto3.session.Session:
    return boto3.session.Session()


def get_s3_client(settings: Settings):
    session = get_boto3_session()
    return session.client("s3", config=_client_config(settings))


def get_textract_client(settings: Settings):
    session = get_boto3_session()
    return session.client("textract", config=_client_config(settings))


def get_bedrock_client(settings: Settings):
    session = get_boto3_session()
    return session.client("bedrock-runtime", config=_client_config(settings))


def get_dynamodb_resource(settings: Settings):
    session = get_boto3_session()
    return session.resource("dynamodb", config=_client_config(settings))


def get_secrets_manager_client(settings: Settings):
    session = get_boto3_session()
    return session.client("secretsmanager", config=_client_config(settings))
