#!/usr/bin/env python3
"""
Daily coffee-themed arcade game generator for the Game Lab.
Runs at 5 AM daily, generates a new self-contained HTML5 canvas game,
tracks used archetypes across runs to avoid repetition, updates games-data.js,
commits and pushes.

Usage:
    python daily_game_gen.py
"""
import json
import os
import random
import re
import subprocess
import sys
import base64
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

SITE_DIR = Path(__file__).parent.parent
GAMES_DIR = SITE_DIR / "games"
DATA_FILE = SITE_DIR / "js" / "games-data.js"
STATE_FILE = SITE_DIR / "scripts" / ".gamelab_state.json"
IMAGES_DIR = SITE_DIR / "assets" / "images"
FLUX_API_URL = "http://192.168.86.2:3033/v1/images/generations"
FLUX_MODEL = "flux.2-klein-9b"
FLUX_SIZE = "1024x768"

# How many days to avoid reusing the same archetype
ARCHETYPE_COOLDOWN_DAYS = 14

# ── Game archetypes with distinct mechanics ──────────────────────────────
GAME_ARCHETYPES = [
    {
        "name": "Bean Rush",
        "category": "action",
        "difficulty": "Medium",
        "emoji": "\u2615",
        "desc": "Navigate your barista through a crowded cafe, collecting specialty beans while avoiding spills and decaf traps.",
        "gradient": ["#6F4E37", "#C4A882"],
        "mechanic": "catch",
    },
    {
        "name": "Espresso Shot",
        "category": "action",
        "difficulty": "Hard",
        "emoji": "\u26a1",
        "desc": "Time your shots perfectly! Pull the lever when the pressure gauge hits the green zone. Too early or late and the shot is ruined.",
        "gradient": ["#3e2723", "#8d6e63"],
        "mechanic": "timing",
    },
    {
        "name": "Grind Master",
        "category": "puzzle",
        "difficulty": "Medium",
        "emoji": "\U0001f527",
        "desc": "Match three or more coffee beans of the same roast level to grind them into the perfect blend. Chain combos for bonus points!",
        "gradient": ["#5d4037", "#a1887f"],
        "mechanic": "match3",
    },
    {
        "name": "Pour Over Pro",
        "category": "puzzle",
        "difficulty": "Easy",
        "emoji": "\U0001fa88",
        "desc": "Guide the pour stream in spirals to evenly saturate the coffee bed. Miss a spot and you get channeling -- every drop counts!",
        "gradient": ["#4e342e", "#bcaaa4"],
        "mechanic": "trace",
    },
    {
        "name": "Latte Art Lab",
        "category": "puzzle",
        "difficulty": "Easy",
        "emoji": "\U0001f3a8",
        "desc": "Trace the latte art pattern by connecting the dots before the milk settles. Faster traces earn more stars from the customer.",
        "gradient": ["#795548", "#d7ccc8"],
        "mechanic": "trace",
    },
    {
        "name": "Roast Runner",
        "category": "action",
        "difficulty": "Hard",
        "emoji": "\U0001f525",
        "desc": "Keep the beans moving through the roaster! Dodge hotspots, control airflow, and eject each batch at the perfect roast level.",
        "gradient": ["#bf360c", "#ff7043"],
        "mechanic": "dodge",
    },
    {
        "name": "Cold Brew Defender",
        "category": "strategy",
        "difficulty": "Medium",
        "emoji": "\U0001f9ca",
        "desc": "Place towers along the brew path to filter out impurities before they reach your precious cold brew concentrate.",
        "gradient": ["#1a237e", "#5c6bc0"],
        "mechanic": "td",
    },
    {
        "name": "Cupping Challenge",
        "category": "strategy",
        "difficulty": "Easy",
        "emoji": "\U0001f375",
        "desc": "Identify the odd cup out in a triangle cupping setup. Train your palate by spotting the different origin or process.",
        "gradient": ["#33691e", "#aed581"],
        "mechanic": "memory",
    },
    {
        "name": "Milk Steamer",
        "category": "action",
        "difficulty": "Medium",
        "emoji": "\U0001f95b",
        "desc": "Steam milk to microfoam perfection. Watch the thermometer and stop at exactly the right temperature -- no scorching allowed!",
        "gradient": ["#f9a825", "#fff59d"],
        "mechanic": "timing",
    },
    {
        "name": "Barista Blitz",
        "category": "action",
        "difficulty": "Hard",
        "emoji": "\U0001f3ca",
        "desc": "Serve a rush of customers their exact orders. Memorize the queue, brew fast, and do not mix up the oat milk order!",
        "gradient": ["#c62828", "#ef5350"],
        "mechanic": "catch",
    },
    {
        "name": "Coffee Invaders",
        "category": "action",
        "difficulty": "Hard",
        "emoji": "\U0001f47d",
        "desc": "Defend the cafe from an onslaught of bad reviews and burnt beans! Shoot them down before they reach your espresso machine.",
        "gradient": ["#4a148c", "#ab47bc"],
        "mechanic": "shooter",
    },
    {
        "name": "Filter Frenzy",
        "category": "puzzle",
        "difficulty": "Medium",
        "emoji": "\U0001f9ed",
        "desc": "Stack filters of different roasts in the correct order. A light roast on top of a dark? Barista blasphemy!",
        "gradient": ["#00695c", "#4db6ac"],
        "mechanic": "stack",
    },
]


def load_state():
    """Load persisted state of used archetypes with dates."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"used": []}


def save_state(state):
    """Persist state, trimming entries older than cooldown window."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ARCHETYPE_COOLDOWN_DAYS * 2)).isoformat()
    state["used"] = [u for u in state.get("used", []) if u.get("date", "") > cutoff]
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_archetype_recently_used(state, archetype_name):
    """Check if an archetype was used within the cooldown window."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ARCHETYPE_COOLDOWN_DAYS)).isoformat()
    for u in state.get("used", []):
        if u.get("name") == archetype_name and u.get("date", "") > cutoff:
            return True
    return False


def record_archetype(state, archetype_name):
    """Record that an archetype was used today."""
    today = datetime.now(timezone.utc).isoformat()
    state.setdefault("used", []).append({"name": archetype_name, "date": today})


def pick_archetype(state):
    """Pick an archetype that hasn't been used recently."""
    available = [a for a in GAME_ARCHETYPES if not is_archetype_recently_used(state, a["name"])]
    if not available:
        # All recently used — pick the oldest one
        used = state.get("used", [])
        oldest = None
        oldest_date = None
        for a in GAME_ARCHETYPES:
            for u in used:
                if u.get("name") == a["name"]:
                    d = u.get("date", "")
                    if oldest_date is None or d < oldest_date:
                        oldest_date = d
                        oldest = a
        if oldest:
            return oldest
        return random.choice(GAME_ARCHETYPES)
    return random.choice(available)


