/* ============================================================
   FAKECAST-DATA.JS — Episode data for FakeCast podcasts
   ============================================================ */

const FAKECAST_DATA = {
  ai: {
    title: "It's Just You and Me..... And AI",
    emoji: "🤖",
    hosts: "Alex & Jordan",
    episodes: [
      {
        title: "Uber's Claude Code Budget, Copilot Co-Authors, and OpenCode RCE",
        date: "2026-05-01",
        description: "We discuss Uber burning through their entire 2026 AI budget in four months using Claude Code, GitHub Copilot silently inserting itself as a co-author, the OpenCode RCE vulnerability, plus new tools like Council and Brifly that are making agentic AI more usable.",
        audioSrc: "fakecast/ai-ep1.mp3",
        duration: 331
      },
      {
        title: "Llama 4, LocalPilot, and the Rise of Open Source Agents",
        date: "2026-04-30",
        description: "Meta's Llama 4 brings Liquid Transformers 2.0 architecture, LocalPilot lets you replace Copilot with local Ollama models, OpenHarness frees you from vendor lock-in, and Nimbalyst adds visual transparency to coding agents.",
        audioSrc: "fakecast/ai-ep2.mp3",
        duration: 357
      }
    ]
  },
  coffee: {
    title: "The Daily Grind",
    emoji: "☕",
    hosts: "Milo & Riley",
    episodes: [
      {
        title: "Electrochemistry, RoastDB, and AI Bean Tracking",
        date: "2026-05-01",
        description: "Scientists discover electrical current can appraise coffee quality, RoastDB catalogs 3,800+ specialty beans, BrewGreat teaches flavor wheel literacy, and BeanBook puts AI to work on your morning ritual.",
        audioSrc: "fakecast/coffee-ep1.mp3",
        duration: 299
      },
      {
        title: "Starbucks Barista Battles and Digital Roasting Twins",
        date: "2026-04-30",
        description: "Starbucks baristas compete for the coffee-making crown, AutoRoaster brings digital twins to browser-based roasting, and BeanBook's AI keeps getting smarter at dialing in your perfect shot.",
        audioSrc: "fakecast/coffee-ep2.mp3",
        duration: 342
      }
    ]
  }
};
