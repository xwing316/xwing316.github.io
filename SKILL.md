# Site Style Guide & Design System

> **CRITICAL:** ALWAYS read this file before making ANY changes to the website. Update it when adding new patterns, components, or changing the design system.

---

## 1. Project Overview

**Site:** Shane Maynard's Personal Blog & Game Arcade  
**URL:** https://xwing316.github.io/  
**Tech Stack:** Vanilla HTML5, CSS3, JavaScript. No frameworks. GitHub Pages hosting.  
**Repo:** `git@github.com:xwing316/xwing316.github.io.git`

---

## 2. Design Philosophy

- **Content-first:** Typography and whitespace carry the design, not decoration.
- **Dark mode default:** Deep navy background (`#0d1117`) with high-contrast text.
- **Warm + Cool accents:** Coffee tones for warmth, cyan for energy/AI.
- **Organic shapes:** Blob-like border-radius on profile images for personality.
- **Minimal, elegant:** Inspired by content-focused blog themes (Fancy Ghost).

---

## 3. Color Palette (CSS Custom Properties)

All colors are defined as CSS custom properties in `:root`. **Never hardcode colors** — always use these variables.

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#0d1117` | Page background |
| `--bg-elevated` | `#161b22` | Cards, nav backdrop, footer |
| `--bg-card` | `rgba(22, 27, 34, 0.60)` | Translucent card backgrounds |
| `--bg-hover` | `rgba(30, 37, 48, 0.80)` | Hover states |
| `--coffee` | `#C4A882` | Primary warm accent, highlights |
| `--coffee-dim` | `rgba(196, 168, 130, 0.12)` | Subtle coffee backgrounds |
| `--coffee-glow` | `rgba(196, 168, 130, 0.20)` | Borders, glows |
| `--cyan` | `#00D4AA` | Primary action color, links |
| `--cyan-dim` | `rgba(0, 212, 170, 0.10)` | Subtle cyan backgrounds |
| `--cyan-glow` | `rgba(0, 212, 170, 0.25)` | Button shadows, hover glows |
| `--text` | `#e6edf3` | Primary headings, important text |
| `--text-soft` | `#8b949e` | Body text, paragraphs |
| `--text-faint` | `#6e7681` | Meta text, captions, dates |
| `--border` | `rgba(139, 148, 158, 0.12)` | Default borders |
| `--border-hover` | `rgba(0, 212, 170, 0.25)` | Hover/active borders |

### Color Usage Rules
- **Links:** `var(--cyan)` by default, `var(--coffee)` on hover.
- **Buttons primary:** `var(--cyan)` background, `var(--bg)` text.
- **Buttons outline:** Transparent bg, `var(--border)` border.
- **Tags/labels:** `var(--cyan)` text on `var(--cyan-dim)` background.
- **Cards:** `var(--bg-card)` background, `var(--border)` border.

---

## 4. Typography

### Font Families
| Role | Font | Fallbacks |
|------|------|-----------|
| **Headings** | DM Serif Display | Georgia, Times New Roman, serif |
| **Body** | DM Sans | -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif |
| **Mono** | JetBrains Mono | Fira Code, Consolas, monospace |

### Font Loading
```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Serif+Display&display=swap');
```

### Type Scale
| Element | Size | Weight | Family |
|---------|------|--------|--------|
| Hero title | `clamp(2.8rem, 6vw, 4.5rem)` | 400 | DM Serif Display |
| Section title | `clamp(1.8rem, 4vw, 2.6rem)` | 400 | DM Serif Display |
| Card title | `1.2–1.25rem` | 400 | DM Serif Display |
| Body | `17px` | 400 | DM Sans |
| Body (cards) | `0.88–1.05rem` | 400 | DM Sans |
| Tag/label | `0.65–0.72rem` | 600 | Mono (uppercase) |
| Button | `0.9rem` | 600 | DM Sans |

### Typography Rules
- Headings use `letter-spacing: -0.02em to -0.03em` for tighter, elegant feel.
- Body line-height: `1.7` default, `1.85` for article content.
- Mono text is **always uppercase** with `letter-spacing: 0.05–0.06em` for tags/labels.

---

## 5. Spacing Scale

| Token | Value |
|-------|-------|
| `--space-xs` | `0.5rem` (8px) |
| `--space-sm` | `1rem` (16px) |
| `--space-md` | `1.5rem` (24px) |
| `--space-lg` | `2.5rem` (40px) |
| `--space-xl` | `4rem` (64px) |
| `--space-2xl` | `6rem` (96px) |
| `--space-3xl` | `8rem` (128px) |

