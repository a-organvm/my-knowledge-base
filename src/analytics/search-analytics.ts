/**
 * Search Analytics Tracker - Track search queries and performance
 * Logs all searches for analytics, trending, and quality measurement
 */

import { logger } from '../logger.js';
import Database from 'better-sqlite3';

export interface SearchQuery {
  id: string;
  query: string;
  normalizedQuery: string;
  searchType: 'fts' | 'semantic' | 'hybrid' | 'federated';
  timestamp: string;
  latencyMs: number;
  resultCount: number;
  userSession?: string;
  filters?: string;
  clickedResult?: string;
  metadata?: string;
}

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

function firstString(values: unknown[]): string | undefined {
  for (const value of values) {
    if (typeof value === 'string' && value.trim().length > 0) {
      return value.trim();
    }
  }
  return undefined;
}

function extractRepoFromFilters(filters: unknown): string | undefined {
  if (!filters) return undefined;

  if (Array.isArray(filters)) {
    for (const entry of filters) {
      if (!entry || typeof entry !== 'object') continue;
      const record = entry as Record<string, unknown>;
      const field = typeof record.field === 'string' ? record.field.trim().toLowerCase() : '';
      if (['repo', 'repository', 'source', 'sourceid', 'sourcename'].includes(field)) {
        const value = firstString([record.value]);
        if (value) return value;
      }
    }
    return undefined;
  }

  if (typeof filters === 'object') {
    const record = filters as Record<string, unknown>;
    return firstString([
      record.repository,
      record.repo,
      record.repoName,
      record.sourceName,
      record.sourceId,
      record.source,
    ]);
  }

  return undefined;
}

function extractRepositoryLabel(row: { metadata: string | null; filters: string | null }): string | undefined {
  const metadata = parseJsonRecord(row.metadata);
  const metadataRepo = firstString([
    metadata.repository,
    metadata.repo,
    metadata.repoName,
    metadata.sourceName,
    metadata.sourceId,
  ]);
  if (metadataRepo) {
    return metadataRepo;
  }

  const filters = parseJsonRecord(row.filters);
  return extractRepoFromFilters(filters);
}

/**
 * SearchAnalyticsTracker - Track search activity
 */
export class SearchAnalyticsTracker {
  private db: Database.Database;

  constructor(dbPathOrInstance: string | Database.Database = './db/knowledge.db') {
    this.db =
      typeof dbPathOrInstance === 'string' ? new Database(dbPathOrInstance) : dbPathOrInstance;
    this.ensureMetadataColumn();
  }

  private hasSearchQueryColumn(columnName: string): boolean {
    try {
      const columns = this.db.prepare('PRAGMA table_info(search_queries)').all() as Array<{ name: string }>;
      return columns.some((column) => column.name === columnName);
    } catch {
      return false;
    }
  }

  private ensureMetadataColumn(): void {
    if (this.hasSearchQueryColumn('metadata')) {
      return;
    }

    try {
      this.db.exec('ALTER TABLE search_queries ADD COLUMN metadata TEXT');
    } catch (error) {
      logger.debug('Search analytics metadata column already available or could not be added', {
        reason: error instanceof Error ? error.message : String(error),
      });
    }
  }

