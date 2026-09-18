# Application showcase

Repositories that **demonstrate what Jev is used for** - working applications, agent systems, games, and measured experiments. This is the "show me what people built" list.

**Excludes:** SDKs, client libraries, CLI wrappers, skill packs, harness plumbing, and curated lists. Those live in [ecosystem.md](ecosystem.md). If you want to *build* with Jev, start here. If you want a client for your language, go there.

**Snapshot:** 2026-09-18, three days after launch. Star counts are live from the GitHub API at collection time. Every project here was created on or after 2026-09-15 and is therefore a **launch-week artifact**. Treat all of them as proofs of concept, and note that measured results are self-reported by their authors unless stated otherwise.

**Method:** 36 GitHub search queries across `jev typesafe`, `topic:jev`, `topic:typesafe-ai`, and application-specific terms (demo, use case, agent, game, trading, browser, review, guardrails, classification, router, robotics, postgres, moderation, extraction, reranking, computer use). **401 unique repositories** found, up from 306 a day earlier. The 102 strongest application candidates were inspected in detail, and every repository cited here was verified to exist via the GitHub API.

---

## The headline applications

These have the most traction, the clearest scope, and in most cases a published measurement.

| Stars | Project | What it does | Measured result |
| ---: | --- | --- | --- |
| 2,466 | [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) | Browser agent with a dynamic indexed action space; Jev picks operation + target, a small LLM writes text only for `TYPE_TEXT` | Zürich → London on Google Flights in **7.1 s, $0.0039** |
| 628 | [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) | Replaces Claude Code's lossy compaction summary with Jev keep/delete decisions; kept content stays verbatim | Not measured; design is the contribution |
| 543 | [jarrodwatts/jev-trader](https://github.com/jarrodwatts/jev-trader) | One trade decision per Monad block on the Kuru MON-USDC order book; posts a post-only limit order one tick inside the touch | **81 ms** model latency, 2 RPC round trips per block |
| 221 | [fhshaik/typesafe-mario](https://github.com/fhshaik/typesafe-mario) | Plays Super Mario Bros. from emulator RAM as object-centric JSON; no screenshots, 7 legal actions | Not measured |
| 203 | [thruwire/foreman](https://github.com/thruwire/foreman) | Independent supervisor above Codex workers: is the work complete, tested, off-track, stuck | Not measured; framed as an architectural experiment |
| 178 | [devagrawal09/jev-review](https://github.com/devagrawal09/jev-review) | Staged code reviewer: Noul risk matrix → Choice/Score file profiles → evidence selection → severity → routing | Not measured; ships a local dashboard |
| 173 | [awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) | macOS computer use via OCR + Jev action choice; a writing model only for free text | **$0.0002/decision, ~1.5 s/step** vs Opus 5 at $0.032 and 5.5 s |
| 105 | [kitze/skillbox](https://github.com/kitze/skillbox) | Self-hosted versioned skill library with optional Jev recommendations | Not measured |
| 84 | [NiazMorshed2007/jev-review](https://github.com/NiazMorshed2007/jev-review) | Local-first MCP plugin for continuous code-quality review | Not measured |
| 63 | [vinilana/jev-eval-agent](https://github.com/vinilana/jev-eval-agent) | Assistant agent with 100 mocked tools; compares LLM-picks-the-tool vs Jev-picks-the-tool on step count | Head-to-head design; run it yourself |
| 53 | [RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone) | Camera-only quadrotor in MuJoCo; Jev advisory at 2.5 Hz, code owns safety at 50 Hz | ~110 calls per 65 s flight |
| 50 | [vlad-terin/jev-browser](https://github.com/vlad-terin/jev-browser) | Jev selects elements inside a continuous observe/act/verify loop, no agent turn per step | Scenario recordings committed |
| 49 | [kitze/unclutter](https://github.com/kitze/unclutter) | WXT browser extension that removes page clutter using reusable template rules | Not measured |
| 45 | [realZachi/pg-jev](https://github.com/realZachi/pg-jev) | Natural-language `WHERE` clauses for PostgreSQL; no index, no embeddings, no vector column | 129-row table: **≈1 s, 4 requests, ≈$0.0009** |
| 44 | [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) | Agent guardrails that steer instead of interrupting: rules, slop, stuck loops, done claims, secrets, irreversible calls | **150 paired runs: 6 rule breaks without, 0 with.** ~$0.00004 and 0.3 s per judgment |
| 37 | [ChetasLua/jevmeter](https://github.com/ChetasLua/jevmeter) | Live "BS meter" over any video: every sentence scored, rendered as a 16:9 edit | Full debate ≈ **$0.05**; 99% held-out preset accuracy (author-reported) |
| 19 | [devanshbatham/commit-miner](https://github.com/devanshbatham/commit-miner) | Classifies Git commit diffs for bug fixes, security fixes/CWEs, and change types | Reports estimated Jev cost per scan |
| 13 | [brainstormity/Jev-Moderation-Bot](https://github.com/brainstormity/Jev-Moderation-Bot) | Content moderation bot | Not measured |
| 13 | [ellipsis-dev/blink](https://github.com/ellipsis-dev/blink) | Codebase search via an ensemble of walkers that score file paths | Returns a probability per path |

---

## By application domain

### Agent supervision and guardrails

The largest cluster. All of these put Jev *around* an agent, not inside it.

| Project | What it does | Evidence |
| --- | --- | --- |
| [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) | Rules, slop, stuck loops, done claims, secrets, irreversible calls | 6-vs-0 across 150 paired runs; 42 held calls across 17,160 guarded calls |
| [caiovicentino/jev-shield](https://github.com/caiovicentino/jev-shield) | Semantic MCP firewall: screens every tool call, result, and tool description | **94% block recall, 0 false positives, ~$0.00002/check**; 10 verifications for $0.0003 |
| [GhalebDweikat/winnow](https://github.com/GhalebDweikat/winnow) | Context sieve: judges each ~25-line block before it enters Claude's context, stubs the rest with a recall key | Not measured |
| [compozy/yoshi](https://github.com/compozy/yoshi) | Context-pruning proxy for Claude Code and Codex | Not measured |
| [qkal/Canny](https://github.com/qkal/Canny) | Stops done claims without evidence; deterministic hooks decide, Jev advises | Not measured |
| [leepokai/jev-guard](https://github.com/leepokai/jev-guard) | Risk-scores every tool call (deny / ask / allow), flags prompt injection | Not measured |
| [y0usaf/pi-jev](https://github.com/y0usaf/pi-jev) | Measured tool-call gate plus typed `jev_ask` for the Pi agent | Not measured |
| [STRML/omp-jevens-classifier](https://github.com/STRML/omp-jevens-classifier) | Permission gate for OMP's bash tool and process-spawning `eval` payloads | Not measured |
| [ndolinschi/toolgate](https://github.com/ndolinschi/toolgate) | allow / ask_human / deny for planned tool calls | Not measured |
| [jomatsu/pi-jev-auto-mode](https://github.com/jomatsu/pi-jev-auto-mode) | Semantically auto-approves bash/write/edit; fails closed | Not measured |
| [ShivamPansuriya/jev-skill-gate](https://github.com/ShivamPansuriya/jev-skill-gate) | Scores installed skills and hides the irrelevant | Cuts the skill manifest by **~75%** (author-reported) |
| [Dicklesworthstone/skillranker](https://github.com/Dicklesworthstone/skillranker) | Rust CLI that ranks skills against live session context, with local calibration | Not measured |
| [alexshpunt/pi-agent-foreman](https://github.com/alexshpunt/pi-agent-foreman) | Sends agents back to work when they stop early | Not measured |
| [furedea/reflex-state](https://github.com/furedea/reflex-state) | Execution state for Pi agents tracked outside the main LLM | Not measured |

**See also:** [usecases/03-agent-harness-engineering.md](../usecases/03-agent-harness-engineering.md)

### Security and adversarial robustness

| Project | What it does | Evidence |
| --- | --- | --- |
| [Gaurav-Gosain/jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) | Blind benchmarks on two public corpora: prompt injection (662 messages) and vulnerable code (200 matched pairs) | Injection: **96.5% accuracy, F1 95.6%, ROC-AUC 0.9927, ECE 0.0588**, p50 325 ms. Also found that telling Jev what the assistant is for improves results more than threshold tuning |
| [caiovicentino/jev-shield](https://github.com/caiovicentino/jev-shield) | MCP firewall across tool calls, results, and descriptions | 94% recall, 0 FP |
| [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) | Action guard holds irreversible calls | 37 held calls stood across 17,160 guarded calls |
| [brainstormity/Jev-Moderation-Bot](https://github.com/brainstormity/Jev-Moderation-Bot) | Moderation | Not measured |

**This is the strongest measured category.** `jev-sec-bench` is one of the few blind, public-corpus evaluations of Jev anywhere. See [usecases/02-llm-guardrails-and-verification.md](../usecases/02-llm-guardrails-and-verification.md).

### Trading and markets

| Project | What it does | Evidence |
| --- | --- | --- |
| [jarrodwatts/jev-trader](https://github.com/jarrodwatts/jev-trader) | Market maker on Kuru MON-USDC; one decision per Monad block | 81 ms latency; dry-run mode with real book data |
| [justinhe16/trade-jev](https://github.com/justinhe16/trade-jev) | Backtests Jev as a BUY/SELL/HOLD trader on NQ L10 order-book data | Not measured |
| [tyleree/jevbot](https://github.com/tyleree/jevbot) | Options trading bot (backtest + Alpaca paper only) | Paper only |
| [zadescoxp/Jev-Trades](https://github.com/zadescoxp/Jev-Trades) | Trading bot | Not measured |
| [sosopop/jev_stock](https://github.com/sosopop/jev_stock) | Short-term stock direction forecasting from structured market data | Not measured |
| [axiomarchitecture/axiom-agent-runtime](https://github.com/axiomarchitecture/axiom-agent-runtime) | Agentic commerce on Kaspa: "Jev proposes. Axiom authorizes. Argent enforces." | Working prototype; Jev connected, execution stubbed |

**Note on honesty:** the two with real measurement (`jev-trader`) or explicit safety framing (`axiom-agent-runtime`, `jevbot` paper-only) are the ones worth reading. The rest are experiments.

### Code review, search, and developer tooling

| Project | What it does | Evidence |
| --- | --- | --- |
| [devagrawal09/jev-review](https://github.com/devagrawal09/jev-review) | Staged review: risk matrix → profiles → evidence → severity → routing | Local dashboard |
| [NiazMorshed2007/jev-review](https://github.com/NiazMorshed2007/jev-review) | MCP code-quality review | Not measured |
| [ellipsis-dev/blink](https://github.com/ellipsis-dev/blink) | Codebase search returning a probability per file path | Example outputs committed |
| [raihankhan-rk/diffjury](https://github.com/raihankhan-rk/diffjury) | PR risk router + review coach | Not measured |
| [opaielsheikh/typesafe-migration-guard](https://github.com/opaielsheikh/typesafe-migration-guard) | Database migration safety reviewer | Not measured |
| [huntedman/JevLint](https://github.com/huntedman/JevLint) | Configurable semantic linting, file-level Noul judgments | Not measured |
| [devanshbatham/commit-miner](https://github.com/devanshbatham/commit-miner) | Commit classification with CWE tagging, HTML/CSV reports | Cost estimates per scan |
| [BunsDev/clarity-judge](https://github.com/BunsDev/clarity-judge) | Multi-axis writing-quality checker | Not measured |
| [kitze/skillbox](https://github.com/kitze/skillbox) | Versioned skill library, MCP, scoped clients | Not measured |
| [tonyzdev/PiJ](https://github.com/tonyzdev/PiJ) | Terminal coding agent with Jev for skill selection, code ranking, failure triage | Not measured |

### Computer use and browser agents

| Project | What it does | Evidence |
| --- | --- | --- |
| [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) | Dynamic indexed action space, speculative target fan-out | Zürich → London **7.1 s, $0.0039** |
| [awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) | macOS OCR → Jev → action | **$0.0002/step**, ~1.5 s end-to-end |
| [NobleSpartan6/otto](https://github.com/NobleSpartan6/otto) | Native macOS + Windows computer use via accessibility APIs and OCR, with an optional planner | Alpha; validation gates listed openly |
| [paulsmith/computer-use-jev](https://github.com/paulsmith/computer-use-jev) | macOS computer use with Jev as the decision maker | Not measured |
| [eriestra/almond-fastloop](https://github.com/eriestra/almond-fastloop) | ~200-line dependency-free browser loop, plus the **Browser Use Olympics** benchmark it competes in | Whitepaper committed |
| [vlad-terin/jev-browser](https://github.com/vlad-terin/jev-browser) | Element selection inside an existing computer-use toolchain | Scenario recordings |
| [superagents-lab/jev-search](https://github.com/superagents-lab/jev-search) | Live web search: Jev picks sources, time ranges, terms, and ranks results | Live at [jev.s1.dev](https://jev.s1.dev) |
| [jkudish/jev-browser](https://github.com/jkudish/jev-browser) | Browser use on Jev | Not measured |
| [Ying-Kai-Liao/jev-browser](https://github.com/Ying-Kai-Liao/jev-browser) | "An LLM plans and Jev decides" | Not measured |
| [tontoko/jev-browser](https://github.com/tontoko/jev-browser) | Grounded Jev/Playwright core with typed SDK, CLI, MCP | Not measured |
| [ranjan2829/AskJev](https://github.com/ranjan2829/AskJev) | Website autopilot with an irreversible-click guard | Not measured |
| [serejaris/voice-browser](https://github.com/serejaris/voice-browser) | Voice and text browser control, Chrome MV3 | Preview demo |
| [KesavanKing/jev-browser](https://github.com/KesavanKing/jev-browser) | Local UI where Jev chooses bounded page actions | Not measured |

**See also:** [usecases/09-browser-and-computer-use.md](../usecases/09-browser-and-computer-use.md)

### Search, retrieval, and reranking

| Project | What it does | Evidence |
| --- | --- | --- |
| [anessbelbati/jev-rerank-bench](https://github.com/anessbelbati/jev-rerank-bench) | Jev vs Cohere Rerank 4 vs ZeroEntropy zerank-2 vs a chat baseline, 14 datasets, every raw response saved | Jev rubric **nDCG@10 0.692** vs Cohere Pro 0.691 vs zerank-2 0.682 across 8 English datasets; 422 ms and **$0.45 per 1,000 queries**; 74% top-pick; AUROC 0.75 on "nothing here" |
| [realZachi/pg-jev](https://github.com/realZachi/pg-jev) | Natural-language SQL predicates as a Postgres extension | 129 rows, ≈1 s, ≈$0.0009 |
| [EugeneBoondock/jevsql](https://github.com/EugeneBoondock/jevsql) | Same idea as a library | Not measured |
| [carlaaiau/jev-reranking](https://github.com/carlaaiau/jev-reranking) | TREC WSJ search-engine reranking experiments | Not measured |
| [superagents-lab/jev-search](https://github.com/superagents-lab/jev-search) | Full web search pipeline | Live demo |
| [reachjalil/jevlogs](https://github.com/reachjalil/jevlogs) | OpenTelemetry log triage: score the signal before expensive LLM analysis | Not measured |

**`jev-rerank-bench` is the most rigorous independent application benchmark in the ecosystem** after `jev-benchmarks`. It publishes raw API responses and bootstrap ranges on every gap, and it reports a tie rather than a win.

**See also:** [usecases/04-search-reranking-and-rag.md](../usecases/04-search-reranking-and-rag.md)

### Classification, extraction, and evaluation

| Project | What it does | Evidence |
| --- | --- | --- |
| [FirasSX914/calibre](https://github.com/FirasSX914/calibre) | Calibration and confidence-based routing on Banking77 | **80.2% accuracy at $0.103 per 500 decisions** |
| [zsavage8/padflow-jev-evals](https://github.com/zsavage8/padflow-jev-evals) | Real SaaS workload benchmark: document routing, transaction coding, import-value classification, with schemas and labelled rows | Publishes accuracy *and* calibration per decision |
| [PistachioAIHQ/jev-synergy-screening](https://github.com/PistachioAIHQ/jev-synergy-screening) | ASReview-style abstract screening vs Cohen 2006 gold labels, ADHD corpus (N=851) | Stratified N=200: **92.0% acc, F1 66.7%**, ~523 ms, **~$0.018** |
| [shibadogcap/kyotsu-ai-bench](https://github.com/shibadogcap/kyotsu-ai-bench) | Japan's 2026 Common Test: Jev vs two luna variants | Static dashboard |
| [TokenTrim/jev-agent-failure-benchmark](https://github.com/TokenTrim/jev-agent-failure-benchmark) | Jev vs a strong LLM on Who&When Pro agent-failure attribution | Not yet reported |
| [Charlyhno-eng/jev-document-classification](https://github.com/Charlyhno-eng/jev-document-classification) | Document classification | Not measured |
| [gtaras7/typesafe-jev](https://github.com/gtaras7/typesafe-jev) | CV screening with an editable policy; re-scoring costs nothing because judgments are cached separately | Reports two bugs its own test data caught |
| [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) | Calibration, selective risk, latency across three datasets | AG News 0.910, Banking77 0.870, DAIR Emotion 0.480 (poorly calibrated) |

**`padflow-jev-evals` is the model to copy** if you want to evaluate Jev against a real product workload: it publishes the schemas, the anonymized labelled rows, and a runner.

**See also:** [../docs/evaluating-jev.md](../docs/evaluating-jev.md)

### Games, simulations, and robotics

| Project | What it does | Evidence |
| --- | --- | --- |
| [fhshaik/typesafe-mario](https://github.com/fhshaik/typesafe-mario) | Super Mario Bros. from emulator RAM; no screenshots | Not measured |
| [phyous/tsai-sc](https://github.com/phyous/tsai-sc) | Completes the first StarCraft shareware mission via keyboard/mouse | **421 decisions**, recorded action probabilities, verification report |
| [phyous/tsai-civ2](https://github.com/phyous/tsai-civ2) | Civilization II in a browser with live action probabilities | Under development; no verified full-game win yet |
| [RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone) | Camera-only quadrotor, Jev advisory at 2.5 Hz | ~110 calls per 65 s flight; safety reflex at 50 Hz |
| [arielweinberger/jev-autopilot](https://github.com/arielweinberger/jev-autopilot) | Drone flying point A to B in a random city, avoiding obstacles | Not measured |
| [lukaske/jev-doom-agent](https://github.com/lukaske/jev-doom-agent) | Two isolated Chocolate Doom WASM instances; Jev picks a tactical macro | Key never persisted; explicit low-confidence handling |
| [lbotinelly/jev-little-airways](https://github.com/lbotinelly/jev-little-airways) | Toy ATC world in a glass dome; every in-flight judgment made live by Jev | ~150 ms per batched 4-question request, every ~1.6 s per aircraft |
| [4anti/jev-broadcast-lab](https://github.com/4anti/jev-broadcast-lab) | Chess arena; chess.js owns legality, Jev only picks among the legal move list | Stockfish is HUD-only and never enters Jev's payload |
| [sorrycc/typesafe-snake](https://github.com/sorrycc/typesafe-snake) | Snake, one System One choice per tick | Legal moves generated in code |
| [AbdelStark/heist-one](https://github.com/AbdelStark/heist-one) | Browser stealth game; Jev makes typed guard judgments | Not measured |
| [hide-G/magi-system-on-jev](https://github.com/hide-G/magi-system-on-jev) | MAGI from Evangelion: three sages, majority vote over calibrated probabilities | Live site |
| [emrickgarrett/OneVOneJev](https://github.com/emrickgarrett/OneVOneJev) | 1v1 quickscope arena | Not measured |
| [ashaazami/river-run-typesafe](https://github.com/ashaazami/river-run-typesafe) | River Raid-inspired shooter | Not measured |
| [Icohen007/jev-play-ping-pong](https://github.com/Icohen007/jev-play-ping-pong) | Browser table tennis with structured telemetry and auditable evidence | Not measured |
| [vinilana/live-jev](https://github.com/vinilana/live-jev) | 2D autonomous car simulation in the browser | Not measured |
| [marcelocantos/jevons](https://github.com/marcelocantos/jevons) | Personal AI assistant: Grok overseer, fleet of coding agents, voice-first web UI | Name is a Jevons paradox reference |
| [wondertwins/jev-benchmark](https://github.com/wondertwins/jev-benchmark) | Chess plus a "who is the player talking to" task for speech-to-text NPCs | Not measured |
| [kw2828/OpenJev](https://github.com/kw2828/OpenJev) | Chess policy experiments, 12 fits across 288 games; Doom control | Exact-delta policy matched Stockfish on **33.15%** of positions vs 31.75%; explicitly says it establishes no Elo |
| [lhemerly/mcts-agent](https://github.com/lhemerly/mcts-agent) | Discriminative Monte Carlo Tree Search over Jev primitives + Gemini | Not measured |
| [opaielsheikh/ps2-ai-agent](https://github.com/opaielsheikh/ps2-ai-agent) | Autonomous PlayStation 2 agent with a visual telemetry HUD | Not measured |

**The recurring architecture in every project here:** the legal action set and the world facts are computed in code, and Jev only picks from the legal set. `sorrycc/typesafe-snake` and `4anti/jev-broadcast-lab` state it explicitly. See [usecases/08-real-time-and-games.md](../usecases/08-real-time-and-games.md).

### Real-time and home automation

| Project | What it does | Evidence |
| --- | --- | --- |
| [AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev) | Home Assistant integration returning a probability, choice, or score as an entity | Not measured |
| [JanOstrowka/typesafe-assist](https://github.com/JanOstrowka/typesafe-assist) | Home Assistant Assist conversation agent | Not measured |
| [jflam/jev1](https://github.com/jflam/jev1) | Recreates TypeSafe's own smart-home demo: one batched request, code acts on relevant answers, low confidence gets a confirmation | Not measured |
| [jarrodwatts/jev-trader](https://github.com/jarrodwatts/jev-trader) | Per-block trading loop | 81 ms |
| [lbotinelly/jev-little-airways](https://github.com/lbotinelly/jev-little-airways) | Per-aircraft ATC loop | ~150 ms batched |

The Syntax channel's demo is the reference for this category: 300 ms to ask Jev, get the answer, and call the Home Assistant API to turn off a device.

### Domain applications

| Project | Domain | What it does |
| --- | --- | --- |
| [Infrawrench/Jeeves](https://github.com/Infrawrench/Jeeves) | Moderation | Discord moderation rules in plain English; live inviteable bot. Jev interprets messages and strike history, Gemini describes images |
| [gtaras7/typesafe-jev](https://github.com/gtaras7/typesafe-jev) | Recruiting | CV screening with an editable role policy |
| [PistachioAIHQ/jev-synergy-screening](https://github.com/PistachioAIHQ/jev-synergy-screening) | Research | Systematic-review abstract screening vs published gold labels |
| [opaielsheikh/typesafe-migration-guard](https://github.com/opaielsheikh/typesafe-migration-guard) | Engineering | Migration safety review |
| [superagents-lab/jev-search](https://github.com/superagents-lab/jev-search) | Search | Source selection and ranking |
| [EdytaKucharska/ticket-quest](https://github.com/EdytaKucharska/ticket-quest) | Product | Ticket triage by Cost of Delay, with a bring-your-own-key LLM race for comparison |
| [tylerjharden/harden-jev-decides](https://github.com/tylerjharden/harden-jev-decides) | Product | Jev picks which stream idea becomes the live MVP |
| [jexp/neo4jev](https://github.com/jexp/neo4jev) | Data | Navigates a Neo4j graph by classifying over neighbouring relationships |
| [brainstormity/Jev-Moderation-Bot](https://github.com/brainstormity/Jev-Moderation-Bot) | Moderation | Content moderation |
| [sriganesh/jevibe-check](https://github.com/sriganesh/jevibe-check) | Social | Live tone labeler for Bluesky posts and drafts |
| [caiovicentino/jev-shield](https://github.com/caiovicentino/jev-shield) | Security | MCP firewall |
| [realZachi/typesafe-adblock](https://github.com/realZachi/typesafe-adblock) | Browser | Chrome extension: "is this DOM element an ad?" |
| [piyush97/focus-tube](https://github.com/piyush97/focus-tube) | Browser | Distraction-free YouTube feed |
| [Foadsf/jev-for-engineers](https://github.com/Foadsf/jev-for-engineers) | Engineering | Eight minimal examples for mechanical and electrical engineering: CAD/CAE/CAM routing |

**See also:** [usecases/10-domain-applications.md](../usecases/10-domain-applications.md)

### Open reproductions and local models

Not Jev itself, but they test whether the *interface* works without the service. Useful if you need to run locally or want to understand the pattern.

| Project | What it does | Evidence |
| --- | --- | --- |
| [TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev) (839★) | Reads typed option probabilities off a frozen 4B model's logits, one forward pass | 2–3x speedup claim; publishes the exact model revision and prompt hash |
| [Heman10x-NGU/Verdict-open-jev](https://github.com/Heman10x-NGU/Verdict-open-jev) | 151M ModernBERT decision engine with RLCD-style calibration, WebGPU playground | Under **35 ms** |
| [kw2828/OpenJev](https://github.com/kw2828/OpenJev) | Reproducible experiments on memory, uncertainty, Doom control, chess | Publishes negative results |
| [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) | Jev-style parallel constrained decisions for any MLX model on Apple Silicon | Not measured |
| [kshetrajna12/reflex](https://github.com/kshetrajna12/reflex) | Small open decision model on Qwen3.5 | Not measured |
| [akash-kamat/system-one-gemma](https://github.com/akash-kamat/system-one-gemma) | Gemma 3 270M with a scoring head | Not measured |
| [mithalouni/system-one-open](https://github.com/mithalouni/system-one-open) | Open replica on Gemma 4 E2B | Not measured |
| [siliconkernel/vllm-jev-decison](https://github.com/siliconkernel/vllm-jev-decison) | Classification-only typed decisions for vLLM | Not measured |
| [r-ms/mini-jev](https://github.com/r-ms/mini-jev) | Reads the option letter's logits instead of generating | Not measured |
| [ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) | Jev-compatible API endpoint on open models | Not measured |
| [rorshopping/jev-on-a-laptop](https://github.com/rorshopping/jev-on-a-laptop) | Jev-style decisions on stock 1.5B–8B models on Apple Silicon | Benchmarks committed |
| [hr98w/jev-visual](https://github.com/hr98w/jev-visual) | Visual inference experiment: shared context, direct candidate scoring | Not measured |

**The consistent caveat from these authors:** they reproduce the *interface pattern*, not Jev's model or training. You get parallelism and typed answers but not the calibration. See [../docs/model-selection.md](../docs/model-selection.md).

---

## How to read these projects

Four things separate the credible ones from the rest:

1. **A published measurement with a stated sample.** `pi-warden` (150 paired runs), `jev-sec-bench` (662 + 400 samples), `jev-rerank-bench` (1,617 questions across 14 datasets), `typesafe-computer-use` (same screenshot, both models). The rest describe architecture without numbers.
2. **Committed raw results.** `jev-rerank-bench` saves every API response. `jev-benchmarks` commits machine-readable metrics with bootstrap intervals. `jev-sec-bench` commits per-sample output.
3. **An honest limitations section.** `RomanSlack/jev-drone` says Jev "cannot be the perception layer, and it cannot run at control rate." `kw2828/OpenJev` says its results "establish neither a learned world model nor an Elo rating." `NobleSpartan6/otto` lists its own launch gates. `PistachioAIHQ` warns against headlining a 100% figure from only 10 positives.
4. **Code owns the control flow.** In every mature project, Jev answers a question and code decides what to do. Where a project lets Jev own the loop, the README usually says it is an experiment.

The projects that do all four are worth your time: [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden), [anessbelbati/jev-rerank-bench](https://github.com/anessbelbati/jev-rerank-bench), [Gaurav-Gosain/jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench), [RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone), and [awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use).

---

## What is missing

Where the ecosystem has *not* built yet, as of 2026-09-18:

- **No production case study at volume.** Everything is launch-week. Nobody has published "we run this on N million requests per day."
- **No independent calibration curve on a customer workload.** `padflow-jev-evals` publishes the harness for it but not results from a live deployment.
- **Almost no regulated-domain deployment.** Legal, insurance, and healthcare appear in TypeSafe's own use-case map but not in shipped community projects, with the single exception of the medical-text benchmarks.
- **No longitudinal studies.** Nothing has run long enough to show drift, cost at scale, or behavior under distribution shift.
- **Thin coverage of extraction.** The documented cookbooks cover it well; community projects mostly do classification and routing instead.

If you build in one of these gaps, it will be the most-cited project in the ecosystem within a week.

---

## Related

- [ecosystem.md](ecosystem.md) - the full 306+ repo census including SDKs and infrastructure
- [question-catalog.md](question-catalog.md) - ready-to-adapt question sets by domain
- [../usecases/README.md](../usecases/README.md) - worked patterns per category
