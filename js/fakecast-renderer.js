/* ============================================================
   FAKECAST-RENDERER.JS — Render episodes and handle tabs/audio
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  renderAllShows();
  initTabs();
});

function initTabs() {
  const tabs = document.querySelectorAll('.fakecast-tab');
  const shows = document.querySelectorAll('.fakecast-show');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetShow = tab.dataset.show;

      tabs.forEach(t => t.classList.remove('active'));
      shows.forEach(s => s.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(`show-${targetShow}`).classList.add('active');
    });
  });
}

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function renderAllShows() {
  renderShow('ai', 'episodes-ai');
  renderShow('coffee', 'episodes-coffee');
}

function renderShow(showKey, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const show = FAKECAST_DATA[showKey];
  if (!show.episodes || show.episodes.length === 0) {
    container.innerHTML = `
      <div class="episode-card" style="text-align:center;padding:var(--space-xl);">
        <div style="font-size:3rem;margin-bottom:var(--space-sm);">🎙️</div>
        <h3 style="font-family:var(--font-heading);color:var(--text);margin-bottom:var(--space-sm);">No Episodes Yet</h3>
        <p style="color:var(--text-faint);">Check back soon — the robots are warming up their vocal cords.</p>
      </div>
    `;
    return;
  }

  // Add show cover art to the show header
  const showHeader = container.parentElement?.querySelector('.fakecast-show__header');
  if (showHeader && show.coverArt && !showHeader.querySelector('.fakecast-show__art')) {
    const artImg = document.createElement('img');
    artImg.src = show.coverArt;
    artImg.alt = `${show.title} cover art`;
    artImg.className = 'fakecast-show__art';
    artImg.loading = 'lazy';
    showHeader.insertBefore(artImg, showHeader.firstChild);
  }

  container.innerHTML = show.episodes.map((ep, idx) => createEpisodeCard(ep, idx + 1, showKey)).join('');

  // Initialize audio players after rendering
  show.episodes.forEach((ep, idx) => {
    initAudioPlayer(`${showKey}-ep-${idx + 1}`, ep.audioSrc, ep.duration);
  });
}

function createEpisodeCard(ep, number, showKey) {
  const playerId = `${showKey}-ep-${number}`;
  const dateStr = new Date(ep.date).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const show = FAKECAST_DATA[showKey];
  const coverArt = show.coverArt
    ? `<img src="${show.coverArt}" alt="${escapeHtml(show.title)} cover art" class="episode-card__cover" loading="lazy">`
    : `<div class="episode-card__cover episode-card__cover--placeholder">${show.emoji}</div>`;

  return `
    <article class="episode-card">
      ${coverArt}
      <div class="episode-card__body">
        <div class="episode-card__header">
          <div class="episode-card__number">EP${number}</div>
          <div class="episode-card__meta">
            <h3 class="episode-card__title">${escapeHtml(ep.title)}</h3>
            <span class="episode-card__date">${dateStr} · ${formatDuration(ep.duration)}</span>
          </div>
        </div>
        <p class="episode-card__desc">${escapeHtml(ep.description)}</p>
        <div class="episode-card__player">
          <audio id="${playerId}" preload="metadata" controls style="width:100%;">
            <source src="${ep.audioSrc}" type="audio/mpeg">
            Your browser does not support the audio element.
          </audio>
        </div>
      </div>
    </article>
  `;
}

function initAudioPlayer(id, src, duration) {
  // Native audio element handles everything — no custom JS needed
  // But we can add error handling
  const audio = document.getElementById(id);
  if (!audio) return;

  audio.addEventListener('error', () => {
    console.warn(`Audio failed to load: ${src}`);
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
