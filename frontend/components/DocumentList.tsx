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
}

export default function DocumentList({
  documents,
  selectedIds,
  onToggleSelect,
  onExtracted,
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

  if (documents.length === 0) {
    return (
      <p className="text-sm text-gray-400 text-center py-4">
        No documents uploaded yet.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {error && <p className="text-xs text-red-600 mb-2">{error}</p>}
      {documents.map((doc) => (
        <div
          key={doc.document_id}
          className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg"
        >
          <input
            type="checkbox"
            checked={selectedIds.includes(doc.document_id)}
            onChange={() => onToggleSelect(doc.document_id)}
            className="rounded border-gray-300"
          />
          <span className="flex-1 text-sm text-gray-700 truncate">{doc.filename}</span>
          <button
            onClick={() => handleExtract(doc.document_id)}
            disabled={extracting === doc.document_id}
            className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-md text-gray-600 disabled:opacity-50"
          >
            {extracting === doc.document_id ? "Extracting..." : "Extract"}
          </button>
        </div>
      ))}
    </div>
  );
}
