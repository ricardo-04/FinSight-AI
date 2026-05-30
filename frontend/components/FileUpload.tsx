"use client";

import { useState, useRef } from "react";
import { uploadPdf, type UploadResponse } from "@/lib/api";

interface FileUploadProps {
  onUploaded: (response: UploadResponse) => void;
}

const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024; // 50 MB

export default function FileUpload({ onUploaded }: FileUploadProps) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    if (file.type !== "application/pdf") {
      setError("Only PDF files are accepted.");
      return;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      setError("File exceeds the maximum size of 50 MB.");
      return;
    }
    setError(null);
    setUploading(true);
    try {
      const response = await uploadPdf(file);
      onUploaded(response);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Upload a PDF. Drop a file here or press Enter to browse."
      aria-busy={uploading}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          inputRef.current?.click();
        }
      }}
      className={`
        border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer
        focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
        ${dragging ? "border-indigo-500 bg-indigo-50" : "border-slate-300 bg-slate-50 hover:border-indigo-400 hover:bg-indigo-50/40"}
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={onFileChange}
      />
      {uploading ? (
        <p className="text-slate-500 animate-pulse">Uploading & processing...</p>
      ) : (
        <>
          <svg className="mx-auto h-11 w-11 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 16v-8m0 0l-3 3m3-3l3 3M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" />
          </svg>
          <p className="mt-2 text-sm text-slate-600">
            Drop a PDF here or <span className="text-indigo-600 font-medium">browse</span>
          </p>
          <p className="mt-1 text-xs text-slate-400">Max 50 MB</p>
        </>
      )}
      {error && <p className="mt-2 text-sm text-red-600" role="alert">{error}</p>}
    </div>
  );
}
