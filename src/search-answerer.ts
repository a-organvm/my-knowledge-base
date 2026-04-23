import { basename } from 'path';
import Database from 'better-sqlite3';

export type SearchAnswerVerdict = 'yes' | 'no' | 'partial' | 'unknown';
export type SearchAnswerConfidence = 'high' | 'medium' | 'low';

export interface SearchAnswerEvidence {
  kind: 'document' | 'federated_document' | 'repository';
  id: string;
  title: string;
  snippet: string;
  score: number;
  matchedTerms: string[];
  url?: string;
  path?: string;
  sourceId?: string;
  sourceName?: string;
}

export interface SearchAnswerResult {
  question: string;
  answer: string;
  verdict: SearchAnswerVerdict;
  confidence: SearchAnswerConfidence;
  primaryLocation?: string;
  locations: string[];
  evidence: SearchAnswerEvidence[];
}

type DocumentRow = {
  id: string;
  title: string;
  content: string;
  url: string | null;
  metadata: string | null;
};

type FederatedDocumentRow = {
  id: string;
  title: string;
  content: string;
  path: string;
  sourceId: string;
  sourceName: string;
  metadata: string | null;
};

type RepositoryRow = {
  id: string;
  name: string;
  rootPath: string;
  indexedFiles: number;
  metadata: string | null;
};

const STOP_WORDS = new Set([
  'a',
  'about',
  'an',
  'and',
  'are',
  'at',
  'be',
  'codebase',
  'did',
  'do',
  'does',
  'for',
  'full',
  'have',
  'in',
  'is',
  'it',
  'of',
  'on',
  'or',
  'researched',
  'that',
  'the',
  'their',
  'there',
  'these',
  'this',
  'to',
  'was',
  'were',
  'where',
  'with',
  'you',
  'your',
]);

function parseJsonRecord(value: string | null | undefined): Record<string, unknown> {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed)
      ? (parsed as Record<string, unknown>)
      : {};
  } catch {
    return {};
  }
}

function unique(values: string[]): string[] {
  return Array.from(new Set(values));
}

function extractTerms(question: string): string[] {
  const normalized = question.toLowerCase();
  const domains: string[] = normalized.match(/\b[a-z0-9-]+(?:\.[a-z0-9-]+)+\b/g) ?? [];
  const rawWords: string[] = normalized
    .replace(/[^\w.\-/\s]+/g, ' ')
    .split(/\s+/)
    .map((word) => word.trim())
    .filter(Boolean);

  const words = rawWords.filter((word) => {
    if (domains.includes(word)) return false;
    if (word.length < 3) return false;
    return !STOP_WORDS.has(word);
  });

  return unique([...domains, ...words]);
}

function includesTerm(value: string | undefined, term: string): boolean {
  return Boolean(value && value.toLowerCase().includes(term));
}

function buildSnippet(text: string, terms: string[]): string {
  const normalizedText = text.replace(/\s+/g, ' ').trim();
  if (normalizedText.length === 0) return '';

  for (const term of terms) {
    const index = normalizedText.toLowerCase().indexOf(term);
    if (index >= 0) {
      const start = Math.max(0, index - 80);
      const end = Math.min(normalizedText.length, index + term.length + 80);
      const prefix = start > 0 ? '...' : '';
      const suffix = end < normalizedText.length ? '...' : '';
      return `${prefix}${normalizedText.slice(start, end)}${suffix}`;
    }
  }

  return normalizedText.slice(0, 180);
}

function extractDocumentPath(metadata: Record<string, unknown>): string | undefined {
  const candidates = [
    metadata.path,
    metadata.filePath,
    metadata.absolutePath,
    metadata.sourcePath,
    metadata.sourceRelativePath,
    metadata.originalFilename,
  ];

  for (const candidate of candidates) {
    if (typeof candidate === 'string' && candidate.trim().length > 0) {
      return candidate.trim();
    }
  }

  return undefined;
}

function confidenceFromEvidence(evidence: SearchAnswerEvidence[]): SearchAnswerConfidence {
  if (evidence.length === 0) return 'low';
  if (evidence[0].matchedTerms.length >= 3 || evidence.length >= 2) return 'high';
  return 'medium';
}

function joinLocations(evidence: SearchAnswerEvidence[]): string[] {
  return unique(
    evidence
      .map((entry) => entry.path ?? entry.url)
      .filter((entry): entry is string => typeof entry === 'string' && entry.length > 0)
  );
}

function preferredLocation(
  evidence: SearchAnswerEvidence | undefined,
  options: { preferPath?: boolean } = {},
): string | undefined {
  if (!evidence) return undefined;
  if (options.preferPath) {
    return evidence.path ?? evidence.url;
  }
  return evidence.url ?? evidence.path;
}

export class SearchAnswerer {
  constructor(private readonly db: Database.Database) {}

