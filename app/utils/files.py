from fastapi import HTTPException, UploadFile, status


ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/octet-stream",
}


def validate_upload_file(upload: UploadFile) -> None:
    filename = upload.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    content_type = upload.content_type or ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file extension. Allowed: PDF, PNG, JPG, JPEG.",
        )

    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported content type. Allowed: application/pdf, image/png, image/jpeg, "
                "application/octet-stream."
            ),
        )
