#!/usr/bin/env node
import Database from 'better-sqlite3';
import { UniverseStore } from './universe/store.js';
import { UniverseIngestService } from './universe/ingest.js';

function parseArg(name: string): string | undefined {
  const prefix = `--${name}=`;
  const entry = process.argv.find((arg) => arg.startsWith(prefix));
  return entry ? entry.slice(prefix.length) : undefined;
}

function hasFlag(name: string): boolean {
  return process.argv.includes(`--${name}`);
}

const dbPath = process.env.KNOWLEDGE_DB_PATH || './db/knowledge.db';
const rootDir = parseArg('root') || 'intake';
const limitValue = parseArg('limit');
const reportDir = parseArg('report-dir') || 'intake/reports';
const save = hasFlag('save');

const limit = limitValue ? Number.parseInt(limitValue, 10) : undefined;
if (limitValue && (!Number.isFinite(limit) || (limit as number) <= 0)) {
  console.error(`Invalid --limit value: ${limitValue}`);
  process.exit(1);
}

const db = new Database(dbPath);

try {
  console.error(`[ingest] db=${dbPath} root=${rootDir} limit=${limit ?? 'none'} save=${save}`);
  const store = new UniverseStore(db);
  const ingest = new UniverseIngestService(store);

  let lastLog = Date.now();
  const report = ingest.run({
    rootDir,
    limit,
    save,
    reportDir,
    onProgress: (event) => {
      const now = Date.now();
      if (event.kind === 'start') {
        console.error(`[ingest] scanning ${event.totalFiles} files...`);
      } else if (event.kind === 'file' && event.outcome !== 'skipped') {
        console.error(`[ingest] ${event.outcome}: ${event.filePath} (chats=${event.fileChatsIngested ?? 0})`);
      } else if (event.kind === 'checkpoint' || now - lastLog > 5000) {
        console.error(`[ingest] ${event.processedFiles}/${event.totalFiles} | ingested=${event.filesIngested} quarantined=${event.filesQuarantined} chats=${event.chatsIngested} turns=${event.turnsIngested}`);
        lastLog = now;
      } else if (event.kind === 'complete') {
        console.error(`[ingest] DONE: ${event.filesIngested} files, ${event.chatsIngested} chats, ${event.turnsIngested} turns`);
      }
    },
  });

  console.log(JSON.stringify(report, null, 2));
} finally {
  db.close();
}
