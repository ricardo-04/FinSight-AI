import logging

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.document import Document

logger = logging.getLogger(__name__)

router = APIRouter()


class DocumentInfo(BaseModel):
    document_id: str
    filename: str


@router.get("/", response_model=list[DocumentInfo])
async def list_documents() -> list[DocumentInfo]:
    """Return all ingested documents, newest first.

    Lets the frontend restore its document list after a page reload instead
    of losing all uploaded files on refresh.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        documents = result.scalars().all()

    return [
        DocumentInfo(document_id=doc.id, filename=doc.filename)
        for doc in documents
    ]
