const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface UploadResponse {
  document_id: string;
  filename: string;
  status: string;
}

export interface FinancialMetrics {
  company: string;
  quarter: string;
  revenue: string;
  growth: string;
  guidance: string;
  risks: string[];
}

export interface ExtractionResponse {
  document_id: string;
  filename: string;
  metrics: FinancialMetrics;
}

export interface Citation {
  document_id: string;
  chunk_index: number;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
}

export interface DocumentMetrics {
  document_id: string;
  filename: string;
  metrics: FinancialMetrics;
}

export interface CompareResponse {
  documents: DocumentMetrics[];
  analysis: string;
}

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(body.detail || res.statusText, res.status);
  }
  return res.json();
}

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload/`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<UploadResponse>(res);
}

export async function extractMetrics(documentId: string): Promise<ExtractionResponse> {
  const res = await fetch(`${API_BASE}/api/extract/${documentId}`, {
    method: "POST",
  });
  return handleResponse<ExtractionResponse>(res);
}

export async function chat(
  question: string,
  documentIds: string[] = []
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, document_ids: documentIds }),
  });
  return handleResponse<ChatResponse>(res);
}

export async function compareDocuments(documentIds: string[]): Promise<CompareResponse> {
  const res = await fetch(`${API_BASE}/api/compare/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_ids: documentIds }),
  });
  return handleResponse<CompareResponse>(res);
}

export async function healthCheck(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE}/health/`);
  return handleResponse(res);
}

// --- Financial Intelligence ---

export interface CompanyOverview {
  name: string;
  symbol: string;
  sector: string;
  industry: string;
  market_cap: string;
  description: string;
}

export interface FinancialHighlights {
  revenue_latest: string;
  net_income_latest: string;
  revenue_growth: string;
  profit_margin: string;
  debt_to_equity: string;
  current_ratio: string;
  roe: string;
  free_cash_flow: string;
}

export interface FinancialAnalysisResponse {
  overview: CompanyOverview;
  highlights: FinancialHighlights;
  report: string;
}

export async function analyzeCompany(query: string): Promise<FinancialAnalysisResponse> {
  const res = await fetch(`${API_BASE}/api/financial/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  return handleResponse<FinancialAnalysisResponse>(res);
}
