# Patterns

Five architectures that recur across the community projects, plus the ones TypeSafe documents. Each pattern is a way to compose Jev's primitives with ordinary code. They combine.

---

## Pattern 1 - Speculative fan-out

**The idea:** questions are evaluated in parallel, so a tenth question costs tokens but almost no time. This inverts the usual instinct to make a cheap call first and a follow-up only if needed. Ask everything up front and let code decide what was relevant.

```python
response = client.system_one(
    state=state,
    questions={
        # always relevant
        "topic": Choice(instructions="Which team should handle this?", criteria={...}),
        # only meaningful if topic == "bug_report". Ask anyway.
        "bug_severity": Score(instructions="How severe is the reported issue?", criteria=[...]),
        "has_repro": Noul(instructions="The user describes steps to reproduce"),
        # only meaningful if topic == "billing". Ask anyway.
        "refund_wanted": Noul(instructions="The user explicitly asks for a refund or credit"),
        "frustration": Score(instructions="How frustrated does the user appear?", criteria=[...]),
    },
)

topic = a["topic"]

if topic.choice == "bug_report":
    if a["bug_severity"].score > 1.5 and a["has_repro"].noul > 0.6:
        escalate_to_engineering(ticket_id, severity="high")
    else:
        add_to_bug_backlog(ticket_id)
elif topic.choice == "billing" and a["refund_wanted"].noul > 0.7:
    start_refund_flow(ticket_id)
```

**Cost evidence:** TypeSafe's parallel-questions cookbook runs a 13-question regulatory briefing over a long article and reports batching every question into one call is **12.2x cheaper and 10.0x faster with identical answers** versus asking one at a time.

**Real example:** [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast) applies this to browser actions. Click, type, and select targets are all asked in the same round trip; only the one matching the chosen operation executes. Two decisions, one network call, and a Zürich to London Google Flights booking in 7.1 seconds for $0.0039.

**Use when:** you have a workflow with branching, and the branch questions are cheap to ask speculatively.

---

## Pattern 2 - Confidence-gated routing

**The idea:** confidence is a second axis. The answer tells you *what*; confidence tells you *whether to act*. Write one threshold per action, scaled to what being wrong costs - not one threshold for the whole system.

```python
action = a["intent"]

if action.confidence < 0.5:
    route_to_human(user_message) # floor: genuinely unsure

elif action.choice == "check_balance":
    show_balance(account_id) # read-only, low bar

elif action.choice == "approve_transfer":
    if action.confidence > 0.85: # moves money, high bar
        approve_transfer(account_id)
    else:
        ask_user_to_confirm("Approve this transfer?")

else:
    route_to_human(user_message)
```

You also get the raw `.probabilities` if TypeSafe's confidence statistic is not the measure you want. A flat distribution means the options were not distinguishable from the state you supplied - which frequently means your criteria are wrong rather than that the model is confused.

**Use when:** almost always. This is the pattern that changes how you architect, not just how you call the model.

**Caveat:** the calibration claim is what makes the threshold meaningful, and it is vendor-asserted. Test it on your data before trusting a threshold in production. See [evaluating-jev.md](evaluating-jev.md).

---

## Pattern 3 - Composite scoring

**The idea:** break a fuzzy judgment into independent dimensions, score each atomically, and combine with weights *you* control. This beats asking "how good is this candidate", which hides several judgments inside one answer.

```python
composite = (
    0.40 * (a["python_depth"].score / 4)
    + 0.25 * (a["team_leadership"].score / 4)
    + 0.35 * (a["system_design"].score / 4)
)
```

Re-weighting is now a code change, not a re-prompt. You can A/B it, version it, and explain it to a reviewer.

**Important limitation:** do not interpolate between score levels to recover an exact number. The docs are explicit that `jev-1.13`'s score levels are weak in numerical calibration. Use the score to check a threshold; do the arithmetic in code.

**Use when:** the decision is a judgment of degree - quality, severity, relevance, risk, seniority, fit.

---

## Pattern 4 - The cascade

**The idea:** Jev is not a replacement for Opus or GPT. It is the thing that decides which requests deserve one.

```python
def handle(message):
    r = client.system_one(state=message, questions={
        "intent": Choice(instructions="Primary intent of this message", criteria={...}),
        "complexity": Score(instructions="How complex is this to resolve?", criteria=[...]),
    })
    intent, complexity = r.answers["intent"], r.answers["complexity"]

    if intent.confidence < 0.5:
        return route_to_human(message)

    if intent.choice == "order_status":
        return lookup_order(message) # pure code, no model at all
    if intent.choice == "product_question":
        return handle_with_llm(message, PRODUCT_SPECIALIST)
    if intent.choice == "return_exchange":
        return handle_with_llm(message, RETURNS_SPECIALIST)
    if intent.choice == "complaint":
        if complexity.score > 1 or complexity.confidence < 0.5:
            return route_to_human(message)
        return handle_with_llm(message, COMPLAINT_RESOLUTION)
```