  /**
   * Track a search query
   */
  trackQuery(options: {
    query: string;
    searchType: 'fts' | 'semantic' | 'hybrid' | 'federated';
    latencyMs?: number;
    latency?: number;
    resultCount?: number;
    userSession?: string;
    filters?: Record<string, any>;
    metadata?: Record<string, unknown>;
  }): string | null {
    try {
      const normalized = options.query
        .toLowerCase()
        .trim()
        .replace(/\s+/g, ' ');
      const id = 'query_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      const latencyMs = options.latencyMs ?? options.latency ?? 0;
      const resultCount = options.resultCount ?? 0;

      const stmt = this.db.prepare(`
        INSERT INTO search_queries
        (id, query, normalized_query, search_type, timestamp, latency_ms, result_count, user_session, filters, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run(
        id,
        options.query,
        normalized,
        options.searchType,
        new Date().toISOString(),
        latencyMs,
        resultCount,
        options.userSession || null,
        options.filters ? JSON.stringify(options.filters) : null,
        options.metadata ? JSON.stringify(options.metadata) : null,
      );

      logger.debug('Tracked search: ' + options.searchType + ' query: ' + options.query);
      return id;
    } catch (error) {
      logger.error('Failed to track query: ' + error);
      return null;
    }
  }

  /**
   * Track a result click
   */
  trackClick(queryId: string, resultId: string): void {
    try {
      const stmt = this.db.prepare(`
        UPDATE search_queries SET clicked_result = ? WHERE id = ?
      `);

      stmt.run(resultId, queryId);
    } catch (error) {
      logger.error('Failed to track click: ' + error);
    }
  }

  /**
   * Get popular queries in time window
   */
  getPopularQueries(options: { windowDays?: number; limit?: number } = {}): Array<{
    query: string;
    count: number;
    avgLatency: number;
    avgResults: number;
  }> {
    try {
      const windowDays = options.windowDays ?? 7;
      const limit = options.limit ?? 20;
      const minDate = new Date(
        Date.now() - windowDays * 24 * 60 * 60 * 1000
      ).toISOString();

      const stmt = this.db.prepare(`
        SELECT
          query,
          COUNT(*) as count,
          AVG(latency_ms) as avgLatency,
          AVG(result_count) as avgResults
        FROM search_queries
        WHERE timestamp >= ?
        GROUP BY normalized_query
        ORDER BY count DESC
        LIMIT ?
      `);

      return stmt.all(minDate, limit) as Array<{
        query: string;
        count: number;
        avgLatency: number;
        avgResults: number;
      }>;
    } catch (error) {
      logger.error('Failed to get popular queries: ' + error);
      return [];
    }
  }

  /**
   * Get search statistics
   */
  getStatistics(days: number = 7): {
    totalQueries: number;
    uniqueQueries: number;
    avgLatency: number;
    avgResults: number;
    byType: Record<string, { count: number; avgLatency: number }>;
  } {
    try {
      const minDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

      const totalStmt = this.db.prepare(`
        SELECT
          COUNT(*) as total,
          COUNT(DISTINCT normalized_query) as unique,
          AVG(latency_ms) as avgLatency,
          AVG(result_count) as avgResults
        FROM search_queries
        WHERE timestamp >= ?
      `);

      const totalResult = totalStmt.get(minDate) as {
        total: number;
        unique: number;
        avgLatency: number;
        avgResults: number;
      };

      const byTypeStmt = this.db.prepare(`
        SELECT
          search_type,
          COUNT(*) as count,
          AVG(latency_ms) as avgLatency
        FROM search_queries
        WHERE timestamp >= ?
        GROUP BY search_type
      `);

      const byType: Record<string, { count: number; avgLatency: number }> = {};

      const typeResults = byTypeStmt.all(minDate) as Array<{
        search_type: string;
        count: number;
        avgLatency: number;
      }>;

      for (const result of typeResults) {
        byType[result.search_type] = {
          count: result.count,
          avgLatency: result.avgLatency
        };
      }

      return {
        totalQueries: totalResult.total,
        uniqueQueries: totalResult.unique,
        avgLatency: totalResult.avgLatency,
        avgResults: totalResult.avgResults,
        byType
      };
    } catch (error) {
      logger.error('Failed to get statistics: ' + error);
      return {
        totalQueries: 0,
        uniqueQueries: 0,
        avgLatency: 0,
        avgResults: 0,
        byType: {}
      };
    }
  }

  getRepoBreakdown(options: { windowDays?: number; limit?: number } = {}): Array<{
    repo: string;
    count: number;
    avgLatency: number;
    avgResults: number;
  }> {
    try {
      const windowDays = options.windowDays ?? 7;
      const limit = options.limit ?? 20;
      const minDate = new Date(Date.now() - windowDays * 24 * 60 * 60 * 1000).toISOString();
      const rows = this.db
        .prepare(`
          SELECT metadata, filters, latency_ms, result_count
          FROM search_queries
          WHERE timestamp >= ?
        `)
        .all(minDate) as Array<{
          metadata: string | null;
          filters: string | null;
          latency_ms: number | null;
          result_count: number | null;
        }>;

      const byRepo = new Map<string, { count: number; latencyTotal: number; resultTotal: number }>();
      for (const row of rows) {
        const repo = extractRepositoryLabel(row);
        if (!repo) continue;

        const current = byRepo.get(repo) ?? {
          count: 0,
          latencyTotal: 0,
          resultTotal: 0,
        };
        current.count += 1;
        current.latencyTotal += row.latency_ms ?? 0;
        current.resultTotal += row.result_count ?? 0;
        byRepo.set(repo, current);
      }

      return Array.from(byRepo.entries())
        .map(([repo, stats]) => ({
          repo,
          count: stats.count,
          avgLatency: stats.count > 0 ? stats.latencyTotal / stats.count : 0,
          avgResults: stats.count > 0 ? stats.resultTotal / stats.count : 0,
        }))
        .sort((a, b) => b.count - a.count || a.repo.localeCompare(b.repo))
        .slice(0, limit);
    } catch (error) {
      logger.error('Failed to get repo breakdown: ' + error);
      return [];
    }
  }

  /**
   * Get query metrics for a window
   */
  getQueryMetrics(options: { windowDays?: number } = {}): {
    totalQueries: number;
    avgLatency: number;
    bySearchType: Record<string, number>;
  } {
    try {
      const windowDays = options.windowDays ?? 7;
      const minDate = new Date(Date.now() - windowDays * 24 * 60 * 60 * 1000).toISOString();

      const totalStmt = this.db.prepare(`
        SELECT COUNT(*) as total, AVG(latency_ms) as avgLatency
        FROM search_queries
        WHERE timestamp >= ?
      `);

      const totalResult = totalStmt.get(minDate) as {
        total: number;
        avgLatency: number;
      };

      const byTypeStmt = this.db.prepare(`
        SELECT search_type, COUNT(*) as count
        FROM search_queries
        WHERE timestamp >= ?
        GROUP BY search_type
      `);

      const typeRows = byTypeStmt.all(minDate) as Array<{
        search_type: string;
        count: number;
      }>;

      const bySearchType: Record<string, number> = {};
      for (const row of typeRows) {
        bySearchType[row.search_type] = row.count;
      }

      return {
        totalQueries: totalResult.total ?? 0,
        avgLatency: totalResult.avgLatency ?? 0,
        bySearchType
      };
    } catch (error) {
      logger.error('Failed to get query metrics: ' + error);
      return {
        totalQueries: 0,
        avgLatency: 0,
        bySearchType: {}
      };
    }
  }

  /**
   * Clean up old queries
   */
  cleanupOldQueries(daysToKeep: number = 90): number {
    try {
      const minDate = new Date(Date.now() - daysToKeep * 24 * 60 * 60 * 1000).toISOString();

      const stmt = this.db.prepare(`
        DELETE FROM search_queries WHERE timestamp < ?
      `);

      const result = stmt.run(minDate);
      const deleted = result.changes || 0;

      logger.info('Cleaned up ' + deleted + ' old queries');
      return deleted;
    } catch (error) {
      logger.error('Failed to cleanup queries: ' + error);
      return 0;
    }
  }
}

export function createAnalyticsTracker(dbPath?: string): SearchAnalyticsTracker {
  return new SearchAnalyticsTracker(dbPath);
}
