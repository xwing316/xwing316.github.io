#!/usr/bin/env python3
"""Generate in-game art assets using LocalAI Flux endpoint."""
import json, base64, sys, os, time, urllib.request, urllib.error

FLUX_URL = "http://192.168.86.2:3033/v1/images/generations"
MODEL = "flux.2-klein-9b"
OUT_DIR = "/home/shane/github-site/assets/images/game-assets"

os.makedirs(OUT_DIR, exist_ok=True)

STYLE_BASE = "dark navy background, high contrast, cinematic lighting, clean modern aesthetic, no text overlay, flat or semi-flat illustration style"
NO_TEXT = "no text, no letters, no words"

# Caffeine Catch game sprites — individual items that fall in the game
# These need to be simple, recognizable icons on transparent-ish dark bg
CAFFEINE_CATCH = {
    "cc-bean": {
        "size": "512x512",
        "prompt": f"single coffee bean, dark roasted, glossy brown surface, centered composition, minimal dark background, game item sprite, top-down view, {STYLE_BASE}, {NO_TEXT}"
    },
    "cc-cup": {
        "size": "512x512",
        "prompt": f"coffee cup mug top-down view, steaming hot coffee inside, ceramic white mug with dark coffee, centered composition, minimal dark background, game item sprite, {STYLE_BASE}, {NO_TEXT}"
    },
    "cc-espresso": {
        "size": "512x512",
        "prompt": f"espresso shot glass, small demitasse cup with dark espresso, golden crema on top, centered composition, minimal dark background, game item sprite, warm coffee tones, {STYLE_BASE}, {NO_TEXT}"
    },
    "cc-ice": {
        "size": "512x512",
        "prompt": f"ice cube, crystalline frozen water cube, cool blue-white tint, centered composition, minimal dark background, game item sprite, {STYLE_BASE}, {NO_TEXT}"
    },
    "cc-decaf": {
        "size": "512x512",
        "prompt": f"crossed-out coffee cup prohibition sign, decaf symbol, red circle with line through coffee cup, centered composition, minimal dark background, game item sprite, {STYLE_BASE}, {NO_TEXT}"
    },
}

# Roast Runner game sprites — coffee roasting themed
ROAST_RUNNER = {
    "rr-bean-green": {
        "size": "512x512",
        "prompt": f"raw green coffee bean, pale sage green color, natural unroasted, centered composition, minimal dark background, game item sprite, {STYLE_BASE}, {NO_TEXT}"
    },
    "rr-bean-light": {
        "size": "512x512",
        "prompt": f"lightly roasted coffee bean, light brown tan color, dry surface, centered composition, minimal dark background, game item sprite, {STYLE_BASE}, {NO_TEXT}"
    },
    "rr-bean-medium": {
        "size": "512x512",
        "prompt": f"medium roasted coffee bean, rich brown color, slight oil sheen, centered composition, minimal dark background, game item sprite, {STYLE_BASE}, {NO_TEXT}"
    },
    "rr-bean-dark": {
        "size": "512x512",
        "prompt": f"dark roasted coffee bean, deep dark brown almost black, oily surface, centered composition, minimal dark background, game item sprite, {STYLE_BASE}, {NO_TEXT}"
    },
    "rr-hotspot": {
        "size": "512x512",
        "prompt": f"red hot danger zone, glowing ember heat spot, orange-red fire glow, centered composition, minimal dark background, game hazard sprite, {STYLE_BASE}, {NO_TEXT}"
    },
    "rr-roaster": {
        "size": "512x512",
        "prompt": f"coffee roasting drum machine, industrial coffee roaster with rotating drum, metallic silver and black, centered composition, minimal dark background, game item, {STYLE_BASE}, {NO_TEXT}"
    },
}

