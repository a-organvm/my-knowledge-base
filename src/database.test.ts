import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { mkdirSync, rmSync } from 'fs';
import { join } from 'path';
import { KnowledgeDatabase } from './database.js';
import { AtomicUnit } from './types.js';

describe('KnowledgeDatabase helpers', () => {
  let tempDir: string;
  let dbPath: string;
  let db: KnowledgeDatabase;

  beforeEach(() => {
    tempDir = join(process.cwd(), '.test-tmp', 'database-helpers');
    dbPath = join(tempDir, 'test.db');
    mkdirSync(tempDir, { recursive: true });
    db = new KnowledgeDatabase(dbPath);

    const timestamp = new Date('2026-01-01T00:00:00.000Z');
    const units: AtomicUnit[] = [
      {
        id: 'unit-1',
        type: 'insight',
        title: 'Focused Graph Node',
        content: 'Graph focus content',
        context: 'context',
        category: 'programming',
        tags: ['graph', 'focus'],
        keywords: ['graph', 'focus'],
        relatedUnits: [],
        timestamp,
      },
      {
        id: 'unit-2',
        type: 'code',
        title: 'Neighbor Node',
        content: 'Neighbor content',
        context: 'context',
        category: 'programming',
        tags: ['graph', 'neighbor'],
        keywords: ['neighbor'],
        relatedUnits: [],
        timestamp: new Date('2026-01-02T00:00:00.000Z'),
      },
      {
        id: 'unit-3',
        type: 'question',
        title: 'Different Category',
        content: 'Design category content',
        context: 'context',
        category: 'design',
        tags: ['design'],
        keywords: ['design'],
        relatedUnits: [],
        timestamp: new Date('2026-01-03T00:00:00.000Z'),
      },
    ];

    units.forEach(unit => db.insertAtomicUnit(unit));

    const rawDb = db['db'];
    rawDb.prepare(`
      INSERT INTO unit_relationships (from_unit, to_unit, relationship_type)
      VALUES (?, ?, 'related')
    `).run('unit-1', 'unit-2');
  });

  afterEach(() => {
    try {
      db.close();
    } catch (error) {
      // Ignore close errors for cleanup robustness in tests
    }
    rmSync(tempDir, { recursive: true, force: true });
  });

  it('getUnitById returns a hydrated unit', () => {
    const unit = db.getUnitById('unit-1');
    expect(unit?.id).toBe('unit-1');
    expect(unit?.tags).toContain('graph');
    expect(unit?.keywords).toContain('focus');
    expect(unit?.relatedUnits).toContain('unit-2');
  });

  it('getUnitsForGraph supports type and category filters', () => {
    const programmingInsights = db.getUnitsForGraph({
      limit: 10,
      type: 'insight',
      category: 'programming',
    });

    expect(programmingInsights.map(u => u.id)).toEqual(['unit-1']);
  });

  it('getRelationshipsForUnitIds returns touching relationships', () => {
    const edges = db.getRelationshipsForUnitIds(['unit-1', 'unit-2']);
    expect(edges.length).toBeGreaterThan(0);
    expect(edges[0]).toMatchObject({ fromUnit: 'unit-1', toUnit: 'unit-2' });
  });

  it('searchTextPaginated falls back to document URLs when chunk text does not contain the query', () => {
    db.insertDocument({
      id: 'doc-url-1',
      title: 'Behavior Blockchain Research',
      content: 'Notes about habit contracts and commitment mechanisms.',
      created: new Date('2026-01-04T00:00:00.000Z'),
      modified: new Date('2026-01-04T00:00:00.000Z'),
      url: 'https://stickk.com/research/behavior-blockchain',
      format: 'html',
      metadata: {
        sourceId: 'research-web',
        originalFilename: 'stickk-research.html',
      },
    });

    db.insertAtomicUnit({
      id: 'unit-url-1',
      type: 'reference',
      title: 'Commitment mechanisms overview',
      content: 'Summarizes the research findings without spelling out the site URL.',
      context: 'From document: Behavior Blockchain Research',
      category: 'research',
      tags: ['research'],
      keywords: ['commitment', 'behavior'],
      relatedUnits: [],
      timestamp: new Date('2026-01-04T00:00:00.000Z'),
      documentId: 'doc-url-1',
    });

    const result = db.searchTextPaginated('stickk.com', 0, 10);

    expect(result.total).toBeGreaterThan(0);
    expect(result.results.map((unit) => unit.id)).toContain('unit-url-1');
  });

  it('searchText can match document metadata such as original filenames', () => {
    db.insertDocument({
      id: 'doc-meta-1',
      title: 'Merlin Archetype',
      content: 'Locates the merlin archetype discussion in a design note.',
      created: new Date('2026-01-05T00:00:00.000Z'),
      modified: new Date('2026-01-05T00:00:00.000Z'),
      format: 'markdown',
      metadata: {
        originalFilename: 'tool-interaction-design/phase-2/merlin-archetype.md',
      },
    });

    db.insertAtomicUnit({
      id: 'unit-meta-1',
      type: 'insight',
      title: 'Merlin Archetype Notes',
      content: 'The archetype appears in the document body.',
      context: 'From document: Merlin Archetype',
      category: 'design',
      tags: ['design'],
      keywords: ['merlin', 'archetype'],
      relatedUnits: [],
      timestamp: new Date('2026-01-05T00:00:00.000Z'),
      documentId: 'doc-meta-1',
    });

    const result = db.searchText('tool-interaction-design');

    expect(result.map((unit) => unit.id)).toContain('unit-meta-1');
  });
});
