"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import DocumentList from "@/components/DocumentList";
import ChatPanel from "@/components/ChatPanel";
import MetricsCard from "@/components/MetricsCard";
import CompareView from "@/components/CompareView";
import FinancialIntelligence from "@/components/FinancialIntelligence";
import ErrorBoundary from "@/components/ErrorBoundary";
import { WorkspaceProvider, useWorkspace } from "@/context/WorkspaceContext";

type Tab = "chat" | "compare" | "financial";

const TABS: { id: Tab; label: string; activeClass: string }[] = [
  { id: "chat", label: "Chat", activeClass: "border-indigo-500 text-indigo-600" },
  { id: "compare", label: "Compare", activeClass: "border-indigo-500 text-indigo-600" },
  {
    id: "financial",
    label: "Financial Intelligence",
    activeClass: "border-emerald-500 text-emerald-600",
  },
];

export default function Home() {
  return (
    <WorkspaceProvider>
      <Workspace />
    </WorkspaceProvider>
  );
}

function Workspace() {
  const {
    documents,
    selectedIds,
    extractions,
    loadingDocs,
    addDocument,
    toggleSelect,
    addExtraction,
  } = useWorkspace();
  const [activeTab, setActiveTab] = useState<Tab>("chat");

  return (
    <main className="flex flex-col h-screen">
      {/* Header */}
      <header className="flex items-center gap-3 border-b border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800 px-6 py-3.5 shadow-sm">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-900/40">
          <svg className="h-5 w-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M3 3v18h18" />
            <path d="M7 14l3-4 3 3 4-6" />
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white">
            FinSight <span className="text-indigo-400">AI</span>
          </h1>
          <p className="text-xs text-slate-400">Financial intelligence powered by AI</p>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-80 border-r border-slate-200 bg-white p-4 flex flex-col gap-5 overflow-y-auto scrollbar-slim">
          <section>
            <h2 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Upload
            </h2>
            <FileUpload onUploaded={addDocument} />
          </section>

          <section className="flex-1">
            <h2 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Documents
            </h2>
            <DocumentList
              documents={documents}
              selectedIds={selectedIds}
              onToggleSelect={toggleSelect}
              onExtracted={addExtraction}
              loading={loadingDocs}
            />
          </section>
        </aside>

        {/* Main Content */}
        <div className="flex-1 min-w-0 flex flex-col bg-slate-100">
          {/* Tabs */}
          <div className="border-b border-slate-200 bg-white px-6">
            <nav className="flex gap-6" role="tablist" aria-label="Workspace views">
              {TABS.map((tab) => {
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    role="tab"
                    id={`tab-${tab.id}`}
                    aria-selected={isActive}
                    aria-controls={`panel-${tab.id}`}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-3.5 text-sm font-medium border-b-2 transition-colors ${
                      isActive
                        ? tab.activeClass
                        : "border-transparent text-slate-500 hover:text-slate-800"
                    }`}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div
            className="flex-1 overflow-hidden"
            role="tabpanel"
            id={`panel-${activeTab}`}
            aria-labelledby={`tab-${activeTab}`}
          >
            {activeTab === "chat" && (
              <ErrorBoundary label="Chat">
                <ChatPanel documentIds={selectedIds} />
              </ErrorBoundary>
            )}
            {activeTab === "compare" && (
              <ErrorBoundary label="Compare">
                <div className="p-6 overflow-y-auto h-full">
                  <CompareView documentIds={selectedIds} />
                </div>
              </ErrorBoundary>
            )}
            {activeTab === "financial" && (
              <ErrorBoundary label="Financial Intelligence">
                <FinancialIntelligence />
              </ErrorBoundary>
            )}
          </div>
        </div>

        {/* Metrics Panel */}
        {extractions.length > 0 && (
          <aside className="w-80 border-l border-slate-200 bg-white p-4 overflow-y-auto scrollbar-slim">
            <h2 className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Extracted Metrics
            </h2>
            <div className="space-y-3">
              {extractions.map((ext) => (
                <MetricsCard
                  key={ext.document_id}
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
