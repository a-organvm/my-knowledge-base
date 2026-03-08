import { API_BASE, ApiError } from './core';

export interface IngestDocumentResult {
  totalUnits: number;
  files: Array<{
    filename: string;
    unitCount: number;
    preview: Array<{ id: string; title: string; type: string }>;
  }>;
}

export interface IngestUrlResult {
  url: string;
  title: string;
  unitCount: number;
  preview: Array<{ id: string; title: string; type: string }>;
}

export interface IngestTextResult {
  unitCount: number;
  units: Array<{ id: string; title: string; type: string; content: string }>;
}

export interface IngestBatchResult {
  totalFiles: number;
  totalUnits: number;
  successCount: number;
  errorCount: number;
  files: Array<{ filename: string; unitCount: number; error?: string }>;
}

export const ingestApi = {
  /**
   * Upload one or more documents for atomization
   */
  uploadDocuments: async (files: File[]): Promise<IngestDocumentResult> => {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }

    const response = await fetch(`${API_BASE}/ingest/document`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type — browser sets multipart boundary automatically
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        (error as Record<string, string>).error || `Upload failed: ${response.statusText}`,
        response.status,
      );
    }

    const result = await response.json();
    return result.data;
  },

  /**
   * Clip a URL and atomize the content
   */
  clipUrl: async (url: string): Promise<IngestUrlResult> => {
    const response = await fetch(`${API_BASE}/ingest/url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        (error as Record<string, string>).error || `URL clip failed: ${response.statusText}`,
        response.status,
      );
    }

    const result = await response.json();
    return result.data;
  },

  /**
   * Create units directly from text
   */
  addText: async (title: string, content: string, type?: string): Promise<IngestTextResult> => {
    const response = await fetch(`${API_BASE}/ingest/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content, type }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        (error as Record<string, string>).error || `Text import failed: ${response.statusText}`,
        response.status,
      );
    }

    const result = await response.json();
    return result.data;
  },

  /**
   * Batch upload multiple documents
   */
  batchUpload: async (files: File[]): Promise<IngestBatchResult> => {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }

    const response = await fetch(`${API_BASE}/ingest/batch-documents`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        (error as Record<string, string>).error || `Batch upload failed: ${response.statusText}`,
        response.status,
      );
    }

    const result = await response.json();
    return result.data;
  },
};