  answer(question: string, options: { limit?: number } = {}): SearchAnswerResult {
    const limit = Math.max(1, Math.min(10, options.limit ?? 5));

    if (this.isCodebaseAccessQuestion(question)) {
      return this.answerCodebaseAccess(question, limit);
    }

    const terms = extractTerms(question);
    const evidence = this.findEvidence(question, terms, limit);

    if (this.isLocationQuestion(question)) {
      return this.answerLocationQuestion(question, evidence);
    }

    if (this.isBinaryEvidenceQuestion(question)) {
      return this.answerBinaryQuestion(question, evidence, terms);
    }

    return this.answerGenericQuestion(question, evidence);
  }

  private isLocationQuestion(question: string): boolean {
    return /^\s*where\b/i.test(question);
  }

  private isBinaryEvidenceQuestion(question: string): boolean {
    return /^\s*(was|were|did|does|do|is|are)\b/i.test(question);
  }

  private isCodebaseAccessQuestion(question: string): boolean {
    return /full access to the codebase|access to the codebase|entire codebase/i.test(question);
  }

  private answerLocationQuestion(question: string, evidence: SearchAnswerEvidence[]): SearchAnswerResult {
    const top = evidence[0];
    const primaryLocation = preferredLocation(top, { preferPath: true });
    const answer = top
      ? top.path
        ? `The best match is in ${top.path}.`
        : top.url
          ? `The best match is associated with ${top.url}.`
          : `The best match is ${top.title}.`
      : 'I could not find a matching file or document location in the indexed sources.';

    return {
      question,
      answer,
      verdict: top ? 'yes' : 'unknown',
      confidence: confidenceFromEvidence(evidence),
      primaryLocation,
      locations: joinLocations(evidence),
      evidence,
    };
  }

  private answerBinaryQuestion(
    question: string,
    evidence: SearchAnswerEvidence[],
    terms: string[],
  ): SearchAnswerResult {
    const top = evidence[0];
    const minimumMatchedTerms = Math.min(2, Math.max(1, terms.length));
    const hasEvidence = Boolean(top && top.matchedTerms.length >= minimumMatchedTerms);
    const primaryLocation = preferredLocation(top);
    const answer = hasEvidence
      ? `Yes. I found evidence in ${primaryLocation ?? top.title}.`
      : 'No strong evidence was found in the indexed documents or federated files.';

    return {
      question,
      answer,
      verdict: hasEvidence ? 'yes' : 'no',
      confidence: confidenceFromEvidence(evidence),
      primaryLocation,
      locations: joinLocations(evidence),
      evidence: hasEvidence ? evidence : [],
    };
  }

  private answerGenericQuestion(question: string, evidence: SearchAnswerEvidence[]): SearchAnswerResult {
    const top = evidence[0];
    const primaryLocation = preferredLocation(top);
    const answer = top
      ? `I found relevant material in ${primaryLocation ?? top.title}.`
      : 'I could not find a relevant answer in the indexed sources.';

    return {
      question,
      answer,
      verdict: top ? 'partial' : 'unknown',
      confidence: confidenceFromEvidence(evidence),
      primaryLocation,
      locations: joinLocations(evidence),
      evidence,
    };
  }

  private answerCodebaseAccess(question: string, limit: number): SearchAnswerResult {
    const rows = this.db
      .prepare(`
        SELECT
          s.id,
          s.name,
          s.root_path AS rootPath,
          s.metadata,
          COUNT(d.id) AS indexedFiles
        FROM federated_sources s
        LEFT JOIN federated_documents d ON d.source_id = s.id
        WHERE s.status = 'active'
        GROUP BY s.id, s.name, s.root_path, s.metadata
        ORDER BY indexedFiles DESC, s.name ASC
      `)
      .all() as RepositoryRow[];

    const activeSources = rows.length;
    const indexedFiles = rows.reduce((total, row) => total + row.indexedFiles, 0);
    const evidence = rows.slice(0, limit).map((row) => {
      const metadata = parseJsonRecord(row.metadata);
      const repoLabel =
        (typeof metadata.repository === 'string' && metadata.repository.trim().length > 0
          ? metadata.repository.trim()
          : undefined) ??
        (typeof metadata.repo === 'string' && metadata.repo.trim().length > 0
          ? metadata.repo.trim()
          : undefined) ??
        basename(row.rootPath);

      return {
        kind: 'repository' as const,
        id: row.id,
        title: repoLabel || row.name,
        snippet: `Indexed ${row.indexedFiles} file(s) from ${row.rootPath}.`,
        score: row.indexedFiles,
        matchedTerms: ['codebase'],
        path: row.rootPath,
        sourceId: row.id,
        sourceName: row.name,
      };
    });

    let answer: string;
    let verdict: SearchAnswerVerdict;
    if (activeSources === 0) {
      answer = 'No. There is no indexed federated code source available in this knowledge base right now.';
      verdict = 'no';
    } else if (indexedFiles === 0) {
      answer = 'Not yet. There are registered code sources, but they do not currently provide indexed files to search.';
      verdict = 'partial';
    } else {
      answer = `Not full live access. I can search ${indexedFiles} indexed file(s) across ${activeSources} active source(s), which is only the indexed subset of the codebase. Unindexed, excluded, binary, or external content is outside that view.`;
      verdict = 'partial';
    }

    return {
      question,
      answer,
      verdict,
      confidence: indexedFiles > 0 ? 'high' : 'medium',
      primaryLocation: evidence[0]?.path,
      locations: joinLocations(evidence),
      evidence,
    };
  }

