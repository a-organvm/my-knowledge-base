/**
 * .orchestrator_state.js — Persistent orchestrator state for multi-agent dispatch.
 *
 * Tracks active agents, pending tasks, completed handoffs, and session context.
 * Read/written by the agent-dispatch CLI and conductor tooling.
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const STATE_FILE = join(import.meta.dirname ?? ".", ".orchestrator_state.json");

const EMPTY_STATE = {
  version: 1,
  session_id: null,
  active_agents: [],
  pending_tasks: [],
  completed: [],
  handoffs: [],
  created_at: null,
  updated_at: null,
};

/**
 * Load the current orchestrator state.
 * @returns {object} State object
 */
export function loadState() {
  if (!existsSync(STATE_FILE)) {
    return { ...EMPTY_STATE, created_at: new Date().toISOString() };
  }
  const raw = readFileSync(STATE_FILE, "utf-8");
  return { ...EMPTY_STATE, ...JSON.parse(raw) };
}

/**
 * Save orchestrator state to disk.
 * @param {object} state - State to persist
 */
export function saveState(state) {
  const data = { ...state, updated_at: new Date().toISOString() };
  writeFileSync(STATE_FILE, JSON.stringify(data, null, 2));
}

/**
 * Register a new active agent.
 * @param {string} agentName - Agent identifier (codex, gemini, opencode, claude)
 * @param {string} taskId - Task being worked
 */
export function registerAgent(agentName, taskId) {
  const state = loadState();
  state.active_agents.push({
    agent: agentName,
    task_id: taskId,
    started_at: new Date().toISOString(),
  });
  saveState(state);
}

/**
 * Mark a task as completed.
 * @param {string} taskId - Completed task ID
 * @param {string} agentName - Agent that completed it
 * @param {object} [result] - Optional result data
 */
export function completeTask(taskId, agentName, result = {}) {
  const state = loadState();
  state.active_agents = state.active_agents.filter((a) => a.task_id !== taskId);
  state.completed.push({
    task_id: taskId,
    agent: agentName,
    completed_at: new Date().toISOString(),
    result,
  });
  saveState(state);
}

export default { loadState, saveState, registerAgent, completeTask };
