"use client";

import { useState } from "react";
import { extractMetrics, type ExtractionResponse } from "@/lib/api";

interface DocumentInfo {
  document_id: string;
  filename: string;
}

interface DocumentListProps {
  documents: DocumentInfo[];
  selectedIds: string[];
  onToggleSelect: (id: string) => void;
  onExtracted: (response: ExtractionResponse) => void;
  loading?: boolean;
}

export default function DocumentList({
  documents,
  selectedIds,
  onToggleSelect,
  onExtracted,
  loading = false,
}: DocumentListProps) {
  const [extracting, setExtracting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleExtract(docId: string) {
    setExtracting(docId);
    setError(null);
    try {
      const result = await extractMetrics(docId);
      onExtracted(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Extraction failed.");
    } finally {
      setExtracting(null);
    }
  }

  if (loading) {
    return (
      <div className="space-y-2" aria-busy="true" aria-label="Loading documents">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 bg-white"
          >
            <div className="h-4 w-4 rounded bg-slate-200 animate-pulse" />
            <div className="h-3 flex-1 rounded bg-slate-200 animate-pulse" />
            <div className="h-6 w-16 rounded-md bg-slate-200 animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <p className="text-sm text-slate-400 text-center py-4">
        No documents uploaded yet.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {error && <p className="text-xs text-red-600 mb-2" role="alert">{error}</p>}
      {documents.map((doc) => {
        const isSelected = selectedIds.includes(doc.document_id);
        return (
          <div
            key={doc.document_id}
            className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
              isSelected
                ? "border-indigo-300 bg-indigo-50/60 ring-1 ring-indigo-200"
                : "border-slate-200 bg-white hover:border-slate-300"
            }`}
          >
            <label className="flex items-center gap-3 flex-1 min-w-0 cursor-pointer">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onToggleSelect(doc.document_id)}
                className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                aria-label={`Select ${doc.filename}`}
              />
              <span className="flex-1 text-sm font-medium text-slate-700 truncate">{doc.filename}</span>
            </label>
            <button
              onClick={() => handleExtract(doc.document_id)}
              disabled={extracting === doc.document_id}
              className="text-xs px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 rounded-md font-medium text-white shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {extracting === doc.document_id ? "Extracting..." : "Extract"}
            </button>
          </div>
        );
      })}
    </div>
  );
}
