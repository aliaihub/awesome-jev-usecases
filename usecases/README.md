# Use case catalog

Eleven categories, each with the decision shape, the evidence, working code shapes, and the pitfalls specific to that domain.

Every use case here is either documented by TypeSafe, shipped by a community project, or both. Project entries state what was measured and who measured it. Launch-week artifacts are labeled as such.

| # | Category | Decision shape | Reach for it when |
| --- | --- | --- | --- |
| 1 | [Routing and triage](01-routing-and-triage.md) | Choice + Score | One known category selects the next code path |
| 2 | [LLM guardrails and verification](02-llm-guardrails-and-verification.md) | Noul + Score | You must check an LLM's input, output, or tool call |
| 3 | [Agent harness engineering](03-agent-harness-engineering.md) | Choice + Noul | A coding agent needs a fast semantic supervisor |
| 4 | [Search, reranking, and RAG](04-search-reranking-and-rag.md) | Choice + Noul | Relevance decides what reaches the context window |
| 5 | [Structured data extraction](05-structured-data-extraction.md) | Choice over candidates | Known fields must be recovered from messy text |
| 6 | [Classification at scale](06-classification-at-scale.md) | Choice | Millions of rows, bounded labels |
| 7 | [Feature extraction for ML](07-feature-extraction-for-ml.md) | Score + Noul | A classical model needs semantic signals |
| 8 | [Real-time loops and games](08-real-time-and-games.md) | Choice per tick | Decisions faster than human perception |
| 9 | [Browser and computer use](09-browser-and-computer-use.md) | Choice + Noul | A screen must become an action |
| 10 | [Domain applications](10-domain-applications.md) | All | Legal, finance, insurance, health, recruiting, commerce, moderation |
| 11 | [Frontier and fun](11-frontier-and-fun.md) | All | The demos that show what the primitive can do |

---

## The two shapes behind every use case

**Classification shape** - you have a known set of labels and something must be sorted into one of them.

```
state + Choice(options, criteria) -> {choice, probabilities, confidence}
```

Routing, triage, classification, moderation, intent, entity type, department. The question is *which one*, and the answer selects a code path.

**Detection shape** - you have a property that may or may not be present.

```
state + Noul(statement) -> {noul: 0..1}
```

Spam, fraud, urgency, jailbreak, sensitive data, citation support, task completion. The question is *is it there*, and the answer is a probability you threshold.

Almost everything else is a composition of these two plus `Score` for degree. The categories below are organized by *domain and workflow*, not by primitive, because that is how the design decisions actually differ.

---

## Cross-cutting reading order

If you are picking a starting point, read in this order:

1. **[Routing and triage](01-routing-and-triage.md)** - the canonical first use case, and the one with the most complete worked example.
2. **[LLM guardrails and verification](02-llm-guardrails-and-verification.md)** - the highest-leverage use case if you already run agents or LLM features.
3. **[Agent harness engineering](03-agent-harness-engineering.md)** - where the community concentrated its effort in the first 72 hours.

If you are evaluating whether to adopt Jev at all, read [../docs/model-selection.md](../docs/model-selection.md) and [../docs/evaluating-jev.md](../docs/evaluating-jev.md) first.
