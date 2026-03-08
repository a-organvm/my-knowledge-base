#!/usr/bin/env node
/**
 * CLI for web-based ingestion — sends files/URLs/text to the running web server.
 * Usage:
 *   tsx src/ingest-cli.ts document file1.md file2.json  # upload documents
 *   tsx src/ingest-cli.ts url https://example.com        # clip a URL
 *   tsx src/ingest-cli.ts text "Title" "Content here"    # quick add
 *   tsx src/ingest-cli.ts batch *.md                     # batch upload
 *
 * Uses the same ingestion API as the web UI, so the server must be running.
 * Set KNOWLEDGE_BASE_URL to override the default (http://localhost:3000/api).
 */

import { readFileSync, statSync } from 'fs';
import { basename } from 'path';

const API_BASE = process.env.KNOWLEDGE_BASE_URL || 'http://localhost:3000/api';

async function ingestDocuments(filePaths: string[]) {
  const formData = new FormData();
  for (const filePath of filePaths) {
    const stat = statSync(filePath);
    if (stat.size > 10 * 1024 * 1024) {
      console.error(`Skipping ${filePath}: exceeds 10MB limit`);
      continue;
    }
    const buffer = readFileSync(filePath);
    const blob = new Blob([buffer]);
    formData.append('files', blob, basename(filePath));
  }

  const res = await fetch(`${API_BASE}/ingest/document`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    console.error('Upload failed:', (err as Record<string, string>).error || res.statusText);
    process.exit(1);
  }

  const result = await res.json();
  console.log(`Imported ${result.data.totalUnits} units from ${result.data.files.length} file(s):`);
  for (const file of result.data.files) {
    console.log(`  ${file.filename}: ${file.unitCount} units`);
  }
}

async function ingestUrl(url: string) {
  const res = await fetch(`${API_BASE}/ingest/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    console.error('URL clip failed:', (err as Record<string, string>).error || res.statusText);
    process.exit(1);
  }

  const result = await res.json();
  console.log(`Clipped "${result.data.title}" — ${result.data.unitCount} units`);
}

async function ingestText(title: string, content: string) {
  const res = await fetch(`${API_BASE}/ingest/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    console.error('Text import failed:', (err as Record<string, string>).error || res.statusText);
    process.exit(1);
  }

  const result = await res.json();
  console.log(`Created ${result.data.unitCount} unit(s)`);
}

async function batchUpload(filePaths: string[]) {
  const formData = new FormData();
  for (const filePath of filePaths) {
    try {
      const stat = statSync(filePath);
      if (stat.size > 10 * 1024 * 1024) {
        console.error(`Skipping ${filePath}: exceeds 10MB limit`);
        continue;
      }
      const buffer = readFileSync(filePath);
      const blob = new Blob([buffer]);
      formData.append('files', blob, basename(filePath));
    } catch (err) {
      console.error(`Skipping ${filePath}: ${(err as Error).message}`);
    }
  }

  const res = await fetch(`${API_BASE}/ingest/batch-documents`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    console.error('Batch upload failed:', (err as Record<string, string>).error || res.statusText);
    process.exit(1);
  }

  const result = await res.json();
  console.log(`Batch: ${result.data.successCount}/${result.data.totalFiles} files, ${result.data.totalUnits} total units`);
  for (const file of result.data.files) {
    const status = file.error ? `ERROR: ${file.error}` : `${file.unitCount} units`;
    console.log(`  ${file.filename}: ${status}`);
  }
}

// --- Main ---

const [command, ...args] = process.argv.slice(2);

if (!command || command === '--help' || command === '-h') {
  console.log(`Usage:
  tsx src/ingest-cli.ts document <file1> [file2] ...   Upload and atomize documents
  tsx src/ingest-cli.ts url <url>                      Clip and atomize a URL
  tsx src/ingest-cli.ts text "<title>" "<content>"     Create unit from text
  tsx src/ingest-cli.ts batch <file1> [file2] ...      Batch upload (up to 20)

Environment:
  KNOWLEDGE_BASE_URL   API base URL (default: http://localhost:3000/api)`);
  process.exit(0);
}

switch (command) {
  case 'document':
    if (args.length === 0) { console.error('Provide at least one file path'); process.exit(1); }
    await ingestDocuments(args);
    break;
  case 'url':
    if (!args[0]) { console.error('Provide a URL'); process.exit(1); }
    await ingestUrl(args[0]);
    break;
  case 'text':
    if (!args[0] || !args[1]) { console.error('Provide title and content'); process.exit(1); }
    await ingestText(args[0], args[1]);
    break;
  case 'batch':
    if (args.length === 0) { console.error('Provide at least one file path'); process.exit(1); }
    await batchUpload(args);
    break;
  default:
    console.error(`Unknown command: ${command}. Use --help for usage.`);
    process.exit(1);
}
