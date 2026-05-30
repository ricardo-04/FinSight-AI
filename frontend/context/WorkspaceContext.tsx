"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  listDocuments,
  type ExtractionResponse,
  type UploadResponse,
} from "@/lib/api";

export interface DocumentInfo {
  document_id: string;
  filename: string;
}

interface WorkspaceContextValue {
  documents: DocumentInfo[];
  selectedIds: string[];
  extractions: ExtractionResponse[];
  loadingDocs: boolean;
  addDocument: (response: UploadResponse) => void;
  toggleSelect: (id: string) => void;
  addExtraction: (response: ExtractionResponse) => void;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

/**
 * Owns all workspace state (documents, selection, extractions) so the tree
 * does not prop-drill and any component can read or mutate it via useWorkspace.
 */
export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [extractions, setExtractions] = useState<ExtractionResponse[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);

  // Restore previously uploaded documents on load so a refresh does not wipe
  // the workspace.
  useEffect(() => {
    let active = true;
    listDocuments()
      .then((docs) => {
        if (active) setDocuments(docs);
      })
      .catch(() => {
        /* backend offline — start empty */
      })
      .finally(() => {
        if (active) setLoadingDocs(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const addDocument = useCallback((response: UploadResponse) => {
    setDocuments((prev) => [
      { document_id: response.document_id, filename: response.filename },
      ...prev,
    ]);
  }, []);

  const toggleSelect = useCallback((id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }, []);

  const addExtraction = useCallback((response: ExtractionResponse) => {
    setExtractions((prev) => {
      const existing = prev.findIndex(
        (e) => e.document_id === response.document_id
      );
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = response;
        return updated;
      }
      return [...prev, response];
    });
  }, []);

  const value = useMemo<WorkspaceContextValue>(
    () => ({
      documents,
      selectedIds,
      extractions,
      loadingDocs,
      addDocument,
      toggleSelect,
      addExtraction,
    }),
    [
      documents,
      selectedIds,
      extractions,
      loadingDocs,
      addDocument,
      toggleSelect,
      addExtraction,
    ]
  );

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace(): WorkspaceContextValue {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return ctx;
}