# Memory card icons — replace emojis with themed illustrations
MEMORY_ICONS = {
    "mem-coffee": {
        "size": "512x512",
        "prompt": f"coffee cup icon, steaming pour-over dripper, warm brown tones, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-robot": {
        "size": "512x512",
        "prompt": f"friendly robot face icon, cyan and teal circuits, glowing eyes, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-snake": {
        "size": "512x512",
        "prompt": f"coiled snake icon, emerald green snake, simplified game style, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-art": {
        "size": "512x512",
        "prompt": f"painter palette icon, colorful paint splotches on dark background, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-rocket": {
        "size": "512x512",
        "prompt": f"rocket ship launching icon, bright orange flame, teal accents, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-lightning": {
        "size": "512x512",
        "prompt": f"lightning bolt icon, electric yellow gold with teal surge, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-fire": {
        "size": "512x512",
        "prompt": f"flame icon, warm orange and amber fire, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-dice": {
        "size": "512x512",
        "prompt": f"six-sided dice showing five dots, white dice on dark background, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-star": {
        "size": "512x512",
        "prompt": f"five-pointed star icon, bright gold with teal outline, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-guitar": {
        "size": "512x512",
        "prompt": f"acoustic guitar icon, warm amber brown wood body, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-target": {
        "size": "512x512",
        "prompt": f"bullseye target icon, red and white concentric rings, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-idea": {
        "size": "512x512",
        "prompt": f"lightbulb icon, glowing warm yellow with teal filament, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-puzzle": {
        "size": "512x512",
        "prompt": f"jigsaw puzzle piece icon, teal green piece, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-moon": {
        "size": "512x512",
        "prompt": f"crescent moon icon, silver and teal glow, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-music": {
        "size": "512x512",
        "prompt": f"musical note icon, golden amber eighth note, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-paw": {
        "size": "512x512",
        "prompt": f"animal paw print icon, warm brown, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-trophy": {
        "size": "512x512",
        "prompt": f"trophy cup icon, golden champion cup, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
    "mem-crystal": {
        "size": "512x512",
        "prompt": f"crystal gem icon, teal and cyan facets glowing, centered composition, dark navy background, matching card game illustration, {STYLE_BASE}, {NO_TEXT}"
    },
}

# Website UI icons — replace emojis in headers, nav, footers
SITE_ICONS = {
    "icon-coffee": {
        "size": "512x512",
        "prompt": f"minimalist coffee cup steam icon, single line art style, warm coffee brown color, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "icon-gamepad": {
        "size": "512x512",
        "prompt": f"minimalist game controller icon, retro arcade style, cyan teal color, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "icon-mic": {
        "size": "512x512",
        "prompt": f"minimalist podcast microphone icon, studio microphone, warm gold and teal color, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "icon-headphones": {
        "size": "512x512",
        "prompt": f"minimalist headphones icon, studio monitor style, warm brown color, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "icon-arrow-right": {
        "size": "512x512",
        "prompt": f"minimalist right arrow chevron icon, cyan teal color, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "icon-arrow-left": {
        "size": "512x512",
        "prompt": f"minimalist left arrow chevron icon, cyan teal color, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
}

# Category filter icons for games page
CATEGORY_ICONS = {
    "cat-all": {
        "size": "512x512",
        "prompt": f"arcade game controller collection icon, multiple game elements, vibrant teal accent, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "cat-puzzle": {
        "size": "512x512",
        "prompt": f"jigsaw puzzle piece icon, warm gold and amber, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "cat-action": {
        "size": "512x512",
        "prompt": f"lightning bolt action icon, hot orange and red, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "cat-strategy": {
        "size": "512x512",
        "prompt": f"chess strategy pieces icon, purple and silver, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
    "cat-classic": {
        "size": "512x512",
        "prompt": f"retro arcade joystick icon, vintage game style, green and teal, centered composition, dark navy background, simple flat design, {STYLE_BASE}, {NO_TEXT}"
    },
}

ALL_ASSETS = {**CAFFEINE_CATCH, **ROAST_RUNNER, **MEMORY_ICONS, **SITE_ICONS, **CATEGORY_ICONS}

def gen_one(name, cfg):
    """Generate a single image."""
    outf = os.path.join(OUT_DIR, f"{name}.png")
    print(f"Generating {name} ({cfg['size']})...", flush=True)
    
    payload = json.dumps({
        "prompt": cfg["prompt"],
        "model": MODEL,
        "n": 1,
        "size": cfg["size"],
        "response_format": "b64_json"
    }).encode()
    
    req = urllib.request.Request(FLUX_URL, data=payload, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  ERROR: HTTP {e.code} - {e.read().decode()[:200]}")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    if "data" in data and len(data["data"]) > 0:
        item = data["data"][0]
        if "b64_json" in item:
            img = base64.b64decode(item["b64_json"])
            with open(outf, "wb") as f:
                f.write(img)
            kb = len(img) / 1024
            print(f"  OK: {outf} ({kb:.0f}KB)")
            return True
    
    print(f"  ERROR: unexpected response")
    return False

def main():
    names = sys.argv[1:] if len(sys.argv) > 1 else list(ALL_ASSETS.keys())
    
    success = 0
    failed = 0
    for name in names:
        if name not in ALL_ASSETS:
            print(f"Unknown: {name}")
            failed += 1
            continue
        if gen_one(name, ALL_ASSETS[name]):
            success += 1
        else:
            failed += 1
        time.sleep(2)
    
    print(f"\nDone: {success} generated, {failed} failed")

if __name__ == "__main__":
    main()