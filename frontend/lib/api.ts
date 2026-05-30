const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

/** Merge the API-key header (when configured) into request headers. */
function withAuth(headers: Record<string, string> = {}): Record<string, string> {
  return API_KEY ? { ...headers, "X-API-Key": API_KEY } : headers;
}

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

export class ApiError extends Error {
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
    headers: withAuth(),
    body: formData,
  });
  return handleResponse<UploadResponse>(res);
}

export interface DocumentInfo {
  document_id: string;
  filename: string;
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${API_BASE}/api/documents/`, { headers: withAuth() });
  return handleResponse<DocumentInfo[]>(res);
}

export async function extractMetrics(documentId: string): Promise<ExtractionResponse> {
  const res = await fetch(`${API_BASE}/api/extract/${documentId}`, {
    method: "POST",
    headers: withAuth(),
  });
  return handleResponse<ExtractionResponse>(res);
}

export async function chat(
  question: string,
  documentIds: string[] = []
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat/`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ question, document_ids: documentIds }),
  });
  return handleResponse<ChatResponse>(res);
}

export interface AnalystResponse {
  answer: string;
  tools_used: string[];
  conversation_id: string;
}

export async function runAnalyst(
  question: string,
  documentIds: string[] = [],
  conversationId?: string
): Promise<AnalystResponse> {
  const res = await fetch(`${API_BASE}/api/analyst/`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      question,
      document_ids: documentIds,
      conversation_id: conversationId ?? null,
    }),
  });
  return handleResponse<AnalystResponse>(res);
}

export interface AnalystStreamHandlers {
  onDelta: (text: string) => void;
  onDone: (info: { tools_used: string[]; conversation_id: string }) => void;
  onError?: (message: string) => void;
}

/**
 * Stream the analyst agent's answer via Server-Sent Events. Calls `onDelta`
 * for each incremental chunk of text, then `onDone` with the tools used and the
 * conversation id to reuse on the next turn.
 */
export async function streamAnalyst(
  question: string,
  documentIds: string[] = [],
  conversationId: string | undefined,
  handlers: AnalystStreamHandlers
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/analyst/stream`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      question,
      document_ids: documentIds,
      conversation_id: conversationId ?? null,
    }),
  });

  if (!res.ok || !res.body) {
    const message = `Request failed with status ${res.status}`;
    handlers.onError?.(message);
    throw new ApiError(res.status, message);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  // Parse the SSE stream frame by frame (frames separated by a blank line).
  // Each frame has an `event:` line and a `data:` line with a JSON payload.
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);

      let event = "message";
      let data = "";
      for (const line of frame.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;

      try {
        const parsed = JSON.parse(data);
        if (event === "delta") handlers.onDelta(parsed.text ?? "");
        else if (event === "done") handlers.onDone(parsed);
        else if (event === "error") handlers.onError?.(parsed.message ?? "Stream failed.");
      } catch {
        // Ignore malformed frames.
      }
    }
  }
}

export async function compareDocuments(documentIds: string[]): Promise<CompareResponse> {
  const res = await fetch(`${API_BASE}/api/compare/`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
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
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify({ query }),
  });
  return handleResponse<FinancialAnalysisResponse>(res);
}
