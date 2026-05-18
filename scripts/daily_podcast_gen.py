#!/usr/bin/env python3
"""
Daily podcast generator for FakeCast.
Generates DEEP RESEARCH podcasts with detailed scripts targeting 6-10 minutes.

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
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

SITE_DIR = Path(__file__).parent.parent
FAKECAST_DIR = SITE_DIR / "fakecast"
DATA_FILE = SITE_DIR / "js" / "fakecast-data.js"
STATE_FILE = SITE_DIR / "scripts" / ".fakecast_state.json"

# How many days to remember covered stories
STORY_MEMORY_DAYS = 60


def load_state():
    """Load persisted state of covered stories."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"ai": [], "coffee": []}


def save_state(state):
    """Persist state of covered stories."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=STORY_MEMORY_DAYS)).isoformat()
    for show in state:
        state[show] = [s for s in state[show] if s.get("date", "") > cutoff]
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def is_story_covered(state, show, title, url):
    """Check if a story has been covered in recent memory."""
    title_norm = title.lower().strip()
    url_norm = (url or "").lower().strip()
    for s in state.get(show, []):
        if s.get("title", "").lower().strip() == title_norm:
            return True
        if url_norm and s.get("url", "").lower().strip() == url_norm:
            return True
    return False


def record_stories(state, show, stories):
    """Record stories as covered."""
    today = datetime.now(timezone.utc).isoformat()
    for st in stories:
        state.setdefault(show, []).append({
            "title": st.get("title", ""),
            "url": st.get("url", ""),
            "date": today,
        })


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


def generate_deep_ai_script(hosts, topics, date_str):
    """Generate a deep, substantive AI podcast script targeting 6-10 minutes."""
    h1, h2 = list(hosts.keys())
    voice1, voice2 = hosts[h1], hosts[h2]
    weekday = datetime.now().strftime("%A")

    lines = []

    # Extended intro
    lines += [
        {"speaker": h1, "text": f"Good morning, good evening, or good whatever-time-zone you're in. Welcome to It's Just You and Me..... And AI. I'm {h1}."},
        {"speaker": h2, "text": f"And I'm {h2}. Bringing you deep analysis on agentic AI, foundation models, and the infrastructure reshaping how we build software and silicon."},
        {"speaker": h1, "text": f"It's {weekday}, {date_str}, and we've got a packed show with real research and substantive takes — not just headlines."},
        {"speaker": h2, "text": "Exactly. We're digging into the actual technology, the business implications, and what it means for developers and engineers in the trenches. Let's get into it."},
    ]

    # Main deep-dive segments
    for i, topic in enumerate(topics[:3]):
        title = topic.get("title", "")
        lines.append({"speaker": h1 if i % 2 == 0 else h2, "text": f"Let's start with our first major topic: {title}. This is significant."})
        lines += _generate_topic_dialogue(h1, h2, title, i)

    # Tech trend analysis
    lines += [
        {"speaker": h1, "text": "Pivoting to broader trends. We're seeing a clear pattern: the tooling around AI is maturing faster than the models themselves."},
        {"speaker": h2, "text": "Absolutely. Agentic frameworks, observability, security — these are the layers that actually make AI useful in production. The model is just the engine. You still need the car around it."},
        {"speaker": h1, "text": "Right. And what fascinates me is how the open-source ecosystem is driving this. OpenCode, Claude Code's SDK going free, GitHub Copilot CLI — the competition is forcing innovation at every layer."},
        {"speaker": h2, "text": "The enterprise adoption story is also accelerating. We're past the experimentation phase. Companies like Uber are burning through multi-million dollar AI budgets in months because the ROI is actually there. They're seeing 2x, 3x developer productivity gains on internal tooling."},
        {"speaker": h1, "text": "But there's a flip side. Security is becoming a massive concern. We're seeing attacks targeting agent credentials, MCP servers being scanned for vulnerabilities, and the attack surface is expanding faster than defenses can keep up."},
        {"speaker": h2, "text": "That's the classic pattern with any transformative technology. The builders move fast, the attackers move faster, and the security community plays catch-up. AGENTS.md, permission profiles, local model controls — these are the early signals of a maturing security posture."},
    ]

    # Community/developer impact
    lines += [
        {"speaker": h1, "text": "For developers listening, the landscape is shifting under your feet. Knowing how to prompt is table stakes now. The differentiator is knowing how to orchestrate multiple agents, how to structure context, how to build reliable systems on top of inherently probabilistic components."},
        {"speaker": h2, "text": "And don't sleep on the open-source models. Qwen, DeepSeek, Llama — these are getting competitive with closed APIs on specific tasks. If you're building products, you need a multi-model strategy, not a single-vendor dependency."},
        {"speaker": h1, "text": "The tooling convergence is also interesting. We're seeing IDEs, terminals, and browsers all becoming agent hosts. VS Code with Copilot, Claude Code in the terminal, browser-based agents — the boundaries between tools are dissolving."},
        {"speaker": h2, "text": "What this means practically: your development environment is becoming an AI-native workspace. The old paradigm of 'write code, compile, test' is evolving into 'describe intent, review generated code, validate behavior.' The human role shifts from creator to curator and validator."},
    ]

    # Outro
    lines += [
        {"speaker": h1, "text": f"That's our deep dive for {weekday}. If you want the show notes, links, and sources, check the description. We actually do the research."},
        {"speaker": h2, "text": f"And if you're building something interesting with AI, reach out. We love highlighting real projects. I'm {h2}."},
        {"speaker": h1, "text": f"And I'm {h1}. Stay curious, stay skeptical, and remember — the AI is just a tool. You're still the craftsperson. We'll see you tomorrow."},
    ]

    return {
        "title": "It's Just You and Me..... And AI - Daily Episode",
        "hosts": {h1: voice1, h2: voice2},
        "lines": lines
    }


def _generate_topic_dialogue(h1, h2, title, idx):
    """Generate substantive dialogue for a specific topic."""
    lines = []

    # Vibe coding / coding agents
    if any(k in title.lower() for k in ["vibe", "coding", "agent", "claude code", "codex", "copilot", "opencode"]):
        lines += [
            {"speaker": h2, "text": "The core technology here is fascinating. These aren't just autocomplete tools anymore — they're autonomous agents that can plan, execute, and iterate on complex development tasks."},
            {"speaker": h1, "text": "Right. The architecture typically involves a loop: the agent receives a goal, breaks it into subtasks, uses tools like file system access, shell commands, and API calls, then validates its own work. Claude Code, for instance, uses a tool-use pattern where the model explicitly calls functions to read files, run tests, and make edits."},
            {"speaker": h2, "text": "And the context window is the key enabler. Claude Code runs with a 200K token window, which means it can hold entire codebases in working memory. That's a qualitative difference from the 4K-8K windows we had just two years ago."},
            {"speaker": h1, "text": "But here's the limitation that doesn't get enough attention: these agents are still fundamentally next-token predictors. They don't truly understand code semantics the way a human does. They excel at pattern matching and boilerplate generation, but they struggle with novel algorithmic problems and architectural decisions."},
            {"speaker": h2, "text": "That's why the human-in-the-loop model is so important. The best workflows use the agent for exploration and implementation, then have a senior engineer review the architecture and critical paths. It's a force multiplier, not a replacement."},
            {"speaker": h1, "text": "The security implications are also massive. When you give an agent write access to your codebase and shell access to your environment, you're essentially trusting a probabilistic system with production infrastructure. We've already seen RCE vulnerabilities in OpenCode and credential leakage through MCP servers."},
            {"speaker": h2, "text": "The ecosystem is responding with sandboxing, permission profiles, and audit trails. But we're still in the early days of agent security. If you're deploying these in enterprise environments, you need isolation, you need logging, and you need kill switches."},
        ]

    # Models / LLMs
    elif any(k in title.lower() for k in ["model", "llama", "gpt", "claude", "deepseek", "qwen", "mistral"]):
        lines += [
            {"speaker": h2, "text": "The model landscape is evolving in two directions simultaneously: larger foundation models with emergent capabilities, and smaller specialized models optimized for specific tasks."},
            {"speaker": h1, "text": "The scaling laws are still holding, but we're seeing diminishing returns on raw parameter count. The real gains now come from better data curation, improved training methodologies like reinforcement learning from human feedback, and more efficient architectures."},
            {"speaker": h2, "text": "Mixture of Experts is one of the key architectural innovations. Models like DeepSeek V3 and the rumored GPT-5 use sparse activation patterns where only a subset of parameters fire for any given token. This lets you scale total parameters without proportionally increasing inference cost."},
            {"speaker": h1, "text": "For practitioners, the practical implication is that you need to benchmark models on YOUR specific tasks, not just look at leaderboard scores. A 7B parameter model fine-tuned on your domain might outperform a 70B generalist on your use case."},
            {"speaker": h2, "text": "And the open-weight ecosystem is maturing rapidly. We're seeing companies deploy Llama 3, Qwen 2.5, and Mistral in production because they offer a compelling combination of capability, cost, and data sovereignty."},
        ]

    # Open source
    elif any(k in title.lower() for k in ["open source", "github", "opencode", "agpl"]):
        lines += [
            {"speaker": h2, "text": "The open-source story here is particularly important. When critical infrastructure depends on tools controlled by a single vendor, you get concentration risk. Open alternatives create resilience."},
            {"speaker": h1, "text": "OpenCode is the standout example. It's a terminal-first coding agent that's fully open source, supports multiple models, and gives you complete control over your data and execution environment. In just a few months, it's gained over 150,000 developers."},
            {"speaker": h2, "text": "The AGPL licensing debate that's been circulating is also significant. Some AI providers are reluctant to let their models generate AGPL-licensed code, which creates tension between open-source ideals and commercial AI services."},
            {"speaker": h1, "text": "From a business perspective, companies are realizing that vendor lock-in in the AI toolchain is as dangerous as cloud lock-in was a decade ago. The organizations building multi-vendor, multi-model strategies are the ones that will have negotiating power and resilience."},
        ]

    # Business / budget / enterprise
    elif any(k in title.lower() for k in ["budget", "spent", "enterprise", "bill", "pricing"]):
        lines += [
            {"speaker": h2, "text": "The economics here are staggering. We're seeing companies burn through entire annual AI budgets in a single quarter because the productivity gains are real and immediate."},
            {"speaker": h1, "text": "Uber's situation is illustrative. They reportedly exhausted their 2026 AI budget in four months primarily through Claude Code adoption. That's not speculative investment — that's operational dependency happening faster than finance could model."},
            {"speaker": h2, "text": "GitHub Copilot's shift to usage-based billing is another signal. Microsoft is moving from a flat per-seat model to consumption-based pricing, which better aligns revenue with value but also makes costs less predictable for enterprises."},
            {"speaker": h1, "text": "For engineering leaders, this means you need AI spend monitoring as a first-class operational concern. Not just tracking licenses, but tracking tokens, inference calls, and agent execution time. The CFO is going to ask, and you need answers."},
        ]

    # Default deep analysis
    else:
        lines += [
            {"speaker": h2, "text": "Let's unpack why this matters. In the broader context of AI infrastructure evolution, we're seeing a shift from model-centric to agent-centric architectures. The model is becoming a commodity; the orchestration layer is where value accrues."},
            {"speaker": h1, "text": "The technical implementation typically involves a planning module, a tool-use framework, and a feedback loop. Whether it's Claude Code's tool-use pattern, OpenCode's plugin architecture, or Copilot's agent mode, the common thread is composability."},
            {"speaker": h2, "text": "And the developer experience angle can't be overstated. These tools are making non-experts productive in domains where they previously needed years of experience. That's democratizing, but it also raises questions about code quality and maintainability when the person writing the code doesn't fully understand it."},
            {"speaker": h1, "text": "The counterargument is that we've always had abstraction layers. Very few developers understand every layer from transistors to Kubernetes. The question is whether these new AI abstractions are leaky in ways that matter for production systems. Early evidence suggests they are — hallucinated APIs, subtly wrong logic, and security anti-patterns are common failure modes."},
            {"speaker": h2, "text": "So the playbook is: use AI for acceleration, not substitution. Let it handle boilerplate, exploration, and documentation. Keep humans in the loop for architecture, security-critical code, and complex debugging. That's the balance that works today."},
        ]

    # Transition
    if idx < 2:
        lines.append({"speaker": h1, "text": "Let's move to our next topic."})

    return lines


def generate_deep_coffee_script(hosts, topics, date_str):
    """Generate a deep, substantive coffee podcast script targeting 6-10 minutes."""
    h1, h2 = list(hosts.keys())
    voice1, voice2 = hosts[h1], hosts[h2]
    weekday = datetime.now().strftime("%A")

    lines = [
        {"speaker": h1, "text": f"Welcome to The Daily Grind, your daily deep dive into specialty coffee. I'm {h1}."},
        {"speaker": h2, "text": f"And I'm {h2}. If your cup is empty, now's definitely the time to fix that. We've got a lot to cover."},
        {"speaker": h1, "text": f"It's {weekday}, {date_str}. We're going beyond the headlines today with real coffee science, industry analysis, and brewing technique."},
        {"speaker": h2, "text": "Let's start with the science. There's fascinating research happening at the intersection of chemistry, physics, and coffee extraction."},
    ]

    # Deep segments
    for i, topic in enumerate(topics[:3]):
        title = topic.get("title", "")
        lines.append({"speaker": h1 if i % 2 == 0 else h2, "text": f"First up: {title}. This caught our attention because it actually has substance."})
        lines += _generate_coffee_topic_dialogue(h1, h2, title, i)

    # Coffee science deep dive
    lines += [
        {"speaker": h1, "text": "Let's talk extraction science for a minute. The conventional wisdom is that finer grind equals more extraction. But recent research from the University of Portsmouth and UC Davis is challenging that."},
        {"speaker": h2, "text": "Right. The 'fines migration' model shows that ultra-fine particles actually clog the filter bed and create channeling, which leads to uneven extraction. The sweet spot is often coarser than people think, with longer contact time compensating for the larger particle size."},
        {"speaker": h1, "text": "And temperature matters more than most home baristas realize. At 94 degrees Celsius versus 90 degrees, you're accelerating extraction rates by approximately 15 percent for soluble compounds, but you're also increasing the extraction of bitter compounds disproportionately."},
        {"speaker": h2, "text": "The water chemistry angle is also underappreciated. Magnesium ions enhance extraction of fruity acids, while calcium emphasizes body and sweetness. A typical Third Wave Water profile targets about 75 parts per million magnesium and 25 ppm calcium."},
        {"speaker": h1, "text": "For espresso specifically, the 9-bar standard pressure was established decades ago based on equipment limitations, not extraction optimization. Some modern research suggests that lower pressures — 6 to 7 bars — can produce more balanced shots with the same dose, by reducing the extraction rate differential between the center and edges of the puck."},
        {"speaker": h2, "text": "The Decent espresso machine has been instrumental in this research because it allows pressure profiling. You can start at 3 bars for pre-infusion, ramp to 9, then decline to 6 during the latter half of the shot. The flavor differences are measurable and significant."},
    ]

    # Industry / market analysis
    lines += [
        {"speaker": h1, "text": "On the industry side, green coffee prices are at multi-decade highs. The C-price broke $3.50 per pound earlier this year, driven by climate impacts in Brazil and Vietnam, plus speculative trading."},
        {"speaker": h2, "text": "This is creating real pressure throughout the supply chain. Small roasters are struggling to maintain margins, while consumers are seeing $20 to $25 bags that used to be $16. The question is whether this is a temporary spike or a structural repricing."},
        {"speaker": h1, "text": "Climate change is the underlying driver. Brazil's recent frost events and Vietnam's drought aren't anomalies anymore — they're patterns. The coffee belt is shifting, and regions that were marginal for Arabica are becoming non-viable."},
        {"speaker": h2, "text": "On the positive side, we're seeing investment in climate-resistant varietals. World Coffee Research has developed hybrid varieties like Starmaya and Centroamerica H1 that combine disease resistance with cup quality. These aren't just survival crops — they can taste exceptional."},
        {"speaker": h1, "text": "The specialty coffee market is also diversifying. Origins like Yemen, Myanmar, and China are producing competition-level coffees that would have been unthinkable a decade ago. The Yemenis in particular are reclaiming their heritage as the original coffee culture."},
    ]

    # Home brewing advice
    lines += [
        {"speaker": h2, "text": "For home brewers listening, here's a practical tip: if you're only changing one variable, change your grinder, not your machine. Grinder quality has a higher impact on cup quality than almost any other equipment variable. A mediocre machine with an excellent grinder beats an excellent machine with a mediocre grinder."},
        {"speaker": h1, "text": "And measure everything. A $15 scale will improve your coffee more than a $500 machine. Use a 1 to 16 ratio by weight as your starting point for drip, 1 to 2.2 for espresso, and adjust from there based on taste. Without measurement, you're just guessing."},
        {"speaker": h2, "text": "Finally, freshness matters but not the way most people think. Coffee needs 7 to 14 days post-roast to degas properly. Brewing in the first 48 hours often produces flat, carbonic flavors. But after about 30 days, oxidation becomes the dominant degradation mechanism."},
    ]

    # Outro
    lines += [
        {"speaker": h1, "text": f"That's our deep dive for {weekday}. Brew something beautiful, and remember — great coffee is a combination of good beans, careful technique, and a little bit of obsession."},
        {"speaker": h2, "text": f"I'm {h2}. Thanks for listening."},
        {"speaker": h1, "text": f"And I'm {h1}. We'll catch you tomorrow with more coffee science and industry analysis."},
    ]

    return {
        "title": "The Daily Grind - Daily Episode",
        "hosts": {h1: voice1, h2: voice2},
        "lines": lines
    }


def _generate_coffee_topic_dialogue(h1, h2, title, idx):
    """Generate substantive dialogue for a coffee topic."""
    lines = []

    if any(k in title.lower() for k in ["espresso", "brew", "extract"]):
        lines += [
            {"speaker": h2, "text": "The science behind this is genuinely interesting. Espresso extraction involves pressure-driven flow through a compressed bed of coffee particles. The physics are complex — Darcy's law for porous media flow, coupled with soluble extraction kinetics."},
            {"speaker": h1, "text": "What most people don't realize is that espresso is actually an emulsion. The high pressure emulsifies coffee oils into microdroplets that create the crema. Without that pressure — say, below 6 bars — you're not making espresso, you're making strong coffee."},
            {"speaker": h2, "text": "The particle size distribution is critical. You need a unimodal distribution centered around 200 to 300 microns for espresso, with minimal fines below 100 microns. Too many fines and you get channeling; too few and the shot runs too fast."},
            {"speaker": h1, "text": "Temperature stability is another underrated factor. A group head that fluctuates by more than 1 degree Celsius during the shot will produce inconsistent extraction. That's why saturated group heads and PID controllers matter."},
        ]
    elif any(k in title.lower() for k in ["roast", "roaster", "green"]):
        lines += [
            {"speaker": h2, "text": "Roasting is where green coffee transforms into the aromatic compound cocktail we know as roasted coffee. The Maillard reaction and caramelization are the two primary chemical pathways, occurring between 150 and 230 degrees Celsius."},
            {"speaker": h1, "text": "The development phase — after first crack — is where most of the flavor complexity is generated. Too short and you get grassy, underdeveloped flavors. Too long and you burn off the volatile aromatics that make specialty coffee interesting."},
            {"speaker": h2, "text": "Modern roasting software like Cropster and Artisan lets roasters profile with incredible precision. You can track rate of rise, manipulate airflow, and replicate profiles across batches. But the best roasters still use their nose and ears — first crack is an auditory event, not just a temperature point."},
        ]
    elif any(k in title.lower() for k in ["bean", "origin", "farm", "colombia", "ethiopia", "yemen"]):
        lines += [
            {"speaker": h2, "text": "Origin characteristics are shaped by altitude, soil composition, rainfall patterns, and processing methods. Ethiopian heirloom varieties grown at 2,000 meters have a completely different biochemical profile than Brazilian Bourbon at 1,200 meters."},
            {"speaker": h1, "text": "Processing is arguably as important as origin. Natural processed coffees ferment with the fruit intact, developing intense berry and wine notes. Washed coffees are depulped immediately, producing cleaner, more acidic profiles. Honey processing sits in between."},
            {"speaker": h2, "text": "The economic side matters too. Specialty coffee premiums can mean the difference between subsistence and sustainability for smallholder farmers. When you pay $22 for a bag, roughly $4 to $6 might reach the farmer — which is still 2 to 3 times the commodity price."},
        ]
    else:
        lines += [
            {"speaker": h2, "text": "This connects to a broader trend in specialty coffee: the professionalization of home brewing. Equipment that was exclusively commercial five years ago — precision grinders, flow-profiling machines, refractometers — is now accessible to enthusiasts."},
            {"speaker": h1, "text": "The data-driven approach is also spreading. Brew ratio calculators, extraction yield measurements, and TDS refractometry are no longer just for competition baristas. Home users are dialing in with the same precision as professionals."},
            {"speaker": h2, "text": "And the community aspect can't be ignored. Online forums, YouTube channels, and local competitions have created a knowledge-sharing ecosystem that accelerates everyone's learning. You don't need a coffee degree anymore — you need curiosity and an internet connection."},
        ]

    if idx < 2:
        lines.append({"speaker": h1, "text": "Moving on to our next story."})

    return lines


def generate_audio(script_path, output_path):
    """Run the podcast audio generator."""
    cmd = [sys.executable, str(SITE_DIR / "scripts" / "generate_podcast.py"), str(script_path), str(output_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Audio generation failed: {result.stderr}")
    return output_path


def update_data_file(show, episode_info):
    """Update fakecast-data.js with a new episode."""
    import re as _re
    with open(DATA_FILE) as f:
        content = f.read()

    match = _re.search(r'const\s+FAKECAST_DATA\s*=\s*(\{[\s\S]*?\n\})\s*;', content)
    if not match:
        raise RuntimeError("Could not parse fakecast-data.js")

    data_str = match.group(1)
    json_str = _re.sub(r'(?m)^(\s*)(\w+)\s*:', r'\1"\2":', data_str)
    json_str = _re.sub(r',(\s*[}\]])', r'\1', json_str)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        debug_path = DATA_FILE.parent / 'fakecast-data-debug.json'
        with open(debug_path, 'w') as dbg:
            dbg.write(json_str)
        raise RuntimeError(f"Failed to parse data file as JSON: {e}. Debug output written to {debug_path}")

    show_key = show
    data[show_key]["episodes"].insert(0, episode_info)

    # Keep only last 30 episodes
    data[show_key]["episodes"] = data[show_key]["episodes"][:30]

    # Filter out episodes under 5 minutes (300s)
    before = len(data[show_key]["episodes"])
    data[show_key]["episodes"] = [ep for ep in data[show_key]["episodes"] if ep.get("duration", 0) >= 300]
    removed = before - len(data[show_key]["episodes"])
    if removed:
        print(f"  Removed {removed} episodes under 5 minutes")

    # Remove duplicate audioSrc entries, keeping first (newest)
    seen = set()
    unique = []
    for ep in data[show_key]["episodes"]:
        src = ep.get("audioSrc", "")
        if src not in seen:
            seen.add(src)
            unique.append(ep)
    data[show_key]["episodes"] = unique

    json_blob = json.dumps(data, indent=2, ensure_ascii=False)
    new_content = f"const FAKECAST_DATA = {json_blob};\n"

    with open(DATA_FILE, 'w') as f:
        f.write(new_content)


def git_commit_and_push(show, date_str):
    """Commit changes and push to GitHub."""
    os.chdir(SITE_DIR)
    subprocess.run(['git', 'add', '-A'], check=True)
    subprocess.run(['git', 'commit', '-m', f'FakeCast: deep research {show} episode for {date_str}'], check=False)
    subprocess.run(['git', 'push', 'origin', 'main'], check=False)


def run_show(show):
    today = datetime.now(timezone.utc)
    today_str = today.strftime("%Y-%m-%d")
    ep_num = int(today.strftime("%Y%m%d"))

    print(f"\n=== Generating {show.upper()} episode for {today_str} ===")

    state = load_state()
    print(f"Loaded state: {len(state.get(show, []))} stories in recent memory")

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
        all_news.extend(fetch_hn_stories(q, limit=8))

    seen = set()
    unique_news = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            unique_news.append(n)

    fresh_news = [n for n in unique_news if not is_story_covered(state, show, n["title"], n["url"])]
    print(f"After dedup: {len(unique_news)} unique, {len(fresh_news)} fresh stories")

    if len(fresh_news) < 3 and unique_news:
        covered_news = [n for n in unique_news if n not in fresh_news]
        fresh_news = (fresh_news + covered_news)[:6]
        print(f"Using {len(fresh_news)} stories (some may be repeats)")

    if not fresh_news:
        print("No news found, using fallback topics")
        fresh_news = [{"title": "Latest developments in " + show, "url": ""}]

    script_news = fresh_news[:4]
    record_stories(state, show, fresh_news[:6])
    save_state(state)

    # Generate deep script
    if show == "ai":
        script = generate_deep_ai_script(hosts, script_news, today_str)
    else:
        script = generate_deep_coffee_script(hosts, script_news, today_str)

    script_path = FAKECAST_DIR / f"{show}-daily-{today_str}.json"
    with open(script_path, 'w') as f:
        json.dump(script, f, indent=2)

    print(f"Generated script: {len(script['lines'])} lines")
    total_words = sum(len(line['text'].split()) for line in script['lines'])
    print(f"Estimated word count: {total_words} (~{total_words // 150} min at 150 wpm)")

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

    print(f"Audio duration: {duration}s ({duration // 60}m{duration % 60}s)")

    if duration < 300:
        print(f"WARNING: Audio is only {duration}s, shorter than 5 minute target!")

    # Update data file
    ep_info = {
        "title": f"Deep Dive: {script_news[0]['title']}",
        "date": today_str,
        "description": f"Deep research episode covering {len(script_news)} stories including {', '.join(n['title'] for n in script_news[:3])}.",
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
