from sqlalchemy import Column, String, ForeignKey
from app.db.base import Base

class FinancialMetric(Base):
    __tablename__ = "financial_metrics"
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"))
    company = Column(String)
    quarter = Column(String)
    revenue = Column(String)
    growth = Column(String)
    guidance = Column(String)
