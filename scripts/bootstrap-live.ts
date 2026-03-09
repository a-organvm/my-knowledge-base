#!/usr/bin/env node
/**
 * Bootstrap the live knowledge base by parsing local source documents
 * and POSTing the resulting atomic units to the remote API in batches.
 *
 * Handles files too large for the 10MB multipart upload limit by
 * parsing locally and sending units via JSON POST.
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, basename, extname } from 'path';
import { ProviderImportDetector } from '../src/sources/providers/detector.js';
import { KnowledgeAtomizer } from '../src/atomizer.js';
import { KnowledgeDocument, AtomicUnit } from '../src/types.js';
import { randomUUID } from 'crypto';

const API_BASE = process.env.KNOWLEDGE_BASE_URL || 'https://organvm-knowledge-base.fly.dev/api';
const BATCH_SIZE = 10; // units per POST (keep small for large content)
const SOURCES_DIR = join(import.meta.dirname, '../intake/canonical/sources');

// Blocklist patterns — never ingest these
const BLOCKLIST = [
  /Login\s*Password/i,
  /\.DS_Store$/,
  /_gemini_visit/,
  /\.webarchive$/,
  /\.webp$/,
  /\.png$/,
  /\.jpg$/,
  /chat\.html$/, // duplicate of conversations.json
];

function isBlocked(path: string): boolean {
  return BLOCKLIST.some(pattern => pattern.test(path));
}

const detector = new ProviderImportDetector();
const atomizer = new KnowledgeAtomizer({ redaction: { enabled: true } });

async function postUnitsBatch(units: AtomicUnit[]): Promise<number> {
  let created = 0;
  for (let i = 0; i < units.length; i += BATCH_SIZE) {
    const batch = units.slice(i, i + BATCH_SIZE);
    const payload = batch.map(u => ({
      type: u.type || 'reference',
      title: u.title || 'Untitled',
      content: u.content || '',
      context: u.context || '',
      category: u.category || 'general',
      tags: u.tags || [],
      keywords: u.keywords || [],
    }));

    // Use the existing POST /api/units/batch endpoint
    const res = await fetch(`${API_BASE}/units/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ units: payload }),
    });

    if (!res.ok) {
      const err = await res.text().catch(() => 'unknown error');
      console.error(`  Batch POST failed (${res.status}): ${err.slice(0, 200)}`);
      // Fall back to individual POSTs
      for (const unit of payload) {
        try {
          const r = await fetch(`${API_BASE}/units`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(unit),
          });
          if (r.ok) created++;
        } catch {
          // skip individual failures
        }
      }
    } else {
      created += batch.length;
    }
  }
  return created;
}

async function processConversationJson(filePath: string): Promise<number> {
  console.log(`\nParsing conversations: ${basename(filePath)} (${(statSync(filePath).size / 1024 / 1024).toFixed(0)}MB)`);
  const content = readFileSync(filePath, 'utf-8');
  const detection = detector.detect(filePath, content);

  if (!detection.importer) {
    console.log('  No conversation format detected, attempting document atomization...');
    // Try as a regular document if small enough
    if (statSync(filePath).size < 10 * 1024 * 1024) {
      const doc: KnowledgeDocument = {
        id: randomUUID(),
        title: basename(filePath, extname(filePath)),
        content,
        created: new Date(),
        modified: new Date(),
        format: 'txt',
        metadata: { sourceId: 'bootstrap', sourceName: 'Bootstrap Import' },
      };
      const units = atomizer.atomizeDocument(doc);
      const created = await postUnitsBatch(units);
      console.log(`  Created ${created} units`);
      return created;
    }
    console.log('  Skipping — too large and no format detected');
    return 0;
  }

  const conversations = detection.importer.parse(detection.context);
  console.log(`  Detected ${conversations.length} conversations from ${detection.importer.id}`);

  const units: AtomicUnit[] = [];
  for (const conv of conversations) {
    for (const turn of conv.turns) {
      if (turn.role === 'assistant' && turn.content.trim().length > 10) {
        units.push({
          id: randomUUID(),
          title: conv.title || 'Untitled Conversation',
          content: turn.content,
          type: 'insight',
          category: 'general',
          timestamp: turn.timestamp ? new Date(turn.timestamp) : new Date(),
          context: `From ${conv.provider} conversation: ${conv.title}`,
          tags: [conv.provider],
          keywords: [],
          relatedUnits: [],
        } as AtomicUnit);
      }
    }
  }

  console.log(`  Extracted ${units.length} assistant turns, uploading...`);
  const created = await postUnitsBatch(units);
  console.log(`  Uploaded ${created}/${units.length} units`);
  return created;
}

async function processSmallFile(filePath: string): Promise<number> {
  const ext = extname(filePath).toLowerCase();
  const content = readFileSync(filePath, 'utf-8');

  if (!content.trim()) return 0;

  // Try conversation detection for JSON files
  if (ext === '.json') {
    const detection = detector.detect(filePath, content);
    if (detection.importer) {
      return processConversationJson(filePath);
    }
  }

  const format = ext === '.md' ? 'markdown' : ext === '.html' || ext === '.htm' ? 'html' : 'txt';
  const title = basename(filePath, ext).replace(/[-_]/g, ' ');

  const doc: KnowledgeDocument = {
    id: randomUUID(),
    title,
    content,
    created: new Date(),
    modified: new Date(),
    format,
    metadata: { sourceId: 'bootstrap', sourceName: 'Bootstrap Import', originalFilename: basename(filePath) },
  };

  const units = atomizer.atomizeDocument(doc);
  if (units.length === 0 && content.trim().length > 0) {
    // Create a single unit for very short content
    units.push({
      id: randomUUID(),
      title,
      content: content.trim(),
      type: 'reference',
      category: 'general',
      timestamp: new Date(),
      context: '',
      tags: [],
      keywords: [],
      relatedUnits: [],
    } as AtomicUnit);
  }

  const created = await postUnitsBatch(units);
  return created;
}

function collectFiles(dir: string): string[] {
  const files: string[] = [];
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (isBlocked(fullPath)) continue;
      if (entry.isDirectory()) {
        files.push(...collectFiles(fullPath));
      } else if (entry.isFile()) {
        const ext = extname(entry.name).toLowerCase();
        if (['.md', '.txt', '.json', '.html', '.htm'].includes(ext)) {
          files.push(fullPath);
        }
      }
    }
  } catch (err) {
    console.error(`Error reading ${dir}: ${(err as Error).message}`);
  }
  return files;
}

// --- Main ---

async function main() {
  console.log(`Bootstrap target: ${API_BASE}`);
  console.log(`Sources: ${SOURCES_DIR}\n`);

  // Verify API is reachable
  try {
    const health = await fetch(`${API_BASE}/health`);
    if (!health.ok) throw new Error(`Health check failed: ${health.status}`);
    console.log('API health check: OK\n');
  } catch (err) {
    console.error(`Cannot reach API at ${API_BASE}: ${(err as Error).message}`);
    process.exit(1);
  }

  let totalCreated = 0;

  // Phase 1: Large conversation exports (parse locally, POST units)
  const largeConversations = [
    join(SOURCES_DIR, 'chat-export-batches/data-2026-01-27-00-26-30-batch-0000/conversations.json'),
    join(SOURCES_DIR, 'curated-sources/chatgpt/raw-121525/0d965e163f42d89ff6ca7c5e2a1f6a9e73dc28abb48ffcb76a68aa547265b4b4-2025-12-16-02-05-44-1932af99f23644ab9bc83ac5a8486a2b/conversations.json'),
  ];

  console.log('=== Phase 1: Large Conversation Exports ===');
  for (const file of largeConversations) {
    try {
      if (!statSync(file).isFile()) continue;
      const created = await processConversationJson(file);
      totalCreated += created;
    } catch (err) {
      console.error(`Failed to process ${basename(file)}: ${(err as Error).message}`);
    }
  }

  // Phase 2: Memories file
  console.log('\n=== Phase 2: Memories ===');
  const memoriesFile = join(SOURCES_DIR, 'chat-export-batches/data-2026-01-27-00-26-30-batch-0000/memories.json');
  try {
    const memoriesContent = readFileSync(memoriesFile, 'utf-8');
    const memories = JSON.parse(memoriesContent);
    if (Array.isArray(memories)) {
      const memoryUnits: AtomicUnit[] = memories
        .filter((m: any) => m.content || m.text || m.memory)
        .map((m: any) => ({
          id: randomUUID(),
          title: 'Memory',
          content: m.content || m.text || m.memory || JSON.stringify(m),
          type: 'reference' as const,
          category: 'general',
          timestamp: m.created_at ? new Date(m.created_at) : new Date(),
          context: 'ChatGPT memory',
          tags: ['chatgpt', 'memory'],
          keywords: [],
          relatedUnits: [],
        } as AtomicUnit));
      console.log(`  Found ${memoryUnits.length} memories`);
      const created = await postUnitsBatch(memoryUnits);
      totalCreated += created;
      console.log(`  Uploaded ${created} memory units`);
    }
  } catch (err) {
    console.error(`Memories: ${(err as Error).message}`);
  }

  // Phase 3: Small files (curated markdown, text, safe JSON, HTML)
  console.log('\n=== Phase 3: Small Documents ===');
  const smallFiles = collectFiles(join(SOURCES_DIR, 'curated-sources'));
  console.log(`Found ${smallFiles.length} ingestible files`);

  for (const file of smallFiles) {
    try {
      const size = statSync(file).size;
      if (size > 10 * 1024 * 1024) {
        // Large file — use conversation parser
        const created = await processConversationJson(file);
        totalCreated += created;
      } else if (size > 0) {
        const relPath = file.replace(SOURCES_DIR + '/', '');
        const created = await processSmallFile(file);
        if (created > 0) {
          console.log(`  ${relPath}: ${created} units`);
        }
        totalCreated += created;
      }
    } catch (err) {
      console.error(`  ${basename(file)}: ${(err as Error).message}`);
    }
  }

  console.log(`\n=== Bootstrap Complete ===`);
  console.log(`Total units created: ${totalCreated}`);

  // Final stats check
  try {
    const stats = await fetch(`${API_BASE}/stats`);
    const data = await stats.json();
    const count = data?.totalUnits?.count ?? data?.data?.totalUnits?.count ?? '?';
    console.log(`Live database unit count: ${count}`);
  } catch {
    // non-critical
  }
}

main().catch(err => {
  console.error('Bootstrap failed:', err);
  process.exit(1);
});
