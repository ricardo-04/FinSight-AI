import os

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, func

from app.db.base import Base

_EMBEDDING_DIMS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "1024"))


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class DocumentChunk(Base):
    """A text chunk from a parsed document, with its pgvector embedding."""

    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(_EMBEDDING_DIMS), nullable=True)
