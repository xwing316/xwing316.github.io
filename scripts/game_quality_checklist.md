# Game Lab Daily Coffee Game Quality Checklist

Daily Game Lab runs must produce a polished, playable coffee game — not a rushed template swap.

## Minimum bar before publish

- **Bespoke concept:** The game title, mechanics, scoring, visuals, thumbnail prompt, and copy all match the selected coffee theme.
- **Distinct mechanic:** Do not ship the same generic loop repeatedly. Use the archetype mechanic (`catch`, `timing`, `dodge`, `shooter`, `memory`, `trace`, `stack`, `td`, `match3`) intentionally.
- **Game feel / juice:** Include at least several of: particles, glow, animation easing, combo/streak feedback, level or wave progression, score popups, warning states, success/fail feedback, and polished game-over state.
- **Playable controls:** Keyboard and touch/mouse controls both work. Controls are explained in-page.
- **Responsive layout:** Canvas or playfield scales on mobile without hiding HUD/buttons.
- **Complete state:** Visible score/status, restart/new game, high score where appropriate, game-over/win feedback.
- **Site style:** Dark navy background, coffee/cyan accents, no visible UI emojis. Use generated images or canvas/vector art; emojis may only remain as functional fallback game pieces in older games.
- **Game header:** Include `../js/game-header.js?v=3` so the fixed header and mobile hamburger menu load freshly.
- **Artwork:** Generate a LocalAI Flux PNG thumbnail at `assets/images/game-<game_id>.png`; no gradient-only publishing.
- **Verification:** `python3 -m py_compile scripts/daily_game_gen.py`, `node --check js/games-data.js`, check the generated game file exists, check the thumbnail is a `1024 x 768` PNG, and inspect `git status --short`.

## Preferred daily workflow

1. Pull latest `origin/main`.
2. Spend time designing the game loop before writing code: objective, fail condition, progression, scoring, polish effects, controls, and thumbnail scene.
3. Generate/modify the game and thumbnail.
4. Run the quality checks above.
5. Commit and push only after the generated game passes verification.
