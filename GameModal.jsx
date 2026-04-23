/**
 * GameModal.jsx — Gamification modal for knowledge base engagement.
 *
 * Displays achievement badges, streaks, exploration progress,
 * and knowledge graph completion metrics as game-like elements.
 */

import React, { useState, useEffect } from "react";

const ACHIEVEMENTS = [
  { id: "first-search", name: "First Search", description: "Performed your first search", icon: "magnifier" },
  { id: "tag-master", name: "Tag Master", description: "Tagged 100 units", icon: "label" },
  { id: "deep-dive", name: "Deep Dive", description: "Explored 10 related units in one session", icon: "layers" },
  { id: "connector", name: "Connector", description: "Created 50 relationships", icon: "link" },
  { id: "completionist", name: "Completionist", description: "All units have tags and categories", icon: "check" },
];

/**
 * @param {Object} props
 * @param {boolean} props.isOpen
 * @param {Function} props.onClose
 * @param {Object} [props.userStats] - Pre-loaded user statistics
 */
export function GameModal({ isOpen, onClose, userStats = {} }) {
  const [stats, setStats] = useState(userStats);

  useEffect(() => {
    if (!isOpen || Object.keys(userStats).length > 0) return;
    // Load stats from API if not provided
    fetch("/api/stats")
      .then((res) => res.json())
      .then((data) => setStats(data.data || data))
      .catch(console.error);
  }, [isOpen, userStats]);

  if (!isOpen) return null;

  const totalUnits = stats.totalUnits || 0;
  const taggedPct = totalUnits > 0 ? Math.round(((stats.taggedUnits || 0) / totalUnits) * 100) : 0;
  const level = Math.floor(Math.log2(Math.max(totalUnits, 1)) + 1);

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-content game-modal" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <h2>Knowledge Quest</h2>
          <button onClick={onClose} aria-label="Close" className="modal-close">&times;</button>
        </header>

        <div className="modal-body">
          <div className="game-level">
            <span className="level-badge">Level {level}</span>
            <span className="level-title">{getLevelTitle(level)}</span>
          </div>

          <div className="game-stats">
            <div className="stat">
              <span className="stat-value">{totalUnits}</span>
              <span className="stat-label">Knowledge Units</span>
            </div>
            <div className="stat">
              <span className="stat-value">{taggedPct}%</span>
              <span className="stat-label">Tagged</span>
            </div>
            <div className="stat">
              <span className="stat-value">{stats.totalRelationships || 0}</span>
              <span className="stat-label">Connections</span>
            </div>
          </div>

          <div className="achievements">
            <h3>Achievements</h3>
            {ACHIEVEMENTS.map((a) => (
              <div key={a.id} className={`achievement ${isUnlocked(a.id, stats) ? "unlocked" : "locked"}`}>
                <span className="achievement-icon">{a.icon}</span>
                <div>
                  <strong>{a.name}</strong>
                  <p>{a.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function getLevelTitle(level) {
  const titles = ["Novice", "Apprentice", "Scholar", "Expert", "Master", "Sage", "Oracle", "Omniscient"];
  return titles[Math.min(level - 1, titles.length - 1)] || "Transcendent";
}

function isUnlocked(achievementId, stats) {
  switch (achievementId) {
    case "first-search": return (stats.totalSearches || 0) >= 1;
    case "tag-master": return (stats.taggedUnits || 0) >= 100;
    case "deep-dive": return (stats.maxSessionDepth || 0) >= 10;
    case "connector": return (stats.totalRelationships || 0) >= 50;
    case "completionist": return (stats.untaggedUnits || 1) === 0;
    default: return false;
  }
}

export default GameModal;
