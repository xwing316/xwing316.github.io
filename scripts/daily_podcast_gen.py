#!/usr/bin/env python3
"""
Daily podcast generator for FakeCast.
Fetches recent news, generates scripts, produces audio, updates site data.

Usage:
    python daily_podcast_gen.py --show ai
    python daily_podcast_gen.py --show coffee
    python daily_podcast_gen.py --show all
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import requests

SITE_DIR = Path(__file__).parent.parent
FAKECAST_DIR = SITE_DIR / "fakecast"
DATA_FILE = SITE_DIR / "js" / "fakecast-data.js"


def fetch_hn_stories(query, limit=10):
    """Fetch recent HN stories matching a query."""
    url = f"https://hn.algolia.com/api/v1/search_by_date"
    params = {"query": query, "tags": "story", "hitsPerPage": limit}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [
            {"title": h.get("title", ""), "url": h.get("url", ""), "points": h.get("points", 0)}
            for h in data.get("hits", []) if h.get("title")
        ]
    except Exception as e:
        print(f"HN fetch error: {e}")
        return []


def generate_script(show, news_items, hosts):
    """Generate a podcast script JSON from news items."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    host_names = list(hosts.keys())
    h1, h2 = host_names[0], host_names[1]
    voice1, voice2 = hosts[h1], hosts[h2]

    # Build the script dynamically
    lines = []

    if show == "ai":
        lines += [
            {"speaker": h1, "text": f"Good morning, good evening, or good whatever-time-zone you're in. Welcome to It's Just You and Me..... And AI. I'm {h1}."},
            {"speaker": h2, "text": f"And I'm {h2}. Bringing you the latest in agentic AI, foundation models, and open-source breakthroughs."},
        ]
    else:
        lines += [
            {"speaker": h1, "text": f"Welcome to The Daily Grind, your daily dose of specialty coffee news. I'm {h1}."},
            {"speaker": h2, "text": f"And I'm {h2}. If your cup is empty, now's the time to fix that."},
        ]

    # Intro banter
    lines += [
        {"speaker": h1, "text": "It's " + datetime.now().strftime("%A, %B %d") + ". Let's dive into what's new."},
        {"speaker": h2, "text": "We've got some interesting stories today."},
    ]

    # Add segments for each news item (up to 4)
    for i, item in enumerate(news_items[:4]):
        title = item.get("title", "Interesting news")
        url = item.get("url", "")

        if i == 0:
            lines.append({"speaker": h2, "text": f"First up: {title}."})
        elif i == 1:
            lines.append({"speaker": h1, "text": f"Next, I saw this: {title}."})
        elif i == 2:
            lines.append({"speaker": h2, "text": f"Also making the rounds: {title}."})
        else:
            lines.append({"speaker": h1, "text": f"And one more thing: {title}."})

        # Generate commentary based on the title
        if "budget" in title.lower() or "spent" in title.lower():
            lines.append({"speaker": h2, "text": "That's a lot of money changing hands in the AI space. The enterprise adoption is real."})
            lines.append({"speaker": h1, "text": "Yeah, companies are going all-in on these agentic tools. The ROI must be there, or they wouldn't keep spending."})
        elif "open source" in title.lower() or "github" in title.lower():
            lines.append({"speaker": h1, "text": "The open source ecosystem around AI coding tools keeps getting richer. More options, more competition, better tools for everyone."})
            lines.append({"speaker": h2, "text": "I love that we're seeing genuine alternatives to the big closed-source players."})
        elif "model" in title.lower() or "llama" in title.lower() or "gpt" in title.lower() or "claude" in title.lower():
            lines.append({"speaker": h2, "text": "Foundation models are evolving so fast it's hard to keep up. But that's what we're here for."})
            lines.append({"speaker": h1, "text": "Exactly. Every week there's a new benchmark, a new architecture, a new capability."})
        elif "coffee" in title.lower() or "espresso" in title.lower() or "roast" in title.lower():
            lines.append({"speaker": h1, "text": "This is exactly the kind of innovation that makes specialty coffee so exciting right now."})
            lines.append({"speaker": h2, "text": "The intersection of science and craft is producing some really cool results."})
        elif "bean" in title.lower() or "brew" in title.lower():
            lines.append({"speaker": h2, "text": "Tools like this are making it easier than ever for enthusiasts to level up their home setups."})
            lines.append({"speaker": h1, "text": "Democratizing good coffee. That's a mission I can get behind."})
        else:
            lines.append({"speaker": h2, "text": "That's a fascinating development. Worth keeping an eye on."})
            lines.append({"speaker": h1, "text": "Definitely. The pace of change in this space is just incredible."})

    # Outro
    if show == "ai":
        lines += [
            {"speaker": h1, "text": f"That's all for today's episode. Thanks for joining us on It's Just You and Me..... And AI. I'm {h1}."},
            {"speaker": h2, "text": f"And I'm {h2}. Stay curious, stay caffeinated, and we'll see you tomorrow."},
        ]
    else:
        lines += [
            {"speaker": h1, "text": f"That's all for The Daily Grind today. I'm {h1}."},
            {"speaker": h2, "text": f"And I'm {h2}. Brew something beautiful, and we'll catch you tomorrow."},
        ]

    script = {
        "title": f"{'It\'s Just You and Me..... And AI' if show == 'ai' else 'The Daily Grind'} - Daily Episode",
        "hosts": {h1: voice1, h2: voice2},
        "lines": lines
    }
    return script


