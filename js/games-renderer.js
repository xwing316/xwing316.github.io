// ============================================
// games-renderer.js — Render & filter game cards
// ============================================

let currentCategory = 'all';
let currentSearch = '';
let currentSort = 'name';

function renderGames() {
  const container = document.getElementById('games-container');
  if (!container) return;

  const filtered = getFilteredGames();
  container.innerHTML = '';

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align:center;padding:3rem 1rem;grid-column:1/-1;">
        <span style="font-size:3rem;display:block;margin-bottom:1rem;">🔍</span>
        <p style="color:var(--text-faint);">No games found. Try a different filter.</p>
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

function createGameCard(game, index) {
  const card = document.createElement('article');
  card.className = 'game-card';
  card.style.animationDelay = `${index * 0.05}s`;
  card.dataset.category = game.category;

  card.innerHTML = `
    <div class="game-card__thumb" style="background: ${game.thumbnail};">
      <span class="game-card__emoji">${game.emoji}</span>
      <span class="game-card__badge">${game.difficulty}</span>
    </div>
    <div class="game-card__content">
      <h3 class="game-card__title">${game.title}</h3>
      <p class="game-card__desc">${game.description}</p>
      <div class="game-card__tags">
        <span class="game-card__tag">${GAME_CATEGORIES[game.category]?.icon || ''} ${game.category}</span>
      </div>
      <a href="${game.file}" class="game-card__play">▶ Play</a>
    </div>
  `;

  return card;
}

function filterByCategory(category) {
  currentCategory = category;
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.category === category);
  });
  renderGames();
}

function searchGames(query) {
  currentSearch = query;
  renderGames();
}

function sortGames(sortBy) {
  currentSort = sortBy;
  renderGames();
}

function initGamesRenderer() {
  renderGames();

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => filterByCategory(btn.dataset.category));
  });
}

document.addEventListener('DOMContentLoaded', initGamesRenderer);
