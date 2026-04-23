/**
 * DogTaleDaily.jsx — Daily dog tale/story component for the knowledge base UI.
 *
 * Displays a rotating daily story or insight from the knowledge base,
 * themed around discovery and exploration.
 */

import React, { useState, useEffect } from "react";

/**
 * @param {Object} props
 * @param {string} [props.apiBase] - API base URL
 * @param {string} [props.category] - Category filter for daily content
 */
export function DogTaleDaily({ apiBase = "/api", category = "general" }) {
  const [tale, setTale] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10);
    const cacheKey = `dogtale-${today}-${category}`;

    // Check session cache first
    const cached = sessionStorage.getItem(cacheKey);
    if (cached) {
      setTale(JSON.parse(cached));
      setLoading(false);
      return;
    }

    fetch(`${apiBase}/units/random?category=${category}&limit=1`)
      .then((res) => res.json())
      .then((data) => {
        const unit = data.data?.[0] || data[0] || null;
        if (unit) {
          setTale(unit);
          sessionStorage.setItem(cacheKey, JSON.stringify(unit));
        }
      })
      .catch((err) => console.error("DogTaleDaily fetch error:", err))
      .finally(() => setLoading(false));
  }, [apiBase, category]);

  if (loading) {
    return (
      <div className="dogtale-container loading">
        <p>Sniffing out today's knowledge...</p>
      </div>
    );
  }

  if (!tale) {
    return (
      <div className="dogtale-container empty">
        <p>No tales to tell today. Add some knowledge units!</p>
      </div>
    );
  }

  return (
    <div className="dogtale-container">
      <header className="dogtale-header">
        <h3>Daily Discovery</h3>
        <span className="dogtale-type">{tale.type}</span>
      </header>
      <div className="dogtale-content">
        <h4>{tale.title}</h4>
        <p>{tale.content}</p>
      </div>
      {tale.tags && tale.tags.length > 0 && (
        <div className="dogtale-tags">
          {tale.tags.map((tag) => (
            <span key={tag} className="tag">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default DogTaleDaily;
