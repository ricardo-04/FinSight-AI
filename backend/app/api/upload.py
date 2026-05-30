import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services.document_service import save_document

logger = logging.getLogger(__name__)

router = APIRouter()

_MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
_ALLOWED_CONTENT_TYPES: set[str] = {"application/pdf"}
# Every valid PDF begins with the "%PDF-" magic signature. Validating the bytes
# (not just the client-supplied Content-Type) prevents a mislabeled or malicious
# non-PDF payload from reaching the parser.
_PDF_MAGIC: bytes = b"%PDF-"


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str


@router.post("/", response_model=UploadResponse, status_code=201)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a PDF document, parse it, and ingest it into the vector store.

    Validates MIME type, byte signature and file size before processing. Returns
    the assigned document ID which can be used in subsequent requests.
    """
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Only PDF files are accepted.",
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {_MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    # Defense in depth: trust the bytes, not the declared Content-Type.
    if not content[:1024].lstrip().startswith(_PDF_MAGIC):
        raise HTTPException(
            status_code=400,
            detail="File content is not a valid PDF (missing %PDF- signature).",
        )

    logger.info(
        "Upload received: filename=%s size_bytes=%d", file.filename, len(content)
    )

    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                document_id = await save_document(
                    filename=file.filename or "document.pdf",
                    content=content,
                    session=session,
                )
            except ValueError as exc:
                logger.warning(
                    "Upload failed validation: filename=%s error=%s",
                    file.filename,
                    str(exc),
                )
                raise HTTPException(status_code=422, detail=str(exc)) from exc

    return UploadResponse(
        document_id=document_id,
        filename=file.filename or "document.pdf",
        status="ingested",
    )
