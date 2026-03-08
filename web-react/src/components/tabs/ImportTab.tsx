/**
 * ImportTab Component
 * Three-panel import interface: Document Upload, URL Clip, Quick Add
 */

import { useState, useRef, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';
import { ingestApi } from '../../api/ingest';
import { useUIStore } from '../../stores/uiStore';

const ACCEPTED_EXTENSIONS = '.md,.txt,.pdf,.json,.html,.htm';
const MAX_FILE_SIZE_MB = 10;

export function ImportTab() {
  const { addToast } = useUIStore();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Import Content</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <DocumentUploadPanel addToast={addToast} />
        <UrlClipPanel addToast={addToast} />
        <QuickAddPanel addToast={addToast} />
      </div>
    </div>
  );
}

// --- Document Upload Panel ---

function DocumentUploadPanel({ addToast }: { addToast: (msg: string, type: 'success' | 'error' | 'info') => void }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useMutation({
    mutationFn: (files: File[]) => ingestApi.uploadDocuments(files),
    onSuccess: (data) => {
      addToast(`Imported ${data.totalUnits} units from ${data.files.length} file(s)`, 'success');
      setSelectedFiles([]);
    },
    onError: (err: Error) => {
      addToast(`Upload failed: ${err.message}`, 'error');
    },
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const validateFiles = (files: FileList | File[]): File[] => {
    const arr = Array.from(files);
    const valid: File[] = [];
    for (const file of arr) {
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        addToast(`${file.name} exceeds ${MAX_FILE_SIZE_MB}MB limit`, 'error');
        continue;
      }
      valid.push(file);
    }
    return valid.slice(0, 5);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files.length > 0) {
      setSelectedFiles(validateFiles(e.dataTransfer.files));
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles(validateFiles(e.target.files));
    }
  };

  return (
    <div className="card p-5 space-y-4">
      <h3 className="text-lg font-medium">Document Upload</h3>
      <p className="text-sm text-[var(--text-secondary)]">
        Upload markdown, text, PDF, HTML, or conversation JSON exports
      </p>

      {/* Drop zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          dragActive
            ? 'border-[var(--accent)] bg-[var(--accent)]/10'
            : 'border-[var(--border)] hover:border-[var(--accent)]/50'
        }`}
      >
        <div className="text-3xl mb-2">+</div>
        <p className="text-sm text-[var(--text-secondary)]">
          Drop files here or click to browse
        </p>
        <p className="text-xs text-[var(--text-secondary)] mt-1">
          .md, .txt, .pdf, .json, .html — max {MAX_FILE_SIZE_MB}MB each, up to 5 files
        </p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS}
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Selected files list */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">{selectedFiles.length} file(s) selected:</p>
          <ul className="text-sm space-y-1">
            {selectedFiles.map((file, i) => (
              <li key={i} className="flex justify-between items-center text-[var(--text-secondary)]">
                <span className="truncate">{file.name}</span>
                <span className="text-xs ml-2 shrink-0">
                  {(file.size / 1024).toFixed(0)} KB
                </span>
              </li>
            ))}
          </ul>
          <button
            onClick={() => uploadMutation.mutate(selectedFiles)}
            disabled={uploadMutation.isPending}
            className="btn-primary w-full"
          >
            {uploadMutation.isPending ? 'Uploading...' : `Upload & Atomize (${selectedFiles.length})`}
          </button>
        </div>
      )}

      {/* Results */}
      {uploadMutation.data && (
        <ResultSummary
          label="Uploaded"
          count={uploadMutation.data.totalUnits}
          items={uploadMutation.data.files.flatMap(f => f.preview)}
        />
      )}
    </div>
  );
}

// --- URL Clip Panel ---

function UrlClipPanel({ addToast }: { addToast: (msg: string, type: 'success' | 'error' | 'info') => void }) {
  const [url, setUrl] = useState('');

  const clipMutation = useMutation({
    mutationFn: (url: string) => ingestApi.clipUrl(url),
    onSuccess: (data) => {
      addToast(`Clipped "${data.title}" — ${data.unitCount} units`, 'success');
      setUrl('');
    },
    onError: (err: Error) => {
      addToast(`Clip failed: ${err.message}`, 'error');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    clipMutation.mutate(url.trim());
  };

  return (
    <div className="card p-5 space-y-4">
      <h3 className="text-lg font-medium">URL Clip</h3>
      <p className="text-sm text-[var(--text-secondary)]">
        Fetch a web page, extract its content, and atomize into knowledge units
      </p>

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/article"
          className="input w-full"
          required
        />
        <button
          type="submit"
          disabled={clipMutation.isPending || !url.trim()}
          className="btn-primary w-full"
        >
          {clipMutation.isPending ? 'Clipping...' : 'Clip URL'}
        </button>
      </form>

      {clipMutation.data && (
        <ResultSummary
          label={clipMutation.data.title}
          count={clipMutation.data.unitCount}
          items={clipMutation.data.preview}
        />
      )}
    </div>
  );
}

// --- Quick Add Panel ---

function QuickAddPanel({ addToast }: { addToast: (msg: string, type: 'success' | 'error' | 'info') => void }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [type, setType] = useState('reference');

  const addMutation = useMutation({
    mutationFn: () => ingestApi.addText(title, content, type),
    onSuccess: (data) => {
      addToast(`Created ${data.unitCount} unit(s)`, 'success');
      setTitle('');
      setContent('');
    },
    onError: (err: Error) => {
      addToast(`Failed: ${err.message}`, 'error');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    addMutation.mutate();
  };

  return (
    <div className="card p-5 space-y-4">
      <h3 className="text-lg font-medium">Quick Add</h3>
      <p className="text-sm text-[var(--text-secondary)]">
        Add a knowledge unit directly from text
      </p>

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Title"
          className="input w-full"
          required
        />
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="input w-full"
        >
          <option value="reference">Reference</option>
          <option value="insight">Insight</option>
          <option value="code">Code</option>
          <option value="question">Question</option>
          <option value="decision">Decision</option>
        </select>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Content (markdown supported)"
          rows={6}
          className="input w-full resize-y"
          required
        />
        <button
          type="submit"
          disabled={addMutation.isPending || !title.trim() || !content.trim()}
          className="btn-primary w-full"
        >
          {addMutation.isPending ? 'Adding...' : 'Add Unit'}
        </button>
      </form>

      {addMutation.data && (
        <ResultSummary
          label="Created"
          count={addMutation.data.unitCount}
          items={addMutation.data.units.map(u => ({ id: u.id, title: u.title, type: u.type }))}
        />
      )}
    </div>
  );
}

// --- Shared result display ---

function ResultSummary({
  label,
  count,
  items,
}: {
  label: string;
  count: number;
  items: Array<{ id: string; title: string; type: string }>;
}) {
  return (
    <div className="border border-[var(--border)] rounded-lg p-3 bg-[var(--bg-secondary)]">
      <p className="text-sm font-medium mb-2">
        {label}: {count} unit(s)
      </p>
      {items.length > 0 && (
        <ul className="text-xs space-y-1 text-[var(--text-secondary)]">
          {items.slice(0, 5).map((item) => (
            <li key={item.id} className="truncate">
              <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-[var(--accent)]/20 text-[var(--accent)] mr-1">
                {item.type}
              </span>
              {item.title}
            </li>
          ))}
          {items.length > 5 && (
            <li className="italic">...and {items.length - 5} more</li>
          )}
        </ul>
      )}
    </div>
  );
}
