import json

from app.utils.prompts import build_chat_prompt, build_summary_prompt


class BedrockService:
    def __init__(self, client, model_id: str) -> None:
        self._client = client
        self._model_id = model_id

    def generate_summary(self, document_text: str) -> str:
        prompt = build_summary_prompt(document_text)
        return self._invoke_model(prompt, max_tokens=400)

    def answer_question(self, document_text: str, question: str) -> str:
        prompt = build_chat_prompt(document_text, question)
        return self._invoke_model(prompt, max_tokens=300)

    def _invoke_model(self, prompt: str, max_tokens: int) -> str:
        if self._model_id.startswith("amazon.nova"):
            body = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": 0,
                },
            }
        else:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": 0,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ],
            }

        response = self._client.invoke_model(
            modelId=self._model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        payload = json.loads(response["body"].read().decode("utf-8"))

        if "output" in payload:
            content = payload.get("output", {}).get("message", {}).get("content", [])
            if content and isinstance(content, list):
                return content[0].get("text", "")

        content = payload.get("content", [])
        if content and isinstance(content, list):
            return content[0].get("text", "")
        return payload.get("completion", "")
