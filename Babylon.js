/**
 * Babylon.js — BabylonJS integration module for 3D knowledge graph visualization.
 *
 * Provides scene setup, node rendering, and camera controls for
 * immersive 3D exploration of knowledge base relationships.
 */

/**
 * BabylonJS is loaded from CDN. This module provides helper functions
 * for creating and managing 3D knowledge graph scenes.
 */

const BABYLON_CDN = "https://cdn.babylonjs.com/babylon.js";
const BABYLON_LOADERS_CDN = "https://cdn.babylonjs.com/loaders/babylonjs.loaders.min.js";

/**
 * @typedef {Object} GraphNode3D
 * @property {string} id - Unit ID
 * @property {string} label - Display label
 * @property {string} type - Unit type (insight, code, question, etc.)
 * @property {number[]} position - [x, y, z] coordinates
 * @property {number} size - Node size based on connections
 */

/**
 * @typedef {Object} GraphEdge3D
 * @property {string} source - Source node ID
 * @property {string} target - Target node ID
 * @property {number} weight - Edge weight/strength
 */

/**
 * Color palette for unit types in the 3D graph.
 */
export const TYPE_COLORS = {
  insight: [0.2, 0.6, 1.0],     // Blue
  code: [0.2, 0.8, 0.4],        // Green
  question: [1.0, 0.8, 0.2],    // Yellow
  reference: [0.8, 0.4, 1.0],   // Purple
  decision: [1.0, 0.4, 0.2],    // Orange
};

/**
 * Create a 3D scene for knowledge graph visualization.
 * Requires BabylonJS to be loaded globally.
 *
 * @param {HTMLCanvasElement} canvas - Canvas element to render into
 * @param {GraphNode3D[]} nodes - Graph nodes
 * @param {GraphEdge3D[]} edges - Graph edges
 * @returns {Object} Scene controller with update/dispose methods
 */
export function createGraphScene(canvas, nodes = [], edges = []) {
  if (typeof BABYLON === "undefined") {
    console.error("BabylonJS not loaded. Include from:", BABYLON_CDN);
    return null;
  }

  const engine = new BABYLON.Engine(canvas, true);
  const scene = new BABYLON.Scene(engine);

  // Camera
  const camera = new BABYLON.ArcRotateCamera(
    "camera",
    -Math.PI / 2,
    Math.PI / 4,
    50,
    BABYLON.Vector3.Zero(),
    scene
  );
  camera.attachControl(canvas, true);
  camera.wheelPrecision = 10;

  // Light
  new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), scene);

  // Render nodes
  const nodeMeshes = new Map();
  for (const node of nodes) {
    const sphere = BABYLON.MeshBuilder.CreateSphere(
      `node-${node.id}`,
      { diameter: node.size || 1 },
      scene
    );
    const [x, y, z] = node.position || [0, 0, 0];
    sphere.position = new BABYLON.Vector3(x, y, z);

    const mat = new BABYLON.StandardMaterial(`mat-${node.id}`, scene);
    const [r, g, b] = TYPE_COLORS[node.type] || [0.5, 0.5, 0.5];
    mat.diffuseColor = new BABYLON.Color3(r, g, b);
    sphere.material = mat;

    nodeMeshes.set(node.id, sphere);
  }

  // Render edges
  for (const edge of edges) {
    const sourceMesh = nodeMeshes.get(edge.source);
    const targetMesh = nodeMeshes.get(edge.target);
    if (!sourceMesh || !targetMesh) continue;

    BABYLON.MeshBuilder.CreateLines(
      `edge-${edge.source}-${edge.target}`,
      { points: [sourceMesh.position, targetMesh.position] },
      scene
    );
  }

  // Start render loop
  engine.runRenderLoop(() => scene.render());

  // Handle resize
  const resizeHandler = () => engine.resize();
  window.addEventListener("resize", resizeHandler);

  return {
    scene,
    engine,
    camera,
    dispose() {
      window.removeEventListener("resize", resizeHandler);
      engine.dispose();
    },
    focusNode(id) {
      const mesh = nodeMeshes.get(id);
      if (mesh) camera.setTarget(mesh.position);
    },
  };
}

export default { createGraphScene, TYPE_COLORS, BABYLON_CDN };
