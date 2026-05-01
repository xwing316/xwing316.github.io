// ============================================
// games-renderer.js — Render, filter & paginate game cards
// ============================================

let currentCategory = 'all';
let currentSearch = '';
let currentSort = 'newest';
let currentPage = 1;
const PER_PAGE = 6;

function renderGames() {
  const container = document.getElementById('games-container');
  if (!container) return;

  const filtered = getFilteredGames();
  container.innerHTML = '';

  const countEl = document.getElementById('games-count');
  if (countEl) countEl.textContent = `${filtered.length} game${filtered.length !== 1 ? 's' : ''}`;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align:center;padding:3rem 1rem;grid-column:1/-1;">
        <span style="font-size:3rem;display:block;margin-bottom:1rem;">🔍</span>
        <p style="color:var(--text-faint);">No games found. Try a different filter.</p>
      </div>`;
    renderPagination(0);
    return;
  }

  // Paginate
  const totalPages = Math.max(1, Math.ceil(filtered.length / PER_PAGE));
  currentPage = Math.min(currentPage, totalPages);
  const start = (currentPage - 1) * PER_PAGE;
  const pageGames = filtered.slice(start, start + PER_PAGE);

  const fragment = document.createDocumentFragment();
  pageGames.forEach((game, index) => {
    const card = createGameCard(game, index);
    fragment.appendChild(card);
  });

  container.appendChild(fragment);
  renderPagination(totalPages);
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
      case 'newest': return (b.createdAt || '').localeCompare(a.createdAt || '');
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

function renderPagination(totalPages) {
  let pagination = document.getElementById('games-pagination');
  if (!pagination) {
    pagination = document.createElement('div');
    pagination.id = 'games-pagination';
    pagination.className = 'games-pagination';
    const container = document.getElementById('games-container');
    if (container && container.parentNode) {
      container.parentNode.insertBefore(pagination, container.nextSibling);
    }
  }

  if (totalPages <= 1) {
    pagination.innerHTML = '';
    return;
  }

  let html = `<button class="pagination-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">← Prev</button>`;
  html += `<div class="pagination-pages">`;
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="pagination-page ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
  }
  html += `</div>`;
  html += `<button class="pagination-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next →</button>`;

  pagination.innerHTML = html;
}

function goToPage(page) {
  currentPage = page;
  renderGames();
  document.getElementById('games-container').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function filterByCategory(category) {
  currentCategory = category;
  currentPage = 1;
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.category === category);
  });
  renderGames();
}

function searchGames(query) {
  currentSearch = query;
  currentPage = 1;
  renderGames();
}

function sortGames(sortBy) {
  currentSort = sortBy;
  currentPage = 1;
  renderGames();
}

function initGamesRenderer() {
  renderGames();

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => filterByCategory(btn.dataset.category));
  });
}

document.addEventListener('DOMContentLoaded', initGamesRenderer);
