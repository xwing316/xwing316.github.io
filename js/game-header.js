// ============================================
// game-header.js — Shared header for all game pages
// Injected automatically when this script is loaded.
// Provides: back link, brand, game title, mobile hamburger nav.
// ============================================
(function () {
  'use strict';

  if (document.getElementById('game-shared-header')) return; // already injected

  const title = document.title || 'Game';
  const gameName = title.split(/[-|—]/)[0].trim();

  // ── Scoped styles ───────────────────────────────────────────────────────
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
      transition: color 0.2s, transform 0.2s, background 0.2s;
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
    .game-header-bar .header-brand {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .game-header-bar .header-brand img {
      width: 18px;
      height: 18px;
      border-radius: 4px;
      display: block;
    }
    .game-header-bar .header-right {
      display: flex;
      align-items: center;
      gap: 12px;
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
    /* Hamburger button */
    .game-header-bar .header-hamburger {
      display: none;
      flex-direction: column;
      justify-content: center;
      gap: 4px;
      width: 32px;
      height: 32px;
      background: transparent;
      border: none;
      cursor: pointer;
      padding: 4px;
      border-radius: 6px;
      transition: background 0.2s;
    }
    .game-header-bar .header-hamburger:hover {
      background: rgba(0,212,170,0.08);
    }
    .game-header-bar .header-hamburger span {
      display: block;
      width: 20px;
      height: 2px;
      background: #e6edf3;
      border-radius: 2px;
      transition: transform 0.25s ease, opacity 0.2s ease;
      transform-origin: center;
    }
    .game-header-bar .header-hamburger.open span:nth-child(1) {
      transform: translateY(6px) rotate(45deg);
    }
    .game-header-bar .header-hamburger.open span:nth-child(2) {
      opacity: 0;
    }
    .game-header-bar .header-hamburger.open span:nth-child(3) {
      transform: translateY(-6px) rotate(-45deg);
    }
    /* Nav panel */
    .game-header-bar .game-nav-panel {
      position: absolute;
      top: 48px;
      right: 8px;
      background: rgba(13,17,23,0.98);
      border: 1px solid rgba(139,148,158,0.18);
      border-radius: 10px;
      padding: 8px;
      min-width: 160px;
      display: flex;
      flex-direction: column;
      gap: 2px;
      opacity: 0;
      transform: translateY(-6px) scale(0.97);
      pointer-events: none;
      transition: opacity 0.2s ease, transform 0.2s ease;
      box-shadow: 0 10px 30px rgba(0,0,0,0.4);
      z-index: 10000;
    }
    .game-header-bar .game-nav-panel.open {
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: auto;
    }
    .game-header-bar .game-nav-panel a {
      color: #e6edf3;
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      padding: 8px 12px;
      border-radius: 6px;
      transition: background 0.15s, color 0.15s;
    }
    .game-header-bar .game-nav-panel a:hover {
      background: rgba(0,212,170,0.1);
      color: #00D4AA;
    }
    /* Mobile: show hamburger, hide desktop inline links if we had any */
    @media (max-width: 768px) {
      .game-header-bar .header-hamburger { display: flex; }
      .game-header-bar .header-title { max-width: 140px; font-size: 12px; }
    }
    @media (max-width: 480px) {
      .game-header-bar .header-brand { display: none; }
      .game-header-bar .header-title { max-width: 100px; font-size: 11px; }
    }
  `;
  document.head.appendChild(style);

  // ── Build nav bar ───────────────────────────────────────────────────────
  const nav = document.createElement('nav');
  nav.id = 'game-shared-header';
  nav.className = 'game-header-bar';
  nav.setAttribute('aria-label', 'Game navigation');
  nav.innerHTML = `
    <div class="header-left">
      <a href="../games.html" class="header-back">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 12L6 8l4-4"/></svg>
        Games
      </a>
      <span class="header-brand"><img src="../assets/images/game-assets/icon-coffee.png" alt="" aria-hidden="true"> Shane Maynard</span>
    </div>
    <div class="header-right">
      <span class="header-title">${gameName}</span>
      <button class="header-hamburger" id="game-hamburger" aria-label="Toggle menu" aria-expanded="false" aria-controls="game-nav-panel">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>
    <div class="game-nav-panel" id="game-nav-panel" role="menu" aria-hidden="true">
      <a href="../index.html" role="menuitem">Home</a>
      <a href="../index.html#about" role="menuitem">About</a>
      <a href="../games.html" role="menuitem">Games</a>
      <a href="../fakecast.html" role="menuitem">FakeCast</a>
      <a href="../index.html#contact" role="menuitem">Contact</a>
    </div>
  `;

  document.body.insertBefore(nav, document.body.firstChild);
  document.body.style.paddingTop = '48px';

  // ── Hamburger logic ─────────────────────────────────────────────────────
  const hamburger = nav.querySelector('#game-hamburger');
  const panel = nav.querySelector('#game-nav-panel');

  function openMenu() {
    panel.classList.add('open');
    hamburger.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    panel.setAttribute('aria-hidden', 'false');
  }

  function closeMenu() {
    panel.classList.remove('open');
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    panel.setAttribute('aria-hidden', 'true');
  }

  hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
    if (panel.classList.contains('open')) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  // Close when a link is clicked
  panel.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeMenu);
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !panel.contains(e.target)) {
      closeMenu();
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && panel.classList.contains('open')) {
      closeMenu();
    }
  });

  // ── Clean up old back-link elements ─────────────────────────────────────
  document.querySelectorAll('a.back-link, .back-link').forEach(el => {
    if (!el.closest('#game-shared-header')) el.remove();
  });
})();