### Layout Rules
- **Max content width:** `720px` (`var(--max-w)`)
- **Nav height:** `64px` (`var(--nav-h)`)
- **Page padding:** `var(--space-md)` horizontal (24px)
- **Section vertical padding:** `var(--space-2xl)` (96px)
- **Hero padding:** `var(--space-3xl)` top, `var(--space-2xl)` bottom

---

## 6. Border Radius Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | `8px` | Buttons, small elements |
| `--radius-md` | `16px` | Cards, game cards |
| `--radius-lg` | `24px` | Spotlight sections |
| **Organic blob** | `48% 52% 34% 66% / 52% 38% 62% 48%` | Profile images ONLY |

---

## 7. Component Library

### 7.1 Navigation (`.navbar`)
- Sticky top, `z-index: 100`
- Height: `var(--nav-h)` (64px)
- Background: `rgba(13, 17, 23, 0.85)` with `backdrop-filter: blur(20px)`
- Border-bottom: `1px solid var(--border)`
- Brand: DM Serif Display, `1.35rem`, `☕ Shane Maynard`
- Links: DM Sans, `0.9rem`, weight 500. Cyan underline on hover/active.
- Mobile: hamburger menu, slide-in panel from right.

### 7.2 Hero Section (`.hero`)
- Centered flex column, max-width `720px`
- Profile image: `160×160px`, organic blob border-radius
- Title: Large DM Serif Display
- Tagline: `1.15rem`, `var(--text-soft)`
- Two buttons: primary (cyan) + outline

### 7.3 Buttons (`.btn`)
**Primary (`.btn--primary`):**
- Background: `var(--cyan)`
- Text: `var(--bg)` (dark)
- Shadow: `0 2px 12px var(--cyan-glow)`
- Hover: translateY(-2px), larger shadow

**Outline (`.btn--outline`):**
- Background: transparent
- Border: `1.5px solid var(--border)`
- Hover: border becomes cyan, text becomes cyan

### 7.4 Cards

**Blog Card (`.blog-card`):**
- Background: `var(--bg-card)`
- Border: `1px solid var(--border)`
- Border-radius: `var(--radius-md)` (16px)
- Hover: translateY(-3px), coffee-glow border
- Tag: cyan mono pill
- Title: DM Serif Display
- Excerpt: `var(--text-faint)`
- Footer: date + "Read More →" link in coffee/cyan

**Game Card (`.game-card`):**
- Same base as blog card
- Thumbnail: gradient background, 16:10 aspect ratio
- Emoji overlay: `3rem`, centered
- Difficulty badge: top-right, dark translucent pill
- Play button: cyan, mono font, "▶ Play"

**Interest Card (`.interest-card`):**
- Centered text
- Icon: `2.4rem` emoji
- Hover: translateY(-4px), cyan border glow

### 7.5 Footer (`.footer`)
- Background: `var(--bg-elevated)`
- Border-top: `1px solid var(--border)`
- Centered layout, social icons in circles
- Social icon hover: cyan background, translateY(-2px)

---

## 8. Page Templates

### 8.1 Homepage (`index.html`)
Sections in order:
1. Navbar
2. Hero (profile, name, tagline, CTA buttons)
3. About Me (text block, 3 paragraphs)
4. Interests (6-card grid: Coffee, AI/ML, Open Source, Gaming, Music, Photography)
5. Blog (6-card grid, most recent first)
6. Games Spotlight (single spotlight card linking to games.html)
7. Footer

### 8.2 Games Page (`games.html`)
1. Navbar
2. Games header (title + subtitle)
3. Filter bar (All, Puzzle, Action, Strategy, Classic)
4. Games grid (rendered dynamically via JS)
5. Footer

**Games are rendered from `js/games-data.js`** — never hardcode game cards in HTML.

### 8.3 Blog Article Pages (`blog/*.html`)
1. Navbar (with `../` paths for assets)
2. Back link: `← Back to Blog` linking to `../index.html#blog`
3. Article header: tag pill, title, meta (date · read time)
4. Article body: styled content with h2, p, ul, blockquote, code
5. Footer (with `../` paths)

**Article page CSS is inline in a `<style>` block** — it extends the base style.css with article-specific rules.

### 8.4 Game Pages (`games/*.html`)
- Self-contained single HTML files with inline CSS and JS
- Dark background matching site palette (`#0d1117` or similar)
- Back button: `a.back` linking to `../games.html`
- Canvas-based games centered on page

