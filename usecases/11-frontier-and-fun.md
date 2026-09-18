# Frontier and fun

The demos, oddities, and experiments that show what the primitive can actually do. Some are jokes. Several are the most informative things in the ecosystem, because a constraint-free demo reveals the shape of the tool better than a business case.

---

## Why the fun demos matter

The launch post calls these "Fun Demos" and they are the clearest demonstration of the central claim: **fast, cheap structured inference is a new computational primitive, not just a faster classifier.**

As Sean Goedecke put it after watching the Doom demo:

> Fast software doesn't just mean we can do the same tasks faster, it means we can do entirely new kinds of tasks. What kinds of new programs can we write by injecting 100ms worth of dirt-cheap intelligence at various decision points?

The fun demos are attempts to answer that question.

---

## The official demos

### Doom

Jev plays Doom by reacting to structured game state at roughly 10 calls per second, at about $7/hour of inference. TypeSafe's own caveats:

- It runs on structured state as a data structure with text, **not on images**.
- A non-AI Doom bot could play better.

The interesting part is not the gameplay. It is that a *general* model - one you can re-instruct in English - can be dropped into a real-time loop at all. The engineer behind it was worried about making 10 queries a second; the team's reaction was that ~$7/hour is lower than expected.

### Wikiracing

Start on one Wikipedia page, reach a target page using only links you encounter while traversing. Each step can mean choosing between hundreds to thousands of links - a great playground for intelligence-per-second and for the compounding benefits of not hallucinating with high-cardinality choices.

Notable details:
- Jev supports cardinality up to 255. For higher cardinality they use a two-stage system: score independently, then make an explicit choice.
- Jev tended to finish in **fewer steps** than the LLMs, which they read as a sign of greater intelligence.

