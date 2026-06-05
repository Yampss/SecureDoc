# Secure Document Intelligence Platform

FastAPI backend for secure document ingestion, processing, and chat-based Q&A. This build targets EC2 behind API Gateway with Cognito User Pools authorizer.

## Key Features
- API Gateway + Cognito auth (no in-app JWT issuance)
- S3 storage for uploads
- DynamoDB metadata and audit logs
- Textract extraction (PDF/PNG/JPG/JPEG)
- Bedrock summarization and chat
- Structured logging and OpenAPI docs

## Architecture Notes
- Authentication is enforced by API Gateway with Cognito User Pools authorizer.
- The app trusts headers injected by API Gateway. Configure integration mapping to pass these headers:
  - `X-Cognito-Username` (from `cognito:username`)
  - `X-Cognito-Role` (from `custom:role`, optional)
- RBAC is enforced in the gateway per your decision.
- A lightweight `POST /auth/login` endpoint records login audits after the client completes Cognito sign-in.

## Required Environment Variables
- `AWS_REGION`
- `S3_BUCKET_NAME`
- `DYNAMODB_TABLE_NAME`
- `AUDIT_TABLE_NAME`
- `BEDROCK_MODEL_ID`
- `JWT_SECRET` (unused in this build; kept for compatibility)
- `JWT_EXPIRATION` (unused in this build)
- `COGNITO_USERNAME_HEADER` (default `x-cognito-username`)
- `COGNITO_ROLE_HEADER` (default `x-cognito-role`)

## Local Run
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker
```bash
docker build -t secure-docs-api .
docker run --rm -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e S3_BUCKET_NAME=your-s3-bucket \
  -e DYNAMODB_TABLE_NAME=documents-table \
  -e AUDIT_TABLE_NAME=audit-table \
  -e BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0 \
  -e JWT_SECRET=unused \
  -e JWT_EXPIRATION=3600 \
  secure-docs-api
```

## API Overview
- `POST /auth/login` - records a login audit (expects Cognito headers)
- `POST /documents/upload`
- `GET /documents`
- `GET /documents/{id}`
- `DELETE /documents/{id}`
- `POST /documents/{id}/chat`
- `GET /documents/search?q=keyword`

## Textract Notes
- PDF processing uses async Textract jobs with polling.
- Images use synchronous Textract calls.

## Bedrock Notes
- The current Bedrock payload is compatible with Anthropic Claude models. If you use a different model family, update the payload in `app/services/bedrock_service.py`.
