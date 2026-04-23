/**
 * AnalyticsModal.jsx — Modal component for knowledge base analytics display.
 *
 * Shows usage statistics, search patterns, tag distributions,
 * and knowledge graph density metrics.
 */

import React, { useState, useEffect } from "react";

/**
 * @param {Object} props
 * @param {boolean} props.isOpen - Whether the modal is visible
 * @param {Function} props.onClose - Close handler
 * @param {string} [props.apiBase] - API base URL
 */
export function AnalyticsModal({ isOpen, onClose, apiBase = "/api" }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    setError(null);

    fetch(`${apiBase}/stats`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setStats(data.data || data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [isOpen, apiBase]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <h2>Knowledge Base Analytics</h2>
          <button onClick={onClose} aria-label="Close" className="modal-close">
            &times;
          </button>
        </header>

        <div className="modal-body">
          {loading && <p className="loading">Loading analytics...</p>}
          {error && <p className="error">Error: {error}</p>}
          {stats && (
            <div className="analytics-grid">
              <StatCard label="Total Units" value={stats.totalUnits ?? 0} />
              <StatCard label="Conversations" value={stats.totalConversations ?? 0} />
              <StatCard label="Tags" value={stats.totalTags ?? 0} />
              <StatCard label="Relationships" value={stats.totalRelationships ?? 0} />
              <StatCard label="Insights" value={stats.insightCount ?? 0} />
              <StatCard label="Code Blocks" value={stats.codeCount ?? 0} />

              {stats.topTags && (
                <div className="stat-section">
                  <h3>Top Tags</h3>
                  <ul>
                    {stats.topTags.map((tag) => (
                      <li key={tag.name}>
                        <span className="tag-name">{tag.name}</span>
                        <span className="tag-count">{tag.count}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {stats.categoryDistribution && (
                <div className="stat-section">
                  <h3>Categories</h3>
                  <ul>
                    {Object.entries(stats.categoryDistribution).map(([cat, count]) => (
                      <li key={cat}>
                        <span className="cat-name">{cat}</span>
                        <span className="cat-count">{count}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{typeof value === "number" ? value.toLocaleString() : value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export default AnalyticsModal;
