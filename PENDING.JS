/**
 * PENDING.JS — Pending items tracker for knowledge base operations.
 *
 * Tracks items awaiting processing: untagged units, orphan relationships,
 * missing embeddings, and queued AI tasks.
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const PENDING_FILE = join(import.meta.dirname ?? ".", ".pending-items.json");

/**
 * @typedef {Object} PendingItem
 * @property {string} id
 * @property {string} type - Item type (untagged, no_embedding, orphan, ai_task)
 * @property {string} description
 * @property {string} priority - P0, P1, P2
 * @property {string} created_at
 */

/**
 * Load pending items from disk.
 * @returns {PendingItem[]}
 */
export function loadPending() {
  if (!existsSync(PENDING_FILE)) return [];
  const raw = readFileSync(PENDING_FILE, "utf-8");
  return JSON.parse(raw);
}

/**
 * Save pending items to disk.
 * @param {PendingItem[]} items
 */
export function savePending(items) {
  writeFileSync(PENDING_FILE, JSON.stringify(items, null, 2));
}

/**
 * Add a pending item.
 * @param {Omit<PendingItem, 'created_at'>} item
 */
export function addPending(item) {
  const items = loadPending();
  items.push({
    ...item,
    created_at: new Date().toISOString(),
  });
  savePending(items);
}

/**
 * Remove a pending item by ID.
 * @param {string} id
 * @returns {boolean} Whether the item was found and removed
 */
export function removePending(id) {
  const items = loadPending();
  const filtered = items.filter((item) => item.id !== id);
  if (filtered.length === items.length) return false;
  savePending(filtered);
  return true;
}

/**
 * Get pending items by type.
 * @param {string} type
 * @returns {PendingItem[]}
 */
export function getPendingByType(type) {
  return loadPending().filter((item) => item.type === type);
}

/**
 * Get a summary of pending items.
 * @returns {{ total: number, byType: Record<string, number>, byPriority: Record<string, number> }}
 */
export function getPendingSummary() {
  const items = loadPending();
  const byType = {};
  const byPriority = {};

  for (const item of items) {
    byType[item.type] = (byType[item.type] || 0) + 1;
    byPriority[item.priority] = (byPriority[item.priority] || 0) + 1;
  }

  return { total: items.length, byType, byPriority };
}

export default { loadPending, savePending, addPending, removePending, getPendingByType, getPendingSummary };
