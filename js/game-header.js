// ============================================
// game-header.js — Shared header for all game pages
// Injected automatically when this script is loaded.
// ============================================
(function () {
  'use strict';

  if (document.getElementById('game-shared-header')) return; // already injected

  const title = document.title || 'Game';
  const gameName = title.split(/[-|—]/)[0].trim();

  const style = document.createElement('style');
  style.textContent = `
    .game-header-bar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 48px;
      background: rgba(13,17,23,0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(139,148,158,0.12);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      z-index: 9999;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .game-header-bar .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .game-header-bar .header-back {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #00D4AA;
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      transition: color 0.2s, transform 0.2s;
      padding: 6px 10px;
      border-radius: 6px;
    }
    .game-header-bar .header-back:hover {
      color: #C4A882;
      transform: translateX(-2px);
      background: rgba(0,212,170,0.06);
    }
    .game-header-bar .header-back svg {
      width: 14px;
      height: 14px;
    }
    .game-header-bar .header-brand {
      color: #e6edf3;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.3px;
      opacity: 0.85;
    }
    .game-header-bar .header-brand span {
      color: #C4A882;
    }
    .game-header-bar .header-title {
      color: #8b949e;
      font-size: 13px;
      font-weight: 500;
      max-width: 200px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    @media (max-width: 480px) {
      .game-header-bar .header-brand { display: none; }
      .game-header-bar .header-title { max-width: 140px; font-size: 12px; }
    }
  `;
  document.head.appendChild(style);

  const nav = document.createElement('nav');
  nav.id = 'game-shared-header';
  nav.className = 'game-header-bar';
  nav.innerHTML = `
    <div class="header-left">
      <a href="../games.html" class="header-back">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 12L6 8l4-4"/></svg>
        Games
      </a>
      <span class="header-brand"><span>☕</span> Shane Maynard</span>
    </div>
    <span class="header-title">${gameName}</span>
  `;

  // Prepend to body, and add padding-top to body so content isn't hidden
  document.body.insertBefore(nav, document.body.firstChild);
  document.body.style.paddingTop = '48px';

  // Also remove any old .back-link elements to avoid duplication
  document.querySelectorAll('a.back-link, .back-link').forEach(el => {
    if (!el.closest('#game-shared-header')) el.remove();
  });
})();
