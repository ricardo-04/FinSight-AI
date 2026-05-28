"use client";

import { useState } from "react";
import {
  analyzeCompany,
  type FinancialAnalysisResponse,
} from "@/lib/api";
import {
  Search,
  TrendingUp,
  Building2,
  DollarSign,
  BarChart3,
  AlertTriangle,
  Loader2,
  History,
} from "lucide-react";

interface AnalysisHistoryItem {
  query: string;
  symbol: string;
  timestamp: Date;
  result: FinancialAnalysisResponse;
}

export default function FinancialIntelligence() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FinancialAnalysisResponse | null>(null);
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  async function handleAnalyze(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeCompany(query.trim());
      setResult(data);
      setHistory((prev) => [
        {
          query: query.trim(),
          symbol: data.overview.symbol,
          timestamp: new Date(),
          result: data,
        },
        ...prev.slice(0, 9), // Keep last 10
      ]);
    } catch (err: any) {
      setError(err.message || "Failed to analyze company.");
    } finally {
      setLoading(false);
    }
  }

  function loadFromHistory(item: AnalysisHistoryItem) {
    setResult(item.result);
    setQuery(item.query);
    setShowHistory(false);
    setError(null);
  }

  return (
    <div className="h-full flex flex-col bg-gray-950 text-gray-100">
      {/* Terminal-style header */}
      <div className="border-b border-gray-800 bg-gray-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-red-500" />
            </div>
            <h2 className="text-sm font-mono font-bold text-green-400 tracking-wide uppercase">
              Financial Intelligence Terminal
            </h2>
          </div>
          {history.length > 0 && (
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-200 transition-colors"
            >
              <History className="w-3.5 h-3.5" />
              History ({history.length})
            </button>
          )}
        </div>

        {/* Search bar */}
        <form onSubmit={handleAnalyze} className="mt-4 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter ticker or company name (e.g., AAPL, Microsoft)..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500 font-mono"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-5 py-2.5 bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm font-semibold rounded-lg transition-colors flex items-center gap-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <BarChart3 className="w-4 h-4" />
            )}
            Analyze
          </button>
        </form>
      </div>

      {/* History dropdown */}
      {showHistory && history.length > 0 && (
        <div className="border-b border-gray-800 bg-gray-900/80 px-6 py-3">
          <div className="space-y-1">
            {history.map((item, i) => (
              <button
                key={i}
                onClick={() => loadFromHistory(item)}
                className="w-full text-left px-3 py-2 rounded text-xs font-mono hover:bg-gray-800 transition-colors flex items-center justify-between"
              >
                <span className="text-green-400">{item.symbol}</span>
                <span className="text-gray-500">
                  {item.timestamp.toLocaleTimeString()}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Content area */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="w-8 h-8 text-green-400 animate-spin" />
            <div className="text-center">
              <p className="text-sm text-gray-300 font-mono">
                Analyzing {query.toUpperCase()}...
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Fetching financial data and generating report
              </p>
            </div>
          </div>
        )}

        {/* Error state */}
        {error && !loading && (
          <div className="flex items-center gap-3 p-4 bg-red-950/50 border border-red-800 rounded-lg">
            <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && !result && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <TrendingUp className="w-12 h-12 text-gray-700 mb-4" />
            <h3 className="text-lg font-semibold text-gray-400">
              Financial Intelligence
            </h3>
            <p className="text-sm text-gray-600 mt-2 max-w-md">
              Search for any public company by name or ticker to get a comprehensive
              AI-powered financial analysis with real-time data.
            </p>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-6 max-w-5xl mx-auto">
            {/* Company Overview Card */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-500/10 border border-green-500/30 rounded-lg flex items-center justify-center">
                    <Building2 className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">
                      {result.overview.name}
                    </h3>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs font-mono bg-green-500/20 text-green-400 px-2 py-0.5 rounded">
                        {result.overview.symbol}
                      </span>
                      {result.overview.sector && (
                        <span className="text-xs text-gray-400">
                          {result.overview.sector}
                        </span>
                      )}
                      {result.overview.industry && (
                        <span className="text-xs text-gray-500">
                          • {result.overview.industry}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                {result.overview.market_cap && (
                  <div className="text-right">
                    <p className="text-xs text-gray-500 uppercase">Market Cap</p>
                    <p className="text-sm font-mono font-bold text-white">
                      {result.overview.market_cap}
                    </p>
                  </div>
                )}
              </div>
              {result.overview.description && (
                <p className="mt-3 text-xs text-gray-400 leading-relaxed">
                  {result.overview.description}
                </p>
              )}
            </div>

            {/* Financial Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <MetricTile
                label="Revenue"
                value={result.highlights.revenue_latest}
                icon={<DollarSign className="w-4 h-4" />}
              />
              <MetricTile
                label="Net Income"
                value={result.highlights.net_income_latest}
                icon={<TrendingUp className="w-4 h-4" />}
              />
              <MetricTile
                label="Revenue Growth"
                value={result.highlights.revenue_growth}
                icon={<BarChart3 className="w-4 h-4" />}
              />
              <MetricTile
                label="Profit Margin"
                value={result.highlights.profit_margin}
                icon={<TrendingUp className="w-4 h-4" />}
              />
              <MetricTile
                label="Debt/Equity"
                value={result.highlights.debt_to_equity}
                icon={<AlertTriangle className="w-4 h-4" />}
              />
              <MetricTile
                label="Current Ratio"
                value={result.highlights.current_ratio}
                icon={<BarChart3 className="w-4 h-4" />}
              />
              <MetricTile
                label="ROE"
                value={result.highlights.roe}
                icon={<TrendingUp className="w-4 h-4" />}
              />
              <MetricTile
                label="Free Cash Flow"
                value={result.highlights.free_cash_flow}
                icon={<DollarSign className="w-4 h-4" />}
              />
            </div>

            {/* AI Report */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <h4 className="text-sm font-mono font-bold text-green-400 uppercase">
                  AI Analysis Report
                </h4>
              </div>
              <div className="prose prose-invert prose-sm max-w-none text-gray-300 leading-relaxed">
                <MarkdownReport content={result.report} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricTile({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  const hasValue = value && value !== "N/A" && value !== "";
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-3">
      <div className="flex items-center gap-2 text-gray-500 mb-1">
        {icon}
        <span className="text-xs uppercase tracking-wide">{label}</span>
      </div>
      <p
        className={`text-sm font-mono font-bold ${
          hasValue ? "text-white" : "text-gray-600"
        }`}
      >
        {hasValue ? value : "—"}
      </p>
    </div>
  );
}

function MarkdownReport({ content }: { content: string }) {
  // Simple markdown rendering for the report
  const lines = content.split("\n");
  return (
    <div className="space-y-2">
      {lines.map((line, i) => {
        if (line.startsWith("### ")) {
          return (
            <h4 key={i} className="text-green-400 font-bold mt-4 mb-1 text-sm">
              {line.replace("### ", "")}
            </h4>
          );
        }
        if (line.startsWith("## ")) {
          return (
            <h3 key={i} className="text-green-300 font-bold mt-5 mb-2 text-base">
              {line.replace("## ", "")}
            </h3>
          );
        }
        if (line.startsWith("# ")) {
          return (
            <h2 key={i} className="text-green-200 font-bold mt-6 mb-2 text-lg">
              {line.replace("# ", "")}
            </h2>
          );
        }
        if (line.startsWith("- ") || line.startsWith("* ")) {
          return (
            <li key={i} className="text-gray-300 text-sm ml-4 list-disc">
              {formatInline(line.slice(2))}
            </li>
          );
        }
        if (line.trim() === "") {
          return <div key={i} className="h-2" />;
        }
        return (
          <p key={i} className="text-gray-300 text-sm">
            {formatInline(line)}
          </p>
        );
      })}
    </div>
  );
}

function formatInline(text: string) {
  // Handle bold **text**
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="text-white font-semibold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}
