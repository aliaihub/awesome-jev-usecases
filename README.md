# Awesome Jev Use Cases

> Real use cases, working patterns, and hard-won guidance for building with **Jev**, TypeSafe AI's System One model — the model that returns typed, probabilistic decisions instead of text.

Jev is not a chatbot. You send it program state and typed questions; it returns typed answers with calibrated probabilities in 70–500 ms. This repository collects what people have actually built with it, and - more importantly - how to use it efficiently and effectively.

```
state + typed questions -> typed answers + probabilities -> your code decides
```

**Status:** research snapshot as of 2026-09-18. Jev is in early access and moving fast. Prices, limits, and aliases will change. Every claim below links to its source.

---

## Start here

| If you want to… | Go to |
| --- | --- |
| Understand what Jev is and when to reach for it | [docs/what-is-jev.md](docs/what-is-jev.md) |
| Make your first call in five minutes | [docs/getting-started.md](docs/getting-started.md) |
| Learn the design method | [docs/how-to-use-jev-effectively.md](docs/how-to-use-jev-effectively.md) |
| Steal a proven architecture | [docs/patterns.md](docs/patterns.md) |
| Avoid the mistakes everyone makes | [docs/failure-modes.md](docs/failure-modes.md) |
| Decide Jev vs LLM vs a classifier | [docs/model-selection.md](docs/model-selection.md) |
| Verify it works on *your* data | [docs/evaluating-jev.md](docs/evaluating-jev.md) |
| See the full use-case catalog | [usecases/README.md](usecases/README.md) |
| Browse real applications people built | [reference/showcase.md](reference/showcase.md) |
| Copy a runnable example | [examples/](examples/) |
| Find ready-made questions | [reference/question-catalog.md](reference/question-catalog.md) |

---

## The 60-second version

Jev is TypeSafe AI's first **System One model**, launched 15 September 2026 by [Diogo Almeida](https://aiwiki.ai/wiki/diogo_almeida) (former OpenAI researcher, co-author of the InstructGPT paper) with roughly $40M in seed funding led by DCVC. The name comes from Daniel Kahneman's *Thinking, Fast and Slow*: LLMs are deliberate System 2 thinkers, and most decisions inside software only need a fast System 1 reflex.

You get exactly three question types, and that is the design, not a limitation:

| Primitive | You declare | Jev returns |
| --- | --- | --- |
| **Choice** | A list of options (up to 255) | The chosen option, a probability per option, a confidence |
| **Score** | An ordered rubric (2–10 levels) | A score (can land between levels), a distribution, a confidence |
| **Noul** | A statement about the state (yes/no) | A single probability 0–1 |

All questions in a request are evaluated **in parallel and in isolation** against the same state. Adding a tenth question costs tokens but barely any time. That single property is what unlocks most of the patterns in this repo.

**The economics, vendor-reported:** $0.042 per million input tokens, output free, 70–500 ms end to end. On TypeSafe's own four-workflow evaluation Jev scores 67.8% agreement with a frontier-model consensus at $0.0004 per case, versus GPT-5.6 Terra at 67.9% and $0.0304. Read [model-selection.md](docs/model-selection.md) for the honest breakdown, including why those multipliers are softer than the headline.

---

## Use-case catalog at a glance

Each category has its own page with the decision shape, evidence, code, and pitfalls.

| # | Use case | Decision shape | Reach for it when |
| --- | --- | --- | --- |
| 1 | [Routing and triage](usecases/01-routing-and-triage.md) | Choice + Score | One known category selects the next code path |
| 2 | [LLM guardrails and verification](usecases/02-llm-guardrails-and-verification.md) | Noul + Score | You must check an LLM's input, output, or tool call |
| 3 | [Agent harness engineering](usecases/03-agent-harness-engineering.md) | Choice + Noul | A coding agent needs a fast semantic supervisor |
| 4 | [Search, reranking, and RAG](usecases/04-search-reranking-and-rag.md) | Choice + Noul | Relevance decides what reaches the context window |
| 5 | [Structured data extraction](usecases/05-structured-data-extraction.md) | Choice over candidates | Known fields must be recovered from messy text |
| 6 | [Classification at scale](usecases/06-classification-at-scale.md) | Choice | Millions of rows, bounded labels |
| 7 | [Feature extraction for ML](usecases/07-feature-extraction-for-ml.md) | Score + Noul | A classical model needs semantic signals |
| 8 | [Real-time loops and games](usecases/08-real-time-and-games.md) | Choice per tick | Decisions faster than human perception |
| 9 | [Browser and computer use](usecases/09-browser-and-computer-use.md) | Choice + Noul | A screen must become an action |
| 10 | [Domain applications](usecases/10-domain-applications.md) | All | Legal, finance, insurance, health, recruiting, commerce, moderation |
| 11 | [Frontier and fun](usecases/11-frontier-and-fun.md) | All | The demos that show what the primitive can do |

Want the raw inventory of everything the community has shipped? See [reference/showcase.md](reference/showcase.md) for the application showcase, or [reference/ecosystem.md](reference/ecosystem.md) for the full census including SDKs and infrastructure.

---

## The one-paragraph summary of how to use Jev well

**Keep control flow in code and give the model narrow, atomic judgments.** Decompose a broad question into several literal ones and recombine their probabilities with weights you own. Send only the state a question needs, because accuracy falls as irrelevant detail grows. Ask everything you might need in one call, then let code discard what was irrelevant. Gate actions on confidence, scaled to what being wrong costs. Do not ask Jev to count, do arithmetic, compare dates, or generate text. And test the thresholds on your own traffic before you trust them, because the calibration claim is asserted by the vendor and not yet independently reproduced.

The rest of this repo is the long version of that paragraph.

---

## Ground rules for this list

- **Evidence over vibes.** Every project entry states what was measured and who measured it. Vendor-reported numbers are labeled as such.
- **Use cases must use Jev.** A generic classifier that merely resembles the pattern is not included.
- **Launch-week artifacts are labeled.** Many projects were built in the first 72 hours. Treat them as proofs of concept, not production case studies.
- **Corrections welcome.** See [CONTRIBUTING.md](CONTRIBUTING.md). If a number here is wrong or stale, open a PR.

---

## Related lists

This repository is use-case and guidance focused. For pure project indexes, see [AbdelStark/awesome-typesafe](https://github.com/AbdelStark/awesome-typesafe), [yibie/awesome-jev](https://github.com/yibie/awesome-jev), [Anil-matcha/awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe), [AnotiaWang/awesome-jev](https://github.com/AnotiaWang/awesome-jev), and [OmniJev/awesome-jev](https://github.com/OmniJev/awesome-jev).

## License

[MIT](LICENSE). Not affiliated with or endorsed by TypeSafe AI.
