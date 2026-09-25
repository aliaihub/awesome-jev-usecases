# Application showcase

Focused applications and use cases built on Jev, **one detailed entry each**: what it does, what questions Jev is actually asked, what was measured, and the pattern you can lift.

This is the "show me what people built" list. It is deliberately not a link dump - a bare table row tells you a project exists but not whether it is worth reading. Every entry here states the decision shape and, where it exists, the number.

**Not included:** SDKs, client libraries, CLI wrappers, skill packs, and harness plumbing. Those are in [ecosystem.md](ecosystem.md).

**Snapshot:** 2026-09-18, three days after launch. Star counts are as of collection time and move daily in this ecosystem.

> **Stars are not the ranking here.** Within a launch week they track attention, not quality. [jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) and [jev-rerank-bench](https://github.com/anessbelbati/jev-rerank-bench) sit at 1 star each and are the two most rigorous projects in this document; a game demo sits at 200+. Entries are ordered by category and by whether they publish evidence, not by star count. The `[measured]` and `[architecture]` labels are the thing to sort by.

> **Read this first.** Every project here was created on or after 2026-09-15 and is therefore a **launch-week artifact**. Treat them as proofs of concept, not production case studies. Measured results are **self-reported by their authors** unless stated otherwise, and none has been independently reproduced. The projects marked **[measured]** publish numbers; those marked **[architecture]** describe a design without evaluation.

---

## Quick index

| Category | Projects with measurements | Projects with architecture only |
| --- | --- | --- |
| [Agent supervision](#agent-supervision-and-guardrails) | pi-warden, jev-shield, jev-skill-gate, pi-jev | fast-jev-compaction, winnow, Canny, yoshi, jev-guard, omp, toolgate, agent-handoff-gate |
| [Security](#security-and-adversarial-robustness) | jev-sec-bench, typesafe-ai-firewall, kiarina safety lab | Jev-Moderation-Bot, Jeeves |
| [Code and developer tools](#code-and-developer-tools) | jev-review (Niaz), commit-miner, JevLint | jev-review (deva), blink, DiffJury, migration-guard |
| [Search and retrieval](#search-and-retrieval) | jev-rerank-bench, pg-jev, JevSQL | jev-search, jev-reranking, jevlogs, jev-tree |
| [Classification and evaluation](#classification-and-evaluation) | calibre, padflow, synergy-screening, agent-failure-bench, jev-benchmarks, tiab-review-plugin, Jev-sample | kyotsu-ai-bench, document-classification, CV screening, nola triage |
| [Computer use](#computer-use-and-browser-agents) | jev-ultrafast, typesafe-computer-use, cua suggest_action (open PR) | otto, almond-fastloop, jev-browser (x5), AskJev, voice-browser, open-typesafe-camoufox |
| [Trading and markets](#trading-and-markets) | jev-trader | Jev-Trades, trade-jev, jevbot, jev_stock, axiom-runtime |
| [Real-time and games](#real-time-loops-games-and-robotics) | tsai-sc, ping-pong, little-airways, live-jev, jev-doom, dr-drone, jev-benchmark | mario, civ2, snake, jev-snake, heist-one, MAGI, + 8 more |
| [Domain applications](#domain-applications) | synergy-screening, ticket-quest, Jev Social | Jeeves, CV screening, adblock, FeedGate, jevibe-check, focus-tube, HA-Jev |
| [Open reproductions](#open-reproductions-and-local-models) | openjev, Verdict, kw2828, jevlike | jevmlx, reflex, gemma, mini-jev, + 6 more |

---

## Agent supervision and guardrails

The largest cluster, and the one with the best evidence. Every project here puts Jev **around** an agent rather than inside it.

### [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) - guardrails that steer instead of interrupting **[measured]**

**What it does.** Judges every write and edit against the rules in your `pi-warden.md`, then quotes the broken rule back into the agent's own context. Six guards: rules, slop, stuck loops, done-claims, context saving, and irreversible actions.

**The measured result.** 150 paired headless runs broke a project rule **6 times with the guard off and 0 times with it on**. Across 321 of the author's own sessions (17,160 guarded calls), the action guard held 42 calls; the next message approved 5, so 37 stood.

**Why the cost matters.** ~1,000 input tokens per judgment, **roughly $0.00004 and 0.3 s**, "which is why it can fire on every guarded call." That number is the whole design.

**The pattern to lift.** Name the violation in the steering message. The difference between a guard that blocks and one that *explains* is the difference between a stuck agent and a self-correcting one.

### [y0usaf/pi-jev](https://github.com/y0usaf/pi-jev) (27★) - decision layer for the Pi coding agent **[measured]**

**What it does.** Three components: a gate that judges `bash`, `write`, and `edit` calls before they run; an output judge that reads what a `bash` call printed; and a `jev_ask` tool letting the model request the same kind of judgment itself.

**The gate questions and their thresholds** - the clearest published example of per-hazard thresholds in the ecosystem:

| Question | Type | Threshold |
| --- | --- | ---: |
| Is this action destructive? | Noul | 0.90 |
| Does this send local data or secrets off-machine? | Noul | 0.70 |
| Does this affect anything beyond what the user asked for? | Noul | - |

**The pattern to lift.** Different thresholds per hazard. Exfiltration is caught at 0.70 because the cost of a false positive is a prompt; destruction needs 0.90 because the cost of a false negative is data.

### [caiovicentino/jev-shield](https://github.com/caiovicentino/jev-shield) - semantic MCP firewall **[measured]**

**What it does.** Sits between any MCP client and server (stdio) and screens every tool call, tool result, and tool description. Three layers: structural (deterministic allowlists), semantic (Jev), and session (taint tracking, so a flagged result escalates subsequent calls).

**The measured result.** **94% block recall, 0 false positives, ~$0.00002/check.** The bundled demo runs 10 verifications for $0.0003 total at 558 ms median. The demo catches a poisoned tool description (`tool_poisoning=0.9x`), injection hidden in search results, and a `.env` leak.

**The argument for a semantic firewall.** Existing MCP proxies are pattern-based and catch payloads that look like known attacks. Attackers paraphrase. This catches the *meaning*.

### [ShivamPansuriya/jev-skill-gate](https://github.com/ShivamPansuriya/jev-skill-gate) - cut the skill manifest by ~75% **[measured]**

**The problem.** Claude Code loads every skill description at session start. On a large skills library that is ~10,000 tokens before you type anything.

**What it does.** Scores each installed skill against the project you are in, then writes `skillOverrides` so only relevant skills reach the model. One parallel pass over all skills.

**The measured result.** **12,750 → 3,185 tokens** on a 217-skill install, for **$0.0009**. And critically, it ships an eval rather than a claim: 20 labelled cases against the live inventory, with state being the prompt only (no project signals), which is the harder test.

**The pattern to lift.** "A gate that saves tokens by hiding what you needed is worse than no gate." If your gate is a filter, you owe it an eval on whether it keeps what matters.

### [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) (707★) - lossless context compaction **[architecture]**

**What it does.** Replaces Claude Code's compaction summary with Jev decisions. Every tool call and result is scored in one fast request; stale ones are dropped or truncated; **everything kept stays verbatim**.

**Why this beats summarization.** A summary is lossy. A file path, exact error, or constraint can disappear even when it matters later. This never rewrites anything - it only deletes what Jev says is no longer needed, and asks Jev while showing it the whole conversation.

**The engineering detail worth copying.** The state is fitted into `maxStateTokens` (25k default) in *stages*, each applied only if the previous was not enough: tool inputs truncated to 1000 → 200 → 60 chars; long texts abridged to head + tail; old messages collapsed to a note; old tool calls reduced to one line each. Tokens are estimated without a tokenizer (a word per six letters, half a token per digit) calibrated to land slightly above Jev's reported count.

**The pattern to lift.** Deletion-plus-recall is a stronger contract than summarization. You can always restore the full text; you can never restore a summary that dropped the one detail that mattered.

### [GhalebDweikat/winnow](https://github.com/GhalebDweikat/winnow) - calibrated context sieve **[architecture]**

**What it does.** Every large `Read`, `Bash`, or `Grep` result is split into ~25-line blocks. Jev answers one Noul per block: *is this block needed for the current task?* Confident-no blocks are replaced with a three-line stub - what was hidden, a cheap summary, and a recall key.

**Two safety rules.** If the judge thinks the output shows an error, nothing is hidden. And the judge uses TypeSafe's adapter as a fallback so the pipeline runs even without Jev access - though the README notes the fallback "is not calibrated."

**The pattern to lift.** Keep confident-**yes** and **uncertain** blocks verbatim; only hide confident-no. Uncertainty should never cause a loss.

### Other agent-supervision projects

| Project | What it does | Status |
| --- | --- | --- |
| [qkal/Canny](https://github.com/qkal/Canny) | Refuses an agent's "done" when the ledger shows no test, build, or lint passed since the last edit. Deterministic hooks decide, Jev advises. | Architecture. Includes the verbatim exchange where it caught Claude Code claiming "Done. Skipped tests" |
| [compozy/yoshi](https://github.com/compozy/yoshi) | Context-pruning proxy for Claude Code and Codex; judges new spans above a 50k-token gate, replays cached omissions without rejudging | Architecture. Explicitly a POC moving into CompozyOS |
| [leepokai/jev-guard](https://github.com/leepokai/jev-guard) | Auto mode for Claude Code, Codex, Copilot, Gemini, Cursor, pi, OpenCode via three typed questions (`risk`, `user_requested`, `from_untrusted`) with shared session memory | Architecture. Publishes its cost math (~$0.00004/tool call) |
| [STRML/omp-jevens-classifier](https://github.com/STRML/omp-jevens-classifier) | Closes two holes in OMP's yolo mode: `curl \| sh`, `rm -rf /`, `dd of=/dev/*`, `mkfs`, `kill -9 1`, `nc -e` | Architecture. Note the finding that the native gate ranks critical-pattern matches above prompt rules, so a pattern rule never fires |
| [ndolinschi/toolgate](https://github.com/ndolinschi/toolgate) | allow / ask_human / deny for planned tool calls | Architecture, live demo |
| [jomatsu/pi-jev-auto-mode](https://github.com/jomatsu/pi-jev-auto-mode) | Semantically auto-approves bash/write/edit and fails closed | Architecture |
| [Dicklesworthstone/skillranker](https://github.com/Dicklesworthstone/skillranker) (25★) | Rust CLI ranking skills against live session context, with local feedback and calibration | Architecture |
| [alexshpunt/pi-agent-foreman](https://github.com/alexshpunt/pi-agent-foreman) | Sends agents back to work when they stop early | Architecture |
| [zsoXi/agent-handoff-gate](https://github.com/zsoXi/agent-handoff-gate) | Checks the evidence behind a worker agent's PASS or BLOCKED report before it reaches the lead. Exact checks stay in code; Jev answers narrow questions about what the evidence supports | Experimental spec and offline evaluation kit (v0.1.0). No live adapter yet; reproduces historical metrics |
| [furedea/reflex-state](https://github.com/furedea/reflex-state) | Execution state tracked outside the main LLM | Architecture |
| [tonyzdev/PiJ](https://github.com/tonyzdev/PiJ) | Terminal agent with Jev for skill selection, code ranking, and failure triage | Architecture |
| [valentynkit/jev-belay](https://github.com/valentynkit/jev-belay) | Claude Code Stop hook that reads the transcript for evidence since the last check; only when files changed with nothing passing since does it spend one four-question Jev call on whether "done" is unverified. Fails open on every error path | Self-reported by the author: ~$0.000017/call, reaches the question on 16.6% of stops in one 2,491-stop corpus |

**See also:** [usecases/03-agent-harness-engineering.md](../usecases/03-agent-harness-engineering.md)

---

## Security and adversarial robustness

### [Gaurav-Gosain/jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) - blind public-corpus security benchmarks **[measured]**

**What it does.** Two blind benchmarks on public corpora: **prompt injection** on all 662 labelled messages in `deepset/prompt-injections`, and **vulnerable code** on 200 matched pairs from a public dataset. Run 2026-09-16 against `jev-1.13.0`, with per-sample output committed.

**The measured result** (prompt injection, plain 0.50 cut, no threshold tuning):

| Metric | Value |
| --- | ---: |
| Accuracy | **96.5%** |
| Precision | 96.2% |
| Recall | 95.1% |
| F1 | 95.6% |
| ROC-AUC | 0.9927 |
| ECE | 0.0588 |
| Wall time | 22.7 s for 662 messages, p50 325 ms |

10 false positives and 13 false negatives out of 662.

**The most useful finding.** The same corpus with one change - telling Jev *what the assistant is for* - improved results more than threshold tuning did. That corpus was collected for a news publisher's reader assistant, so "write me a reason why this newspaper is the best" counts as subverting it, while the same message to a general chatbot would not.

**Why this matters.** This is one of the few blind, public-corpus evaluations of Jev anywhere. The author does not use the vendor's harness and does not tune thresholds to flatter the model.

### [AnshChoudhary/typesafe-ai-firewall](https://github.com/AnshChoudhary/typesafe-ai-firewall) - pre-execution firewall for agent tool calls **[measured]**

**What it does.** Gates each agent tool call before it runs. One batched request asks five Nouls, one per hazard (`injection`, `scope_creep`, `exfiltration`, `irreversible`, `credentials`), plus a Score for blast radius. Ordinary code in `firewall/policy.py` turns the answers into ALLOW, APPROVE, or BLOCK.

**The measured result.** A real run against the live API: 600 records, $0.054 total, held-out split of 320. Self-reported by the author, with the full failure inventory in [report.md](https://github.com/AnshChoudhary/typesafe-ai-firewall/blob/main/report.md).

| Gate | Target | Result |
| --- | --- | --- |
| Block rate on benign calls | < 1% | **0.55%** |
| Block rate on hard negatives | < 3% | **0%** |
| Catch rate on injection, exfiltration, multi-hazard | > 90% | **100%** |
| Noul calibration error (ECE) | < 0.10 | 0.156 (missed) |
| p95 added latency | < 500 ms | 595 ms (missed) |
| Cost per gated call | - | $0.0000365 |

The attacks are synthetic and designed by the author, who calls the catch rate a floor rather than proof against a real adversary.

**The ablation is the lesson.** Replacing the five hazard Nouls with one "is this dangerous?" question kept the 100% catch rate but blocked **39.2%** of hard negatives, up from 0%. Removing the situational context dropped the catch rate to **61.6%**.

**The pattern to lift.** One Noul per named hazard, with the final decision in auditable code. Decomposition is what keeps legitimate but scary requests out of the block list.

### [kiarina/labs: typesafe-jev-safety-judgment](https://github.com/kiarina/labs/tree/main/2026/09/17/typesafe-jev-safety-judgment) - moderation and shell-command safety **[measured]**

**What it does.** Evaluates `jev-1.13.0` on two safety jobs: moderation compared with the OpenAI Moderation API, and sorting AI-generated shell commands into safe, needs review, and dangerous before they run. The folder holds all 134 commands, the criteria, the moderation data pipeline, and unit tests for the metrics. Written in Japanese. The `labs` repository predates launch; this experiment was run on 2026-09-17.

**The measured result.** Self-reported by the author.

- Across 134 commands, Jev labeled **no dangerous command as safe**. A regex blocklist missed 14.
- Japanese moderation: of 826 harmful texts, Jev missed **36** and OpenAI Moderation missed **292** (threshold 0.5).
- English moderation: OpenAI was slightly ahead, and its probabilities were better calibrated.
- Jev's recall was 0.956. The author describes it as a gate that rarely misses but over-flags.

**A companion lab measures the API itself.** [typesafe-jev-evaluation](https://github.com/kiarina/labs/tree/main/2026/09/17/typesafe-jev-evaluation) found the input limit at about 33,000 tokens for the state plus one question. Going over returns `400 max_tokens_exceeded` instead of silently truncating. In eight languages, facts planted near the limit were retrieved regardless of position.

**The pattern to lift.** For a safety gate, measure misses and over-flags separately and set the threshold by the cost of a miss. High recall with extra flags suits "auto-allow only when confidently safe, send the rest to a human".

### [brainstormity/Jev-Moderation-Bot](https://github.com/brainstormity/Jev-Moderation-Bot) (15★) - real-time Discord moderation **[architecture]**

**What it does.** Detects phishing links, spam, and social engineering in real time. Evaluates message content plus contextual metadata (author account age, link presence, channel) in parallel, then applies a **4-stage progressive escalation ladder**: warning DM → final warning DM → timeout → ban. Logs to native Discord audit logs and a `#mod-log` channel.

**The pattern to lift.** Escalation as a ladder rather than a single threshold, with the model's confidence feeding the stage. Also note the "dynamic in-context learning" feature that adapts criteria to the specific community.

### [Infrawrench/Jeeves](https://github.com/Infrawrench/Jeeves) - Discord moderation in plain English **[architecture]**

**What it does.** Admins describe rules in natural language:

```
/addaction question:Strike users who make your mum jokes.
/addaction question:Ban a user when they have at least 3 strikes.
```

Jev interprets messages and strike history; Gemini describes image attachments and generates rules needing computation; PostgreSQL tracks messages, rules, and strikes. **It ships an inviteable live bot**, not just a repo.

**The pattern to lift.** Natural-language policy as the interface, with the model interpreting rather than hard-coding rules. Split multi-modal work by capability: Jev for text judgment, a generative model for descriptions.

---

## Code and developer tools

### [devagrawal09/jev-review](https://github.com/devagrawal09/jev-review) (180★) - staged code review **[architecture]**

**What it does.** Reviews a Git diff or scans a whole codebase as a **staged pipeline**, not one big prompt:

```
Noul risk matrix
  -> Choice + Score file profiles
  -> Choice evidence selection
  -> Choice mechanism classification
  -> Score severity
  -> conditional Choice reviewer routing
```

**Why the staging matters.** It "selects concrete diff hunks or source regions before scoring impact" - so the model reads the relevant evidence, not the whole diff, at each stage. Screens correctness, security, reliability, compatibility, and test coverage. Uses changed or related tests as context when judging test gaps.

**The engineering detail.** Applies thresholds and workflow policy in code; binds the dashboard to `127.0.0.1` and never serves environment files.

**The pattern to lift.** [Retrieve, then judge](../docs/patterns.md#pattern-5---retrieve-then-judge) applied to code: select the evidence before scoring it.

### [NiazMorshed2007/jev-review](https://github.com/NiazMorshed2007/jev-review) (86★) - continuous quality scores in-context **[measured]**

**What it does.** Runs as a local MCP server and gives Claude Code, Codex, Cursor, and OpenCode structured quality scores **while they work**. One tool: `jev_review`. The agent remains responsible for diagnosing and fixing; Jev supplies a fast scalar signal across correctness, complexity, changeability, modularity, tests, and security.

**Measured?** It publishes a demo video and a quality-dimension breakdown. The notable design property is the security posture: no hosted backend, no database, no telemetry, no author-operated proxy. The only remote request goes directly to Jev with your key.

**The pattern to lift.** Give the agent a **scalar signal mid-work** rather than a report at the end. Cheap enough to run continuously.

### [devanshbatham/commit-miner](https://github.com/devanshbatham/commit-miner) (19★, Rust) - commit classification **[measured]**

**What it does.** Classifies Git commit diffs and messages into bug fixes, security fixes with **CWE tags**, and change types. Scans a local repo or a remote GitHub URL, with `--since`/`--until` ranges and worker pooling (default and max 8).

```bash
commit-miner scan . -n 500 -o report.html
commit-miner scan . --only security,change_performance
commit-miner scan . --cwe 79,89
```

**Measured?** It shows estimated Jev cost from reported token usage and known model pricing, and supports saving/exporting scans as HTML or CSV with filters that preserve the full saved scan.

**The pattern to lift.** CWE tagging makes the output auditable and filterable. A semantic classifier over git history is a genuinely new capability - you could not write this as a regex.

### [huntedman/JevLint](https://github.com/huntedman/JevLint) - semantic linting **[architecture]**

**What it does.** A configurable semantic linter for JS/TS. The built-in `magic-strings` plugin finds application-defined string literals (states, modes, actions) that should be named constants, while exempting display text, paths, and library values. An optional `descriptive-names` plugin finds vague or misleading identifiers.

**The threshold.** Default finding threshold is 0.8, configurable per run: `npx jevlint src --threshold 0.9 --format json`.

**Honest scope note from the README:** naming findings "do not include suggested replacements or automatic renames." It flags, it does not fix.

**The pattern to lift.** This is the category of check you simply cannot write as a regex: "is this string literal a state that should be a constant, or is it display text?" That is a judgment, and it is cheap enough to run on every file.

### Other developer tools

| Project | What it does | Status |
| --- | --- | --- |
| [ellipsis-dev/blink](https://github.com/ellipsis-dev/blink) (13★) | Codebase search with an ensemble of walkers that walk the filesystem and score each node. Returns `src/services/auth/login.ts 74.0%` style distributions | Architecture, with example outputs committed |
| [raihankhan-rk/diffjury](https://github.com/raihankhan-rk/diffjury) | Paste a public PR URL, get a risk judgment. Nine questions in one call: `risk` (Score), `review_depth` (Choice: skim/standard/deep), `needs_design`, `needs_security`, `merge_blocker` (Nouls), `missing_tests`/`docs_debt`/`blast_radius` (Scores), `verdict` (Choice) | Architecture. The question set is a good template |
| [opaielsheikh/typesafe-migration-guard](https://github.com/opaielsheikh/typesafe-migration-guard) | Intercepts DDL in CI/CD and blocks destructive operations (`DROP TABLE`, `DROP COLUMN`, unindexed truncation) with an HTTP 403 before touching production | Architecture. Argues static regex/AST linters are brittle at the edges |
| [BunsDev/clarity-judge](https://github.com/BunsDev/clarity-judge) | Writing quality on **separate named checks** - hedging, em-dash overuse, clarity, filler, tone, passive voice, actionability - each with its own verdict and confidence | Architecture. Ships a no-key demo |
| [kitze/skillbox](https://github.com/kitze/skillbox) (109★) | Self-hosted versioned skill library with MCP, scoped clients, and optional Jev recommendations | Architecture |
| [samtay32/jev-system-architect](https://github.com/samtay32/jev-system-architect) | A skill that finds fuzzy semantic judgment in a design and turns it into small Choice/Score/Noul primitives | Architecture - meta-tooling for the design method |
| [dbreunig/building-with-jev-skill](https://github.com/dbreunig/building-with-jev-skill) (23★) | A skill for writing and improving programs that call Jev | Architecture |
| [valentynkit/jev-commit](https://github.com/valentynkit/jev-commit) | Pre-commit hook: one Jev call judges whether the commit message matches the staged diff, plus debug leftovers and unmentioned work; warns except on a leaked credential, which it blocks | Self-reported by the author: ~$0.00001/commit |
| [valentynkit/jev.nvim](https://github.com/valentynkit/jev.nvim) | Neovim plugin: ask the buffer a plain-language question, Treesitter splits it into functions, Jev scores each one, answers land in quickfix ranked by probability | Architecture. Demo is rendered against a test fixture, not a live measurement |

---

## Search and retrieval

### [anessbelbati/jev-rerank-bench](https://github.com/anessbelbati/jev-rerank-bench) - is Jev a good reranker? **[measured]**

**The question.** Thirty search results, one question: which are useful? Then the same passages to Cohere and ZeroEntropy.

**The measured result** (8 English datasets, 1,617 scored questions, each dataset counting once):

| Model | nDCG@10 | Top pick right | Time/query | $/1,000 | AUROC on "nothing here" |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Jev 4-level rubric, 30 in one call** | **0.692** | **74%** | 422 ms | **$0.45** | 0.75 |
| Cohere Pro | 0.691 | - | - | - | - |
| ZeroEntropy zerank-2 | 0.682 | - | - | - | - |

**The honest conclusion.** The average **does not establish a winner** - Jev 0.692 vs Cohere 0.691. Giving every query equal weight puts Cohere ahead. Jev did better on the negation test (NevIR). An open-source Qwen recipe improved substantially when given one passage at a time but still showed no clear gain over keyword ranking.

**Why this is the best benchmark in the ecosystem.** Every raw API response is saved, the evidence viewer is public, and it reports a tie rather than manufacturing a win. Five more BRIGHT subsets, NevIR negation pairs, and MIRACL French are reported separately. Jev calls used `jev-latest` reporting 1.13.0.

**The pattern to lift.** A 4-level Score rubric over 30 candidates in one call is the right shape for reranking - and at **$0.45 per 1,000 queries** it competes with dedicated rerankers on cost.

### [realZachi/pg-jev](https://github.com/realZachi/pg-jev) (50★) - natural-language SQL predicates **[measured]**

**What it does.** A PostgreSQL extension where `jev()` is an ordinary boolean function, so it composes with everything else in SQL:

```sql
SELECT * FROM people WHERE jev(people, 'the name is European');

SELECT subject, jev_prob(tickets, 'the customer is angry') AS p
FROM tickets ORDER BY p DESC LIMIT 20;

SELECT jev_choice(tickets, 'which team should handle this?',
                  ARRAY['billing', 'technical', 'security', 'sales']) AS team, count(*)
FROM tickets GROUP BY 1;
```

**The measured result.** On a 129-row table: first run **≈1 s, 4 requests, ≈21k input tokens, ≈$0.0009**. Answers are cached per row content for the session, so re-running, changing the threshold, or sorting by probability is **free**.

**The implementation detail that matters.** Rows are packed `jev.batch_size` per request into one shared state (`{"condition": ..., "rows": [...]}`) with one Noul per row. Rows from a subquery or CTE use an anonymous `record` type that cannot be read ahead and are judged one request at a time, so **put `jev()` on base tables when you can**.

**The pattern to lift.** No index, no embeddings, no vector column. For moderate tables, a semantic predicate is simpler than a vector pipeline, and caching makes re-thresholding free.

### [EugeneBoondock/jevsql](https://github.com/EugeneBoondock/jevsql) - the same idea as a library **[measured]**

```sql
SELECT id, customer,
       jev_choice(body, 'Which team should handle this?', 'billing,technical,sales') AS team
FROM tickets
WHERE status = 'open'
  AND jev_bool(body, 'Is the customer angry or frustrated?', 0.6) = 1
ORDER BY jev_score(body, 'How urgent is this?', 'no rush,this week,today,production is down') DESC
LIMIT 10;
```

**The measured result** (100 rows × 2 questions = 200 judgments):

```
cold : 1535 ms · 4 requests · 14567 tokens · $0.00061 · 8 ms per judgment
warm :    3 ms · 0 requests · 200 served from cache · $0.00000
explain (dry run, no API calls): 200 judgments, 4 requests, ~7777 tokens, ~$0.00033
```

**The pattern to lift.** The `explain` dry run. Being able to see the cost of a query before running it is what makes this usable in a pipeline with a budget.

### Other retrieval projects

| Project | What it does | Status |
| --- | --- | --- |
| [superagents-lab/jev-search](https://github.com/superagents-lab/jev-search) | Live web search where Jev chooses sources, time ranges, and query terms, then ranks results with visible relevance scores. Streams newline-delimited JSON: `intent`, `found`, `lane`, `done` | Live at [jev.s1.dev](https://jev.s1.dev). No generated answers - links and snippets only |
| [reachjalil/jev-tree](https://github.com/reachjalil/jev-tree) | Recursive Choice over a taxonomy to get past the 255-option cap. Walks a JSON tree, one call per level, auto-bucketing oversized sibling lists | Architecture. Reports that truncating to 255 "drops the tail (in our bake-off, all of Cape Town)" |
| [reachjalil/jevlogs](https://github.com/reachjalil/jevlogs) | OpenTelemetry log triage: score the signal before expensive LLM analysis | Architecture |
| [carlaiau/jev-reranking](https://github.com/carlaiau/jev-reranking) | Autonomous search-engine experimentation on the TREC WSJ collection | Architecture |
| [Charlyhno-eng/jev-document-classification](https://github.com/Charlyhno-eng/jev-document-classification) | Document classification | Architecture |
| [kylemclaren/jevql](https://github.com/kylemclaren/jevql) | The pg-jev idea without an extension. A psql-style client parses the query, runs the plain SQL on vanilla Postgres, sends the returned rows to Jev in Noul/Choice/Score batches, and applies `jev()` filters, sorts, and groups in the client. `--explain` shows the cost before any API call. Also ships an MCP server and Go/TypeScript/Python SDKs | Architecture. Launch-week artifact. Playground at [jevql.fly.dev](https://jevql.fly.dev/playground) |

**See also:** [usecases/04-search-reranking-and-rag.md](../usecases/04-search-reranking-and-rag.md)

---

## Classification and evaluation

### [FirasSX914/calibre](https://github.com/FirasSX914/calibre) - calibration on a public benchmark **[measured]**

**The measured result.** Calibration and confidence-based routing on **Banking77**: **80.2% accuracy at $0.103 per 500 decisions.**

**Why it matters.** Banking77 is the same dataset where [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) found Jev strong (0.870 accuracy, 0.860 coverage at a 5% error budget). Two independent evaluations on the same public benchmark pointing the same direction is the strongest signal in the ecosystem.

### [zsavage8/padflow-jev-evals](https://github.com/zsavage8/padflow-jev-evals) - a real SaaS workload benchmark **[measured]**

**What it does.** PadFlow is a land-development SaaS. Rather than benchmark on an academic dataset, it publishes the decisions **its own product makes** as JSON schemas plus labelled anonymized rows:

| Decision | The question the software asks |
| --- | --- |
| `route_document` | An email or file arrived. Which project, and what kind of document? |
| `code_transaction` | A QuickBooks transaction synced. Which budget line and draw? |
| `classify_import_value` | A value was read from an import. What is it? |

Every schema shares one shape: an `input` object, a `decision` enum, and a `confidence` in `[0,1]`. The product posts automatically above a threshold and queues the rest for a human.

**Measured:** accuracy *and* calibration per decision, with a runner that scores any OpenAI-compatible model.

**The pattern to lift.** This is the template to copy. **Publish your own workload** rather than evaluating on someone else's dataset. Note the framing: "The threshold is a product decision; the model's job is to be calibrated."

**See also:** [../docs/evaluating-jev.md](../docs/evaluating-jev.md)

### [PistachioAIHQ/jev-synergy-screening](https://github.com/PistachioAIHQ/jev-synergy-screening) - medical abstract screening **[measured]**

**What it does.** Screens MEDLINE title + abstract as include/exclude against **Cohen et al. 2006** abstract-triage gold labels on an ADHD corpus (N=851, 84 include, 9.9%). One Choice (`include|exclude`) plus atomic Nouls (codes 2-7, monograph/imaging/formulation gates), combined in code.

**The measured result** (stratified N=200, seed 20260917):

| Acc | Prec | Rec | F1 | TP/FP/FN/TN | Mean latency | Est. cost |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| **92.0%** | 57.1% | 80.0% | 66.7% | 16/12/4/168 | ~523 ms | **~$0.018** |

**The methodological care is the lesson.** The README warns explicitly: *"H2H-100 has only N=10 positives - do not headline H2H 100%."* It also documents why the comparison is fair: gold is abstract triage only, evidence is the same modality (title + abstract), and it never touches article triage, full-text labels, or MEDLINE publication types.

**The pattern to lift.** Match the gold label's modality exactly, and warn readers off the flattering subsample. This is how you make a benchmark trustworthy.

### [TokenTrim/jev-agent-failure-benchmark](https://github.com/TokenTrim/jev-agent-failure-benchmark) - agent failure attribution **[measured]**

**The question.** Can a fast, cheap decision model find what broke an AI agent as well as a frontier LLM? Benchmarked on the text subset of **Who&When Pro**: given a failed multi-agent run, predict the responsible agent, the decisive step, and the error type.

**The measured result** (all 6,257 text traces):

| Model | Who | When | What (error F1) | All |
| --- | ---: | ---: | ---: | ---: |
| **Jev** | **73.4** | **76.4** | **23.7** | **31.3** |
| GPT-5.4 | 55.7 | 72.3 | 15.3 | 21.3 |
| Claude Sonnet 4.6 | 54.9 | 69.8 | 19.1 | 22.4 |
| GLM-5 | 54.9 | 71.1 | 22.2 | 25.3 |
| Qwen3.5-122B | 57.5 | 73.9 | 17.0 | 21.6 |

**Jev outperforms GPT-5.4 on every axis for ~$1.28 total.** The like-for-like axis is "What" (error type over the same 17-code taxonomy every model sees), where Jev's 23.7 tops the field.

**Why this is remarkable.** Failure attribution is a multi-hop reasoning task - the kind of thing Jev is documented as struggling with. This is the strongest counterexample in the ecosystem to "Jev only does simple classification."

### [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) - the calibration benchmark **[measured]**

**What it measures.** "Whether the reported probabilities are calibrated enough to support automation, how much work can be accepted at a fixed error budget, what resources each decision uses, and how long it takes end to end."

**The measured result** (300 held-out examples, 100 per condition, vs GLiNER2.5):

| Dataset | Labels | Jev acc | GLiNER acc | Jev coverage at ≤5% error |
| --- | ---: | ---: | ---: | ---: |
| AG News | 4 | **0.910** | 0.700 | **0.830** |
| Banking77/BTZSC | 72 | **0.870** | 0.610 | **0.860** |
| DAIR Emotion | 6 | 0.480 | 0.440 | 0.000 |

**The result is deliberately mixed.** Jev wins clearly on news and banking. On DAIR Emotion the accuracy difference is unresolved and Jev is **substantially worse calibrated**: Brier 0.846 vs 0.668, and zero probability on the true label for 16% of examples.

**The lesson.** Jev is well calibrated on concrete, well-defined taxonomies and poorly calibrated on subjective ones. Your label set sits somewhere on that spectrum, and you need to know where.

**Method:** fixed model and dataset revisions, identical examples and label descriptions, a uniform negative control, and paired target-stratified bootstrap intervals. Machine-readable metrics committed.

### [youkiti/tiab-review-plugin](https://github.com/youkiti/tiab-review-plugin/blob/main/experiments/typesafe-jev/report.md) - systematic-review screening at scale **[measured]**

**What it does.** Title and abstract screening for systematic reviews, with one overall Noul per record against each review's criteria. The plugin predates launch; the Jev experiment was added on 2026-09-17. Report in Japanese.

**The measured result.** Six labeled datasets, every record completed, threshold 0.3 (the plugin's default). Self-reported by the author.

| Dataset | N | Recall@0.3 | Specificity@0.3 | Precision@0.3 | Author's verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| depression | 1,993 | 96.1% | 73.1% | 36.9% | Candidate |
| cq1 | 5,628 | 91.2% | 55.0% | 4.0% | Rejected |
| cq2 | 3,400 | 100.0% | 67.9% | 1.5% | Candidate |
| cq3 | 1,038 | 87.5% | 61.3% | 3.4% | Rejected |
| cq4 | 4,326 | 100.0% | 71.9% | 5.7% | Candidate |
| cq5 | 2,253 | 97.6% | 90.5% | 15.9% | Candidate |
| CQ1-5 combined | 16,645 | 95.0% | 67.2% | 4.4% | - |

The adoption rule is recall of at least 95% at threshold 0.3. For comparison, the best existing configuration recorded in the repository reached 99.2% recall on CQ1-5 combined at threshold 0.5.

**The pattern to lift.** Screening is a recall problem: set the threshold for recall first, then read precision. With precision between 1.5% and 5.7% on rare-positive corpora, Jev narrows the pile rather than replacing the reviewer.

### [zephel01/Jev-sample](https://github.com/zephel01/Jev-sample) - one Choice vs four Nouls, measured **[measured]**

**What it does.** Asks Jev the same decision two ways: one 4-option Choice, or four precondition Nouls in parallel in one request. 120 scenarios are generated from every combination of five attributes, and the correct labels come from rules, not from a model. Standard-library client, resumable runner, analysis script, and the raw logs of all 2,320 requests ([PR #1](https://github.com/zephel01/Jev-sample/pull/1)).

**The measured result.** On 120 Japanese scenarios: direct Choice **48.3%**, decomposed Nouls **98.3%**. The individual Nouls scored 120/120, 120/120, 120/120, and 112/120. Self-reported by the author, with raw logs committed.

**The pattern to lift.** This is the cleanest public evidence for [step 4 of the method](../docs/how-to-use-jev-effectively.md#4-decompose-the-questions---this-is-the-most-important-step): same state, same model, and a 50-point accuracy gap from question shape alone.

### Other classification and evaluation projects

| Project | What it does | Status |
| --- | --- | --- |
| [shibadogcap/kyotsu-ai-bench](https://github.com/shibadogcap/kyotsu-ai-bench) | Japan's 2026 Common Test: Jev vs luna-none vs luna-low | Static dashboard |
| [gtaras7/typesafe-jev](https://github.com/gtaras7/typesafe-jev) | CV screening with an editable role policy. Re-scoring every stored candidate takes ~20 ms and costs nothing because judgments are kept separate from the arithmetic | Architecture. Openly documents **the two bugs its own test data caught** - rare and valuable |
| [EdytaKucharska/ticket-quest](https://github.com/EdytaKucharska/ticket-quest) | Ticket triage by Cost of Delay, with a bring-your-own-key LLM race for direct comparison | Live demo in fixture mode. Six narrow questions in one call |
| [nola-lang/nola-typesafe-test](https://github.com/nola-lang/nola-typesafe-test) | Ticket triage in the Nola language. TypeScript literal unions and booleans become Choice and Noul questions, and the same tickets can run through gpt-oss-120b on Cerebras or an OpenAI model | Architecture. A comparison playground with no published numbers |
| [mahlernim/jev-korean-benchmark](https://github.com/mahlernim/jev-korean-benchmark) | Korean understanding and medical text, with runtime and cost evidence | Architecture. Relevant because Jev's non-English support is uneven |
| [Foadsf/jev-for-engineers](https://github.com/Foadsf/jev-for-engineers) | Eight minimal engineering examples: CAD/CAE/CAM routing, FEM result triage, DFM screening, BOM alignment, hallucination-proof extraction. Zero dependencies | Architecture. Every example ends by "taking a decision in ordinary Python, because that is the actual argument" |

---

## Computer use and browser agents

### [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) (2,564★) - the flagship **[measured]**

**What it does.** A browser agent with a dynamic, indexed action space. Every observation produces a numbered element table; one Jev request picks both the operation and its target; a small LLM writes text only when the operation is `TYPE_TEXT`.

**The measured result.** **Zürich → London on real Google Flights in 7.1 seconds, $0.0039**, one natural-language goal, actual text generation, and loading waits included.

**The architectural trick - speculative target fan-out:**

```
                      one TypeSafe request
                     +---------------------------+
page -> element table -> operation                 |
                     | click_target              |
                     | type_text_target          |
                     | select_target, if present |
                     +-------------+-------------+
                         use the matching target
                                   |
                    CLICK [7] -----+---> browser
                TYPE_TEXT [3] -----+
                          |
                   small LLM -> text -> browser
```

Click, type, and select targets are all asked in the same round trip; only the one matching the chosen operation executes. **Two decisions, one network call.** Each target head contains only compatible elements, and native dropdowns carry observed element/option indices.

**The detail that makes it general.** "There are no site-specific action scripts or prepared field strings in the policy."

**The pattern to lift.** [Speculative fan-out](../docs/patterns.md#pattern-1---speculative-fan-out) applied to actions, with the legal action set generated in code so the model cannot choose something impossible.

### [awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) (174★) - macOS computer use at $0.0002/step **[measured]**

**What it does.** Drives a Mac toward a plain-English goal without ever sending a screenshot to a large model. OCR reads the screen, Jev picks the next action, and a writing model is called only when a text field genuinely needs free text.

**The measured result** (same screenshot, same goal, one decision each):

| | Jev | Claude Opus 5 (bare screenshot) |
| --- | ---: | ---: |
| Input tokens | 4,882 | 4,785 |
| **Cost per decision** | **$0.0002** | $0.032 |
| **Cost per 12-step task** | **$0.003** | $0.40–$0.90 |
| **Model latency** | **0.13–0.38 s** | 5.2 s |
| End-to-end step | ~1.5 s | ~5.5 s |

Same input token count, 160x cheaper per decision. The saving comes entirely from how the input is represented (OCR text vs pixels) and what is asked (a bounded choice vs an open plan).

**The caveat that matters most.** From the README:

> Every piece of reasoning the frontier model does for free has to be rebuilt here as deterministic state.

Specifically: the frontier model read event dates off the pixels and compared them unaided, while this pipeline needed explicit date parsing built around it. **This is the real cost of the approach and the most quoted line in the ecosystem.**

### [NobleSpartan6/otto](https://github.com/NobleSpartan6/otto) - native desktop computer use **[architecture]**

**What it does.** macOS and Windows via native accessibility APIs (macOS Accessibility, Windows UI Automation) plus local OCR for targets accessibility misses. Two modes: Jev-only (TypeSafe key required) and Hybrid (adds a planner for the plan and generated text, with Jev choosing concrete actions between planning calls). A Guided mode presents each action before it executes.

**The honesty is the notable feature.** The README states: "This is not yet a validated SOTA release: broad app compatibility, real model-driven task success, signed installers, and subscription sign-in remain launch gates." It also says model confidence is "shown as a model score, not a guarantee of success."

### [eriestra/almond-fastloop](https://github.com/eriestra/almond-fastloop) - a loop and a benchmark **[architecture]**

**Two artifacts.** A ~200-line, dependency-free browser computer-use loop (Chrome DevTools state → bounded Choice → executor), and **the Browser Use Olympics**, a public benchmark for browser agents with a server-side clock and a Hall of Fame. One prompt, five events, every event scored by the page itself. A whitepaper is committed.

**The pattern to lift.** Ship a benchmark alongside your agent so others can compare. "Nothing a human does is inside the clock."

### Other computer-use projects

| Project | What it does | Status |
| --- | --- | --- |
| [vlad-terin/jev-browser](https://github.com/vlad-terin/jev-browser) (51★) | Uses Jev to select elements inside a continuous observe/act/verify loop **without an agent turn between every step**. The agent supplies directional guidance once; Jev picks the actual observed links | Architecture, with recorded WikiRace scenarios |
| [trycua/cua PR #3914](https://github.com/trycua/cua/pull/3914) | Optional `suggest_action` tool for Cua Driver: Jev picks the next element from an accessibility snapshot (capped at 120 elements) and returns separate `done` and `blocked` readings. No screenshots | **Open, not merged.** The PR reports 8,186 ms per decision step without it vs 580 ms with it, on one Calculator flow. Recipe in [PR #3916](https://github.com/trycua/cua/pull/3916) |
| [matthewdonsemail-lab/open-typesafe-camoufox](https://github.com/matthewdonsemail-lab/open-typesafe-camoufox) | CLI browser agent on a headed Camoufox browser. Code reads the page, Jev picks the next action, and a writing model is called only when a field needs free text. Modeled on `awlevin/typesafe-computer-use` | Architecture. Author estimates ~$0.0002 per step; every run leaves an audit folder |
| [paulsmith/computer-use-jev](https://github.com/paulsmith/computer-use-jev) | macOS computer use in Go, Jev as decision maker. Extracted from the author's `herbie` project | Architecture |
| [Ying-Kai-Liao/jev-browser](https://github.com/Ying-Kai-Liao/jev-browser) | "An LLM plans and Jev decides." Library, CLI, and MCP server | Architecture |
| [tontoko/jev-browser](https://github.com/tontoko/jev-browser) | Grounded Jev/Playwright core with typed SDK, persistent CLI, MCP server, and deterministic assertions | Architecture |
| [jkudish/jev-browser](https://github.com/jkudish/jev-browser) (13★) | Browser use on Jev | Architecture |
| [KesavanKing/jev-browser](https://github.com/KesavanKing/jev-browser) | Local UI where Jev chooses bounded page actions and a text model supplies field values | Architecture |
| [ranjan2829/AskJev](https://github.com/ranjan2829/AskJev) | Website autopilot with a specific guard on irreversible clicks | Architecture |
| [serejaris/voice-browser](https://github.com/serejaris/voice-browser) | Voice and text browser control via Chrome MV3 and a local AI Gateway bridge. Shows an observed abstention screenshot | Architecture |
| [himomohi/aside-jev](https://github.com/himomohi/aside-jev) | Aside browser runtime where Jev supplies Choice/Score/Noul decisions | Architecture |

**See also:** [usecases/09-browser-and-computer-use.md](../usecases/09-browser-and-computer-use.md)

---

## Trading and markets

### [jarrodwatts/jev-trader](https://github.com/jarrodwatts/jev-trader) (555★) - one decision per blockchain block **[measured]**

**What it does.** A market maker on **Kuru MON-USDC**. Every ~300 ms Monad block, Jev reads the order book and answers buy or sell; the bot posts a **post-only limit order one tick inside the touch**, replacing the last one. Fills happen when a taker hits it, so the bot earns the spread instead of paying it.

**The measured result.** Reported model latency in the event stream is **~81 ms**, and the hot loop makes exactly **two RPC round trips** to fit the block budget.

**The engineering details worth studying:**

- **Event schema is fully specified**, including `decision.probabilities`, `upIn10`, `latencyMs`, and `late` - so you can see whether a decision missed its block.
- **`totals.jevUsd`** tracks model cost separately from gas (`gasMon`, `gasUsd`), realized PnL, and unrealized PnL.
- **Dry-run by default.** With no `PRIVATE_KEY` it uses real book data and simulated fills. `MODEL=mock` is a momentum heuristic stand-in.
- **SSE stream** (`/events`) emits one `block` event per block plus `fill` events for live orders.

**The pattern to lift.** Budget the loop to the deadline explicitly. "One decision per block" is a design constraint, not an optimization. And separate model cost from execution cost in your telemetry from day one.

### Other trading projects

| Project | What it does | Status |
| --- | --- | --- |
| [zadescoxp/Jev-Trades](https://github.com/zadescoxp/Jev-Trades) | Next.js dashboard streaming one-minute candles via `yfinance`, computing technical indicators, sending enabled states to Jev, applying decisions to a simulated portfolio. Seven assets | Paper only - **no broker or live order API is connected** |
| [justinhe16/trade-jev](https://github.com/justinhe16/trade-jev) | Backtests Jev as a BUY/SELL/HOLD trader on NQ L10 order-book data | Architecture |
| [tyleree/jevbot](https://github.com/tyleree/jevbot) | Options trading bot, backtest + Alpaca paper only, with Jev as the decision core | Paper only by design |
| [sosopop/jev_stock](https://github.com/sosopop/jev_stock) | Hong Kong stock direction forecasting. Deliberately small reference market (target + HSI + HSTECH) so it "does not silently add a basket of unrelated stocks" | Architecture. **Read its self-assessment**: "JEV is more useful here as a disciplined reasoning layer than as a proven quantitative trading model... The risky part is the word 'probability'" |
| [axiomarchitecture/axiom-agent-runtime](https://github.com/axiomarchitecture/axiom-agent-runtime) | Agentic commerce on Kaspa: **"Jev proposes. Axiom authorizes. Argent enforces."** Jev produces a structured decision (`action`, `asset`, `amount`, `condition`, `confidence`), Axiom turns it into deterministic authorization, Argent prepares covenant-native execution | Working prototype. Real Jev connected; execution prepared but not broadcasting |

**The pattern worth stealing from `axiom-agent-runtime`:** the three-way separation. Probabilistic model proposes, a policy layer authorizes deterministically, an execution layer enforces. That is the correct boundary for anything that moves money.

---

## Real-time loops, games, and robotics

### [phyous/tsai-sc](https://github.com/phyous/tsai-sc) - StarCraft with verified evidence **[measured]**

**What it does.** A harness for **Strongarm**, the first combat mission in the original StarCraft shareware campaign. The 1998 Windows executable runs inside BottleShip; the harness observes structured state, asks `jev-latest` to choose a command, and executes it through ordinary mouse and keyboard input. The game is paused during state reads and inference.

**The verified result.** Jev completed Strongarm. Development attempt 16 reached the game's committed victory outcome, the "Congratulations! You are victorious!" screen was visually reviewed, and the evidence verifier passed.

**The honesty is the point.** The README pre-empts misreading: *"'attempt 16' does not mean sixteen completed matches or sixteen model defeats."* Earlier attempts included interrupted runs and runtime faults. It also states plainly: "This is a bounded mission experiment, not a benchmark of real-time competitive play," and notes it does not use TypeSafe's Doom harness code.

### [Icohen007/jev-play-ping-pong](https://github.com/Icohen007/jev-play-ping-pong) - real-time with a full evidence table **[measured]**

**The measured result** (one recorded Club-difficulty run, no inference pauses):

| Measure | Result |
| --- | ---: |
| Outcome | **Jev won 11-0** |
| Timing mode | Real-time, no inference pauses |
| Decisions | 124 |
| Late actions | 0 |
| Median / max API latency | **325 ms / 889 ms** |
| Elapsed wall time | 269.031 s |
| Input / output tokens | 124,258 / - |

**The pattern to lift.** "Late actions: 0" is the metric that matters in a real-time loop, not win rate. Track whether a decision arrived in time.

### [lbotinelly/jev-little-airways](https://github.com/lbotinelly/jev-little-airways) - a small ATC world with real judgments **[measured]**

**What it does.** A toy archipelago in a glass dome. Airliners and props fly routes; every ~1.6 s each aircraft asks Jev **four questions in one batched request**:

| Question | Options |
| --- | --- |
| `route` | continue / divert to *airport* / hold |
| `broadcast` | declare an emergency? |
| `response` | maintain / give way / relay the mayday / hold / divert |
| `clearance` | approach / go around |

The tower asks Jev to sequence landings (`landing_order`). **The drama plays out because the state carries honest estimates** - `fuel`, `fuelMinutesRemaining`, `destinationMinutesRemaining`, `minutesToReach` per airport - so "can I make it?" is a one-line comparison in code.

**Measured:** ~150 ms per batched request. Each airplane only has information about itself, its surroundings, and nearby traffic.

**The pattern to lift.** Put the arithmetic in the state and the judgment in the model. The model never computes whether fuel suffices; it decides what to do about it.

### [RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone) (53★) - the reference architecture **[measured]**

**What it does.** A Skydio X2 quadrotor flies a five-station obstacle course in MuJoCo using **only its onboard camera**. Nothing about the flight is scripted.

**The layer table is the contribution:**

| Rate | Layer | Owner |
| ---: | --- | --- |
| 500 Hz | Geometric flight controller | Code |
| 50 Hz | Guidance + safety reflex | Code, **always owns safety** |
| 15 Hz | Camera → symbolic scene | Classical CV |
| ~2.5 Hz | Tactical judgment | **Jev, advisory only** |

Classical CV compresses depth and segmentation into five forward range sectors, obstruction height, whether its top edge is visible, and target bearing. Jev answers three questions in one call: `maneuver` (Choice, 6 options), `risk` (Score), `target_truly_lost` (Noul).

**The measured result.** **~110 calls per typical 65 s flight.** Code decides *when* to ask - on an open corridor with the target in view, no call is made - and scenes are fingerprinted so an unchanged situation reuses the last judgment.

**The sentence that defines the architecture:** *"Jev can propose `climb`, but code refuses it unless the obstruction's measured top edge is actually within the aircraft's climb capability."*

### [wondertwins/jev-benchmark](https://github.com/wondertwins/jev-benchmark) - testing in-lane and out-of-lane **[measured]**

**The design.** Two deliberately contrasting tasks:

1. **Chess** - "deliberately outside its lane. Chess is calculation and search wearing a judgment costume."
2. **"Who is the player talking to?"** - "squarely inside its lane." A game where the player speaks aloud to NPCs via speech-to-text and the engine must decide which characters should pay attention.

**The measured result:**

| | Chess | NPC addressee detection |
| --- | --- | --- |
| Result | **No better than random** from a raw board. Beats random by ~65% with code-supplied facts and ~78% with one-ply tactical facts. Finds mate-in-one **24%** of the time. ~**950 Elo** with tactical facts | In-lane task |

**Why it is valuable.** It publishes the negative result alongside the positive one, and it quantifies exactly how much code-supplied context buys you. Everything is committed: code, labelled data, **every raw request and response** (`runs/raw/`), metrics, and a playground. Model served as `jev-1.13.0` on 2026-09-16.

**The pattern to lift.** This is the cleanest demonstration of the [jaggedness page](../docs/failure-modes.md#2-it-is-not-a-calculator)'s warning: Jev is not a calculator, and chess is calculation.

### [lukaske/jev-doom-agent](https://github.com/lukaske/jev-doom-agent) - two engines, one decision-maker **[architecture]**

**What it does.** Two isolated instances of the real Chocolate Doom 3.1.1 engine compiled to WebAssembly play the same Freedoom map from the same initial state. A Jev Choice selects a tactical macro; a local motor controller turns it into Doom controls.

**The details that matter.** A vendored GPL fork exposes health, armor, ammo, damage, coordinates, kills, line-of-sight monsters, and visible pickups to JavaScript via `browser_doom_bridge.c`. **"Jev receives structured game state, not raw pixels."** Jev never controls engine internals directly - the controller executes each macro as movement, turning, firing, weapon, or use inputs. The API key is transmitted once to the local server, kept only in process memory, never logged or persisted, and removed on disconnect.

### [vinilana/live-jev](https://github.com/vinilana/live-jev) - browser self-driving with confidence-gated routing **[measured]**

**What it does.** A 2D top-down autonomous car. Every ~200 ms it converts sensor state to JSON and asks four questions in one call:

| Question | Type | Options |
| --- | --- | --- |
| `lane_action` | Choice | keep_lane / change_left / change_right |
| `speed_action` | Choice | stop / slow_down / hold / speed_up |
| `hazard` | Score | 0 (clear) - 3 (collision likely within seconds) |
| `pedestrian_yield` | Noul | probability ego must stop for a pedestrian |

**The code-side policy is the interesting part:** a low-confidence lane change is ignored; a strong `pedestrian_yield` overrides speed; a severe `hazard` forces at least `slow_down`; and a `stop` is **softened to `slow_down` when nothing is within 1.5x the stopping distance** - so distant pedestrians cause a gentle slowdown, not a halt. Speed steps scale by time since the previous answer, "so a fast Jev does not brake harder than a slow one." A small code reflex (emergency brake, blind-spot abort) exists only for imminent impacts and can be switched off in the UI.

**The pattern to lift.** Two of them: (1) scale actuation by elapsed time so model latency does not change behavior, and (2) never let a model's raw output reach an actuator untranslated.

### Other games and simulations

| Project | What it does | Status |
| --- | --- | --- |
| [fhshaik/typesafe-mario](https://github.com/fhshaik/typesafe-mario) (223★) | Super Mario Bros. from emulator RAM translated to object-centric JSON - motion, jump trajectory, upcoming enemies, terrain, measured response delay, recent-control results, episode progress. Seven legal actions. No screenshots | Architecture. Ships `state-demo` to inspect the exact JSON without launching the game |
| [phyous/tsai-civ2](https://github.com/phyous/tsai-civ2) | Civilization II in a browser with live action probabilities. Named Choice vectors cover empire policy, cities, research, diplomacy, units, exploration, warfare | **Explicitly unverified:** "no complete-game victory has been verified yet" and "displayed values are action probabilities, not a probability of victory" |
| [AbdelStark/heist-one](https://github.com/AbdelStark/heist-one) | A stealth game where guards receive imperfect evidence. Select any guard to inspect its probability distributions, confidence, proposed vs applied intent, latency, and fallback state | Architecture. Ships a 37-second film and live-run evidence. **"Jev proposes / deterministic code owns"** table is a clean specification of the boundary |
| [4anti/jev-broadcast-lab](https://github.com/4anti/jev-broadcast-lab) | A chess arena where chess.js owns legality and Jev only picks from the closed LAN list. Stockfish runs in the browser for the operator HUD | Architecture. **"Engine scores never go into Jev's payload"** - a clean information-boundary demo |
| [sorrycc/typesafe-snake](https://github.com/sorrycc/typesafe-snake) | Snake, one Choice per tick | Architecture. Legal moves and facts generated in code |
| [iammusham/jev-snake](https://github.com/iammusham/jev-snake) | Snake where the engine owns the rules and Jev picks a direction every tick. The engine rejects only 180-degree reversals and never steers Jev away from walls. Ships a human baseline and live confidence and latency telemetry | Architecture |
| [hide-G/magi-system-on-jev](https://github.com/hide-G/magi-system-on-jev) | MAGI from Evangelion: three sages judge independently and decide by majority vote over calibrated probabilities | Live site. A joke that is also a legitimate multi-judge ensemble demo |
| [ashaazami/river-run-typesafe](https://github.com/ashaazami/river-run-typesafe) | A River Raid-inspired river shooter with a Jev pilot. Original code, graphics, and sounds | Architecture. Game is fully playable by a human too |
| [kw2828/OpenJev](https://github.com/kw2828/OpenJev) | Chess policy experiments: four policies, twelve fits, 288 games, plus Doom control | **[measured]** but explicitly negative: exact-delta matched Stockfish on **33.15%** of positions vs 31.75% for direct scoring, and "**fails the engine-loss and game-score continuation criteria**... These development results establish neither a learned world model nor an Elo rating" |
| [arielweinberger/jev-autopilot](https://github.com/arielweinberger/jev-autopilot) | Drone flying point A to B in a random city, avoiding obstacles | Architecture |
| [emrickgarrett/OneVOneJev](https://github.com/emrickgarrett/OneVOneJev) | 1v1 quickscope arena in Three.js | Architecture |
| [marcelocantos/jevons](https://github.com/marcelocantos/jevons) | Personal AI assistant: a coordinator session that decides whether to answer directly or delegate to worker coding agents, with a voice-first UI and iOS wrapper. Named after the Jevons paradox | Architecture |
| [opaielsheikh/ps2-ai-agent](https://github.com/opaielsheikh/ps2-ai-agent) | Autonomous PS2 agent with low-latency frame capture, virtual controller injection, and a broadcast-quality telemetry HUD | Architecture |
| [lhemerly/mcts-agent](https://github.com/lhemerly/mcts-agent) | Discriminative Monte Carlo Tree Search over Jev primitives plus Gemini | Architecture |
| [valentynkit/jev-plays-pokemon-red](https://github.com/valentynkit/jev-plays-pokemon-red) | Pokemon Red on PyBoy: code owns the route and the arithmetic, Jev picks only at branches, and every battle turn logs a faint prediction scored by Brier against what the RAM says | Architecture. Author states calibration is not yet published; the labelled sample (n=5-6 turns) is too small for a meaningful Brier score |

**The recurring lesson across every project in this section:** the legal action set and the world facts are computed in code, and Jev only picks from the legal set. `sorrycc/typesafe-snake`, `4anti/jev-broadcast-lab`, and `fhshaik/typesafe-mario` all state it explicitly.

---

## Domain applications

### [AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev) - Home Assistant integration **[architecture]**

**What it does.** Questions in `configuration.yaml` become sensors: a probability, one of your options with its distribution, or a number that can land between levels. Four actions (`jev.noul`, `jev.choice`, `jev.score`, `jev.ask`) answer inside an automation.

```yaml
automation:
  - alias: Remind about the washing
    triggers:
      - trigger: state
        entity_id: binary_sensor.jev_laundry_forgotten
        to: "on"
        for: "00:10:00"
```

**Three details worth copying.** (1) You point a question at entities, devices, areas, floors, or labels in the normal picker and the state is built for you, so no template is needed. (2) It **reports what it spends** - calls, input tokens, estimated cost per day - plus a daily budget that halts evaluation when it trips. (3) It ships 13 worked examples, four pairing Jev with an LLM.

**The pattern to lift.** A model decision surfaced as an ordinary entity you automate on. That is the cleanest integration shape in the ecosystem: Jev's output becomes a first-class primitive in an existing platform rather than a special case.

### [Infrawrench/Jeeves](https://github.com/Infrawrench/Jeeves) - live Discord bot **[architecture]**

Covered under [Security](#security-and-adversarial-robustness). Notable for being a genuinely inviteable, deployed bot.

### [sriganesh/jevibe-check](https://github.com/sriganesh/jevibe-check) - live tone labeling on Bluesky **[architecture]**

**What it does.** A Chrome extension that labels Bluesky posts and drafts in real time: warmth, constructiveness, tension, sarcasm, clarity, and intent. You can **add custom classifiers with your own questions and labels**, blur or collapse posts matching your filters, and track requests, tokens, and estimated cost.

**Honest scope note:** "Labels are based on text only. Attached images and videos are not analyzed."

**The pattern to lift.** User-defined classifiers. Rather than shipping a fixed model, it exposes the question definition as a setting - which is Jev's actual strength.

### [Foadsf/jev-for-engineers](https://github.com/Foadsf/jev-for-engineers) - mechanical and electrical engineering **[architecture]**

**What it does.** Eight minimal, zero-dependency examples: CAD/CAE/CAM routing, FEM result triage, DFM screening, BOM alignment, and hallucination-proof extraction. Every example ends by "taking a decision in ordinary Python, because that is the actual argument."

**The measured claim it cites** (TypeSafe's own): a 13-question briefing batched into one call is **12.2x cheaper and 10.0x faster** than asking one at a time, with no change in answers.

### [socai-io/jev-social](https://github.com/socai-io/jev-social) - browser-grounded social research **[measured]**

**What it does.** Jev first chooses Instagram, TikTok, or LinkedIn, then makes a new `Choice` over the exact read-only operations currently available. Search results add concrete post and profile URLs to the next choice set. Deterministic Node code rejects unknown choices, cross-platform targets, malformed confidence, and decisions below 0.35; the local [socai CLI](https://github.com/socai-io/socai) executes the accepted operation in the user's signed-in Chrome and returns the observed result to the next decision.

**The measured result.** The project authors preserve [one local Instagram run](https://github.com/socai-io/jev-social/blob/v0.1.5/docs/example-report.md): two searches and one post-detail read captured four source-linked records in **63.969 s**. Only one post was inspected in detail and no individual comment text was captured. The project explicitly labels this a single observation rather than a benchmark or latency guarantee.

**The pattern to lift.** Rebuild the action space from capabilities and observed targets before every decision. Jev selects from concrete operations, while code owns URL validation, confidence gates, access failures, step limits, and execution. This keeps arbitrary shell commands and DOM coordinates outside the model's action space.

### Other domain projects

| Project | Domain | What it does |
| --- | --- | --- |
| [opaielsheikh/typesafe-migration-guard](https://github.com/opaielsheikh/typesafe-migration-guard) | Engineering | Database migration safety gate in CI/CD |
| [gtaras7/typesafe-jev](https://github.com/gtaras7/typesafe-jev) | Recruiting | CV screening with an editable role policy |
| [PistachioAIHQ/jev-synergy-screening](https://github.com/PistachioAIHQ/jev-synergy-screening) | Research | Abstract screening vs published gold labels |
| [brainstormity/Jev-Moderation-Bot](https://github.com/brainstormity/Jev-Moderation-Bot) | Moderation | Discord moderation with a 4-stage escalation ladder |
| [realZachi/typesafe-adblock](https://github.com/realZachi/typesafe-adblock) (23★) | Browser | Chrome extension: "is this DOM element an ad?" |
| [piyush97/focus-tube](https://github.com/piyush97/focus-tube) | Browser | Distraction-free YouTube learning feed |
| [zsoXi/FeedGate](https://github.com/zsoXi/FeedGate) | Browser | Chrome extension that filters X feed noise. Promotion alone never hides a post; a post collapses only when spam signals are high and usefulness is low. A personal-use preview |
| [JanOstrowka/typesafe-assist](https://github.com/JanOstrowka/typesafe-assist) | Home | Home Assistant Assist conversation agent |
| [jflam/jev1](https://github.com/jflam/jev1) | Home | Recreates TypeSafe's own smart-home demo: one batched request, code acts on relevant answers, low confidence gets a confirmation step |
| [jexp/neo4jev](https://github.com/jexp/neo4jev) (7★) | Data | Graph navigation: outgoing relationships become Choice options; a `Noul` for "has the goal been reached?" rides in the same call, so **each hop costs exactly one round trip**. Top-k over returned probabilities implements beam search ranked by sum of log-probabilities to avoid length bias |
| [ChetasLua/jevmeter](https://github.com/ChetasLua/jevmeter) (40★) | Media | A live "BS meter" over any video: every sentence scored, rendered as a 16:9 edit. Presets for debates, earnings calls, and podcasts. **Full debate ≈$0.05**; author reports 99% held-out preset accuracy |
| [adhyaay-karnwal/jev-chat](https://github.com/adhyaay-karnwal/jev-chat) | Research | Autoregression over Jev as a language model - deliberately the wrong use. Ships a paper measuring both the wrong and the TypeSafe-native approach |
| [superagents-lab/jev-search](https://github.com/superagents-lab/jev-search) | Search | Live web search with Jev source selection |
| [kostysh/goblin-hr](https://github.com/kostysh/goblin-hr) | HR | Simple usage demo |
| [EdytaKucharska/ticket-quest](https://github.com/EdytaKucharska/ticket-quest) | Product | Cost of Delay triage with an LLM comparison race |
| [tylerjharden/harden-jev-decides](https://github.com/tylerjharden/harden-jev-decides) | Product | Jev picks which stream idea becomes the live MVP |
| [BunsDev/clarity-judge](https://github.com/BunsDev/clarity-judge) | Writing | Named writing-quality checks with per-check confidence |
| [valentynkit/jev-skip](https://github.com/valentynkit/jev-skip) | Media/Browser | Reads the YouTube caption track and paints a per-segment sponsor probability on the seek bar before the intro ends, no crowd database. Self-reported by the author: 77% of SponsorBlock's sponsor seconds caught over 23 videos, $0.0008/video |

---

## Open reproductions and local models

Not Jev itself. These test whether the *interface* works without the service - relevant if you need local inference, and useful for understanding the pattern. **All of them state plainly that they reproduce the interface, not the model or training.** You get parallelism and typed answers, but not the calibration.

| Project | What it does | Measured |
| --- | --- | --- |
| [TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev) (890★) | Reads typed option probabilities directly off a frozen 4B model's logits. No answer sentence, no JSON repair, no decoding loop. Pins the exact model revision and commits a prompt hash per row | Author reports **2-3x speedup** over prefixed structured output on Qwen2.5-1.5B |
| [Heman10x-NGU/Verdict-open-jev](https://github.com/Heman10x-NGU/Verdict-open-jev) | A 151M ModernBERT decision engine with RLCD-style calibration (Brier loss), a WebGPU in-browser playground, and a **Jev benchmark audit** | **Under 35 ms** per decision |
| [kw2828/OpenJev](https://github.com/kw2828/OpenJev) | Browser decision playground plus reproducible experiments on memory, uncertainty, Doom control, and chess | Publishes negative results in full |
| [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) | Jev-style parallel constrained decisions for any MLX model on Apple Silicon; typed schema-valid JSON in one forward pass | - |
| [kshetrajna12/reflex](https://github.com/kshetrajna12/reflex) (25★) | A small open decision model: state + typed questions → calibrated probabilities, on Qwen3.5 | - |
| [akash-kamat/system-one-gemma](https://github.com/akash-kamat/system-one-gemma) | Gemma 3 270M with a scoring head for fast calibrated decisions in a single forward pass | - |
| [mithalouni/system-one-open](https://github.com/mithalouni/system-one-open) | Open replica on Gemma 4 E2B | - |
| [siliconkernel/vllm-jev-decison](https://github.com/siliconkernel/vllm-jev-decison) | Classification-only typed decisions for vLLM: finite-schema candidate scoring with probabilities | - |
| [kikoncuo/jevfire](https://github.com/kikoncuo/jevfire) | Parallel decisions for CUDA LLMs via vLLM, using the pretrained head to score verified single-token labels and assembling JSON in code | **28 decisions in 497 ms**, reported as **10.3x faster** than generating equivalent constrained JSON on Qwen3.8-27B-FP8 |
| [r-ms/mini-jev](https://github.com/r-ms/mini-jev) | Reads the option letter's logits instead of generating | - |
| [ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) (55★) | A Jev-compatible API endpoint based on open models (prefill-only) | - |
| [rorshopping/jev-on-a-laptop](https://github.com/rorshopping/jev-on-a-laptop) | Jev-style parallel typed decisions on stock 1.5B-8B models on Apple Silicon | Benchmarks committed |
| [hr98w/jev-visual](https://github.com/hr98w/jev-visual) | Visual inference experiment: shared context, direct candidate scoring | - |
| [vinnylarouge/jevlike](https://github.com/vinnylarouge/jevlike) (719★) | Trains a small model with Jev's input and output shape: text plus N options in, one probability per option out, in one pass. The same option-attention head also scores controller buttons from image patches | Doom checkpoint averaged 0.60 kills over 10 episodes. Chess: 4 wins, 46 draws, 0 losses vs a random mover; 0 wins, 2 draws, 48 losses vs Stockfish level 0. The author says the demo clips are not competence claims |
| [olanotolu/jevbetter](https://github.com/olanotolu/jevbetter) | A stronger one-pass scorer over a variable list of text options, with a hashed n-gram encoder and rival-aware attention | - |
| [JoshuaSP/open-jev](https://github.com/JoshuaSP/open-jev) | Typed JSON inference with DiffusionGemma, with Every and Jev benchmark results | - |

**The consistent engineering lesson:** `kikoncuo/jevfire` and `TheoLeeCJ/openjev` both show that the speed advantage comes from **reading logits at fixed option positions instead of sampling tokens**. If you are evaluating whether to self-host, this is the technique to understand.

**See also:** [../docs/model-selection.md](../docs/model-selection.md)

---

## How to read these projects

Four things separate the credible ones from the rest.

**1. A published measurement with a stated sample.**
`pi-warden` (150 paired runs), `jev-sec-bench` (662 + 400 samples), `jev-rerank-bench` (1,617 questions across 14 datasets), `agent-failure-benchmark` (6,257 traces), `typesafe-computer-use` (same screenshot, both models), `ping-pong` (124 decisions, 0 late). The rest describe architecture without numbers.

**2. Committed raw results.**
`jev-rerank-bench` saves every API response. `jev-benchmarks` commits machine-readable metrics with bootstrap intervals. `jev-sec-bench` commits per-sample output. `wondertwins/jev-benchmark` commits every raw request and response. `openjev` pins the model revision and prompt hash per row.

**3. An honest limitations section.**
`RomanSlack/jev-drone`: Jev "cannot be the perception layer, and it cannot run at control rate." `kw2828/OpenJev`: results "establish neither a learned world model nor an Elo rating." `phyous/tsai-sc`: "'attempt 16' does not mean sixteen completed matches." `NobleSpartan6/otto` lists its own launch gates. `PistachioAIHQ` warns against headlining a 100% figure from 10 positives. `sosopop/jev_stock` says "the risky part is the word 'probability'."

**4. Code owns the control flow.**
In every mature project, Jev answers a question and code decides. Where a project lets Jev own the loop, the README usually says it is an experiment.

The projects that do all four are worth your time: **[DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden)**, **[anessbelbati/jev-rerank-bench](https://github.com/anessbelbati/jev-rerank-bench)**, **[Gaurav-Gosain/jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench)**, **[RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone)**, **[awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use)**, and **[TokenTrim/jev-agent-failure-benchmark](https://github.com/TokenTrim/jev-agent-failure-benchmark)**.

---

## What is missing

Where the ecosystem has *not* built yet, as of 2026-09-18. If you build in one of these gaps, it will be the most-cited project in the ecosystem within a week.

- **No production case study at volume.** Everything is launch-week. Nobody has published "we run this on N million requests per day."
- **No independent calibration curve on a live customer workload.** [padflow-jev-evals](https://github.com/zsavage8/padflow-jev-evals) publishes the harness for exactly this, but not results from a deployment.
- **Almost no regulated-domain deployment.** Legal, insurance, and healthcare appear in TypeSafe's own use-case map but not in shipped community projects, with the single exception of the medical screening demo.
- **No longitudinal studies.** Nothing has run long enough to show drift, cost at scale, or behaviour under distribution shift.
- **Thin coverage of extraction.** The documented cookbooks cover it well; community projects mostly do classification and routing instead.
- **No multi-tenant or cost-governance pattern.** Only [HA-Jev](https://github.com/AboveColin/HA-Jev) ships a budget that halts evaluation when it trips.

---

## Related

- [ecosystem.md](ecosystem.md) - the full 401-repo census including SDKs and infrastructure
- [question-catalog.md](question-catalog.md) - ready-to-adapt question sets by domain
- [../usecases/README.md](../usecases/README.md) - worked patterns per category
- [../docs/evaluating-jev.md](../docs/evaluating-jev.md) - how to run the measurements these projects publish
