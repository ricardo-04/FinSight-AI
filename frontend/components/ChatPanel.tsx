"use client";

import { useEffect, useRef, useState } from "react";
import { chat, streamAnalyst, type ChatResponse, type Citation } from "@/lib/api";

interface ChatPanelProps {
  documentIds: string[];
}

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  toolsUsed?: string[];
}

export default function ChatPanel({ documentIds }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [agentMode, setAgentMode] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const conversationIdRef = useRef<string | undefined>(undefined);
  const endRef = useRef<HTMLDivElement>(null);

  // Reset agent conversation memory when toggling modes so context doesn't leak.
  useEffect(() => {
    conversationIdRef.current = undefined;
  }, [agentMode]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      if (agentMode) {
        // Insert an empty assistant message and stream tokens into the last one.
        setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

        const updateLast = (patch: (m: Message) => Message) => {
          setMessages((prev) => {
            if (prev.length === 0) return prev;
            const next = [...prev];
            next[next.length - 1] = patch(next[next.length - 1]);
            return next;
          });
        };

        await streamAnalyst(question, documentIds, conversationIdRef.current, {
          onDelta: (text) => {
            updateLast((m) => ({ ...m, content: m.content + text }));
          },
          onDone: ({ tools_used, conversation_id }) => {
            conversationIdRef.current = conversation_id;
            updateLast((m) => ({ ...m, toolsUsed: tools_used }));
          },
          onError: (message) => {
            updateLast((m) => ({ ...m, content: `Error: ${message}` }));
          },
        });
      } else {
        const response: ChatResponse = await chat(question, documentIds);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: response.answer, citations: response.citations },
        ]);
      }
    } catch (err: unknown) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err instanceof Error ? err.message : "Request failed."}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div
        className="flex-1 overflow-y-auto overflow-x-hidden space-y-4 p-4"
        role="log"
        aria-live="polite"
        aria-label="Chat messages"
      >
        {messages.length === 0 && (
          <div className="mx-auto mt-6 max-w-md text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-100">
              <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h8M8 14h5m-5 6l-3 1V6a2 2 0 012-2h12a2 2 0 012 2v8a2 2 0 01-2 2H9l-1 1z" />
              </svg>
            </div>
            <h3 className="mt-3 text-base font-semibold text-slate-800">
              Chat with your documents
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              {documentIds.length === 0
                ? "Answers will search across all uploaded documents."
                : `Scoped to ${documentIds.length} selected document${
                    documentIds.length === 1 ? "" : "s"
                  }.`}
            </p>
            <ol className="mx-auto mt-5 space-y-2 text-left">
              {[
                "Upload a PDF in the left sidebar",
                "Click Extract to pull key metrics",
                "Ask questions about revenue, risks or guidance",
              ].map((step, i) => (
                <li key={i} className="flex items-center gap-3 text-sm text-slate-600">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-200 text-xs font-semibold text-slate-600">
                    {i + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-[80%] min-w-0 p-3 rounded-2xl text-sm shadow-sm ${
              msg.role === "user"
                ? "ml-auto bg-indigo-600 text-white rounded-br-md"
                : "mr-auto bg-white border border-slate-200 text-slate-700 rounded-bl-md"
            }`}
          >
            <p className="whitespace-pre-wrap break-words">
              {msg.content}
              {loading &&
                msg.role === "assistant" &&
                i === messages.length - 1 &&
                agentMode && (
                  <span className="ml-0.5 inline-block h-3.5 w-1.5 animate-pulse bg-indigo-400 align-middle" />
                )}
            </p>
            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-2 pt-2 border-t border-slate-100">
                <p className="text-xs text-slate-400 font-medium">Sources:</p>
                {msg.citations.map((c, j) => (
                  <p key={j} className="text-xs text-slate-400 line-clamp-2 break-words">
                    [{j + 1}] {c.snippet}
                  </p>
                ))}
              </div>
            )}
            {msg.toolsUsed && msg.toolsUsed.length > 0 && (
              <div className="mt-2 flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100">
                <span className="text-xs font-medium text-slate-400">Tools:</span>
                {msg.toolsUsed.map((t, j) => (
                  <span
                    key={j}
                    className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-600"
                  >
                    {t}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && !agentMode && (
          <div className="mr-auto bg-white border border-slate-200 p-3 rounded-2xl rounded-bl-md">
            <p className="text-sm text-slate-400 animate-pulse">Thinking...</p>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-slate-200 bg-white p-4">
        <label className="mb-2 flex items-center gap-2 text-xs font-medium text-slate-500">
          <button
            type="button"
            role="switch"
            aria-checked={agentMode}
            onClick={() => setAgentMode((v) => !v)}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
              agentMode ? "bg-indigo-600" : "bg-slate-300"
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                agentMode ? "translate-x-4" : "translate-x-0.5"
              }`}
            />
          </button>
          Agent mode
          <span className="text-slate-400">
            {agentMode ? "autonomous tool-calling (docs + live financials)" : "standard RAG"}
          </span>

          {/* Info icon + popover */}
          <span
            className="relative ml-auto"
            onMouseEnter={() => setShowHelp(true)}
            onMouseLeave={() => setShowHelp(false)}
          >
            <svg
              className="h-3.5 w-3.5 cursor-help text-slate-400 hover:text-slate-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
              aria-label="Agent mode help"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20A10 10 0 0012 2z" />
            </svg>
            {showHelp && (
              <div
                role="tooltip"
                className="absolute bottom-6 right-0 z-10 w-72 rounded-xl border border-slate-200 bg-white p-3.5 shadow-lg text-left"
              >
                <p className="mb-2 text-xs font-semibold text-slate-700">Standard RAG</p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Hybrid search (vector + keyword) over your uploaded documents. Fast and focused on the content of your PDFs.
                </p>
                <hr className="my-2.5 border-slate-100" />
                <p className="mb-2 text-xs font-semibold text-indigo-600">Agent mode</p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  An autonomous agent that decides which tools to call:
                </p>
                <ul className="mt-1.5 space-y-1 text-xs text-slate-500">
                  <li className="flex items-start gap-1.5">
                    <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-[9px] font-bold text-indigo-600">1</span>
                    <span><strong className="text-slate-600">search_documents</strong> — searches your uploaded PDFs</span>
                  </li>
                  <li className="flex items-start gap-1.5">
                    <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-[9px] font-bold text-indigo-600">2</span>
                    <span><strong className="text-slate-600">get_company_financials</strong> — live data (profile, income statement, key ratios)</span>
                  </li>
                </ul>
                <p className="mt-2 text-xs text-slate-400">
                  Best for cross-referencing document data with live market metrics.
                </p>
              </div>
            )}
          </span>
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about revenue, risks, guidance..."
            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
