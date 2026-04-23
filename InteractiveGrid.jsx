/**
 * InteractiveGrid.jsx — Interactive grid display for knowledge units.
 *
 * Renders atomic units in a filterable, sortable grid with
 * drag-and-drop reordering and inline editing support.
 */

import React, { useState, useMemo, useCallback } from "react";

const SORT_OPTIONS = [
  { value: "date-desc", label: "Newest first" },
  { value: "date-asc", label: "Oldest first" },
  { value: "title-asc", label: "Title A-Z" },
  { value: "title-desc", label: "Title Z-A" },
  { value: "type", label: "By type" },
];

/**
 * @param {Object} props
 * @param {Array} props.units - Array of atomic unit objects
 * @param {Function} [props.onUnitClick] - Click handler for a unit
 * @param {Function} [props.onTagClick] - Click handler for a tag
 * @param {number} [props.columns] - Number of grid columns
 */
export function InteractiveGrid({ units = [], onUnitClick, onTagClick, columns = 3 }) {
  const [filter, setFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [sortBy, setSortBy] = useState("date-desc");

  const filteredUnits = useMemo(() => {
    let result = [...units];

    if (filter) {
      const q = filter.toLowerCase();
      result = result.filter(
        (u) =>
          u.title?.toLowerCase().includes(q) ||
          u.content?.toLowerCase().includes(q) ||
          u.tags?.some((t) => t.toLowerCase().includes(q))
      );
    }

    if (typeFilter !== "all") {
      result = result.filter((u) => u.type === typeFilter);
    }

    result.sort((a, b) => {
      switch (sortBy) {
        case "date-desc": return new Date(b.timestamp || 0) - new Date(a.timestamp || 0);
        case "date-asc": return new Date(a.timestamp || 0) - new Date(b.timestamp || 0);
        case "title-asc": return (a.title || "").localeCompare(b.title || "");
        case "title-desc": return (b.title || "").localeCompare(a.title || "");
        case "type": return (a.type || "").localeCompare(b.type || "");
        default: return 0;
      }
    });

    return result;
  }, [units, filter, typeFilter, sortBy]);

  const handleUnitClick = useCallback(
    (unit) => {
      if (onUnitClick) onUnitClick(unit);
    },
    [onUnitClick]
  );

  return (
    <div className="interactive-grid">
      <div className="grid-controls">
        <input
          type="search"
          placeholder="Filter units..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="grid-search"
        />
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
          <option value="all">All types</option>
          <option value="insight">Insights</option>
          <option value="code">Code</option>
          <option value="question">Questions</option>
          <option value="reference">References</option>
          <option value="decision">Decisions</option>
        </select>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <span className="grid-count">{filteredUnits.length} units</span>
      </div>

      <div
        className="grid-container"
        style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
      >
        {filteredUnits.map((unit) => (
          <div
            key={unit.id}
            className={`grid-card type-${unit.type}`}
            onClick={() => handleUnitClick(unit)}
            role="button"
            tabIndex={0}
          >
            <div className="card-type">{unit.type}</div>
            <h4 className="card-title">{unit.title}</h4>
            <p className="card-preview">
              {unit.content?.slice(0, 120)}
              {unit.content?.length > 120 ? "..." : ""}
            </p>
            {unit.tags?.length > 0 && (
              <div className="card-tags">
                {unit.tags.slice(0, 4).map((tag) => (
                  <span
                    key={tag}
                    className="tag"
                    onClick={(e) => {
                      e.stopPropagation();
                      onTagClick?.(tag);
                    }}
                  >
                    {tag}
                  </span>
                ))}
                {unit.tags.length > 4 && (
                  <span className="tag-more">+{unit.tags.length - 4}</span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredUnits.length === 0 && (
        <div className="grid-empty">
          <p>No units match your filters.</p>
        </div>
      )}
    </div>
  );
}

export default InteractiveGrid;
