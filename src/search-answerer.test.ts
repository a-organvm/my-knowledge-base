import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { mkdirSync, rmSync } from 'fs';
import { join } from 'path';
import { KnowledgeDatabase } from './database.js';
import { SearchAnswerer } from './search-answerer.js';

describe('SearchAnswerer', () => {
  let tempDir: string;
  let db: KnowledgeDatabase;
  let answerer: SearchAnswerer;

  beforeEach(() => {
    tempDir = join(process.cwd(), '.test-tmp', 'search-answerer');
    mkdirSync(tempDir, { recursive: true });
    db = new KnowledgeDatabase(join(tempDir, 'test.db'));
    answerer = new SearchAnswerer(db.getRawHandle());
  });

  afterEach(() => {
    try {
      db.close();
    } catch {
      // Ignore cleanup errors in tests.
    }
    rmSync(tempDir, { recursive: true, force: true });
  });

  it('answers evidence-backed research questions from ingested documents with URLs', () => {
    db.insertDocument({
      id: 'doc-stickk',
      title: 'Behavior Blockchain Research',
      content: 'We researched stickk.com as part of the behavior blockchain scan and documented the evidence trail.',
      created: new Date('2026-01-10T00:00:00.000Z'),
      modified: new Date('2026-01-10T00:00:00.000Z'),
      url: 'https://stickk.com/research/behavior-blockchain',
      format: 'html',
      metadata: {
        originalFilename: 'stickk-research.html',
      },
    });

    const result = answerer.answer('Was stickk.com researched for behavior blockchain?');

    expect(result.verdict).toBe('yes');
    expect(result.answer).toContain('Yes.');
    expect(result.primaryLocation).toContain('stickk.com');
    expect(result.evidence[0]?.url).toBe('https://stickk.com/research/behavior-blockchain');
  });

  it('returns a file path for location questions answered from federated docs', () => {
    const sql = db.getRawHandle();
    sql.prepare(`
      INSERT INTO federated_sources (
        id, name, kind, status, root_path, include_patterns, exclude_patterns, metadata, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      'source-tool-interaction-design',
      'Tool Interaction Design',
      'local-filesystem',
      'active',
      '/workspace/tool-interaction-design',
      '["**/*.md"]',
      '[]',
      '{}',
      '2026-01-10T00:00:00.000Z',
      '2026-01-10T00:00:00.000Z',
    );
    sql.prepare(`
      INSERT INTO federated_documents (
        id, source_id, external_id, path, title, content, hash, size_bytes, mime_type, modified_at, indexed_at, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      'fdoc-merlin',
      'source-tool-interaction-design',
      'notes/merlin-archetype.md',
      'tool-interaction-design/notes/merlin-archetype.md',
      'Merlin Archetype',
      'The merlin archetype is discussed here as part of the tool interaction design phase 2 notes.',
      'hash-merlin',
      128,
      'text/markdown',
      '2026-01-10T00:00:00.000Z',
      '2026-01-10T00:00:00.000Z',
      '{}',
    );

    const result = answerer.answer('where is the merlin archetype in tool-interaction-design?');

    expect(result.verdict).toBe('yes');
    expect(result.primaryLocation).toBe('tool-interaction-design/notes/merlin-archetype.md');
    expect(result.answer).toContain('tool-interaction-design/notes/merlin-archetype.md');
    expect(result.evidence[0]?.path).toBe('tool-interaction-design/notes/merlin-archetype.md');
  });

  it('answers codebase access questions honestly from indexed repository coverage', () => {
    const sql = db.getRawHandle();
    sql.prepare(`
      INSERT INTO federated_sources (
        id, name, kind, status, root_path, include_patterns, exclude_patterns, metadata, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      'source-codebase',
      'Main Codebase',
      'local-filesystem',
      'active',
      '/workspace/my-knowledge-base',
      '["**/*.ts"]',
      '[]',
      '{"repository":"my-knowledge-base"}',
      '2026-01-10T00:00:00.000Z',
      '2026-01-10T00:00:00.000Z',
    );
    sql.prepare(`
      INSERT INTO federated_documents (
        id, source_id, external_id, path, title, content, hash, size_bytes, mime_type, modified_at, indexed_at, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      'fdoc-api',
      'source-codebase',
      'src/api.ts',
      'src/api.ts',
      'API',
      'router.get("/search/answer")',
      'hash-api',
      64,
      'text/plain',
      '2026-01-10T00:00:00.000Z',
      '2026-01-10T00:00:00.000Z',
      '{}',
    );

    const result = answerer.answer('do you have full access to the codebase?');

    expect(result.verdict).toBe('partial');
    expect(result.answer).toContain('Not full live access.');
    expect(result.answer).toContain('indexed subset');
    expect(result.evidence[0]?.title).toBe('my-knowledge-base');
  });
});
