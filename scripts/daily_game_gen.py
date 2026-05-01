#!/usr/bin/env python3
"""
Daily coffee-themed arcade game generator for the Game Lab.
Runs at 5 AM daily, generates a new self-contained HTML5 canvas game,
updates games-data.js, commits and pushes.

Usage:
    python daily_game_gen.py
"""
import json
import os
import random
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SITE_DIR = Path(__file__).parent.parent
GAMES_DIR = SITE_DIR / "games"
DATA_FILE = SITE_DIR / "js" / "games-data.js"

# Game archetypes with coffee themes
GAME_ARCHETYPES = [
    {
        "name": "Bean Rush",
        "category": "action",
        "difficulty": "Medium",
        "emoji": "\u2615",
        "desc": "Navigate your barista through a crowded cafe, collecting specialty beans while avoiding spills and decaf traps.",
        "gradient": ["#6F4E37", "#C4A882"],
    },
    {
        "name": "Espresso Shot",
        "category": "action",
        "difficulty": "Hard",
        "emoji": "\u26a1",
        "desc": "Time your shots perfectly! Pull the lever when the pressure gauge hits the green zone. Too early or late and the shot is ruined.",
        "gradient": ["#3e2723", "#8d6e63"],
    },
    {
        "name": "Grind Master",
        "category": "puzzle",
        "difficulty": "Medium",
        "emoji": "\U0001f527",
        "desc": "Match three or more coffee beans of the same roast level to grind them into the perfect blend. Chain combos for bonus points!",
        "gradient": ["#5d4037", "#a1887f"],
    },
    {
        "name": "Pour Over Pro",
        "category": "puzzle",
        "difficulty": "Easy",
        "emoji": "\U0001fa88",
        "desc": "Guide the pour stream in spirals to evenly saturate the coffee bed. Miss a spot and you get channeling -- every drop counts!",
        "gradient": ["#4e342e", "#bcaaa4"],
    },
    {
        "name": "Latte Art Lab",
        "category": "puzzle",
        "difficulty": "Easy",
        "emoji": "\U0001f3a8",
        "desc": "Trace the latte art pattern by connecting the dots before the milk settles. Faster traces earn more stars from the customer.",
        "gradient": ["#795548", "#d7ccc8"],
    },
    {
        "name": "Roast Runner",
        "category": "action",
        "difficulty": "Hard",
        "emoji": "\U0001f525",
        "desc": "Keep the beans moving through the roaster! Dodge hotspots, control airflow, and eject each batch at the perfect roast level.",
        "gradient": ["#bf360c", "#ff7043"],
    },
    {
        "name": "Cold Brew Defender",
        "category": "strategy",
        "difficulty": "Medium",
        "emoji": "\U0001f9ca",
        "desc": "Place towers along the brew path to filter out impurities before they reach your precious cold brew concentrate.",
        "gradient": ["#1a237e", "#5c6bc0"],
    },
    {
        "name": "Cupping Challenge",
        "category": "strategy",
        "difficulty": "Easy",
        "emoji": "\U0001f375",
        "desc": "Identify the odd cup out in a triangle cupping setup. Train your palate by spotting the different origin or process.",
        "gradient": ["#33691e", "#aed581"],
    },
    {
        "name": "Milk Steamer",
        "category": "action",
        "difficulty": "Medium",
        "emoji": "\U0001f95b",
        "desc": "Steam milk to microfoam perfection. Watch the thermometer and stop at exactly the right temperature -- no scorching allowed!",
        "gradient": ["#f9a825", "#fff59d"],
    },
    {
        "name": "Barista Blitz",
        "category": "action",
        "difficulty": "Hard",
        "emoji": "\U0001f3ca",
        "desc": "Serve a rush of customers their exact orders. Memorize the queue, brew fast, and do not mix up the oat milk order!",
        "gradient": ["#c62828", "#ef5350"],
    },
]

USED_NAMES_FILE = SITE_DIR / ".daily_games_used"


def load_used_names():
    if USED_NAMES_FILE.exists():
        return set(USED_NAMES_FILE.read_text().strip().split("\n"))
    return set()


def save_used_name(name):
    with open(USED_NAMES_FILE, "a") as f:
        f.write(name + "\n")


def pick_archetype():
    used = load_used_names()
    available = [a for a in GAME_ARCHETYPES if a["name"] not in used]
    if not available:
        USED_NAMES_FILE.write_text("")
        available = GAME_ARCHETYPES
    return random.choice(available)