  private findEvidence(question: string, terms: string[], limit: number): SearchAnswerEvidence[] {
    if (terms.length === 0) {
      return [];
    }

    const candidates = [
      ...this.searchDocuments(question, terms),
      ...this.searchFederatedDocuments(question, terms),
    ];

    return candidates
      .filter((entry) => entry.matchedTerms.length > 0)
      .sort((left, right) => right.score - left.score || left.title.localeCompare(right.title))
      .slice(0, limit);
  }

  private searchDocuments(question: string, terms: string[]): SearchAnswerEvidence[] {
    const whereClause = terms
      .map(() => '(title LIKE ? OR content LIKE ? OR IFNULL(url, \'\') LIKE ? OR IFNULL(metadata, \'\') LIKE ?)')
      .join(' OR ');
    const params = terms.flatMap((term) => {
      const pattern = `%${term}%`;
      return [pattern, pattern, pattern, pattern];
    });

    const rows = this.db
      .prepare(`
        SELECT id, title, content, url, metadata
        FROM documents
        WHERE ${whereClause}
        ORDER BY modified DESC, created DESC
        LIMIT 50
      `)
      .all(...params) as DocumentRow[];

    return rows
      .map((row) => this.scoreDocumentRow(question, terms, row))
      .filter((entry): entry is SearchAnswerEvidence => entry !== null);
  }

  private searchFederatedDocuments(question: string, terms: string[]): SearchAnswerEvidence[] {
    const whereClause = terms
      .map(() => '(d.title LIKE ? OR d.content LIKE ? OR d.path LIKE ? OR IFNULL(d.metadata, \'\') LIKE ?)')
      .join(' OR ');
    const params = terms.flatMap((term) => {
      const pattern = `%${term}%`;
      return [pattern, pattern, pattern, pattern];
    });

    const rows = this.db
      .prepare(`
        SELECT
          d.id,
          d.title,
          d.content,
          d.path,
          d.source_id AS sourceId,
          s.name AS sourceName,
          d.metadata
        FROM federated_documents d
        JOIN federated_sources s ON s.id = d.source_id
        WHERE ${whereClause}
        ORDER BY d.modified_at DESC, d.indexed_at DESC
        LIMIT 50
      `)
      .all(...params) as FederatedDocumentRow[];

    return rows
      .map((row) => this.scoreFederatedDocumentRow(question, terms, row))
      .filter((entry): entry is SearchAnswerEvidence => entry !== null);
  }

  private scoreDocumentRow(
    question: string,
    terms: string[],
    row: DocumentRow,
  ): SearchAnswerEvidence | null {
    const metadata = parseJsonRecord(row.metadata);
    const path = extractDocumentPath(metadata);
    const metadataText = JSON.stringify(metadata);
    const matchedTerms = terms.filter((term) =>
      includesTerm(row.title, term) ||
      includesTerm(row.content, term) ||
      includesTerm(row.url ?? undefined, term) ||
      includesTerm(path, term) ||
      includesTerm(metadataText, term)
    );
    if (matchedTerms.length === 0) {
      return null;
    }

    let score = 0;
    for (const term of matchedTerms) {
      if (includesTerm(row.url ?? undefined, term)) score += 8;
      if (includesTerm(path, term)) score += 7;
      if (includesTerm(row.title, term)) score += 6;
      if (includesTerm(row.content, term)) score += 3;
      if (includesTerm(metadataText, term)) score += 2;
    }
    if (includesTerm(row.content, question.toLowerCase())) score += 10;

    return {
      kind: 'document',
      id: row.id,
      title: row.title,
      snippet: buildSnippet(`${row.title} ${row.content}`, matchedTerms),
      score,
      matchedTerms,
      url: row.url ?? undefined,
      path,
    };
  }

  private scoreFederatedDocumentRow(
    question: string,
    terms: string[],
    row: FederatedDocumentRow,
  ): SearchAnswerEvidence | null {
    const metadata = parseJsonRecord(row.metadata);
    const metadataText = JSON.stringify(metadata);
    const matchedTerms = terms.filter((term) =>
      includesTerm(row.title, term) ||
      includesTerm(row.content, term) ||
      includesTerm(row.path, term) ||
      includesTerm(metadataText, term)
    );
    if (matchedTerms.length === 0) {
      return null;
    }

    let score = 0;
    for (const term of matchedTerms) {
      if (includesTerm(row.path, term)) score += 8;
      if (includesTerm(row.title, term)) score += 6;
      if (includesTerm(row.content, term)) score += 4;
      if (includesTerm(metadataText, term)) score += 2;
    }
    if (includesTerm(row.content, question.toLowerCase())) score += 10;

    return {
      kind: 'federated_document',
      id: row.id,
      title: row.title,
      snippet: buildSnippet(`${row.path} ${row.title} ${row.content}`, matchedTerms),
      score,
      matchedTerms,
      path: row.path,
      sourceId: row.sourceId,
      sourceName: row.sourceName,
    };
  }
}