def build_prompt(archetype):
    """Construct a LocalAI Flux prompt following xwing-site-image-design rules."""
    name = archetype["name"]
    desc = archetype["desc"]
    mechanic = archetype.get("mechanic", "catch")

    # Subject description derived from the game theme
    subject_fragments = {
        "catch": f"a barista catching falling coffee beans and espresso cups",
        "timing": f"a pressure gauge and espresso machine with steam",
        "match3": f"glowing coffee beans in a matching grid pattern",
        "trace": f"a hand pouring latte art with swirling milk patterns",
        "dodge": f"coffee beans rushing through a roasting machine with flames",
        "td": f"tower defense filters protecting a cold brew path",
        "memory": f"three coffee cups in a triangle cupping setup",
        "shooter": f"an espresso machine defending against burnt beans",
        "stack": f"stacked coffee filters forming a tower",
    }
    subject = subject_fragments.get(mechanic, f"coffee themed arcade game scene")

    prompt = (
        f"{subject}, "
        f"dark navy background, high contrast, cinematic lighting, "
        f"clean modern aesthetic, no text overlay, flat or semi-flat illustration style, "
        f"warm coffee brown and golden caramel tones with vibrant teal and cyan accents, "
        f"game-art style illustration, bold vibrant colors, no text, no letters, no words"
    )
    return prompt


def generate_thumbnail(archetype, game_id):
    """Generate a 1024x768 PNG thumbnail via LocalAI Flux and save to assets/images."""
    prompt = build_prompt(archetype)
    output_path = IMAGES_DIR / f"game-{game_id}.png"

    print(f"Generating Flux thumbnail for {game_id}...")
    print(f"Prompt: {prompt}")

    try:
        resp = requests.post(
            FLUX_API_URL,
            json={
                "model": FLUX_MODEL,
                "prompt": prompt,
                "size": FLUX_SIZE,
                "n": 1,
                "response_format": "b64_json",
            },
            timeout=300,
        )
        resp.raise_for_status()
        data = resp.json()
        b64 = data["data"][0]["b64_json"]
        img_bytes = base64.b64decode(b64)
        with open(output_path, "wb") as f:
            f.write(img_bytes)
        print(f"Thumbnail saved: {output_path} ({len(img_bytes)} bytes)")
        return f"assets/images/game-{game_id}.png"
    except Exception as e:
        print(f"WARNING: Thumbnail generation failed: {e}")
        # Fallback to gradient if image gen fails
        g1, g2 = archetype["gradient"]
        return f"linear-gradient(135deg, {g1} 0%, {g2} 100%)"


# ── Game mechanic generators ─────────────────────────────────────────────

def generate_catch_game(archetype, game_id, date_str):
    """Generate a 'catch falling items' game."""
    name = archetype["name"]
    g1, g2 = archetype["gradient"]
    return f'''<!DOCTYPE html>
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
    padding: 8px;
    overflow-x: hidden;
  }}
  h1 {{ font-size: clamp(20px, 5vw, 28px); font-weight: 700; margin: 48px 0 6px; letter-spacing: 1px; color: #C4A882; }}
  .subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 12px; text-align: center; max-width: 420px; }}
  .scores {{ display: flex; gap: 24px; margin-bottom: 12px; font-size: 15px; }}
  .scores span {{ color: #8b949e; }}
  .scores strong {{ color: #00D4AA; font-weight: 600; }}
  canvas {{ border: 2px solid #30363d; border-radius: 6px; background: #161b22; display: block; max-width: 100%; touch-action: none; }}
  .controls {{ margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }}
  button {{ background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; }}
  button:hover {{ background: #30363d; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
  .game-over {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; background: rgba(13,17,23,0.95); border: 1px solid #30363d; border-radius: 12px; padding: 28px 36px; display: none; z-index: 10; }}
  .game-over h2 {{ font-size: 22px; margin-bottom: 8px; }}
  .canvas-wrap {{ position: relative; }}
  @media (max-width: 480px) {{ .scores {{ gap: 16px; font-size: 13px; }} }}
</style>
</head>
<body>
<script src="../js/game-header.js"></script>
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
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W = 400, H = 520;
let score = 0, high = parseInt(localStorage.getItem('gh_{game_id}') || '0');
let level = 1, lives = 3, paused = false, running = false;
let player = {{ x: W/2 - 25, y: H - 55, w: 50, h: 40, speed: 5 }};
let items = [], particles = [], spawnTimer = 0;
document.getElementById('high').textContent = high;

function resize() {{
  const maxW = Math.min(window.innerWidth - 32, 400);
  const scale = maxW / 400;
  canvas.style.width = maxW + 'px';
  canvas.style.height = (520 * scale) + 'px';
}}
resize(); window.addEventListener('resize', resize);

let keys = {{}};
window.addEventListener('keydown', e => {{ keys[e.key] = true; if (['ArrowLeft','ArrowRight'].includes(e.key)) e.preventDefault(); }});
window.addEventListener('keyup', e => keys[e.key] = false);
canvas.addEventListener('touchstart', e => {{ e.preventDefault(); const r = canvas.getBoundingClientRect(); const x = (e.touches[0].clientX - r.left) * (W/r.width); keys['ArrowLeft'] = x < W/2; keys['ArrowRight'] = x >= W/2; }});
canvas.addEventListener('touchend', e => {{ e.preventDefault(); keys['ArrowLeft'] = false; keys['ArrowRight'] = false; }});

function pickItem() {{
  const good = Math.random() > 0.35;
  const pool = good ? [
    {{ emoji: '\u2615', score: 15, speed: 2.8 }}, {{ emoji: '\U0001fa88', score: 10, speed: 2.5 }}, {{ emoji: '\u26a1', score: 30, speed: 3.5 }}
  ] : [
    {{ emoji: '\U0001f9ca', score: -20, speed: 3.0 }}, {{ emoji: '\U0001f4a4', score: -15, speed: 2.8 }}
  ];
  const it = pool[Math.floor(Math.random() * pool.length)];
  return {{ ...it, x: Math.random() * (W - 30) + 15, y: -30, good }};
}}

function update() {{
  if (!running || paused) return;
  if (keys['ArrowLeft'] || keys['a']) player.x -= player.speed;
  if (keys['ArrowRight'] || keys['d']) player.x += player.speed;
  player.x = Math.max(0, Math.min(W - player.w, player.x));
  spawnTimer++;
  if (spawnTimer >= Math.max(12, 40 - level * 2)) {{ spawnTimer = 0; items.push(pickItem()); }}
  for (let i = items.length - 1; i >= 0; i--) {{
    const it = items[i]; it.y += it.speed + level * 0.2;
    if (it.y + 18 > player.y && it.y < player.y + player.h && it.x + 12 > player.x && it.x - 12 < player.x + player.w) {{
      score += it.score; if (score < 0) score = 0;
      items.splice(i, 1);
      if (!it.good) {{ lives--; if (lives <= 0) endGame(); }}
      continue;
    }}
    if (it.y > H && it.good) {{ lives--; if (lives <= 0) endGame(); items.splice(i, 1); }}
    else if (it.y > H) items.splice(i, 1);
  }}
  level = 1 + Math.floor(score / 120);
}}

function draw() {{
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#C4A882';
  ctx.fillRect(player.x, player.y, player.w, player.h);
  ctx.font = '22px serif'; ctx.textAlign = 'center';
  for (const it of items) ctx.fillText(it.emoji, it.x, it.y);
  ctx.font = '15px sans-serif'; ctx.textAlign = 'left';
  ctx.fillText('Lives: ' + '\u2615'.repeat(Math.max(0, lives)), 12, 24);
  document.getElementById('score').textContent = score;
  document.getElementById('level').textContent = level;
}}

function loop() {{ update(); draw(); if (running) requestAnimationFrame(loop); }}
function startGame() {{ score = 0; level = 1; lives = 3; items = []; paused = false; running = true; document.getElementById('over').style.display = 'none'; loop(); }}
function togglePause() {{ if (running) paused = !paused; }}
function endGame() {{ running = false; if (score > high) {{ high = score; localStorage.setItem('gh_{game_id}', high); document.getElementById('high').textContent = high; }} document.getElementById('final').textContent = score; document.getElementById('over').style.display = 'block'; }}
startGame();
</script>
</body>
</html>
'''


