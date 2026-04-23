/**
 * VectorManager.ts — Vector embedding management for the CCE (Conversation Corpus Engine).
 *
 * Handles vector storage, retrieval, similarity search, and index management
 * for the knowledge base embedding pipeline.
 */

export interface VectorEntry {
  id: string;
  embedding: number[];
  metadata: Record<string, unknown>;
  createdAt: string;
}

export interface SimilarityResult {
  id: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface VectorManagerConfig {
  dimensions: number;
  distanceMetric: "cosine" | "euclidean" | "dot";
  maxEntries: number;
}

const DEFAULT_CONFIG: VectorManagerConfig = {
  dimensions: 1536, // OpenAI text-embedding-3-small
  distanceMetric: "cosine",
  maxEntries: 100_000,
};

export class VectorManager {
  private config: VectorManagerConfig;
  private entries: Map<string, VectorEntry>;

  constructor(config: Partial<VectorManagerConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.entries = new Map();
  }

  /**
   * Add a vector entry.
   */
  add(id: string, embedding: number[], metadata: Record<string, unknown> = {}): void {
    if (embedding.length !== this.config.dimensions) {
      throw new Error(
        `Embedding dimension mismatch: expected ${this.config.dimensions}, got ${embedding.length}`
      );
    }
    if (this.entries.size >= this.config.maxEntries) {
      throw new Error(`Maximum entries (${this.config.maxEntries}) reached`);
    }
    this.entries.set(id, {
      id,
      embedding,
      metadata,
      createdAt: new Date().toISOString(),
    });
  }

  /**
   * Remove a vector entry by ID.
   */
  remove(id: string): boolean {
    return this.entries.delete(id);
  }

  /**
   * Get a vector entry by ID.
   */
  get(id: string): VectorEntry | undefined {
    return this.entries.get(id);
  }

  /**
   * Find the most similar vectors to the query embedding.
   */
  search(queryEmbedding: number[], topK = 10): SimilarityResult[] {
    if (queryEmbedding.length !== this.config.dimensions) {
      throw new Error(
        `Query dimension mismatch: expected ${this.config.dimensions}, got ${queryEmbedding.length}`
      );
    }

    const scored: SimilarityResult[] = [];

    for (const entry of this.entries.values()) {
      const score = this.computeSimilarity(queryEmbedding, entry.embedding);
      scored.push({ id: entry.id, score, metadata: entry.metadata });
    }

    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, topK);
  }

  /**
   * Get the total number of stored vectors.
   */
  get size(): number {
    return this.entries.size;
  }

  /**
   * Clear all stored vectors.
   */
  clear(): void {
    this.entries.clear();
  }

  /**
   * Compute similarity between two vectors using the configured metric.
   */
  private computeSimilarity(a: number[], b: number[]): number {
    switch (this.config.distanceMetric) {
      case "cosine":
        return this.cosineSimilarity(a, b);
      case "dot":
        return this.dotProduct(a, b);
      case "euclidean":
        return 1 / (1 + this.euclideanDistance(a, b));
      default:
        return this.cosineSimilarity(a, b);
    }
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    let dot = 0;
    let normA = 0;
    let normB = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    const denom = Math.sqrt(normA) * Math.sqrt(normB);
    return denom === 0 ? 0 : dot / denom;
  }

  private dotProduct(a: number[], b: number[]): number {
    let sum = 0;
    for (let i = 0; i < a.length; i++) {
      sum += a[i] * b[i];
    }
    return sum;
  }

  private euclideanDistance(a: number[], b: number[]): number {
    let sum = 0;
    for (let i = 0; i < a.length; i++) {
      const diff = a[i] - b[i];
      sum += diff * diff;
    }
    return Math.sqrt(sum);
  }
}

export default VectorManager;