---

## 9. JavaScript Architecture

### 9.1 File Organization
```
js/
  main.js           — Global site JS (nav, smooth scroll, animations)
  games-data.js     — Game definitions array (GAMES)
  games-renderer.js — Dynamic game card rendering + filtering
```

### 9.2 Games Data Structure
Each game in `GAMES` array must have:
```javascript
{
  id: 'unique-id',
  title: 'Game Title',
  description: 'Short description.',
  category: 'puzzle' | 'action' | 'strategy' | 'classic',
  thumbnail: 'linear-gradient(...)',
  file: 'games/filename.html',
  difficulty: 'Easy' | 'Medium' | 'Hard',
  emoji: '🎮'
}
```

### 9.3 Games Renderer API
- `renderGames()` — Renders filtered/sorted games into `#games-container`
- `filterByCategory(category)` — Filter by category string
- `searchGames(query)` — Filter by search term
- `sortGames(sortBy)` — Sort by 'name' | 'difficulty' | 'category'
- Auto-initializes on DOMContentLoaded.

---

## 10. File Structure

```
/
├── index.html                    # Homepage
├── games.html                    # Games catalog
├── css/
│   └── style.css                 # Global styles (ONE stylesheet)
├── js/
│   ├── main.js                   # Site-wide JS
│   ├── games-data.js             # Game definitions
│   └── games-renderer.js         # Game grid renderer
├── blog/
│   ├── ai-powered-apps.html
│   ├── coffee-brewing-setup.html
│   ├── open-source-first-contribution.html
│   ├── fine-tuning-first-model.html
│   ├── best-dev-tools-2025.html
│   └── prompt-engineering-deep-dive.html
├── games/
│   ├── snake.html
│   ├── memory.html
│   ├── pong.html
│   ├── flappy.html
│   ├── tictactoe.html
│   ├── breakout.html
│   ├── 2048.html
│   └── invaders.html
├── assets/
│   └── profile.png               # Profile picture (organic blob shape via CSS)
└── SKILL.md                      # THIS FILE
```

---

## 11. Game Design Rules

### 11.1 Visual Consistency
- Game pages should use colors from the site palette (`#0d1117` bg, `#00D4AA` accents)
- Back button must link to `../games.html`
- Self-contained: all CSS and JS inline in the HTML file

### 11.2 Coffee Theme Rule (CRITICAL)
**All future games added to the site MUST be coffee-themed unless the user explicitly states otherwise.**

This means:
- Coffee-related visuals, characters, or mechanics
- Coffee color palette (browns, creams, warm tones)
- Coffee shop, barista, bean, or brewing motifs
- Existing games are grandfathered in (classic arcade games)

---

## 12. Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| `≥1024px` | Blog grid 2-col, interests 3-col, games grid 2-col |
| `≤768px` | Mobile nav hamburger, hero padding reduced, interests 2-col, games 1-col |
| `≤480px` | Nav height 56px, interests 1-col, hero profile 110px |

---

## 13. Accessibility

- All interactive elements have focus states
- `prefers-reduced-motion` respected (disables animations)
- Semantic HTML: `<nav>`, `<section>`, `<article>`, `<footer>`
- ARIA labels on icon-only links
- Color contrast meets WCAG AA (cyan `#00D4AA` on `#0d1117` = 7.2:1)

---

## 14. Git Workflow

1. **Always pull before starting:** `git pull origin main`
2. **Make atomic commits:** one logical change per commit
3. **Commit messages:** descriptive, e.g. "Fix nav brand, add blog articles, fix game links"
4. **Push to main:** `git push origin main`
5. **Verify on live site:** https://xwing316.github.io/ (may take 1–2 min to propagate)

---

## 15. Checklist Before Deploying

- [ ] Navbar brand says "☕ Shane Maynard"
- [ ] All nav links work on every page
- [ ] Blog "Read More" links point to real article pages
- [ ] Game "Play" buttons link to existing game files
- [ ] Footer brand matches navbar
- [ ] Mobile hamburger menu works
- [ ] No 404s on game pages
- [ ] CSS uses custom properties, no hardcoded colors
- [ ] New games follow coffee theme (unless exempted)

---

## 16. Change Log

| Date | Change |
|------|--------|
| 2026-05-01 | Initial style guide created. Documented design system, colors, typography, components, file structure. |

---

> **Remember:** When in doubt, reference this guide. When you learn something new about the site, update this guide.
