<!--
  App.svelte — Root Svelte component for the knowledge base UI.

  Provides the main application shell with navigation, search,
  and content area for displaying knowledge units.
-->
<script>
  import { onMount } from "svelte";

  let searchQuery = "";
  let units = [];
  let loading = false;
  let error = null;
  let searchMode = "hybrid";

  const API_BASE = "/api";

  async function search() {
    if (!searchQuery.trim()) return;
    loading = true;
    error = null;

    try {
      const endpoint =
        searchMode === "semantic"
          ? `${API_BASE}/search/semantic`
          : searchMode === "fulltext"
            ? `${API_BASE}/search`
            : `${API_BASE}/search/hybrid`;

      const res = await fetch(`${endpoint}?q=${encodeURIComponent(searchQuery)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      units = data.data || [];
    } catch (err) {
      error = err.message;
      units = [];
    } finally {
      loading = false;
    }
  }

  async function loadRecent() {
    loading = true;
    try {
      const res = await fetch(`${API_BASE}/units?limit=20&sort=created_at&order=desc`);
      if (res.ok) {
        const data = await res.json();
        units = data.data || [];
      }
    } catch {
      // Silently handle
    } finally {
      loading = false;
    }
  }

  function handleKeydown(event) {
    if (event.key === "Enter") search();
  }

  onMount(loadRecent);
</script>

<main class="app">
  <header class="app-header">
    <h1>Knowledge Base</h1>
    <div class="search-bar">
      <input
        type="search"
        bind:value={searchQuery}
        on:keydown={handleKeydown}
        placeholder="Search your knowledge..."
        aria-label="Search"
      />
      <select bind:value={searchMode}>
        <option value="hybrid">Hybrid</option>
        <option value="semantic">Semantic</option>
        <option value="fulltext">Full-text</option>
      </select>
      <button on:click={search} disabled={loading}>Search</button>
    </div>
  </header>

  <section class="content">
    {#if loading}
      <p class="status">Loading...</p>
    {:else if error}
      <p class="status error">Error: {error}</p>
    {:else if units.length === 0}
      <p class="status">No results. Try a different query.</p>
    {:else}
      <div class="unit-grid">
        {#each units as unit (unit.id)}
          <article class="unit-card type-{unit.type}">
            <span class="unit-type">{unit.type}</span>
            <h3>{unit.title}</h3>
            <p>{unit.content?.slice(0, 200)}{unit.content?.length > 200 ? "..." : ""}</p>
            {#if unit.tags?.length}
              <div class="tags">
                {#each unit.tags as tag}
                  <span class="tag">{tag}</span>
                {/each}
              </div>
            {/if}
          </article>
        {/each}
      </div>
    {/if}
  </section>
</main>

<style>
  .app { max-width: 1200px; margin: 0 auto; padding: 1rem; }
  .app-header { margin-bottom: 2rem; }
  .search-bar { display: flex; gap: 0.5rem; }
  .search-bar input { flex: 1; padding: 0.5rem; }
  .unit-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
  .unit-card { padding: 1rem; border: 1px solid #ddd; border-radius: 8px; }
  .unit-type { font-size: 0.75rem; text-transform: uppercase; opacity: 0.7; }
  .tags { display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.5rem; }
  .tag { font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; background: #eee; }
  .status { text-align: center; padding: 2rem; opacity: 0.6; }
  .error { color: red; }
</style>
