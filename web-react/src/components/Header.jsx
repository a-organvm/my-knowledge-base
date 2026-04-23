/**
 * Header component for the knowledge base web interface.
 * Renders navigation, search, and status indicators.
 */

import React, { useState } from 'react';

export const Header = ({ title = 'Knowledge Base', onSearch, status }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (onSearch && searchQuery.trim()) {
      onSearch(searchQuery.trim());
    }
  };

  return (
    <header className="kb-header">
      <div className="kb-header__brand">
        <h1 className="kb-header__title">{title}</h1>
        {status && (
          <span className={`kb-header__status kb-header__status--${status}`}>
            {status}
          </span>
        )}
      </div>

      <nav className="kb-header__nav">
        <a href="/" className="kb-header__link">Dashboard</a>
        <a href="/atoms" className="kb-header__link">Atoms</a>
        <a href="/search" className="kb-header__link">Search</a>
        <a href="/pipeline" className="kb-header__link">Pipeline</a>
      </nav>

      <form className="kb-header__search" onSubmit={handleSearch}>
        <input
          type="search"
          className="kb-header__search-input"
          placeholder="Search knowledge base..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          aria-label="Search knowledge base"
        />
        <button type="submit" className="kb-header__search-btn">
          Search
        </button>
      </form>
    </header>
  );
};
