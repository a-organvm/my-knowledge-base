/**
 * Ingestion API — web-based document upload, URL clipping, and text import
 * Exposes endpoints for importing content through the UI rather than CLI-only.
 */

import { Router, Request, Response } from 'express';
import multer from 'multer';
import { randomUUID } from 'crypto';
import { KnowledgeDatabase } from './database.js';
import { KnowledgeAtomizer } from './atomizer.js';
import { ProviderImportDetector } from './sources/providers/detector.js';
import { KnowledgeDocument, AtomicUnit } from './types.js';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_FILES = 5;

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: MAX_FILE_SIZE,
    files: MAX_FILES,
  },
  fileFilter: (_req, file, cb) => {
    const allowed = ['.md', '.txt', '.pdf', '.json', '.html', '.htm'];
    const ext = '.' + (file.originalname.split('.').pop()?.toLowerCase() ?? '');
    if (allowed.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`Unsupported file type: ${ext}. Allowed: ${allowed.join(', ')}`));
    }
  },
});

/**
 * Insert atomized units into the database using the canonical method
 * which handles tags, keywords, relationships, and FTS indexing.
 */
function persistUnits(db: KnowledgeDatabase, units: AtomicUnit[]): AtomicUnit[] {
  for (const unit of units) {
    // Ensure timestamp is a Date (atomizer may produce string timestamps)
    if (!(unit.timestamp instanceof Date)) {
      unit.timestamp = typeof unit.timestamp === 'string'
        ? new Date(unit.timestamp)
        : new Date();
    }
    db.insertAtomicUnit(unit);
  }
  return units;
}

function persistDocumentWithUnits(
  db: KnowledgeDatabase,
  doc: KnowledgeDocument,
  units: AtomicUnit[],
): AtomicUnit[] {
  db.insertDocument(doc);
  return persistUnits(db, units);
}

/**
 * Build a KnowledgeDocument from raw text content
 */
function buildDocument(
  title: string,
  content: string,
  format: KnowledgeDocument['format'],
  filename?: string,
  metadataOverrides: Record<string, unknown> = {},
): KnowledgeDocument {
  return {
    id: randomUUID(),
    title,
    content,
    created: new Date(),
    modified: new Date(),
    format,
    metadata: {
      sourceId: 'web-upload',
      sourceName: 'Web Upload',
      originalFilename: filename,
      ...metadataOverrides,
    },
  };
}

/**
 * Detect format from file extension
 */
function detectFormat(filename: string): KnowledgeDocument['format'] {
  const ext = filename.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'md': return 'markdown';
    case 'txt': return 'txt';
    case 'pdf': return 'pdf';
    case 'html':
    case 'htm': return 'html';
    default: return 'txt';
  }
}

