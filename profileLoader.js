/**
 * profileLoader.js — Loads and merges user profile data for the knowledge base.
 *
 * Profiles define per-user preferences, search history, bookmarks, and
 * custom tag sets. Stored in the profile/ directory as JSON files.
 */

import { readFileSync, existsSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const PROFILE_DIR = join(import.meta.dirname ?? ".", "profile");
const DEFAULT_PROFILE = {
  version: 1,
  name: "default",
  preferences: {
    searchMode: "hybrid",
    resultsPerPage: 20,
    theme: "system",
    showRelationships: true,
  },
  bookmarks: [],
  recentSearches: [],
  customTags: [],
  createdAt: null,
  updatedAt: null,
};

/**
 * Load a user profile by name.
 * @param {string} name - Profile name (filename without .json)
 * @returns {object} Merged profile with defaults
 */
export function loadProfile(name = "default") {
  const filePath = join(PROFILE_DIR, `${name}.json`);
  if (!existsSync(filePath)) {
    return { ...DEFAULT_PROFILE, name, createdAt: new Date().toISOString() };
  }
  const raw = readFileSync(filePath, "utf-8");
  const stored = JSON.parse(raw);
  return {
    ...DEFAULT_PROFILE,
    ...stored,
    preferences: { ...DEFAULT_PROFILE.preferences, ...stored.preferences },
  };
}

/**
 * Save a user profile.
 * @param {object} profile - Profile object to persist
 */
export function saveProfile(profile) {
  if (!existsSync(PROFILE_DIR)) {
    mkdirSync(PROFILE_DIR, { recursive: true });
  }
  const filePath = join(PROFILE_DIR, `${profile.name || "default"}.json`);
  const data = { ...profile, updatedAt: new Date().toISOString() };
  writeFileSync(filePath, JSON.stringify(data, null, 2));
}

/**
 * Add a search query to the profile's recent history.
 * @param {object} profile - Profile object
 * @param {string} query - Search query string
 * @param {number} [maxRecent=50] - Maximum recent searches to keep
 * @returns {object} Updated profile
 */
export function addRecentSearch(profile, query, maxRecent = 50) {
  const updated = { ...profile };
  updated.recentSearches = [
    { query, timestamp: new Date().toISOString() },
    ...(updated.recentSearches || []).filter((s) => s.query !== query),
  ].slice(0, maxRecent);
  return updated;
}

/**
 * List all available profile names.
 * @returns {string[]}
 */
export function listProfiles() {
  if (!existsSync(PROFILE_DIR)) return ["default"];
  const { readdirSync } = await import("node:fs");
  return readdirSync(PROFILE_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""));
}

export default { loadProfile, saveProfile, addRecentSearch, listProfiles };