def generate_timing_game(archetype, game_id, date_str):
    """Generate a timing-based game (stop the gauge in the zone)."""
    name = archetype["name"]
    g1, g2 = archetype["gradient"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 8px; }}
  h1 {{ font-size: clamp(20px, 5vw, 28px); font-weight: 700; margin: 48px 0 6px; letter-spacing: 1px; color: #C4A882; }}
  .subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 16px; text-align: center; max-width: 420px; }}
  .gauge-wrap {{ width: 320px; max-width: 90vw; height: 40px; background: #161b22; border: 2px solid #30363d; border-radius: 20px; position: relative; overflow: hidden; margin-bottom: 20px; }}
  .gauge-zone {{ position: absolute; left: 35%; width: 30%; height: 100%; background: rgba(0, 212, 170, 0.25); }}
  .gauge-needle {{ position: absolute; top: 0; width: 4px; height: 100%; background: #00D4AA; transition: left 0.05s linear; }}
  .scores {{ display: flex; gap: 24px; margin-bottom: 16px; font-size: 15px; }}
  .scores strong {{ color: #00D4AA; }}
  button {{ background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 10px 28px; border-radius: 6px; font-size: 16px; cursor: pointer; margin: 4px; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
  .feedback {{ font-size: 18px; margin: 10px 0; height: 28px; font-weight: 600; }}
  .perfect {{ color: #00D4AA; }} .good {{ color: #C4A882; }} .miss {{ color: #e74c3c; }}
  .streak {{ color: #8b949e; font-size: 14px; margin-top: 4px; }}
</style>
</head>
<body>
<script src="../js/game-header.js"></script>
<h1>{archetype["emoji"]} {name}</h1>
<p class="subtitle">{archetype["desc"]}</p>
<div class="scores">
  <span>Score: <strong id="score">0</strong></span>
  <span>High: <strong id="high">0</strong></span>
  <span>Round: <strong id="round">1</strong></span>
</div>
<div class="gauge-wrap">
  <div class="gauge-zone"></div>
  <div class="gauge-needle" id="needle" style="left:0%"></div>
</div>
<div class="feedback" id="feedback"></div>
<div>
  <button class="primary" id="stopBtn" onclick="stopGauge()">STOP!</button>
  <button onclick="startRound()">New Game</button>
</div>
<p class="streak">Streak: <span id="streak">0</span> | Best Streak: <span id="bestStreak">0</span></p>
<script>
let score = 0, high = parseInt(localStorage.getItem('gh_{game_id}') || '0');
let round = 1, streak = 0, bestStreak = parseInt(localStorage.getItem('bs_{game_id}') || '0');
let needlePos = 0, needleDir = 1, needleSpeed = 1.2, running = false;
document.getElementById('high').textContent = high;
document.getElementById('bestStreak').textContent = bestStreak;

function updateNeedle() {{
  if (!running) return;
  needlePos += needleSpeed * needleDir;
  if (needlePos >= 100) {{ needlePos = 100; needleDir = -1; }}
  if (needlePos <= 0) {{ needlePos = 0; needleDir = 1; }}
  document.getElementById('needle').style.left = needlePos + '%';
  requestAnimationFrame(updateNeedle);
}}

function stopGauge() {{
  if (!running) return;
  running = false;
  const inZone = needlePos >= 35 && needlePos <= 65;
  const nearZone = (needlePos >= 25 && needlePos < 35) || (needlePos > 65 && needlePos <= 75);
  const fb = document.getElementById('feedback');
  if (inZone) {{
    const points = 100 + Math.round((60 - Math.abs(needlePos - 50)) * 2);
    score += points; streak++;
    fb.textContent = `PERFECT! +${{points}}`; fb.className = 'feedback perfect';
  }} else if (nearZone) {{
    score += 30; streak = 0;
    fb.textContent = 'Good +30'; fb.className = 'feedback good';
  }} else {{
    streak = 0;
    fb.textContent = 'Miss!'; fb.className = 'feedback miss';
  }}
  if (streak > bestStreak) {{ bestStreak = streak; localStorage.setItem('bs_{game_id}', bestStreak); document.getElementById('bestStreak').textContent = bestStreak; }}
  document.getElementById('score').textContent = score;
  document.getElementById('streak').textContent = streak;
  if (score > high) {{ high = score; localStorage.setItem('gh_{game_id}', high); document.getElementById('high').textContent = high; }}
  setTimeout(startRound, 900);
}}

function startRound() {{
  round++;
  needleSpeed = 1.2 + round * 0.15;
  document.getElementById('round').textContent = round;
  document.getElementById('feedback').textContent = '';
  running = true;
  updateNeedle();
}}

function startGame() {{ score = 0; round = 1; streak = 0; needlePos = 0; needleDir = 1; document.getElementById('score').textContent = 0; document.getElementById('streak').textContent = 0; document.getElementById('round').textContent = 1; startRound(); }}

startGame();
</script>
</body>
</html>
'''


def generate_dodge_game(archetype, game_id, date_str):
    """Generate a dodging / runner game."""
    name = archetype["name"]
    g1, g2 = archetype["gradient"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 8px; }}
  h1 {{ font-size: clamp(20px, 5vw, 28px); font-weight: 700; margin: 48px 0 6px; letter-spacing: 1px; color: #C4A882; }}
  .subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 12px; text-align: center; max-width: 420px; }}
  .scores {{ display: flex; gap: 24px; margin-bottom: 12px; font-size: 15px; }}
  .scores strong {{ color: #00D4AA; }}
  canvas {{ border: 2px solid #30363d; border-radius: 6px; background: #161b22; display: block; max-width: 100%; touch-action: none; }}
  .controls {{ margin-top: 14px; display: flex; gap: 10px; }}
  button {{ background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
  .game-over {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; background: rgba(13,17,23,0.95); border: 1px solid #30363d; border-radius: 12px; padding: 28px; display: none; }}
  .canvas-wrap {{ position: relative; }}
</style>
</head>
<body>
<script src="../js/game-header.js"></script>
<h1>{archetype["emoji"]} {name}</h1>
<p class="subtitle">{archetype["desc"]}</p>
<div class="scores">
  <span>Score: <strong id="score">0</strong></span>
  <span>High: <strong id="high">0</strong></span>
  <span>Speed: <strong id="speed">1x</strong></span>
</div>
<div class="canvas-wrap">
  <canvas id="game" width="360" height="540"></canvas>
  <div class="game-over" id="over">
    <h2>Too Hot!</h2>
    <p>Score: <strong id="final">0</strong></p>
    <button class="primary" onclick="startGame()">Retry</button>
  </div>
</div>
<div class="controls">
  <button onclick="startGame()">New Game</button>
  <button onclick="togglePause()">Pause</button>
</div>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W = 360, H = 540;
let score = 0, high = parseInt(localStorage.getItem('gh_{game_id}') || '0');
let player, obstacles = [], particles = [], running = false, paused = false, speedMult = 1;
document.getElementById('high').textContent = high;

function resize() {{
  const maxW = Math.min(window.innerWidth - 32, 360);
  const scale = maxW / 360;
  canvas.style.width = maxW + 'px';
  canvas.style.height = (540 * scale) + 'px';
}}
resize(); window.addEventListener('resize', resize);

let keys = {{}};
window.addEventListener('keydown', e => {{ keys[e.key] = true; if (['ArrowLeft','ArrowRight'].includes(e.key)) e.preventDefault(); }});
window.addEventListener('keyup', e => keys[e.key] = false);
canvas.addEventListener('touchstart', e => {{ e.preventDefault(); const r = canvas.getBoundingClientRect(); const x = (e.touches[0].clientX - r.left) * (W/r.width); keys['ArrowLeft'] = x < W/2; keys['ArrowRight'] = x >= W/2; }});
canvas.addEventListener('touchend', e => {{ e.preventDefault(); keys['ArrowLeft'] = false; keys['ArrowRight'] = false; }});

function spawnObstacle() {{
  const w = 40 + Math.random() * 50;
  const x = Math.random() * (W - w);
  obstacles.push({{ x, y: -30, w, h: 20, speed: 2.5 + speedMult }});
}}

function update() {{
  if (!running || paused) return;
  if (keys['ArrowLeft'] || keys['a']) player.x -= player.speed;
  if (keys['ArrowRight'] || keys['d']) player.x += player.speed;
  player.x = Math.max(0, Math.min(W - player.w, player.x));
  score++;
  speedMult = 1 + Math.floor(score / 300) * 0.3;
  document.getElementById('speed').textContent = speedMult.toFixed(1) + 'x';
  if (Math.random() < 0.02 + speedMult * 0.005) spawnObstacle();
  for (let i = obstacles.length - 1; i >= 0; i--) {{
    const ob = obstacles[i]; ob.y += ob.speed;
    if (ob.y > H) {{ obstacles.splice(i, 1); continue; }}
    if (player.x < ob.x + ob.w && player.x + player.w > ob.x && player.y < ob.y + ob.h && player.y + player.h > ob.y) {{
      endGame(); return;
    }}
  }}
  document.getElementById('score').textContent = score;
}}

function draw() {{
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#bf360c';
  ctx.fillRect(player.x, player.y, player.w, player.h);
  ctx.fillStyle = '#ff7043';
  for (const ob of obstacles) ctx.fillRect(ob.x, ob.y, ob.w, ob.h);
}}

function loop() {{ update(); draw(); if (running) requestAnimationFrame(loop); }}
function startGame() {{ score = 0; speedMult = 1; player = {{ x: W/2 - 18, y: H - 60, w: 36, h: 36, speed: 5 }}; obstacles = []; paused = false; running = true; document.getElementById('over').style.display = 'none'; loop(); }}
function togglePause() {{ if (running) paused = !paused; }}
function endGame() {{ running = false; if (score > high) {{ high = score; localStorage.setItem('gh_{game_id}', high); document.getElementById('high').textContent = high; }} document.getElementById('final').textContent = score; document.getElementById('over').style.display = 'block'; }}
startGame();
</script>
</body>
</html>
'''


def generate_shooter_game(archetype, game_id, date_str):
    """Generate a simple shooter / defender game."""
    name = archetype["name"]
    g1, g2 = archetype["gradient"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 8px; }}
  h1 {{ font-size: clamp(20px, 5vw, 28px); font-weight: 700; margin: 48px 0 6px; letter-spacing: 1px; color: #C4A882; }}
  .subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 12px; text-align: center; max-width: 420px; }}
  .scores {{ display: flex; gap: 24px; margin-bottom: 12px; font-size: 15px; }}
  .scores strong {{ color: #00D4AA; }}
  canvas {{ border: 2px solid #30363d; border-radius: 6px; background: #161b22; display: block; max-width: 100%; touch-action: none; }}
  .controls {{ margin-top: 14px; display: flex; gap: 10px; }}
  button {{ background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
  .game-over {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; background: rgba(13,17,23,0.95); border: 1px solid #30363d; border-radius: 12px; padding: 28px; display: none; }}
  .canvas-wrap {{ position: relative; }}
</style>
</head>
<body>
<script src="../js/game-header.js"></script>
<h1>{archetype["emoji"]} {name}</h1>
<p class="subtitle">{archetype["desc"]}</p>
<div class="scores">
  <span>Score: <strong id="score">0</strong></span>
  <span>High: <strong id="high">0</strong></span>
  <span>Wave: <strong id="wave">1</strong></span>
</div>
<div class="canvas-wrap">
  <canvas id="game" width="400" height="520"></canvas>
  <div class="game-over" id="over">
    <h2>Cafe Overrun!</h2>
    <p>Score: <strong id="final">0</strong></p>
    <button class="primary" onclick="startGame()">Retry</button>
  </div>
</div>
<div class="controls">
  <button onclick="startGame()">New Game</button>
  <button onclick="togglePause()">Pause</button>
</div>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W = 400, H = 520;
let score = 0, high = parseInt(localStorage.getItem('gh_{game_id}') || '0');
let player, bullets = [], enemies = [], particles = [], running = false, paused = false, wave = 1;
document.getElementById('high').textContent = high;

function resize() {{
  const maxW = Math.min(window.innerWidth - 32, 400);
  const scale = maxW / 400;
  canvas.style.width = maxW + 'px';
  canvas.style.height = (520 * scale) + 'px';
}}
resize(); window.addEventListener('resize', resize);

let keys = {{}};
window.addEventListener('keydown', e => {{ keys[e.key] = true; if (['ArrowLeft','ArrowRight',' '].includes(e.key)) e.preventDefault(); }});
window.addEventListener('keyup', e => keys[e.key] = false);
canvas.addEventListener('touchstart', e => {{ e.preventDefault(); const r = canvas.getBoundingClientRect(); const x = (e.touches[0].clientX - r.left) * (W/r.width); keys['ArrowLeft'] = x < W/2; keys['ArrowRight'] = x >= W/2; if (e.touches.length === 2) keys['shoot'] = true; }});
canvas.addEventListener('touchend', e => {{ e.preventDefault(); keys['ArrowLeft'] = false; keys['ArrowRight'] = false; keys['shoot'] = false; }});

function spawnWave() {{
  const cols = 3 + wave;
  const rows = 2 + Math.floor(wave / 2);
  for (let c = 0; c < cols; c++) for (let r = 0; r < rows; r++)
    enemies.push({{ x: 30 + c * 50, y: 30 + r * 35, w: 30, h: 24, speed: 0.5 + wave * 0.1, dir: 1, hp: 1 }});
}}

function update() {{
  if (!running || paused) return;
  if (keys['ArrowLeft'] || keys['a']) player.x -= player.speed;
  if (keys['ArrowRight'] || keys['d']) player.x += player.speed;
  player.x = Math.max(0, Math.min(W - player.w, player.x));
  if (keys[' '] || keys['shoot']) {{
    if (!player.cooldown) {{ bullets.push({{ x: player.x + player.w/2, y: player.y, speed: 6 }}); player.cooldown = 12; }}
  }}
  if (player.cooldown > 0) player.cooldown--;
  for (const b of bullets) b.y -= b.speed;
  bullets = bullets.filter(b => b.y > -10);
  let hitEdge = false;
  for (const e of enemies) {{
    e.x += e.speed * e.dir;
    if (e.x <= 0 || e.x + e.w >= W) hitEdge = true;
  }}
  if (hitEdge) enemies.forEach(e => {{ e.dir *= -1; e.y += 12; }});
  for (let bi = bullets.length - 1; bi >= 0; bi--) {{
    const b = bullets[bi];
    for (let ei = enemies.length - 1; ei >= 0; ei--) {{
      const e = enemies[ei];
      if (b.x > e.x && b.x < e.x + e.w && b.y > e.y && b.y < e.y + e.h) {{
        enemies.splice(ei, 1); bullets.splice(bi, 1); score += 50; break;
      }}
    }}
  }}
  for (const e of enemies) {{
    if (e.y + e.h >= player.y) {{ endGame(); return; }}
  }}
  if (enemies.length === 0) {{ wave++; spawnWave(); document.getElementById('wave').textContent = wave; }}
  document.getElementById('score').textContent = score;
}}

function draw() {{
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#00D4AA';
  ctx.fillRect(player.x, player.y, player.w, player.h);
  ctx.fillStyle = '#ab47bc';
  for (const e of enemies) ctx.fillRect(e.x, e.y, e.w, e.h);
  ctx.fillStyle = '#fff';
  for (const b of bullets) ctx.fillRect(b.x - 1, b.y, 2, 8);
}}

function loop() {{ update(); draw(); if (running) requestAnimationFrame(loop); }}
function startGame() {{ score = 0; wave = 1; player = {{ x: W/2 - 18, y: H - 50, w: 36, h: 24, speed: 5, cooldown: 0 }}; bullets = []; enemies = []; spawnWave(); paused = false; running = true; document.getElementById('over').style.display = 'none'; loop(); }}
function togglePause() {{ if (running) paused = !paused; }}
function endGame() {{ running = false; if (score > high) {{ high = score; localStorage.setItem('gh_{game_id}', high); document.getElementById('high').textContent = high; }} document.getElementById('final').textContent = score; document.getElementById('over').style.display = 'block'; }}
startGame();
</script>
</body>
</html>
'''


def generate_memory_game(archetype, game_id, date_str):
    """Generate a memory / cupping identification game."""
    name = archetype["name"]
    g1, g2 = archetype["gradient"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 8px; }}
  h1 {{ font-size: clamp(20px, 5vw, 28px); font-weight: 700; margin: 48px 0 6px; letter-spacing: 1px; color: #C4A882; }}
  .subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 16px; text-align: center; max-width: 420px; }}
  .grid {{ display: grid; grid-template-columns: repeat(3, 90px); gap: 12px; margin-bottom: 16px; }}
  .cup {{ width: 90px; height: 90px; background: #161b22; border: 2px solid #30363d; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 36px; cursor: pointer; transition: all 0.2s; user-select: none; }}
  .cup:hover {{ border-color: #00D4AA; }}
  .cup.selected {{ border-color: #00D4AA; background: #00D4AA11; }}
  .cup.wrong {{ border-color: #e74c3c; background: #e74c3c11; animation: shake 0.3s; }}
  .cup.correct {{ border-color: #00D4AA; background: #00D4AA22; }}
  @keyframes shake {{ 0%,100% {{ transform: translateX(0); }} 25% {{ transform: translateX(-5px); }} 75% {{ transform: translateX(5px); }} }}
  .scores {{ display: flex; gap: 24px; margin-bottom: 12px; font-size: 15px; }}
  .scores strong {{ color: #00D4AA; }}
  button {{ background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
  .feedback {{ font-size: 16px; margin: 8px 0; height: 24px; font-weight: 600; }}
</style>
</head>
<body>
<script src="../js/game-header.js"></script>
<h1>{archetype["emoji"]} {name}</h1>
<p class="subtitle">{archetype["desc"]}</p>
<div class="scores">
  <span>Score: <strong id="score">0</strong></span>
  <span>High: <strong id="high">0</strong></span>
  <span>Round: <strong id="round">1</strong></span>
</div>
<div class="feedback" id="feedback">Spot the different origin!</div>
<div class="grid" id="grid"></div>
<div>
  <button class="primary" onclick="nextRound()">Next Round</button>
  <button onclick="startGame()">New Game</button>
</div>
<script>
let score = 0, high = parseInt(localStorage.getItem('gh_{game_id}') || '0');
let round = 1, oddIndex = 0, canClick = false;
document.getElementById('high').textContent = high;

const origins = ['\u2615', '\u2615', '\u2615', '\u2615', '\u2615', '\u2615', '\u2615', '\u2615'];
const oddOrigins = ['\U0001f375', '\U0001f9cb', '\U0001fad6', '\u26fe'];

function buildGrid() {{
  oddIndex = Math.floor(Math.random() * 9);
  const odd = oddOrigins[Math.floor(Math.random() * oddOrigins.length)];
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  for (let i = 0; i < 9; i++) {{
    const cup = document.createElement('div');
    cup.className = 'cup';
    cup.textContent = i === oddIndex ? odd : '\u2615';
    cup.dataset.index = i;
    cup.onclick = () => handleClick(i, cup);
    grid.appendChild(cup);
  }}
  canClick = true;
  document.getElementById('feedback').textContent = 'Spot the different origin!';
  document.getElementById('feedback').style.color = '#e6edf3';
}}

function handleClick(index, el) {{
  if (!canClick) return;
  canClick = false;
  if (index === oddIndex) {{
    el.classList.add('correct');
    score += 100 + round * 10;
    document.getElementById('feedback').textContent = 'Correct! Great palate!'; document.getElementById('feedback').style.color = '#00D4AA';
    if (score > high) {{ high = score; localStorage.setItem('gh_{game_id}', high); document.getElementById('high').textContent = high; }}
  }} else {{
    el.classList.add('wrong');
    document.getElementById('feedback').textContent = 'Nope! That one was the same.'; document.getElementById('feedback').style.color = '#e74c3c';
  }}
  document.getElementById('score').textContent = score;
}}

function nextRound() {{ round++; document.getElementById('round').textContent = round; buildGrid(); }}
function startGame() {{ score = 0; round = 1; document.getElementById('score').textContent = 0; document.getElementById('round').textContent = 1; buildGrid(); }}

startGame();
</script>
</body>
</html>
'''


def generate_trace_game(archetype, game_id, date_str):
    """Generate a tracing / drawing game."""
    name = archetype["name"]
    g1, g2 = archetype["gradient"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 8px; }}
  h1 {{ font-size: clamp(20px, 5vw, 28px); font-weight: 700; margin: 48px 0 6px; letter-spacing: 1px; color: #C4A882; }}
  .subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 12px; text-align: center; max-width: 420px; }}
  .scores {{ display: flex; gap: 24px; margin-bottom: 12px; font-size: 15px; }}
  .scores strong {{ color: #00D4AA; }}
  canvas {{ border: 2px solid #30363d; border-radius: 6px; background: #161b22; display: block; max-width: 100%; touch-action: none; cursor: crosshair; }}
  .controls {{ margin-top: 14px; display: flex; gap: 10px; }}
  button {{ background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
</style>
</head>
<body>
<script src="../js/game-header.js"></script>
<h1>{archetype["emoji"]} {name}</h1>
<p class="subtitle">{archetype["desc"]}</p>
<div class="scores">
  <span>Score: <strong id="score">0</strong></span>
  <span>High: <strong id="high">0</strong></span>
  <span>Target: <strong id="target">1</strong></span>
</div>
<canvas id="game" width="400" height="400"></canvas>
<div class="controls">
  <button class="primary" onclick="nextTarget()">Next Pattern</button>
  <button onclick="startGame()">New Game</button>
</div>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W = 400, H = 400;
let score = 0, high = parseInt(localStorage.getItem('gh_{game_id}') || '0');
let targetPoints = [], drawnPoints = [], targetIndex = 0, drawing = false;
document.getElementById('high').textContent = high;

function resize() {{
  const maxW = Math.min(window.innerWidth - 32, 400);
  const scale = maxW / 400;
  canvas.style.width = maxW + 'px';
  canvas.style.height = maxW + 'px';
}}
resize(); window.addEventListener('resize', resize);

const patterns = [
  [{{x:200,y:80}},{{x:280,y:200}},{{x:200,y:320}},{{x:120,y:200}}],
  [{{x:200,y:60}},{{x:260,y:140}},{{x:340,y:180}},{{x:260,y:260}},{{x:200,y:340}},{{x:140,y:260}},{{x:60,y:180}},{{x:140,y:140}}],
  [{{x:100,y:100}},{{x:300,y:100}},{{x:300,y:300}},{{x:100,y:300}}],
  [{{x:200,y:50}},{{x:250,y:150}},{{x:350,y:160}},{{x:270,y:230}},{{x:300,y:340}},{{x:200,y:280}},{{x:100,y:340}},{{x:130,y:230}},{{x:50,y:160}},{{x:150,y:150}}],
];

function loadPattern(idx) {{
  targetPoints = patterns[idx % patterns.length].map(p => ({{...p}}));
  drawnPoints = [];
  targetIndex = 0;
  drawing = false;
  draw();
}}

function getPos(e) {{
  const r = canvas.getBoundingClientRect();
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  return {{ x: (clientX - r.left) * (W/r.width), y: (clientY - r.top) * (H/r.height) }};
}}

function dist(a,b) {{ return Math.hypot(a.x-b.x, a.y-b.y); }}

function draw() {{
  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle = 'rgba(196,168,130,0.4)'; ctx.lineWidth = 2;
  ctx.beginPath(); targetPoints.forEach((p,i) => {{ if(i===0) ctx.moveTo(p.x,p.y); else ctx.lineTo(p.x,p.y); }}); ctx.closePath(); ctx.stroke();
  targetPoints.forEach((p,i) => {{
    ctx.fillStyle = i === targetIndex ? '#00D4AA' : '#8b949e';
    ctx.beginPath(); ctx.arc(p.x, p.y, i === targetIndex ? 8 : 4, 0, Math.PI*2); ctx.fill();
  }});
  if (drawnPoints.length > 1) {{
    ctx.strokeStyle = '#00D4AA'; ctx.lineWidth = 3; ctx.lineCap = 'round';
    ctx.beginPath(); drawnPoints.forEach((p,i) => {{ if(i===0) ctx.moveTo(p.x,p.y); else ctx.lineTo(p.x,p.y); }}); ctx.stroke();
  }}
}}

function handleStart(e) {{
  e.preventDefault();
  const pos = getPos(e);
  if (dist(pos, targetPoints[targetIndex]) < 20) {{ drawing = true; drawnPoints = [pos]; }}
}}
function handleMove(e) {{
  e.preventDefault();
  if (!drawing) return;
  const pos = getPos(e);
  if (dist(pos, targetPoints[targetIndex + 1]) < 20) {{ targetIndex++; drawnPoints.push(pos); if (targetIndex >= targetPoints.length - 1) {{ drawing = false; score += 150; document.getElementById('score').textContent = score; if (score > high) {{ high = score; localStorage.setItem('gh_{game_id}', high); document.getElementById('high').textContent = high; }} }} }}
  else {{ drawnPoints.push(pos); }}
  draw();
}}
function handleEnd(e) {{ e.preventDefault(); drawing = false; }}

canvas.addEventListener('mousedown', handleStart);
canvas.addEventListener('mousemove', handleMove);
canvas.addEventListener('mouseup', handleEnd);
canvas.addEventListener('touchstart', handleStart, {{passive:false}});
canvas.addEventListener('touchmove', handleMove, {{passive:false}});
canvas.addEventListener('touchend', handleEnd, {{passive:false}});

let currentPattern = 0;
function nextTarget() {{ currentPattern++; document.getElementById('target').textContent = currentPattern + 1; loadPattern(currentPattern); }}
function startGame() {{ score = 0; currentPattern = 0; document.getElementById('score').textContent = 0; document.getElementById('target').textContent = 1; loadPattern(0); }}

startGame();
</script>
</body>
</html>
'''


def generate_stack_game(archetype, game_id, date_str):
    """Generate a stacking / tower-building game."""
    name = archetype["name"]
    g1, g2 = archetype["gradient"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 8px; }}
  h1 {{ font-size: clamp(20px, 5vw, 28px); font-weight: 700; margin: 48px 0 6px; letter-spacing: 1px; color: #C4A882; }}
  .subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 12px; text-align: center; max-width: 420px; }}
  .scores {{ display: flex; gap: 24px; margin-bottom: 12px; font-size: 15px; }}
  .scores strong {{ color: #00D4AA; }}
  canvas {{ border: 2px solid #30363d; border-radius: 6px; background: #161b22; display: block; max-width: 100%; touch-action: none; }}
  .controls {{ margin-top: 14px; display: flex; gap: 10px; }}
  button {{ background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
  .game-over {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; background: rgba(13,17,23,0.95); border: 1px solid #30363d; border-radius: 12px; padding: 28px; display: none; }}
  .canvas-wrap {{ position: relative; }}
</style>
</head>
<body>
<script src="../js/game-header.js"></script>
<h1>{archetype["emoji"]} {name}</h1>
<p class="subtitle">{archetype["desc"]}</p>
<div class="scores">
  <span>Score: <strong id="score">0</strong></span>
  <span>High: <strong id="high">0</strong></span>
  <span>Height: <strong id="height">0</strong></span>
</div>
<div class="canvas-wrap">
  <canvas id="game" width="360" height="520"></canvas>
  <div class="game-over" id="over">
    <h2>Stack Collapsed!</h2>
    <p>Score: <strong id="final">0</strong></p>
    <button class="primary" onclick="startGame()">Retry</button>
  </div>
</div>
<div class="controls">
  <button class="primary" onclick="dropBlock()">DROP</button>
  <button onclick="startGame()">New Game</button>
</div>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W = 360, H = 520;
let score = 0, high = parseInt(localStorage.getItem('gh_{game_id}') || '0');
let blocks = [], currentBlock = null, running = false, speed = 2, dir = 1;
document.getElementById('high').textContent = high;

function resize() {{
  const maxW = Math.min(window.innerWidth - 32, 360);
  const scale = maxW / 360;
  canvas.style.width = maxW + 'px';
  canvas.style.height = (520 * scale) + 'px';
}}
resize(); window.addEventListener('resize', resize);

const colors = ['#6F4E37', '#8d6e63', '#a1887f', '#5d4037', '#4e342e'];

function newBlock() {{
  const prev = blocks.length > 0 ? blocks[blocks.length - 1] : {{ x: 80, w: 200 }};
  const w = Math.max(40, prev.w - 8);
  currentBlock = {{ x: 0, y: 60, w: w, h: 24, color: colors[blocks.length % colors.length] }};
  speed = 2 + blocks.length * 0.25;
}}

function dropBlock() {{
  if (!running || !currentBlock) return;
  const prev = blocks.length > 0 ? blocks[blocks.length - 1] : {{ x: 0, w: W }};
  const overlap = Math.max(0, Math.min(currentBlock.x + currentBlock.w, prev.x + prev.w) - Math.max(currentBlock.x, prev.x));
  if (overlap <= 0) {{ endGame(); return; }}
  const diff = currentBlock.x - prev.x;
  currentBlock.x = Math.max(currentBlock.x, prev.x);
  currentBlock.w = overlap;
  score += Math.round(overlap * 2);
  blocks.push({{ x: currentBlock.x, y: H - 40 - blocks.length * 24, w: currentBlock.w, h: 24, color: currentBlock.color }});
  if (score > high) {{ high = score; localStorage.setItem('gh_{game_id}', high); document.getElementById('high').textContent = high; }}
  document.getElementById('score').textContent = score;
  document.getElementById('height').textContent = blocks.length;
  if (blocks.length >= 18) {{ endGame(true); return; }}
  newBlock();
}}

function update() {{
  if (!running || !currentBlock) return;
  currentBlock.x += speed * dir;
  if (currentBlock.x <= 0) {{ currentBlock.x = 0; dir = 1; }}
  if (currentBlock.x + currentBlock.w >= W) {{ currentBlock.x = W - currentBlock.w; dir = -1; }}
}}

function draw() {{
  ctx.clearRect(0, 0, W, H);
  for (const b of blocks) {{ ctx.fillStyle = b.color; ctx.fillRect(b.x, b.y, b.w, b.h); ctx.strokeStyle = '#C4A882'; ctx.strokeRect(b.x, b.y, b.w, b.h); }}
  if (currentBlock) {{ ctx.fillStyle = currentBlock.color; ctx.fillRect(currentBlock.x, currentBlock.y, currentBlock.w, currentBlock.h); }}
}}

function loop() {{ update(); draw(); if (running) requestAnimationFrame(loop); }}
function startGame() {{ score = 0; blocks = []; running = true; document.getElementById('score').textContent = 0; document.getElementById('height').textContent = 0; document.getElementById('over').style.display = 'none'; newBlock(); loop(); }}
function endGame(win=false) {{ running = false; document.getElementById('final').textContent = score; document.getElementById('over').querySelector('h2').textContent = win ? 'Perfect Stack!' : 'Stack Collapsed!'; document.getElementById('over').style.display = 'block'; }}

window.addEventListener('keydown', e => {{ if (e.code === 'Space') {{ e.preventDefault(); dropBlock(); }} }});
canvas.addEventListener('touchstart', e => {{ e.preventDefault(); dropBlock(); }});

startGame();
</script>
</body>
</html>
'''


def generate_td_game(archetype, game_id, date_str):
    """Generate a tower defense game."""
    name = archetype["name"]
    g1, g2 = archetype["gradient"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 8px; }}
  h1 {{ font-size: clamp(20px, 5vw, 28px); font-weight: 700; margin: 48px 0 6px; letter-spacing: 1px; color: #C4A882; }}
  .subtitle {{ font-size: 13px; color: #8b949e; margin-bottom: 12px; text-align: center; max-width: 420px; }}
  .scores {{ display: flex; gap: 24px; margin-bottom: 12px; font-size: 15px; }}
  .scores strong {{ color: #00D4AA; }}
  canvas {{ border: 2px solid #30363d; border-radius: 6px; background: #161b22; display: block; max-width: 100%; touch-action: none; }}
  .controls {{ margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }}
  button {{ background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer; }}
  button.primary {{ background: #00D4AA22; border-color: #00D4AA55; color: #00D4AA; }}
  .game-over {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; background: rgba(13,17,23,0.95); border: 1px solid #30363d; border-radius: 12px; padding: 28px; display: none; }}
  .canvas-wrap {{ position: relative; }}
</style>
</head>
<body>
<script src="../js/game-header.js"></script>
<h1>{archetype["emoji"]} {name}</h1>
<p class="subtitle">{archetype["desc"]}</p>
<div class="scores">
  <span>Score: <strong id="score">0</strong></span>
  <span>Health: <strong id="health">20</strong></span>
  <span>Wave: <strong id="wave">1</strong></span>
</div>
<div class="canvas-wrap">
  <canvas id="game" width="400" height="400"></canvas>
  <div class="game-over" id="over">
    <h2>Brew Contaminated!</h2>
    <p>Score: <strong id="final">0</strong></p>
    <button class="primary" onclick="startGame()">Retry</button>
  </div>
</div>
<div class="controls">
  <button onclick="placeTower()">Place Filter ($50)</button>
  <button onclick="startGame()">New Game</button>
</div>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let W = 400, H = 400;
let score = 0, health = 20, wave = 1, money = 100;
let enemies = [], towers = [], projectiles = [], running = false;

function resize() {{
  const maxW = Math.min(window.innerWidth - 32, 400);
  const scale = maxW / 400;
  canvas.style.width = maxW + 'px';
  canvas.style.height = maxW + 'px';
}}
resize(); window.addEventListener('resize', resize);

const path = [{{x:0,y:80}},{{x:120,y:80}},{{x:120,y:200}},{{x:280,y:200}},{{x:280,y:320}},{{x:400,y:320}}];

function spawnEnemy() {{
  enemies.push({{ x: 0, y: 80, hp: 2 + wave, maxHp: 2 + wave, speed: 0.8 + wave * 0.1, pathIdx: 0, reward: 10 }});
}}

function update() {{
  if (!running) return;
  for (const e of enemies) {{
    const target = path[Math.min(e.pathIdx + 1, path.length - 1)];
    const dx = target.x - e.x, dy = target.y - e.y;
    const d = Math.hypot(dx, dy);
    if (d < e.speed) {{ e.pathIdx++; if (e.pathIdx >= path.length - 1) {{ health--; e.hp = 0; }} else {{ e.x = path[e.pathIdx].x; e.y = path[e.pathIdx].y; }} }}
    else {{ e.x += (dx/d) * e.speed; e.y += (dy/d) * e.speed; }}
  }}
  enemies = enemies.filter(e => e.hp > 0);
  for (const t of towers) {{
    if (t.cooldown > 0) t.cooldown--;
    if (t.cooldown <= 0) {{
      const target = enemies.find(e => Math.hypot(e.x - t.x, e.y - t.y) < 80);
      if (target) {{ projectiles.push({{ x: t.x, y: t.y, tx: target.x, ty: target.y, speed: 4 }}); t.cooldown = 30; }}
    }}
  }}
  for (const p of projectiles) {{
    const dx = p.tx - p.x, dy = p.ty - p.y;
    const d = Math.hypot(dx, dy);
    if (d < p.speed) {{ p.hit = true; const target = enemies.find(e => Math.hypot(e.x - p.tx, e.y - p.ty) < 20); if (target) {{ target.hp--; if (target.hp <= 0) {{ score += target.reward; money += target.reward; }} }} }}
    else {{ p.x += (dx/d) * p.speed; p.y += (dy/d) * p.speed; }}
  }}
  projectiles = projectiles.filter(p => !p.hit);
  if (enemies.length === 0 && running) {{ wave++; money += 30; for (let i = 0; i < 3 + wave; i++) setTimeout(spawnEnemy, i * 600); }}
  if (health <= 0) endGame();
  document.getElementById('score').textContent = score;
  document.getElementById('health').textContent = health;
  document.getElementById('wave').textContent = wave;
}}

function draw() {{
  ctx.clearRect(0, 0, W, H);
  ctx.strokeStyle = '#30363d'; ctx.lineWidth = 20; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); path.forEach((p,i) => {{ if(i===0) ctx.moveTo(p.x,p.y); else ctx.lineTo(p.x,p.y); }}); ctx.stroke();
  ctx.fillStyle = '#5c6bc0'; for (const e of enemies) {{ ctx.beginPath(); ctx.arc(e.x, e.y, 8, 0, Math.PI*2); ctx.fill(); ctx.fillStyle = '#e74c3c'; ctx.fillRect(e.x - 8, e.y - 14, 16 * (e.hp / e.maxHp), 3); ctx.fillStyle = '#5c6bc0'; }}
  ctx.fillStyle = '#00D4AA'; for (const t of towers) {{ ctx.beginPath(); ctx.arc(t.x, t.y, 10, 0, Math.PI*2); ctx.fill(); }}
  ctx.fillStyle = '#fff'; for (const p of projectiles) {{ ctx.fillRect(p.x - 2, p.y - 2, 4, 4); }}
}}

function loop() {{ update(); draw(); if (running) requestAnimationFrame(loop); }}
function placeTower() {{
  if (money < 50) return;
  const x = Math.random() * (W - 40) + 20;
  const y = Math.random() * (H - 40) + 20;
  towers.push({{ x, y, cooldown: 0 }});
  money -= 50;
}}
function startGame() {{
  score = 0; health = 20; wave = 1; money = 100; enemies = []; towers = []; projectiles = []; running = true;
  document.getElementById('score').textContent = 0; document.getElementById('health').textContent = 20; document.getElementById('wave').textContent = 1;
  document.getElementById('over').style.display = 'none';
  for (let i = 0; i < 4; i++) setTimeout(spawnEnemy, i * 600);
  loop();
}}
function endGame() {{ running = false; document.getElementById('final').textContent = score; document.getElementById('over').style.display = 'block'; }}

canvas.addEventListener('click', e => {{
  const r = canvas.getBoundingClientRect();
  const x = (e.clientX - r.left) * (W/r.width);
  const y = (e.clientY - r.top) * (H/r.height);
  if (money >= 50) {{ towers.push({{ x, y, cooldown: 0 }}); money -= 50; }}
}});

startGame();
</script>
</body>
</html>
'''


# Map mechanics to generators
MECHANIC_GENERATORS = {
    "catch": generate_catch_game,
    "timing": generate_timing_game,
    "dodge": generate_dodge_game,
    "shooter": generate_shooter_game,
    "memory": generate_memory_game,
    "trace": generate_trace_game,
    "stack": generate_stack_game,
    "td": generate_td_game,
    "match3": generate_catch_game,  # fallback to catch for now
}


def generate_game_html(archetype, game_id, date_str):
    """Dispatch to the correct mechanic generator."""
    mechanic = archetype.get("mechanic", "catch")
    generator = MECHANIC_GENERATORS.get(mechanic, generate_catch_game)
    return generator(archetype, game_id, date_str)


def update_games_data(game_id, title, category, difficulty, emoji, desc, thumbnail_path, date_str):
    """Update games-data.js by prepending the new game entry."""
    with open(DATA_FILE) as f:
        content = f.read()

    escaped_desc = desc.replace("'", "\\'")
    # New generated games use PNG thumbnail and blank emoji
    new_entry = f"""  {{
    id: '{game_id}',
    title: '{title}',
    description: '{escaped_desc}',
    category: '{category}',
    thumbnail: '{thumbnail_path}',
    file: 'games/{game_id}.html',
    difficulty: '{difficulty}',
    emoji: '',
    createdAt: '{date_str}',
  }},
"""

    # Insert after the opening bracket of GAMES array
    import re
    match = re.search(r'(const\s+GAMES\s*=\s*\[)', content)
    if not match:
        raise RuntimeError("Could not find GAMES array in games-data.js")

    insert_pos = match.end()
    updated = content[:insert_pos] + '\n' + new_entry + content[insert_pos:]

    with open(DATA_FILE, 'w') as f:
        f.write(updated)


def git_commit_and_push(date_str, game_name):
    """Commit changes and push to GitHub."""
    os.chdir(SITE_DIR)
    subprocess.run(['git', 'add', '-A'], check=True)
    subprocess.run(['git', 'commit', '-m', f'Game Lab: daily coffee game "{game_name}" for {date_str}'], check=False)
    subprocess.run(['git', 'push', 'origin', 'main'], check=False)


def main():
    today = datetime.now(timezone.utc)
    date_str = today.strftime("%Y-%m-%d")
    game_id = f"coffee-{date_str}"

    print(f"=== Generating daily coffee game for {date_str} ===")

    # Load state and pick an unused archetype
    state = load_state()
    archetype = pick_archetype(state)
    print(f"Selected archetype: {archetype['name']} ({archetype['mechanic']})")

    # Record usage
    record_archetype(state, archetype["name"])
    save_state(state)

    # Generate game
    html = generate_game_html(archetype, game_id, date_str)
    game_path = GAMES_DIR / f"{game_id}.html"
    with open(game_path, 'w') as f:
        f.write(html)

    # Generate thumbnail via LocalAI Flux
    thumbnail_path = generate_thumbnail(archetype, game_id)

    # Update data
    update_games_data(
        game_id=game_id,
        title=archetype["name"],
        category=archetype["category"],
        difficulty=archetype["difficulty"],
        emoji=archetype["emoji"],
        desc=archetype["desc"],
        thumbnail_path=thumbnail_path,
        date_str=date_str,
    )

    # Commit
    git_commit_and_push(date_str, archetype["name"])
    print(f"Done! Game: {game_path}")


if __name__ == "__main__":
    main()
