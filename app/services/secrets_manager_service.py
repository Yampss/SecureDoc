class SecretsManagerService:
    def __init__(self, client) -> None:
        self._client = client

    def get_secret_value(self, secret_id: str) -> str:
        response = self._client.get_secret_value(SecretId=secret_id)
        return response.get("SecretString", "")
