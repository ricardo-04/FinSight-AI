"""
Extraction Agent — pulls structured financial metrics from markdown chunks using an LLM.
"""
from pydantic import BaseModel

class FinancialMetrics(BaseModel):
    company: str
    quarter: str
    revenue: str
    growth: str
    guidance: str
    risks: list[str]

async def run_extraction(text: str) -> FinancialMetrics:
    # TODO: call LLM with extraction prompt, validate response with FinancialMetrics
    raise NotImplementedError
