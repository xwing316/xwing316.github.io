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
      <div class="no-games">
        <span class="no-games-emoji">🔍</span>
        <p>No games found. Try a different filter or search term.</p>
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

  // Filter by category
  if (currentCategory !== 'all') {
    games = games.filter(g => g.category === currentCategory);
  }

  // Filter by search term
  if (currentSearch.trim()) {
    const term = currentSearch.toLowerCase().trim();
    games = games.filter(g =>
      g.title.toLowerCase().includes(term) ||
      g.description.toLowerCase().includes(term) ||
      g.category.toLowerCase().includes(term)
    );
  }

  // Sort
  games.sort((a, b) => {
    switch (currentSort) {
      case 'name':
        return a.title.localeCompare(b.title);
      case 'difficulty':
        return (DIFFICULTY_ORDER[a.difficulty] || 0) - (DIFFICULTY_ORDER[b.difficulty] || 0);
      case 'category':
        return a.category.localeCompare(b.category) || a.title.localeCompare(b.title);
      default:
        return 0;
    }
  });

  return games;
}

// -------------------------------------------
// Create a single game card element
// -------------------------------------------
function createGameCard(game, index) {
  const card = document.createElement('article');
  card.className = 'game-card fade-in';
  card.style.animationDelay = `${index * 0.05}s`;
  card.dataset.category = game.category;
  card.dataset.difficulty = game.difficulty;

  const difficultyClass = game.difficulty.toLowerCase();

  card.innerHTML = `
    <div class="game-thumbnail" style="background: ${game.thumbnail};">
      <span class="game-emoji">${game.emoji}</span>
    </div>
    <div class="game-info">
      <h3 class="game-title">${game.title}</h3>
      <p class="game-description">${game.description}</p>
      <div class="game-tags">
        <span class="tag category-tag">${GAME_CATEGORIES[game.category]?.icon || ''} ${game.category}</span>
        <span class="tag difficulty-tag ${difficultyClass}">${game.difficulty}</span>
      </div>
    </div>
    <a href="${game.file}" class="play-btn" title="Play ${game.title}">▶ Play</a>
  `;

  return card;
}

// -------------------------------------------
// Filter by category
// -------------------------------------------
function filterByCategory(category) {
  currentCategory = category;

  // Update active filter button
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

  // Update active sort button
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.sort === sortBy);
  });

  renderGames();
}

// -------------------------------------------
// Initialize renderer & bind events
// -------------------------------------------
function initGamesRenderer() {
  // Render initial game cards
  renderGames();

  // Bind filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      filterByCategory(btn.dataset.category);
    });
  });

  // Bind sort buttons/select
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sortGames(btn.dataset.sort);
    });
  });

  // Bind sort dropdown (if using <select>)
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.value = currentSort;
    sortSelect.addEventListener('change', () => {
      sortGames(sortSelect.value);
    });
  }

  // Bind search input
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