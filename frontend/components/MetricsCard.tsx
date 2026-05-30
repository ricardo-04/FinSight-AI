"use client";

import type { FinancialMetrics } from "@/lib/api";

interface MetricsCardProps {
  filename: string;
  metrics: FinancialMetrics;
}

function growthTone(growth: string): { text: string; bg: string; ring: string } {
  if (growth.trim().startsWith("-")) {
    return { text: "text-rose-700", bg: "bg-rose-50", ring: "ring-rose-200" };
  }
  return { text: "text-emerald-700", bg: "bg-emerald-50", ring: "ring-emerald-200" };
}

export default function MetricsCard({ filename, metrics }: MetricsCardProps) {
  const hasRevenue = Boolean(metrics.revenue);
  const hasGrowth = Boolean(metrics.growth);
  const hasGuidance = Boolean(metrics.guidance);
  const tone = growthTone(metrics.growth);

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm ring-1 ring-slate-900/5">
      {/* Header */}
      <div className="border-b border-slate-100 bg-slate-50/60 px-5 py-3">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-900 text-[10px] font-bold uppercase text-white">
            PDF
          </span>
          <h3 className="flex-1 truncate text-sm font-semibold text-slate-800">
            {filename}
          </h3>
        </div>
        <div className="mt-1.5 flex items-center gap-2 pl-9">
          <span className="truncate text-sm font-medium text-slate-700">
            {metrics.company || "Unknown company"}
          </span>
          {metrics.quarter && (
            <span className="shrink-0 rounded-full bg-slate-200 px-2 py-0.5 text-[11px] font-medium text-slate-600">
              {metrics.quarter}
            </span>
          )}
        </div>
      </div>

      <div className="p-5">
        {/* Headline stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-slate-100 bg-slate-50 p-3">
            <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
              Revenue
            </p>
            <p
              className={`mt-1 text-lg font-bold tabular-nums ${
                hasRevenue ? "text-slate-900" : "text-slate-300"
              }`}
            >
              {hasRevenue ? metrics.revenue : "—"}
            </p>
          </div>
          <div
            className={`rounded-xl border p-3 ${
              hasGrowth
                ? `${tone.bg} border-transparent ring-1 ${tone.ring}`
                : "border-slate-100 bg-slate-50"
            }`}
          >
            <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
              YoY Growth
            </p>
            <p
              className={`mt-1 text-lg font-bold tabular-nums ${
                hasGrowth ? tone.text : "text-slate-300"
              }`}
            >
              {hasGrowth ? metrics.growth : "—"}
            </p>
          </div>
        </div>

        {/* Guidance */}
        <div className="mt-3 rounded-xl border border-slate-100 bg-slate-50 p-3">
          <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
            Guidance
          </p>
          {hasGuidance ? (
            <p className="mt-1 text-sm text-slate-700">{metrics.guidance}</p>
          ) : (
            <p className="mt-1 text-sm italic text-slate-400">
              Not disclosed in this document
            </p>
          )}
        </div>

        {/* Risks */}
        {metrics.risks.length > 0 && (
          <div className="mt-4">
            <p className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-amber-600">
              <svg
                className="h-3.5 w-3.5"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z"
                  clipRule="evenodd"
                />
              </svg>
              Key Risks
            </p>
            <ul className="space-y-1.5">
              {metrics.risks.map((risk, i) => (
                <li
                  key={i}
                  className="flex gap-2 text-xs leading-relaxed text-slate-600"
                >
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-400" />
                  <span>{risk}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
