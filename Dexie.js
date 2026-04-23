/**
 * Dexie.js — IndexedDB wrapper using Dexie for client-side knowledge base storage.
 *
 * Provides offline-capable storage for atomic units, search history,
 * and cached embeddings in the browser using IndexedDB via Dexie.
 */

// Dexie is expected to be installed: npm install dexie

/**
 * Initialize the knowledge base IndexedDB schema.
 * @param {import('dexie').Dexie} Dexie - Dexie constructor
 * @returns {import('dexie').Dexie} Configured database instance
 */
export function createKnowledgeDB(Dexie) {
  const db = new Dexie("KnowledgeBase");

  db.version(1).stores({
    units: "id, type, category, *tags, created_at, updated_at",
    conversations: "id, title, source, created_at",
    tags: "id, &name, count",
    relationships: "id, source_id, target_id, type",
    searchHistory: "++id, query, timestamp, mode",
    cachedEmbeddings: "unit_id, model, created_at",
    syncQueue: "++id, action, entity_type, entity_id, timestamp",
  });

  return db;
}

/**
 * Sync local IndexedDB data with the remote API.
 * @param {import('dexie').Dexie} db - Dexie database instance
 * @param {string} apiBase - API base URL
 * @returns {Promise<{ synced: number, failed: number }>}
 */
export async function syncWithRemote(db, apiBase = "/api") {
  const queue = await db.syncQueue.toArray();
  let synced = 0;
  let failed = 0;

  for (const item of queue) {
    try {
      const endpoint = `${apiBase}/${item.entity_type}s/${item.entity_id}`;
      const method = item.action === "delete" ? "DELETE" : item.action === "create" ? "POST" : "PUT";

      let body = undefined;
      if (method !== "DELETE") {
        const entity = await db[`${item.entity_type}s`]?.get(item.entity_id);
        if (entity) body = JSON.stringify(entity);
      }

      const res = await fetch(
        method === "POST" ? `${apiBase}/${item.entity_type}s` : endpoint,
        {
          method,
          headers: { "Content-Type": "application/json" },
          body,
        }
      );

      if (res.ok) {
        await db.syncQueue.delete(item.id);
        synced++;
      } else {
        failed++;
      }
    } catch {
      failed++;
    }
  }

  return { synced, failed };
}

/**
 * Add a search to the local history.
 * @param {import('dexie').Dexie} db
 * @param {string} query
 * @param {string} mode - Search mode used
 */
export async function addSearchHistory(db, query, mode = "hybrid") {
  await db.searchHistory.add({
    query,
    mode,
    timestamp: new Date().toISOString(),
  });

  // Keep only last 200 searches
  const count = await db.searchHistory.count();
  if (count > 200) {
    const oldest = await db.searchHistory.orderBy("id").limit(count - 200).toArray();
    await db.searchHistory.bulkDelete(oldest.map((s) => s.id));
  }
}

export default { createKnowledgeDB, syncWithRemote, addSearchHistory };