def generate_audio(script_path, output_path):
    """Run the podcast audio generator."""
    cmd = [sys.executable, str(SITE_DIR / "scripts" / "generate_podcast.py"), str(script_path), str(output_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Audio generation failed: {result.stderr}")
    return output_path


def update_data_file(show, episode_info):
    """Update fakecast-data.js with a new episode."""
    with open(DATA_FILE) as f:
        content = f.read()

    # Parse the JS object by finding the const declaration
    import re
    match = re.search(r'const\s+FAKECAST_DATA\s*=\s*(\{[\s\S]*?\n\}\s*);', content)
    if not match:
        raise RuntimeError("Could not parse fakecast-data.js")

    data_str = match.group(1)
    # Replace JS-specific syntax to make it JSON-parseable
    json_str = data_str.replace("'", '"').replace(',\n    ]', '\n    ]').replace(',\n  }', '\n  }')
    # Remove trailing commas before closing brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse data file as JSON: {e}")

    # Prepend new episode
    show_key = show
    data[show_key]["episodes"].insert(0, episode_info)

    # Keep only last 30 episodes
    data[show_key]["episodes"] = data[show_key]["episodes"][:30]

    # Rebuild the JS file
    def val_to_js(v):
        if isinstance(v, str):
            return "'" + v.replace("'", "\\'") + "'"
        if isinstance(v, bool):
            return 'true' if v else 'false'
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, list):
            return '[\n' + ',\n'.join('      ' + val_to_js(item) for item in v) + '\n    ]'
        if isinstance(v, dict):
            return '{\n' + ',\n'.join(f"        {key}: {val_to_js(value)}" for key, value in v.items()) + '\n      }'
        return str(v)

    lines = ['const FAKECAST_DATA = {']
    for show_key, show_data in data.items():
        lines.append(f"  {show_key}: {{")
        for key, value in show_data.items():
            if key == 'episodes':
                lines.append(f"    {key}: [")
                for ep in value:
                    lines.append("      {")
                    for ep_key, ep_val in ep.items():
                        lines.append(f"        {ep_key}: {val_to_js(ep_val)},")
                    lines.append("      },")
                lines.append("    ]")
            else:
                lines.append(f"    {key}: {val_to_js(value)},")
        lines.append("  },")
    lines.append("};")

    with open(DATA_FILE, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def git_commit_and_push(show, date_str):
    """Commit changes and push to GitHub."""
    os.chdir(SITE_DIR)
    subprocess.run(['git', 'add', '-A'], check=True)
    subprocess.run(['git', 'commit', '-m', f'FakeCast: daily {show} episode for {date_str}'], check=False)
    subprocess.run(['git', 'push', 'origin', 'main'], check=False)


def run_show(show):
    today = datetime.now(timezone.utc)
    today_str = today.strftime("%Y-%m-%d")
    ep_num = int(today.strftime("%Y%m%d"))

    print(f"\n=== Generating {show.upper()} episode for {today_str} ===")

    # Fetch news
    if show == "ai":
        queries = ["opencode cli", "github copilot", "claude code anthropic", "openai codex", "foundation model llama mistral"]
        hosts = {"Alex": "en-US-Andrew:DragonHDLatestNeural", "Jordan": "en-US-Emma:DragonHDLatestNeural"}
        show_title = "It's Just You and Me..... And AI"
    else:
        queries = ["specialty coffee", "espresso brewing", "coffee roaster", "coffee beans"]
        hosts = {"Milo": "en-US-Davis:DragonHDLatestNeural", "Riley": "en-US-Phoebe:DragonHDLatestNeural"}
        show_title = "The Daily Grind"

    all_news = []
    for q in queries:
        all_news.extend(fetch_hn_stories(q, limit=5))

    # Deduplicate by title
    seen = set()
    unique_news = []
    for n in all_news:
        if n["title"] not in seen and len(unique_news) < 6:
            seen.add(n["title"])
            unique_news.append(n)

    if not unique_news:
        print("No news found, using fallback topics")
        unique_news = [{"title": "Latest developments in " + show, "url": ""}]

    print(f"Found {len(unique_news)} news items")

    # Generate script
    script = generate_script(show, unique_news, hosts)
    script_path = FAKECAST_DIR / f"{show}-daily-{today_str}.json"
    with open(script_path, 'w') as f:
        json.dump(script, f, indent=2)

    # Generate audio
    audio_path = FAKECAST_DIR / f"{show}-daily-{today_str}.mp3"
    generate_audio(script_path, audio_path)

    # Get duration
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(audio_path)],
        capture_output=True, text=True
    )
    try:
        duration = int(float(result.stdout.strip()))
    except:
        duration = 300

    # Update data file
    ep_info = {
        "title": f"Daily Briefing: {unique_news[0]['title']}",
        "date": today_str,
        "description": f"Today's episode covers {len(unique_news)} stories including {', '.join(n['title'] for n in unique_news[:3])}.",
        "audioSrc": f"fakecast/{show}-daily-{today_str}.mp3",
        "duration": duration
    }
    update_data_file(show, ep_info)

    # Commit
    git_commit_and_push(show, today_str)
    print(f"Done! Audio: {audio_path} ({duration}s)")


def main():
    parser = argparse.ArgumentParser(description="Generate daily FakeCast episodes")
    parser.add_argument("--show", choices=["ai", "coffee", "all"], default="all", help="Which show to generate")
    args = parser.parse_args()

    FAKECAST_DIR.mkdir(exist_ok=True)

    if args.show in ("ai", "all"):
        run_show("ai")
    if args.show in ("coffee", "all"):
        run_show("coffee")


if __name__ == "__main__":
    main()
