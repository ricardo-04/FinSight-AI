"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import DocumentList from "@/components/DocumentList";
import ChatPanel from "@/components/ChatPanel";
import MetricsCard from "@/components/MetricsCard";
import CompareView from "@/components/CompareView";
import FinancialIntelligence from "@/components/FinancialIntelligence";
import type { UploadResponse, ExtractionResponse } from "@/lib/api";

type Tab = "chat" | "compare" | "financial";

interface DocumentInfo {
  document_id: string;
  filename: string;
}

export default function Home() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [extractions, setExtractions] = useState<ExtractionResponse[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>("chat");

  function handleUploaded(response: UploadResponse) {
    setDocuments((prev) => [
      ...prev,
      { document_id: response.document_id, filename: response.filename },
    ]);
  }

  function handleToggleSelect(id: string) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  function handleExtracted(response: ExtractionResponse) {
    setExtractions((prev) => {
      const existing = prev.findIndex((e) => e.document_id === response.document_id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = response;
        return updated;
      }
      return [...prev, response];
    });
  }

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-gray-900">FinSight AI</h1>
        <p className="text-sm text-gray-500">Financial intelligence powered by AI</p>
      </header>

      <div className="flex h-[calc(100vh-73px)]">
        {/* Sidebar */}
        <aside className="w-80 border-r bg-white p-4 flex flex-col gap-4 overflow-y-auto">
          <section>
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Upload
            </h2>
            <FileUpload onUploaded={handleUploaded} />
          </section>

          <section className="flex-1">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Documents
            </h2>
            <DocumentList
              documents={documents}
              selectedIds={selectedIds}
              onToggleSelect={handleToggleSelect}
              onExtracted={handleExtracted}
            />
          </section>
        </aside>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Tabs */}
          <div className="border-b bg-white px-6">
            <nav className="flex gap-4">
              <button
                onClick={() => setActiveTab("chat")}
                className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "chat"
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                Chat
              </button>
              <button
                onClick={() => setActiveTab("compare")}
                className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "compare"
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                Compare
              </button>
              <button
                onClick={() => setActiveTab("financial")}
                className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "financial"
                    ? "border-green-600 text-green-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                Financial Intelligence
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === "chat" && (
              <ChatPanel documentIds={selectedIds} />
            )}
            {activeTab === "compare" && (
              <div className="p-6 overflow-y-auto h-full">
                <CompareView documentIds={selectedIds} />
              </div>
            )}
            {activeTab === "financial" && (
              <FinancialIntelligence />
            )}
          </div>
        </div>

        {/* Metrics Panel */}
        {extractions.length > 0 && (
          <aside className="w-80 border-l bg-gray-50 p-4 overflow-y-auto">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Extracted Metrics
            </h2>
            <div className="space-y-3">
              {extractions.map((ext) => (
                <MetricsCard
                  key={ext.document_id}
                  documentId={ext.document_id}
                  filename={ext.filename}
                  metrics={ext.metrics}
                />
              ))}
            </div>
          </aside>
        )}
      </div>
    </main>
  );
}
