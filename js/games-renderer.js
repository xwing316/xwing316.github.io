// ============================================
// games-renderer.js — Render & filter game cards
// ============================================

// Current state
let currentCategory = 'all';
let currentSearch = '';
let currentSort = 'name';

// -------------------------------------------
// Main render function
// -------------------------------------------
function renderGames() {
  const container = document.getElementById('games-container');
  if (!container) return;

  const filtered = getFilteredGames();
  container.innerHTML = '';

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align:center;padding:3rem 1rem;grid-column:1/-1;">
        <span style="font-size:3rem;display:block;margin-bottom:1rem;">🔍</span>
        <p style="color:var(--text-secondary);">No games found. Try a different filter.</p>
      </div>`;
    return;
  }

  const fragment = document.createDocumentFragment();

  filtered.forEach((game, index) => {
    const card = createGameCard(game, index);
    fragment.appendChild(card);
  });

  container.appendChild(fragment);
}

// -------------------------------------------
// Get filtered & sorted games list
// -------------------------------------------
function getFilteredGames() {
  let games = [...GAMES];

  if (currentCategory !== 'all') {
    games = games.filter(g => g.category === currentCategory);
  }

  if (currentSearch.trim()) {
    const term = currentSearch.toLowerCase().trim();
    games = games.filter(g =>
      g.title.toLowerCase().includes(term) ||
      g.description.toLowerCase().includes(term) ||
      g.category.toLowerCase().includes(term)
    );
  }

  games.sort((a, b) => {
    switch (currentSort) {
      case 'name': return a.title.localeCompare(b.title);
      case 'difficulty': return (DIFFICULTY_ORDER[a.difficulty] || 0) - (DIFFICULTY_ORDER[b.difficulty] || 0);
      case 'category': return a.category.localeCompare(b.category) || a.title.localeCompare(b.title);
      default: return 0;
    }
  });

  return games;
}

// -------------------------------------------
// Create a single game card element
// -------------------------------------------
function createGameCard(game, index) {
  const card = document.createElement('article');
  card.className = 'game-card';
  card.style.animationDelay = `${index * 0.05}s`;
  card.dataset.category = game.category;

  const difficultyClass = game.difficulty.toLowerCase();

  card.innerHTML = `
    <div class="game-card__thumbnail-wrapper" style="background: ${game.thumbnail};">
      <span style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:3rem;z-index:1;text-shadow:0 2px 10px rgba(0,0,0,0.3);">${game.emoji}</span>
      <span class="game-card__badge">${game.difficulty}</span>
    </div>
    <div class="game-card__content">
      <h3 class="game-card__title">${game.title}</h3>
      <p class="game-card__description">${game.description}</p>
      <div class="game-card__tech">
        <span class="game-card__tech-tag">${GAME_CATEGORIES[game.category]?.icon || ''} ${game.category}</span>
      </div>
      <a href="${game.file}" class="game-card__play-btn">▶ Play</a>
    </div>
  `;

  return card;
}

// -------------------------------------------
// Filter by category
// -------------------------------------------
function filterByCategory(category) {
  currentCategory = category;

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.category === category);
  });

  renderGames();
}

// -------------------------------------------
// Search / filter by title
// -------------------------------------------
function searchGames(query) {
  currentSearch = query;
  renderGames();
}

// -------------------------------------------
// Sort games
// -------------------------------------------
function sortGames(sortBy) {
  currentSort = sortBy;

  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.sort === sortBy);
  });

  renderGames();
}

// -------------------------------------------
// Initialize renderer & bind events
// -------------------------------------------
function initGamesRenderer() {
  renderGames();

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      filterByCategory(btn.dataset.category);
    });
  });

  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sortGames(btn.dataset.sort);
    });
  });

  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.value = currentSort;
    sortSelect.addEventListener('change', () => {
      sortGames(sortSelect.value);
    });
  }

  const searchInput = document.getElementById('game-search');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        searchGames(searchInput.value);
      }, 200);
    });
  }
}

// Auto-init when DOM is ready
document.addEventListener('DOMContentLoaded', initGamesRenderer);