One branch never touches a model. Two load different specialists. One escalates.

**Cost evidence:** on a million tickets using TypeSafe's per-case figures, that is roughly **$6,480 instead of $30,400**, with about 800,000 answered in under half a second instead of ten.

**The best real example is not about Jev.** [Hassan El Mghari](https://x.com/nutlope/status/2100426999546184123) classified 1,018 research papers in a hybrid pipeline: summaries with DeepSeek V4 Flash cost **$3.99**, classifications with Jev cost **$0.08**, median 256 ms per paper. Different models for different parts of the workflow, instead of one model for everything.

TypeSafe's own eval table quietly makes the same point from the other direction: *every* LLM in it scored higher, cost less, and ran faster in decomposed workflow mode than when given the same policy as a single prompt. Haiku 4.5 went from 18.1% as a prompt to 53.6% as a decision graph.

**Use when:** you are currently sending everything to your most expensive model.

---

## Pattern 5 - Retrieve, then judge

**The idea:** Jev has no knowledge of the world beyond the state you hand it. It cannot look anything up. And accuracy falls as state fills with irrelevant material. Whatever assembles the state decides what Jev is allowed to know. So the full pattern is two layers: **fetch precisely, then judge cheaply.**

```python
# 1. Retrieval: primary sources, filtered before anything reaches the model.
hits = search("GLP-1 receptor agonists cardiovascular outcomes",
              included_sources=["pubmed", "arxiv"], max_num_results=20)

# 2. Judgment: one bounded call per paper, roughly $0.0004 each.
shortlist = []
for paper in hits.results:
    verdict = jev.system_one(
        state={"title": paper.title, "source": paper.url, "content": paper.content},
        questions={
            "is_rct": Noul("This paper reports a randomised controlled trial"),
            "reports_mace": Noul("The paper reports major adverse cardiovascular events as an outcome"),
            "evidence_strength": Score(
                instructions="How strong is the causal evidence presented",
                criteria=["Anecdotal or preclinical", "Observational",
                          "Single randomised trial", "Meta-analysis of randomised trials"],
            ),
        },
    )
    a = verdict.answers
    if a["is_rct"].noul > 0.7 and a["evidence_strength"].score > 1.5:
        shortlist.append((paper, a["evidence_strength"].confidence))
```

Twenty papers screened on four dimensions for well under a cent, against primary literature rather than a general crawl.

**Grounding warning:** pad the state and you lose accuracy to context rot. Ground it in a weak source and Jev returns a *well-calibrated judgment about bad material*, because the state is the only world it has. Retrieval quality sets the ceiling on everything downstream.

**Use when:** RAG, literature review, evidence retrieval, or any pipeline where an expensive context window is the bottleneck. The filter costs less than the context window it saves.

---

## Supporting patterns from TypeSafe's docs

These are documented, smaller, and compose with the five above.

### Intent routing
Classify incoming requests and route each to the optimal handler: deterministic logic, a specialist LLM, or a human. This is pattern 4 formalized.

### Fan-out with relevance filtering
When you cannot filter the state before sending, ask a `Noul` per candidate to filter for relevance rather than trimming arbitrarily. See [classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages).

### Composite scoring → classical model
Instead of weighted sums in code, feed the probabilities as features into a downstream classical ML model (CatBoost, logistic regression). TypeSafe's [AutoResearch cookbook](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery) shows an autoresearch loop that proposes questions, extracts numeric features, and uses model errors to improve a supervised regressor.

### Hierarchical classification
For deep taxonomies, do parallel beam search over `Choice` probabilities rather than one flat 255-way choice. See [hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification).

### Cascade for extraction
A two-stage structured-data-extraction cascade (mini → verify → reasoning) gets most of the quality of a big reasoning model at a fraction of the cost. See [SDE cascade](https://docs.typesafe.ai/cookbooks/sde_cascade).

---

## Pattern selection cheatsheet

| Your situation | Start with |
| --- | --- |
| Branching workflow, several possible next steps | Pattern 4 (cascade) |
| Need to decide but also decide whether to trust it | Pattern 2 (confidence-gated) |
| Judgment of degree or quality | Pattern 3 (composite scoring) |
| Several questions about the same state | Pattern 1 (speculative fan-out) |
| Large corpus, expensive downstream context | Pattern 5 (retrieve then judge) |
| Deep taxonomy with many labels | Hierarchical classification |
| You have labels and want a predictive model | Composite → classical model |

---

## Next

- [failure-modes.md](failure-modes.md) - what breaks these patterns
- [evaluating-jev.md](evaluating-jev.md) - how to know a threshold is safe
