# Ecosystem reference

A census of public Jev projects as of **2026-09-18**. Jev launched on 15 September 2026, so everything here is at most three days old. Treat the whole list as launch-week artifacts.

> **Looking for applications rather than libraries?** See [showcase.md](showcase.md) - the curated list of working apps, agents, games, and measured experiments. This page is the broad census including SDKs, CLIs, and infrastructure.

**Method:** GitHub API search for `jev typesafe`, `topic:jev`, `topic:typesafe-ai`, plus manual inspection of the 55 most relevant repositories. Star counts are live from the API at the time of writing.

**Caveat:** this list is deliberately broad and deliberately unvetted. Inclusion is not endorsement and is not a claim that anything works. Many of these are one-evening experiments.

---

## Totals

- **401** unique repositories found across 36 search queries (up from 306 the previous day)
- **55** inspected in detail for the original build; **102** application candidates inspected for [showcase.md](showcase.md)
- Dominant languages: Python (~45%), TypeScript (~40%), then Rust, Go, Elixir, PHP, Swift, C#, Dart, Java

---

## The most-established projects

Ranked by stars. These are the ones worth reading the source of.

| Stars | Project | What it does |
| ---: | --- | --- |
| 2,303 | [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) | Browser agent with dynamic indexed action space. Zürich→London in 7.1s, $0.0039. |
| 839 | [TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev) | Runs "something like Jev" on a 3090 by reading option logits from a 4B model. |
| 527 | [jarrodwatts/jev-trader](https://github.com/jarrodwatts/jev-trader) | One trade decision per Monad block (~300ms), 81ms model latency. |
| 492 | [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) | Replaces Claude Code compaction summaries with Jev delete/keep decisions. |
| 409 | [Anil-matcha/awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe) | Evidence-backed use cases, patterns, prompts, starter code. |
| 217 | [fhshaik/typesafe-mario](https://github.com/fhshaik/typesafe-mario) | Plays Super Mario Bros. from structured emulator state. |
| 200 | [thruwire/foreman](https://github.com/thruwire/foreman) | Software factory foreman: Jev supervises Codex workers. |
| 174 | [devagrawal09/jev-review](https://github.com/devagrawal09/jev-review) | Staged code-review workflow with local dashboard. |
| 169 | [awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) | macOS computer use at $0.0002 per step. |
| 97 | [kitze/skillbox](https://github.com/kitze/skillbox) | Self-hosted skill library with Jev recommendations. |
| 66 | [AbdelStark/awesome-typesafe](https://github.com/AbdelStark/awesome-typesafe) | Curated list with independent-research labeling. |
| 53 | [RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone) | Camera-only autonomous drone, Jev advisory at 2.5Hz. |
| 49 | [jkudish/jev-mcp](https://github.com/jkudish/jev-mcp) | MCP server PoC. |
| 49 | [kitze/unclutter](https://github.com/kitze/unclutter) | Browser extension for Jev-powered clutter removal. |
| 45 | [ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) | Jev-compatible API endpoint on open models. |
| 44 | [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) | Agent guardrails with a controlled 6-vs-0 measurement. |
| 43 | [pithings/advocaat](https://github.com/pithings/advocaat) | Type-safe client for asking questions about your data. |
| 36 | [ChetasLua/jevmeter](https://github.com/ChetasLua/jevmeter) | Live "BS meter" over any video. |
| 35 | [yibie/awesome-jev](https://github.com/yibie/awesome-jev) | Category-organized curated list. |
| 36 | [realZachi/pg-jev](https://github.com/realZachi/pg-jev) | Natural-language WHERE clauses for PostgreSQL. |

---

## By category

### Curated lists
[yibie/awesome-jev](https://github.com/yibie/awesome-jev) · [AnotiaWang/awesome-jev](https://github.com/AnotiaWang/awesome-jev) · [Anil-matcha/awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [AbdelStark/awesome-typesafe](https://github.com/AbdelStark/awesome-typesafe) · [hellogumbo/awesome-jev](https://github.com/hellogumbo/awesome-jev) · [rhc98/awesome-jev](https://github.com/rhc98/awesome-jev) · [OmniJev/awesome-jev](https://github.com/OmniJev/awesome-jev) (research-focused)

### Agent harness and guardrails
[DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) · [y0usaf/pi-jev](https://github.com/y0usaf/pi-jev) · [jomatsu/pi-jev-auto-mode](https://github.com/jomatsu/pi-jev-auto-mode) · [leepokai/jev-guard](https://github.com/leepokai/jev-guard) · [qkal/Canny](https://github.com/qkal/Canny) · [thruwire/foreman](https://github.com/thruwire/foreman) · [alexshpunt/pi-agent-foreman](https://github.com/alexshpunt/pi-agent-foreman) · [GhalebDweikat/winnow](https://github.com/GhalebDweikat/winnow) · [compozy/yoshi](https://github.com/compozy/yoshi) · [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) · [leonaaardob/fast-dev-compaction](https://github.com/leonaaardob/fast-dev-compaction) · [furedea/reflex-state](https://github.com/furedea/reflex-state) · [huntedman/JevLint](https://github.com/huntedman/JevLint) · [BeLazy167/typesafe-mod](https://github.com/BeLazy167/typesafe-mod) · [tonyzdev/PiJ](https://github.com/tonyzdev/PiJ) · [legacybridge-tech/pi-typesafe-jev](https://github.com/legacybridge-tech/pi-typesafe-jev) · [TheoOliveira/pi-jev](https://github.com/TheoOliveira/pi-jev)

### Skill routing
[Dicklesworthstone/skillranker](https://github.com/Dicklesworthstone/skillranker) · [ShivamPansuriya/jev-skill-gate](https://github.com/ShivamPansuriya/jev-skill-gate) · [DECRUX9812/typesafe-skill-router](https://github.com/DECRUX9812/typesafe-skill-router) · [GodsBoy/jev-agent-skill-router](https://github.com/GodsBoy/jev-agent-skill-router) · [HyunjunJeon/jev-judgment](https://github.com/HyunjunJeon/jev-judgment) · [kitze/skillbox](https://github.com/kitze/skillbox)

### Model and task routing
[nidhi-singh02/agent-router](https://github.com/nidhi-singh02/agent-router) · [0xNatoshi/jev-codex-router](https://github.com/0xNatoshi/jev-codex-router) · [iamvatsalpatel/tiershift](https://github.com/iamvatsalpatel/tiershift) · [tylerjharden/ailerix](https://github.com/tylerjharden/ailerix) · [MongLong0214/jev-gate](https://github.com/MongLong0214/jev-gate) · [mejiasd3v/pi-jev-router](https://github.com/mejiasd3v/pi-jev-router) · [hugo-alves/jev-router-playground](https://github.com/hugo-alves/jev-router-playground) · [aniruddh-krovvidi/switchboard](https://github.com/aniruddh-krovvidi/switchboard) · [iammrduncan/typesafe-ai-benchmark](https://github.com/iammrduncan/typesafe-ai-benchmark) (mimics structured output as a baseline)

### Browser agents
[browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) · [jkudish/jev-browser](https://github.com/jkudish/jev-browser) · [Ying-Kai-Liao/jev-browser](https://github.com/Ying-Kai-Liao/jev-browser) · [tontoko/jev-browser](https://github.com/tontoko/jev-browser) · [romaluev/jev-ego](https://github.com/romaluev/jev-ego) · [KesavanKing/jev-browser](https://github.com/KesavanKing/jev-browser) · [vinilana/jev-browser](https://github.com/vinilana/jev-browser) · [CorieW/JevTest](https://github.com/CorieW/JevTest) · [juancristobalgd1/jevRemote](https://github.com/juancristobalgd1/jevRemote) · [ranjan2829/AskJev](https://github.com/ranjan2829/AskJev) · [himomohi/aside-jev](https://github.com/himomohi/aside-jev) · [feliperfpereira/jevBrowser](https://github.com/feliperfpereira/jevBrowser)

### Browser extensions
[kitze/unclutter](https://github.com/kitze/unclutter) · [realZachi/typesafe-adblock](https://github.com/realZachi/typesafe-adblock) · [piyush97/focus-tube](https://github.com/piyush97/focus-tube)

### Computer use
[awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) · [opaielsheikh/ps2-ai-agent](https://github.com/opaielsheikh/ps2-ai-agent)

### Search, retrieval, and data
[ellipsis-dev/blink](https://github.com/ellipsis-dev/blink) · [realZachi/pg-jev](https://github.com/realZachi/pg-jev) · [EugeneBoondock/jevsql](https://github.com/EugeneBoondock/jevsql) · [carlaaiau/jev-reranking](https://github.com/carlaaiau/jev-reranking) · [Charlyhno-eng/jev-document-classification](https://github.com/Charlyhno-eng/jev-document-classification) · [pithings/advocaat](https://github.com/pithings/advocaat) · [Obrais-cloud/ticket-rerank](https://github.com/Obrais-cloud/ticket-rerank) · [Obrais-cloud/typesafe-translate](https://github.com/Obrais-cloud/typesafe-translate) · [mateonunez/jod](https://github.com/mateonunez/jod) (semantic schemas)

### Code review and quality
[devagrawal09/jev-review](https://github.com/devagrawal09/jev-review) · [NiazMorshed2007/jev-review](https://github.com/NiazMorshed2007/jev-review) · [devagrawal09/jev-code](https://github.com/devagrawal09/jev-code) · [raihankhan-rk/diffjury](https://github.com/raihankhan-rk/diffjury) · [opaielsheikh/typesafe-migration-guard](https://github.com/opaielsheikh/typesafe-migration-guard) · [BunsDev/clarity-judge](https://github.com/BunsDev/clarity-judge) · [huntedman/JevLint](https://github.com/huntedman/JevLint) · [JacobLinCool/jev-paper-judge](https://github.com/JacobLinCool/jev-paper-judge)

### Games and simulations
[fhshaik/typesafe-mario](https://github.com/fhshaik/typesafe-mario) · [phyous/tsai-sc](https://github.com/phyous/tsai-sc) · [sorrycc/typesafe-snake](https://github.com/sorrycc/typesafe-snake) · [KyleKreuter/jev2048](https://github.com/KyleKreuter/jev2048) · [AbdelStark/heist-one](https://github.com/AbdelStark/heist-one) · [emrickgarrett/OneVOneJev](https://github.com/emrickgarrett/OneVOneJev) · [ashaazami/river-run-typesafe](https://github.com/ashaazami/river-run-typesafe) · [Icohen007/jev-play-ping-pong](https://github.com/Icohen007/jev-play-ping-pong) · [rchovatiya88/cyber-breach-jev](https://github.com/rchovatiya88/cyber-breach-jev) · [onionminionops-beep/pdoom-protocol](https://github.com/onionminionops-beep/pdoom-protocol) · [vinilana/live-jev](https://github.com/vinilana/live-jev) · [moedesux/tic-tac-toe-jev](https://github.com/moedesux/tic-tac-toe-jev) · [leftspace89/JevBird](https://github.com/leftspace89/JevBird)

### Robotics
[RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone) · [arielweinberger/jev-autopilot](https://github.com/arielweinberger/jev-autopilot) · [lhemerly/mcts-agent](https://github.com/lhemerly/mcts-agent)

### Trading and markets
[jarrodwatts/jev-trader](https://github.com/jarrodwatts/jev-trader) · [justinhe16/trade-jev](https://github.com/justinhe16/trade-jev) · [zadescoxp/Jev-Trades](https://github.com/zadescoxp/Jev-Trades) · [sosopop/jev_stock](https://github.com/sosopop/jev_stock) · [rthomas24/jev-realtime](https://github.com/rthomas24/jev-realtime)

### Home automation
[AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev) · [JanOstrowka/typesafe-assist](https://github.com/JanOstrowka/typesafe-assist) · [haseeb-heaven/jev-system-one](https://github.com/haseeb-heaven/jev-system-one) · [kostysh/goblin-hr](https://github.com/kostysh/goblin-hr) (demo)

### Media and language
[ChetasLua/jevmeter](https://github.com/ChetasLua/jevmeter) · [y0usaf/jev-lm](https://github.com/y0usaf/jev-lm) · [adhyaay-karnwal/jev-chat](https://github.com/adhyaay-karnwal/jev-chat) · [sriganesh/jevibe-check](https://github.com/sriganesh/jevibe-check) · [mkotlikov/jev-grug](https://github.com/mkotlikov/jev-grug) · [nsillik/jevvin-off](https://github.com/nsillik/jevvin-off)

### Evaluations and research
[AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) · [RINNECODER/jev-behavior-study](https://github.com/RINNECODER/jev-behavior-study) · [mahlernim/jev-korean-benchmark](https://github.com/mahlernim/jev-korean-benchmark) · [wondertwins/jev-benchmark](https://github.com/wondertwins/jev-benchmark) · [FirasSX914/calibre](https://github.com/FirasSX914/calibre) · [iammrduncan/typesafe-ai-benchmark](https://github.com/iammrduncan/typesafe-ai-benchmark) · [OmniJev/awesome-jev](https://github.com/OmniJev/awesome-jev) · [Heman10x-NGU/Verdict-open-jev](https://github.com/Heman10x-NGU/Verdict-open-jev) · [dnakhoa/jev-deferred-crispification](https://github.com/dnakhoa/jev-deferred-crispification) (position paper)

### Open reproductions and local models
[TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev) · [ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) · [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) · [r-ms/mini-jev](https://github.com/r-ms/mini-jev) · [kshetrajna12/reflex](https://github.com/kshetrajna12/reflex) · [akash-kamat/system-one-gemma](https://github.com/akash-kamat/system-one-gemma) · [JoshuaSP/open-jev](https://github.com/JoshuaSP/open-jev) · [daseinlabs/open-jev](https://github.com/daseinlabs/open-jev) · [TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) · [olanotolu/jevbetter](https://github.com/olanotolu/jevbetter) · [rorshopping/jev-on-a-laptop](https://github.com/rorshopping/jev-on-a-laptop) · [hr98w/jev-visual](https://github.com/hr98w/jev-visual) · [kikoncuo/jevfire](https://github.com/kikoncuo/jevfire) · [stephanj/parallelConstraintDecoding](https://github.com/stephanj/parallelConstraintDecoding)

### SDKs and clients
Official: [typesafe-ai/system-one-adapter-python](https://github.com/typesafe-ai/system-one-adapter-python) (80★, drop-in replacement backed by LLM APIs for comparison).

Community SDKs: [AboveColin/jevclient](https://github.com/AboveColin/jevclient) (Python) · [anilsenay/jev](https://github.com/anilsenay/jev) (Go) · [zhirschtritt/typesafe-go](https://github.com/zhirschtritt/typesafe-go) (Go) · [valksor/typesafe-sdk-go](https://github.com/valksor/typesafe-sdk-go) (Go) · [Stumble/jev-go](https://github.com/Stumble/jev-go) (Go) · [kazz187/jev-sdk-go](https://github.com/kazz187/jev-sdk-go) (Go) · [AbdelStark/typesafe-rs](https://github.com/AbdelStark/typesafe-rs) (Rust) · [AbdelStark/s1-rs](https://github.com/AbdelStark/s1-rs) (Rust) · [dannote/jev](https://github.com/dannote/jev) (Elixir) · [typesend/typesafe_ai](https://github.com/typesend/typesafe_ai) (Elixir) · [nshkrdotcom/typesafe_sdk](https://github.com/nshkrdotcom/typesafe_sdk) (Elixir) · [InsaneArts/typesafe-sdk-swift](https://github.com/InsaneArts/typesafe-sdk-swift) (Swift) · [Hawxy/TypeSafeAI.Net](https://github.com/Hawxy/TypeSafeAI.Net) (.NET) · [valksor/typesafe-sdk-php](https://github.com/valksor/typesafe-sdk-php) (PHP) · [binnash/typesafe-sdk](https://github.com/binnash/typesafe-sdk) (PHP/Laravel)

### CLIs
[y0usaf/typesafe-cli](https://github.com/y0usaf/typesafe-cli) · [shiftynick/jev-axi](https://github.com/shiftynick/jev-axi) · [jtsang4/jev-cli](https://github.com/jtsang4/jev-cli) · [tumf/jev-cli](https://github.com/tumf/jev-cli) · [geilt/typesafe-cli](https://github.com/geilt/typesafe-cli) · [sharziki/semdecide](https://github.com/sharziki/semdecide) (Unix pipelines and CI) · [StefanoITA/ts-jev-cost-calculator](https://github.com/StefanoITA/ts-jev-cost-calculator)

### MCP servers
[jkudish/jev-mcp](https://github.com/jkudish/jev-mcp) · [blakestone-x/jev-mcp](https://github.com/blakestone-x/jev-mcp) · [rashedInt32/jev-mcp](https://github.com/rashedInt32/jev-mcp) · plus browser MCPs from [Ying-Kai-Liao](https://github.com/Ying-Kai-Liao/jev-browser) and [tontoko](https://github.com/tontoko/jev-browser)

### Agent framework integrations
[3clyp50/a0-typesafe-ai](https://github.com/3clyp50/a0-typesafe-ai) (Agent Zero) · [shantanugoel/ask-jev-skill](https://github.com/shantanugoel/ask-jev-skill) (Hermes) · [DE CRUX9812/typesafe-skill-router](https://github.com/DECRUX9812/typesafe-skill-router) (Hermes) · [Kevthetech143/super-jev](https://github.com/Kevthetech143/super-jev) · [hamakyo/jev-starter](https://github.com/hamakyo/jev-starter) · [docxology/daf-jev](https://github.com/docxology/daf-jev) · [GiesN/typesafe-jev-workflow](https://github.com/GiesN/typesafe-jev-workflow) · [BrendanH18/jev-lab](https://github.com/BrendanH18/jev-lab)

### Skills and agent guidance
[dbreunig/building-with-jev-skill](https://github.com/dbreunig/building-with-jev-skill) - "a skill for writing and improving programs that call Jev" · [samtay32/jev-system-architect](https://github.com/samtay32/jev-system-architect) - finds fuzzy semantic judgment and turns it into primitives · official: `typesafe-ai/skills`

### Domain-specific
[gtaras7/typesafe-jev](https://github.com/gtaras7/typesafe-jev) (CV screening) · [Foadsf/jev-for-engineers](https://github.com/Foadsf/jev-for-engineers) (mechanical/electrical engineering: CAD/CAE/CAM routing) · [brainstormity/Jev-Moderation-Bot](https://github.com/brainstormity/Jev-Moderation-Bot) · [kostysh/goblin-hr](https://github.com/kostysh/goblin-hr) · [bahramzada/jev-taxi-dispatch](https://github.com/bahramzada/jev-taxi-dispatch) · [opaielsheikh/ai-elo-ranker](https://github.com/opaielsheikh/ai-elo-ranker) · [KesavanKing](https://github.com/KesavanKing/jev-browser)

### Games-adjacent / misc
[tentacode/jevendsdestrucs](https://github.com/tentacode/jevendsdestrucs) · [monteduro/killmyidea](https://github.com/monteduro/killmyidea) · [DeepBlueDynamics/typesafe-arena](https://github.com/DeepBlueDynamics/typesafe-arena) · [amithkk/jev-experiments](https://github.com/amithkk/jev-experiments) · [Bud-ro/jev-demos](https://github.com/Bud-ro/jev-demos) · [dnellis74/doctrine](https://github.com/dnellis74/doctrine) · [cardotrejos/jev-user-jury](https://github.com/cardotrejos/jev-user-jury) · [jdhornsby/typesafe-jev](https://github.com/jdhornsby/typesafe-jev)

---

## Official TypeSafe resources

| Resource | Link |
| --- | --- |
| Product | [typesafe.ai](https://typesafe.ai/) |
| Launch post | [Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) |
| Documentation | [docs.typesafe.ai](https://docs.typesafe.ai/introduction) |
| Models and pricing | [docs.typesafe.ai/models](https://docs.typesafe.ai/models) |
| Primitives | [docs.typesafe.ai/primitives](https://docs.typesafe.ai/primitives) |
| Patterns | [docs.typesafe.ai/patterns](https://docs.typesafe.ai/patterns) |
| Use-case map | [docs.typesafe.ai/concepts/use-case-map](https://docs.typesafe.ai/concepts/use-case-map) |
| Design guide | [docs.typesafe.ai/concepts/how-to-build-with-system-one](https://docs.typesafe.ai/concepts/how-to-build-with-system-one) |
| Jaggedness (failure modes) | [docs.typesafe.ai/model-jaggedness/jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13) |
| Cookbooks | [docs.typesafe.ai/cookbooks](https://docs.typesafe.ai/) |
| Workflow evals | [evals.typesafe.ai](https://evals.typesafe.ai/) |
| Console | [console.typesafe.ai](https://console.typesafe.ai) |
| Agent skill | [docs.typesafe.ai/agent-skill](https://docs.typesafe.ai/agent-skill) |
| Python SDK | [typesafe-ai/typesafe-sdk-python](https://github.com/typesafe-ai/typesafe-sdk-python) |
| JS SDK | [typesafe-ai/typesafe-sdk-js](https://github.com/typesafe-ai/typesafe-sdk-js) |
| System One adapter | [typesafe-ai/system-one-adapter-python](https://github.com/typesafe-ai/system-one-adapter-python) |
| Discord | [discord.gg/WUujKYBp8s](https://discord.com/invite/WUujKYBp8s) |
| X | [@typesafeai](https://x.com/typesafeai) |
| Founder on X | [@CompleteSkeptic](https://x.com/CompleteSkeptic) (Diogo Almeida) |

---

## Writing and analysis

| Source | Angle |
| --- | --- |
| [DataCamp](https://www.datacamp.com/blog/system-one-models-jev) | Accessible explainer with the vendor benchmark table |
| [Valyu AI practical guide](https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e) | The most complete practical guide; five patterns and the failure modes |
| [Pere Pages](https://pearpages.com/blog/2026/09/16/jev-sorted-what-typesafes-system-one-model-actually-is-and-what-is-still-just-a-claim) | Sharpest skeptical analysis of the claims |
| [Sean Goedecke](https://www.seangoedecke.com/jev-means-structured-output-is-interesting-again/) | Technical argument that the moat is thin |
| [Every / Mike Taylor](https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds) | The only independent measurement in the launch window |
| [The Register](https://www.theregister.com/ai-and-ml/2026/09/16/typesafe-ai-debuts-model-for-machines-that-plays-doom/5296711) | Neutral launch coverage; funding and stealth details |
| [RuntimeWire](https://runtimewire.com/article/typesafe-jev-system-one-ai-model-early-access) | Notes the largest claims remain internally tested |
| [Kingy AI](https://kingy.ai/blog/typesafe-jev-review-the-ai-model-that-doesnt-generate-text/) | Frames "System One" as a company term, not a standard category |
| [Hacker News thread](https://news.ycombinator.com/item?id=49717558) | 1,861 points, 490 comments, with the founder replying |
| [AI Wiki: Diogo Almeida](https://aiwiki.ai/wiki/diogo_almeida) | Founder background and funding |

---

## How this list was built

```
gh search repos "jev typesafe" --limit 60
gh search repos --topic=jev --limit 60
gh search repos --topic=typesafe-ai --limit 50
gh search repos "jev system one" --limit 60
gh search repos "jev" language:Python --limit 60
gh search repos "jev" language:TypeScript --limit 60
```

Then metadata and READMEs for the 55 most relevant repositories via `gh api`. Star counts are live at the time of collection.

**This list will go stale within days.** If something here is wrong or missing, open a PR.
