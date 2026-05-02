#!/usr/bin/env python3
"""Regenerate game catalog thumbnails so only coffee games use coffee art."""
import base64, json, os, time, urllib.request

URL = "http://192.168.86.2:3033/v1/images/generations"
MODEL = "flux.2-klein-9b"
OUT = "/home/shane/github-site/assets/images"
BASE = "dark navy background, high contrast, cinematic lighting, clean modern aesthetic, no text overlay, flat or semi-flat illustration style, no text, no letters, no words"

PROMPTS = {
  "game-roast-runner.png": "stylized top-down arcade gameplay scene inside a coffee roasting drum, polished coffee bean player dodging glowing orange hotspot obstacles, radial roaster rings, warm caramel and ember lighting, game screenshot style, " + BASE,
  "game-caffeine-catch.png": "stylized arcade gameplay scene with a ceramic mug catching falling coffee beans, espresso cups, ice cubes and decaf hazard symbols, clean vector game art, warm coffee tones with teal score glow, " + BASE,
  "game-snake.png": "classic snake arcade gameplay on a dark grid, glowing green snake winding toward a simple neon pellet, retro terminal aesthetic, teal and emerald accents, no coffee elements, " + BASE,
  "game-memory.png": "memory matching card game gameplay board, grid of flipped illustrated cards with colorful abstract symbols, dark tabletop, warm gold and teal accents, no coffee elements, " + BASE,
  "game-pong.png": "classic pong gameplay scene, two glowing paddles and bright ball crossing a dark court, center dashed line, minimal retro arcade style, cyan blue glow, no coffee elements, " + BASE,
  "game-flappy.png": "flappy bird style gameplay scene, small stylized bird flying between green pipes over dark twilight background, clean arcade art, orange action accents, no coffee elements, " + BASE,
  "game-tictactoe.png": "tic tac toe gameplay board, glowing 3 by 3 grid with X and O marks, strategic minimal board game style, purple blue and cyan accents, no coffee elements, " + BASE,
  "game-breakout.png": "breakout arcade gameplay scene, paddle at bottom, ball bouncing upward, colorful brick wall at top, dark background, orange red action glow, no coffee elements, " + BASE,
  "game-2048.png": "2048 puzzle gameplay board, sliding numbered tile grid with warm amber tiles, clean minimal puzzle interface, dark background, no coffee elements, no readable text, " + BASE,
  "game-invaders.png": "space invaders gameplay scene, rows of pixel alien ships descending, player cannon at bottom firing laser, starfield dark background, cyan purple arcade glow, no coffee elements, " + BASE,
}

def gen(filename, prompt):
    print(f"Generating {filename}...")
    payload = json.dumps({"prompt": prompt, "model": MODEL, "n": 1, "size": "1024x768", "response_format": "b64_json"}).encode()
    req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=150) as r:
        data = json.loads(r.read().decode())
    img = base64.b64decode(data["data"][0]["b64_json"])
    path = os.path.join(OUT, filename)
    with open(path, "wb") as f:
        f.write(img)
    print(f"  wrote {path} ({len(img)//1024}KB)")

for filename, prompt in PROMPTS.items():
    gen(filename, prompt)
    time.sleep(2)
