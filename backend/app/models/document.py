from sqlalchemy import Column, String, DateTime, func
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