The [Hacker News discussion](https://news.ycombinator.com/item?id=49717558) noted that LLMs looked much worse because they were run without reasoning enabled, to keep the demo watchable - a fair criticism of the comparison.

Source: [launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

---

## The community's experiments

### Games

| Project | What it does |
| --- | --- |
| [**fhshaik/typesafe-mario**](https://github.com/fhshaik/typesafe-mario) (217★) | Plays Super Mario Bros. from emulator RAM as object-centric JSON. No screenshots. |
| [**phyous/tsai-sc**](https://github.com/phyous/tsai-sc) | Completes the first StarCraft shareware mission across 421 decisions, with a verification report. |
| [**sorrycc/typesafe-snake**](https://github.com/sorrycc/typesafe-snake) | Snake, one System One choice per tick, legal moves generated in code. |
| [**KyleKreuter/jev2048**](https://github.com/KyleKreuter/jev2048) | Lets Jev solve 2048. |
| [**emrickgarrett/OneVOneJev**](https://github.com/emrickgarrett/OneVOneJev) | 1v1 quickscope arena. |
| [**AbdelStark/heist-one**](https://github.com/AbdelStark/heist-one) | Browser stealth game: Jev makes typed guard judgments, deterministic code owns the world. |
| [**ashaazami/river-run-typesafe**](https://github.com/ashaazami/river-run-typesafe) | River Raid-inspired shooter played by a TypeSafe pilot. |
| [**Icohen007/jev-play-ping-pong**](https://github.com/Icohen007/jev-play-ping-pong) | Browser table tennis with auditable evidence. |
| [**rchovatiya88/cyber-breach-jev**](https://github.com/rchovatiya88/cyber-breach-jev) | Tactical cyberpunk arena combat. |
| [**onionminionops-beep/pdoom-protocol**](https://github.com/onionminionops-beep/pdoom-protocol) | Co-op platform shooter - the name is a joke about p(doom). |

**The recurring lesson:** in every one, the legal action set and the world facts are computed deterministically and Jev only picks from the legal set. [sorrycc/typesafe-snake](https://github.com/sorrycc/typesafe-snake)'s description says it explicitly. That is the architecture that works, even in a toy.

### Simulations and robotics

| Project | What it does |
| --- | --- |
| [**RomanSlack/jev-drone**](https://github.com/RomanSlack/jev-drone) (53★) | Camera-only autonomous drone in MuJoCo, Jev advisory at 2.5 Hz. |
| [**arielweinberger/jev-autopilot**](https://github.com/arielweinberger/jev-autopilot) | Flies a drone point A to point B in a random city, avoiding obstacles. |
| [**vinilana/live-jev**](https://github.com/vinilana/live-jev) | 2D autonomous car simulation in the browser. |
| [**lhemerly/mcts-agent**](https://github.com/lhemerly/mcts-agent) | Discriminative Monte Carlo Tree Search using TypeSafe primitives plus Gemini. |

The drone is the one to study, and it has [its own write-up](08-real-time-and-games.md#the-architecture-that-works-jev-advises-code-controls).

### The absurd ones

- [**nagata_hideyuki/magi**](https://x.com/nagata_hideyuki/status/2100695580096016611) recreates the MAGI system from *Neon Genesis Evangelion*: three sages judge your question independently and decide by majority vote over calibrated probabilities. This is a joke that is also a legitimate architectural demonstration - independent judgments, combined in code.
- [**mkotlikov/jev-grug**](https://github.com/mkotlikov/jev-grug) - "helping JEV speak <3". Also the source of the [Talk to JEV](https://jev-grug-chat.mkotlikov.chatgpt.site) Hacker News post.
- [**monteduro/killmyidea**](https://github.com/monteduro/killmyidea) - describe your startup idea, Jev decides: kill it, fix it, or ship it.
- [**tentacode/jevendsdestrucs**](https://github.com/tentacode/jevendsdestrucs) - a personal helper to synchronize ads on Leboncoin and Audiofanzine.

### Media and language

- [**ChetasLua/jevmeter**](https://github.com/ChetasLua/jevmeter) (36★) puts a live "BS meter" on any video: every sentence scored, rendered as a 16:9 edit. A full debate costs about $0.05. It ships presets for debates and interviews, earnings calls, and podcasts, with a claimed 99% held-out preset accuracy.
- [**y0usaf/jev-lm**](https://github.com/y0usaf/jev-lm) - a word-level language model whose output layer is Jev: an n-gram drafter with Noul chunk verification and bits-per-token evaluation. This is the most direct test of the "can you force Jev to generate" question, and the answer is that it works poorly, as documented.
- [**nagata_hideyuki**](https://x.com/nagata_hideyuki/status/2100695580096016611) and [**mkotlikov**](https://github.com/mkotlikov/jev-grug) both build conversational interfaces on top of a model that does not converse. They are informative precisely because they show where the boundary is.
- [**sriganesh/jevibe-check**](https://github.com/sriganesh/jevibe-check) - a live tone labeler for Bluesky posts and drafts.
- [**adhyaay-karnwal/jev-chat**](https://github.com/adhyaay-karnwal/jev-chat) - hierarchical speculative decoding over System One probabilities.

### Home automation

- [**AboveColin/HA-Jev**](https://github.com/AboveColin/HA-Jev) - a Home Assistant integration. Ask a question about your house, get a probability, choice, or score as an entity.
- [**JanOstrowka/typesafe-assist**](https://github.com/JanOstrowka/typesafe-assist) - a Home Assistant Assist conversation agent powered by Jev.

The [Syntax channel demo](https://www.youtube.com/watch?v=QbYBRjOaGOo) is the best illustration: 300 ms to ask Jev a question, get the answer, and call the Home Assistant API to turn off a device.

---

## The demos that are actually research

Three projects in this category are doing real work:

### [**AbdelStark/jev-benchmarks**](https://github.com/AbdelStark/jev-benchmarks)
Probability-aware evaluation of typed decision models: calibration, selective risk, latency, and reproducible benchmarks with paired bootstrap intervals. This is the most rigorous independent work in the ecosystem and it produced the mixed result (Jev strong on news and banking classification, poorly calibrated on emotion). See [evaluating-jev](../docs/evaluating-jev.md).

### [**TheoLeeCJ/openjev**](https://github.com/TheoLeeCJ/openjev) (839★)
Can you run something like Jev on a 3090 at home? It reads typed option probabilities directly from a frozen 4B model's logits with no answer sentence, no JSON repair, and no decoding loop. It is explicit that it reproduces the *interface pattern*, not Jev's model or training.

Its sibling projects test the same question on different hardware:
- [**bnsd55/jevmlx**](https://github.com/bnsd55/jevmlx) - Jev-style parallel constrained decisions for any MLX model on Apple Silicon, typed schema-valid JSON in one forward pass.
- [**r-ms/mini-jev**](https://github.com/r-ms/mini-jev) - reads the option letter's logits instead of generating.
- [**kshetrajna12/reflex**](https://github.com/kshetrajna12/reflex) - an open decision model on Qwen3.5.
- [**akash-kamat/system-one-gemma**](https://github.com/akash-kamat/system-one-gemma) - Gemma 3 270M with a scoring head.
- [**ekzhang/openjev-sglang**](https://github.com/ekzhang/openjev-sglang) - a Jev-compatible API endpoint based on open models.

### [**RINNECODER/jev-behavior-study**](https://github.com/RINNECODER/jev-behavior-study)
An independent Jev 1.13.0 behavior study with a report, controlled prompt experiments, raw results, and offline verification. Small, but it is the kind of work the ecosystem needs more of.

---

## What the fun demos teach

Strip away the novelty and four lessons recur across every project in this category:

1. **Generate the legal action set in code.** Every successful game and simulation project does this. The model picks from a set it cannot break out of.
2. **Compute the world state deterministically.** No project sends raw pixels. Screens become tables, game state becomes JSON, camera data becomes symbolic scenes.
3. **Ask more than you need, read what matters.** Speculative fan-out is what makes the loops fast - several candidate answers per round trip.
4. **Keep a deterministic veto.** The drone's 50 Hz reflex layer overrides Jev. The games validate moves. Code always has the last word.

None of these are specific to games. They are the same four rules that govern production agent harnesses, browser agents, and real-time pipelines. The fun demos are just a cheaper place to learn them.

---

## Related

- [08-real-time-and-games.md](08-real-time-and-games.md) - the production version of these loops
- [09-browser-and-computer-use.md](09-browser-and-computer-use.md) - the screen-as-state variant
- [Reference: ecosystem](../reference/ecosystem.md) - the full inventory including open reproductions
