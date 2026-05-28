"use client";

import type { FinancialMetrics } from "@/lib/api";

interface MetricsCardProps {
  documentId: string;
  filename: string;
  metrics: FinancialMetrics;
}

export default function MetricsCard({ filename, metrics }: MetricsCardProps) {
  const fields: { label: string; value: string }[] = [
    { label: "Company", value: metrics.company },
    { label: "Quarter", value: metrics.quarter },
    { label: "Revenue", value: metrics.revenue },
    { label: "Growth", value: metrics.growth },
    { label: "Guidance", value: metrics.guidance },
  ];

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700 truncate">{filename}</h3>
      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2">
        {fields.map((f) => (
          <div key={f.label}>
            <dt className="text-xs text-gray-400">{f.label}</dt>
            <dd className="text-sm font-medium text-gray-900">{f.value || "—"}</dd>
          </div>
        ))}
      </dl>
      {metrics.risks.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-400 mb-1">Risks</p>
          <ul className="list-disc list-inside space-y-0.5">
            {metrics.risks.map((risk, i) => (
              <li key={i} className="text-xs text-gray-600">{risk}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
