/**
 * scene-manager.js — OBS/streaming scene management for knowledge base presentations.
 *
 * Manages scene configurations for live-streaming knowledge base dashboards
 * and presentations. Reads from configs/obs/ and provides programmatic
 * scene switching via OBS WebSocket protocol.
 */

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const SCENE_CONFIG_DIR = join(import.meta.dirname ?? ".", "configs", "obs");

/**
 * @typedef {Object} Scene
 * @property {string} name - Scene name
 * @property {string} type - Scene type (dashboard, presentation, overlay)
 * @property {Object[]} sources - OBS sources in this scene
 * @property {boolean} active - Whether this scene is currently active
 */

/**
 * Load a scene configuration from the OBS configs directory.
 * @param {string} sceneName - Name of the scene config file (without extension)
 * @returns {Scene|null}
 */
export function loadScene(sceneName) {
  const filePath = join(SCENE_CONFIG_DIR, `${sceneName}.json`);
  if (!existsSync(filePath)) {
    console.warn(`Scene config not found: ${filePath}`);
    return null;
  }
  const raw = readFileSync(filePath, "utf-8");
  return JSON.parse(raw);
}

/**
 * Get the default studio scene configuration.
 * @returns {Scene}
 */
export function getDefaultScene() {
  const loaded = loadScene("studio-scene");
  if (loaded) return loaded;

  // Fallback default
  return {
    name: "Knowledge Base Studio",
    type: "dashboard",
    sources: [
      { name: "browser-source", type: "browser", url: "http://localhost:3000", width: 1920, height: 1080 },
      { name: "webcam", type: "video_capture", device: "default" },
      { name: "overlay", type: "image", path: "" },
    ],
    active: false,
  };
}

/**
 * Generate an OBS scene collection export from configurations.
 * @param {string[]} sceneNames - Scene config names to include
 * @returns {Object} OBS-compatible scene collection JSON
 */
export function buildSceneCollection(sceneNames) {
  const scenes = sceneNames
    .map(loadScene)
    .filter(Boolean);

  return {
    name: "Knowledge Base Scenes",
    scenes,
    current_scene: scenes[0]?.name || "Default",
    exported_at: new Date().toISOString(),
  };
}

export default { loadScene, getDefaultScene, buildSceneCollection };
