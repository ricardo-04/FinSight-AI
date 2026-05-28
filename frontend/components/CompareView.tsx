"use client";

import { useState } from "react";
import { compareDocuments, type CompareResponse } from "@/lib/api";
import MetricsCard from "./MetricsCard";

interface CompareViewProps {
  documentIds: string[];
}

export default function CompareView({ documentIds }: CompareViewProps) {
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCompare() {
    if (documentIds.length < 2) {
      setError("Select at least 2 documents to compare.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await compareDocuments(documentIds);
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Comparison failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button
        onClick={handleCompare}
        disabled={loading || documentIds.length < 2}
        className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? "Comparing..." : `Compare ${documentIds.length} Documents`}
      </button>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      {result && (
        <div className="mt-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.documents.map((doc) => (
              <MetricsCard
                key={doc.document_id}
                documentId={doc.document_id}
                filename={doc.filename || doc.document_id}
                metrics={doc.metrics}
              />
            ))}
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-xl p-5">
            <h4 className="text-sm font-semibold text-purple-800 mb-2">Analysis</h4>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{result.analysis}</p>
          </div>
        </div>
      )}
    </div>
  );
}