def generate_game_html(archetype, game_id, date_str):
    name = archetype["name"]
    g1, g2 = archetype["gradient"]

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
    overflow-x: hidden;
  }}
  a.back-link {{
    position: fixed;
    top: 20px;
    left: 24px;
    color: #00D4AA;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.2s, transform 0.2s;
    z-index: 100;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  a.back-link:hover {{ color: #C4A882; transform: translateX(-3px); }}
  a.back-link svg {{ width: 16px; height: 16px; }}
  h1 {{
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 6px;
    letter-spacing: 1px;
    color: #C4A882;
  }}
  .subtitle {{
    font-size: 13px;
    color: #8b949e;
    margin-bottom: 12px;
    text-align: center;
    max-width: 420px;
  }}
  .scores {{
    display: flex;
    gap: 24px;
    margin-bottom: 12px;
    font-size: 15px;
  }}
  .scores span {{ color: #8b949e; }}
  .scores strong {{ color: #00D4AA; font-weight: 600; }}
  canvas {{
    border: 2px solid #30363d;
    border-radius: 6px;
    background: #161b22;
    display: block;
    max-width: 100%;
    touch-action: none;
  }}
  .controls {{
    margin-top: 14px;
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
    justify-content: center;
  }}
  button {{
    background: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    padding: 8px 20px;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background .15s, border-color .15s;
  }}
  button:hover {{ background: #30363d; border-color: #8b949e; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
  button.primary:hover {{ background: #00D4AA33; }}
  .instructions {{
    margin-top: 14px;
    color: #8b949e;
    font-size: 13px;
    text-align: center;
    max-width: 420px;
    line-height: 1.5;
  }}
  .game-over {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    background: rgba(13,17,23,0.95);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 28px 36px;
    display: none;
    z-index: 10;
  }}
  .game-over h2 {{ font-size: 22px; margin-bottom: 8px; color: #e6edf3; }}
  .game-over p {{ color: #8b949e; margin-bottom: 16px; font-size: 14px; }}
  .canvas-wrap {{ position: relative; }}
  @media (max-width: 480px) {{
    h1 {{ font-size: 22px; }}
    .scores {{ gap: 16px; font-size: 13px; }}
    .instructions {{ font-size: 12px; }}
  }}
</style>
</head>
<body>
<a href="../games.html" class="back-link">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
  Back to Games
</a>

<h1>{archetype["emoji"]} {name}</h1>
<p class="subtitle">{archetype["desc"]}</p>

<div class="scores">
  <span>Score: <strong id="score">0</strong></span>
  <span>High: <strong id="high">0</strong></span>
  <span>Level: <strong id="level">1</strong></span>
</div>

<div class="canvas-wrap">
  <canvas id="game" width="400" height="520"></canvas>
  <div class="game-over" id="over">
    <h2>Game Over!</h2>
    <p>Final Score: <strong id="final">0</strong></p>
    <button class="primary" onclick="startGame()">Play Again</button>
  </div>
</div>

<div class="controls">
  <button onclick="startGame()">New Game</button>
  <button onclick="togglePause()">Pause</button>
</div>

<p class="instructions">
  Use <strong>Arrow Keys</strong> or <strong>A / D</strong> to move.<br>
  On mobile, tap left or right side of the screen.
</p>

<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const highEl = document.getElementById('high');
const levelEl = document.getElementById('level');
const overEl = document.getElementById('over');
const finalEl = document.getElementById('final');

let W = 400, H = 520;
let score = 0, high = parseInt(localStorage.getItem('game_high_{game_id}') || '0');
let level = 1, lives = 3, paused = false, running = false;
let player = {{ x: W/2 - 25, y: H - 55, w: 50, h: 40, speed: 5 }};
let items = [], particles = [], spawnTimer = 0, spawnInterval = 40;
let frameCount = 0;

highEl.textContent = high;

const GOOD_ITEMS = [
  {{ emoji: '\u2615', score: 15, speed: 2.8 }},
  {{ emoji: '\U0001fa88', score: 10, speed: 2.5 }},
  {{ emoji: '\u26a1', score: 30, speed: 3.5 }},
];
const BAD_ITEMS = [
  {{ emoji: '\U0001f9ca', score: -20, speed: 3.0 }},
  {{ emoji: '\U0001f4a4', score: -15, speed: 2.8 }},
];

function resize() {{
  const maxW = Math.min(window.innerWidth - 40, 400);
  const scale = maxW / 400;
  canvas.style.width = maxW + 'px';
  canvas.style.height = (520 * scale) + 'px';
}}
resize();
window.addEventListener('resize', resize);

let keys = {{}};
window.addEventListener('keydown', e => {{
  keys[e.key] = true;
  if (['ArrowLeft','ArrowRight','a','d','A','D'].includes(e.key)) e.preventDefault();
}});
window.addEventListener('keyup', e => keys[e.key] = false);

canvas.addEventListener('touchstart', e => {{
  e.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const touch = e.touches[0];
  const x = (touch.clientX - rect.left) * (W / rect.width);
  if (x < W/2) keys['ArrowLeft'] = true;
  else keys['ArrowRight'] = true;
}});
canvas.addEventListener('touchend', e => {{
  e.preventDefault();
  keys['ArrowLeft'] = false;
  keys['ArrowRight'] = false;
}});

function pickItem() {{
  const isGood = Math.random() > 0.35;
  const pool = isGood ? GOOD_ITEMS : BAD_ITEMS;
  const it = pool[Math.floor(Math.random() * pool.length)];
  return {{ ...it, x: Math.random() * (W - 30) + 15, y: -30, good: isGood }};
}}

function spawnParticles(x, y, color) {{
  for (let i = 0; i < 8; i++) {{
    particles.push({{
      x, y,
      vx: (Math.random() - 0.5) * 4,
      vy: (Math.random() - 0.5) * 4,
      life: 1,
      color
    }});
  }}
}}

function update() {{
  if (!running || paused) return;
  frameCount++;

  if (keys['ArrowLeft'] || keys['a'] || keys['A']) player.x -= player.speed;
  if (keys['ArrowRight'] || keys['d'] || keys['D']) player.x += player.speed;
  player.x = Math.max(0, Math.min(W - player.w, player.x));

  spawnTimer++;
  const interval = Math.max(12, spawnInterval - level * 2);
  if (spawnTimer >= interval) {{
    spawnTimer = 0;
    items.push(pickItem());
  }}

  for (let i = items.length - 1; i >= 0; i--) {{
    const it = items[i];
    it.y += it.speed + level * 0.2;

    if (it.y + 18 > player.y && it.y < player.y + player.h &&
        it.x + 12 > player.x && it.x - 12 < player.x + player.w) {{
      score += it.score;
      if (score < 0) score = 0;
      const color = it.good ? '#00D4AA' : '#e74c3c';
      spawnParticles(it.x, it.y, color);
      items.splice(i, 1);
      if (!it.good) {{
        lives--;
        if (lives <= 0) endGame();
      }}
      continue;
    }}

    if (it.y > H && it.good) {{
      lives--;
      if (lives <= 0) endGame();
      items.splice(i, 1);
      continue;
    }}
    if (it.y > H && !it.good) {{
      items.splice(i, 1);
    }}
  }}

  for (let i = particles.length - 1; i >= 0; i--) {{
    const p = particles[i];
    p.x += p.vx; p.y += p.vy;
    p.life -= 0.04;
    if (p.life <= 0) particles.splice(i, 1);
  }}

  level = 1 + Math.floor(score / 120);
}}

function draw() {{
  ctx.clearRect(0, 0, W, H);

  ctx.fillStyle = '#C4A882';
  ctx.beginPath();
  ctx.roundRect(player.x, player.y, player.w, player.h, 6);
  ctx.fill();
  ctx.strokeStyle = '#8b6914';
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(player.x + player.w, player.y + player.h/2, 10, -Math.PI/2, Math.PI/2);
  ctx.strokeStyle = '#C4A882';
  ctx.stroke();
  ctx.fillStyle = '#3e2723';
  ctx.beginPath();
  ctx.roundRect(player.x + 4, player.y + 4, player.w - 8, player.h - 12, 4);
  ctx.fill();

  for (let i = 0; i < 3; i++) {{
    const sx = player.x + 12 + i * 13;
    const sy = player.y - 8 + Math.sin(frameCount/10 + i) * 4;
    ctx.fillStyle = 'rgba(255,255,255,0.08)';
    ctx.beginPath();
    ctx.arc(sx, sy, 3 + Math.sin(frameCount/8 + i)*1.5, 0, Math.PI*2);
    ctx.fill();
  }}

  ctx.font = '22px serif';
  ctx.textAlign = 'center';
  for (const it of items) {{
    ctx.fillText(it.emoji, it.x, it.y);
  }}

  for (const p of particles) {{
    ctx.globalAlpha = p.life;
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 3, 0, Math.PI*2);
    ctx.fill();
    ctx.globalAlpha = 1;
  }}

  ctx.font = '15px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillStyle = '#e6edf3';
  ctx.fillText('Lives: ' + '\u2615'.repeat(Math.max(0, lives)), 12, 24);

  scoreEl.textContent = score;
  levelEl.textContent = level;
}}

function loop() {{
  update();
  draw();
  if (running) requestAnimationFrame(loop);
}}

function startGame() {{
  score = 0; level = 1; lives = 3;
  items = []; particles = []; spawnTimer = 0;
  paused = false; running = true; frameCount = 0;
  overEl.style.display = 'none';
  loop();
}}

function togglePause() {{
  if (!running) return;
  paused = !paused;
}}

function endGame() {{
  running = false;
  if (score > high) {{
    high = score;
    localStorage.setItem('game_high_{game_id}', high);
    highEl.textContent = high;
  }}
  finalEl.textContent = score;
  overEl.style.display = 'block';
}}

startGame();
</script>
</body>
</html>'''
    return html


def update_games_data(game_info):
    with open(DATA_FILE) as f:
        content = f.read()

    match = re.search(r'const\s+GAMES\s*=\s*(\[[\s\S]*?\]);', content)
    if not match:
        raise RuntimeError("Could not parse games-data.js")

    data_str = match.group(1)
    json_str = data_str.replace("'", '"').replace('true', 'true').replace('false', 'false')
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

    try:
        games = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse games data: {e}")

    games.insert(0, game_info)

    def val_to_js(v):
        if isinstance(v, str):
            return "'" + v.replace("'", "\\'") + "'"
        if isinstance(v, bool):
            return 'true' if v else 'false'
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, list):
            return '[\n' + ',\n'.join('    ' + val_to_js(item) for item in v) + '\n  ]'
        if isinstance(v, dict):
            return '{\n' + ',\n'.join(f"    {k}: {val_to_js(val)}" for k, val in v.items()) + '\n  }'
        return str(v)

    lines = ['const GAMES = [']
    for g in games:
        lines.append('  {')
        for key, val in g.items():
            lines.append(f"    {key}: {val_to_js(val)},")
        lines.append('  },')
    lines.append('];')

    cat_match = re.search(r'const\s+GAME_CATEGORIES\s*=\s*\{[\s\S]*?\};', content)
    diff_match = re.search(r'const\s+DIFFICULTY_ORDER\s*=\s*\{[\s\S]*?\};', content)

    new_content = '\n'.join(lines) + '\n\n'
    if cat_match:
        new_content += cat_match.group(0) + '\n\n'
    if diff_match:
        new_content += diff_match.group(0) + '\n'

    with open(DATA_FILE, 'w') as f:
        f.write(new_content)


def git_commit_and_push(date_str):
    os.chdir(SITE_DIR)
    subprocess.run(['git', 'add', '-A'], check=False)
    subprocess.run(['git', 'commit', '-m', f'Game Lab: daily coffee game for {date_str}'], check=False)
    subprocess.run(['git', 'push', 'origin', 'main'], check=False)


def run():
    today = datetime.now(timezone.utc)
    date_str = today.strftime("%Y-%m-%d")
    game_id = f"coffee-{today.strftime('%Y%m%d')}"

    print(f"=== Generating coffee game for {date_str} ===")

    archetype = pick_archetype()
    print(f"Selected archetype: {archetype['name']}")

    html = generate_game_html(archetype, game_id, date_str)
    game_path = GAMES_DIR / f"{game_id}.html"
    game_path.write_text(html, encoding='utf-8')
    print(f"Wrote {game_path}")

    game_info = {
        "id": game_id,
        "title": archetype["name"],
        "description": archetype["desc"],
        "category": archetype["category"],
        "thumbnail": f"linear-gradient(135deg, {archetype['gradient'][0]} 0%, {archetype['gradient'][1]} 100%)",
        "file": f"games/{game_id}.html",
        "difficulty": archetype["difficulty"],
        "emoji": archetype["emoji"],
        "createdAt": date_str,
    }
    update_games_data(game_info)
    print("Updated games-data.js")

    save_used_name(archetype["name"])
    git_commit_and_push(date_str)
    print(f"Done! Game: {archetype['name']}")


if __name__ == "__main__":
    run()