export function createIngestionRouter(db: KnowledgeDatabase): Router {
  const router = Router();
  const atomizer = new KnowledgeAtomizer({ redaction: { enabled: false } });
  const detector = new ProviderImportDetector();

  /**
   * POST /api/ingest/document
   * Upload one or more documents (multipart form-data)
   */
  router.post('/document', upload.array('files', MAX_FILES), async (req: Request, res: Response) => {
    try {
      const files = req.files as Express.Multer.File[];
      if (!files || files.length === 0) {
        res.status(400).json({ error: 'No files provided' });
        return;
      }

      const results: Array<{ filename: string; unitCount: number; units: AtomicUnit[] }> = [];

      for (const file of files) {
        const content = file.buffer.toString('utf-8');
        const ext = file.originalname.split('.').pop()?.toLowerCase();
        let units: AtomicUnit[] = [];

        // Try conversation JSON detection first
        if (ext === 'json') {
          const detection = detector.detect(file.originalname, content);
          if (detection.importer) {
            const conversations = detection.importer.parse(detection.context);
            for (const conv of conversations) {
              // Convert NormalizedConversation turns into atomic units
              for (const turn of conv.turns) {
                if (turn.role === 'assistant' && turn.content.trim()) {
                  units.push({
                    id: randomUUID(),
                    title: conv.title || 'Imported Conversation',
                    content: turn.content,
                    type: 'insight',
                    category: 'general',
                    timestamp: turn.timestamp ? new Date(turn.timestamp) : new Date(),
                    tags: [conv.provider],
                    keywords: [],
                    context: `From ${conv.provider} conversation: ${conv.title}`,
                    relatedUnits: [],
                  } as AtomicUnit);
                }
              }
            }
          }
        }

        // If not a conversation JSON (or detection failed), atomize as document
        if (units.length === 0) {
          const format = detectFormat(file.originalname);

          // For PDF, use pdf-parse
          let textContent = content;
          if (ext === 'pdf') {
            try {
              const pdfParse = (await import('pdf-parse')).default;
              const pdfData = await pdfParse(file.buffer);
              textContent = pdfData.text;
            } catch (err) {
              res.status(400).json({ error: `Failed to parse PDF: ${(err as Error).message}` });
              return;
            }
          }

          const title = file.originalname.replace(/\.[^.]+$/, '').replace(/[-_]/g, ' ');
          const doc = buildDocument(title, textContent, format, file.originalname);
          units = atomizer.atomizeDocument(doc);
          persistDocumentWithUnits(db, doc, units);
        } else {
          persistUnits(db, units);
        }
        results.push({
          filename: file.originalname,
          unitCount: units.length,
          units: units.slice(0, 5), // Preview first 5
        });
      }

      const totalUnits = results.reduce((sum, r) => sum + r.unitCount, 0);
      res.status(201).json({
        success: true,
        data: {
          totalUnits,
          files: results.map(r => ({
            filename: r.filename,
            unitCount: r.unitCount,
            preview: r.units.map(u => ({ id: u.id, title: u.title, type: u.type })),
          })),
        },
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      console.error('Document ingestion error:', err);
      res.status(500).json({ error: `Ingestion failed: ${(err as Error).message}` });
    }
  });

  /**
   * POST /api/ingest/url
   * Clip a URL and atomize the content
   */
  router.post('/url', async (req: Request, res: Response) => {
    try {
      const { url } = req.body;
      if (!url || typeof url !== 'string') {
        res.status(400).json({ error: 'URL is required' });
        return;
      }

      // Validate URL format
      try {
        new URL(url);
      } catch {
        res.status(400).json({ error: 'Invalid URL format' });
        return;
      }

      // Use JSDOM + Readability for lighter-weight clipping (no Playwright needed for server)
      const { JSDOM } = await import('jsdom');
      const { Readability } = await import('@mozilla/readability');

      const response = await fetch(url, {
        headers: { 'User-Agent': 'KnowledgeBase/1.0 (Web Clipper)' },
        signal: AbortSignal.timeout(15000),
      });

      if (!response.ok) {
        res.status(400).json({ error: `Failed to fetch URL: ${response.status} ${response.statusText}` });
        return;
      }

      const html = await response.text();
      const dom = new JSDOM(html, { url });
      const reader = new Readability(dom.window.document);
      const article = reader.parse();

      if (!article) {
        res.status(400).json({ error: 'Could not extract article content from URL' });
        return;
      }

      // Convert HTML article to markdown-ish text for atomization
      const textContent = article.textContent || '';
      const title = article.title || new URL(url).hostname;

      const doc = buildDocument(title, textContent, 'html', url, {
        sourceId: 'web-url',
        sourceName: 'Web URL',
        sourceUrl: url,
        originalUrl: url,
      });
      doc.url = url;
      const units = atomizer.atomizeDocument(doc);
      persistDocumentWithUnits(db, doc, units);

      res.status(201).json({
        success: true,
        data: {
          url,
          title,
          unitCount: units.length,
          preview: units.slice(0, 5).map(u => ({ id: u.id, title: u.title, type: u.type })),
        },
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      console.error('URL ingestion error:', err);
      res.status(500).json({ error: `URL ingestion failed: ${(err as Error).message}` });
    }
  });

  /**
   * POST /api/ingest/text
   * Create units directly from text content
   */
  router.post('/text', async (req: Request, res: Response) => {
    try {
      const { title, content, type } = req.body;

      if (!title || typeof title !== 'string') {
        res.status(400).json({ error: 'Title is required' });
        return;
      }
      if (!content || typeof content !== 'string') {
        res.status(400).json({ error: 'Content is required' });
        return;
      }

      const doc = buildDocument(title, content, 'markdown');
      const units = atomizer.atomizeDocument(doc);

      // If atomization produces nothing (very short content), create a single unit
      if (units.length === 0) {
        const unit: AtomicUnit = {
          id: randomUUID(),
          title,
          content,
          type: type || 'reference',
          category: 'general',
          timestamp: new Date(),
          context: `From document: ${title}`,
          tags: [],
          keywords: [],
          documentId: doc.id,
          relatedUnits: [],
        } as AtomicUnit;
        units.push(unit);
      }

      persistDocumentWithUnits(db, doc, units);

      res.status(201).json({
        success: true,
        data: {
          unitCount: units.length,
          units: units.slice(0, 10).map(u => ({ id: u.id, title: u.title, type: u.type, content: u.content.slice(0, 200) })),
        },
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      console.error('Text ingestion error:', err);
      res.status(500).json({ error: `Text ingestion failed: ${(err as Error).message}` });
    }
  });

  /**
   * POST /api/ingest/batch-documents
   * Upload multiple files for batch processing
   */
  router.post('/batch-documents', upload.array('files', 20), async (req: Request, res: Response) => {
    try {
      const files = req.files as Express.Multer.File[];
      if (!files || files.length === 0) {
        res.status(400).json({ error: 'No files provided' });
        return;
      }

      const results: Array<{ filename: string; unitCount: number; error?: string }> = [];
      let totalUnits = 0;

      for (const file of files) {
        try {
          const content = file.buffer.toString('utf-8');
          const ext = file.originalname.split('.').pop()?.toLowerCase();
          let units: AtomicUnit[] = [];

          // Try conversation JSON detection
          if (ext === 'json') {
            const detection = detector.detect(file.originalname, content);
            if (detection.importer) {
              const conversations = detection.importer.parse(detection.context);
              for (const conv of conversations) {
                for (const turn of conv.turns) {
                  if (turn.role === 'assistant' && turn.content.trim()) {
                    units.push({
                      id: randomUUID(),
                      title: conv.title || 'Imported Conversation',
                      content: turn.content,
                      type: 'insight',
                      category: 'general',
                      timestamp: turn.timestamp ? new Date(turn.timestamp) : new Date(),
                      tags: [conv.provider],
                      keywords: [],
                      context: `From ${conv.provider} conversation: ${conv.title}`,
                      relatedUnits: [],
                    } as AtomicUnit);
                  }
                }
              }
            }
          }

          // Atomize as document if not conversation
          if (units.length === 0) {
            const format = detectFormat(file.originalname);
            let textContent = content;

            if (ext === 'pdf') {
              const pdfParse = (await import('pdf-parse')).default;
              const pdfData = await pdfParse(file.buffer);
              textContent = pdfData.text;
            }

            const title = file.originalname.replace(/\.[^.]+$/, '').replace(/[-_]/g, ' ');
            const doc = buildDocument(title, textContent, format, file.originalname);
            units = atomizer.atomizeDocument(doc);
            persistDocumentWithUnits(db, doc, units);
          } else {
            persistUnits(db, units);
          }
          totalUnits += units.length;
          results.push({ filename: file.originalname, unitCount: units.length });
        } catch (err) {
          results.push({
            filename: file.originalname,
            unitCount: 0,
            error: (err as Error).message,
          });
        }
      }

      res.status(201).json({
        success: true,
        data: {
          totalFiles: files.length,
          totalUnits,
          successCount: results.filter(r => !r.error).length,
          errorCount: results.filter(r => r.error).length,
          files: results,
        },
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      console.error('Batch ingestion error:', err);
      res.status(500).json({ error: `Batch ingestion failed: ${(err as Error).message}` });
    }
  });

  return router;
}
