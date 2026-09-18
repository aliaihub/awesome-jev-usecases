# Classification at scale

**Decision shape:** `Choice` over the label set, batched many rows per request.

**Reach for it when:** you have millions of rows, bounded labels, and the cost of a frontier call per row is the reason you have not done it yet.

This is the use case where Jev's price advantage is most decisive, because it is the one where the alternative is often *doing nothing at all*.

---

## The economics that unlock it

At $0.042 per million input tokens with free output, Jev costs roughly **$0.0004 per decision case** on TypeSafe's benchmark. That number is what changes the category - it moves classification from "expensive" to "routinely affordable as a build step".

A concrete example from the launch coverage: scoring every product review in a 50-million-row table for sentiment and policy violation would cost roughly **$20** with Jev at the reported rate, versus thousands with a token-billed LLM.

That is not an optimization. It is a different class of product.

---

## The measured hybrid result

The single best evidence in this category is Hassan El Mghari's paper classifier, which ran a generative model and a decision model in the same pipeline and showed the bill for each:

1. Summarize 1,018 papers with DeepSeek V4 Flash
2. Send title + summary + 24 candidate topics to Jev
3. Classify with one `Choice`
4. Visualize

| Stage | Cost |
| --- | --- |
| Summaries (DeepSeek V4 Flash) | **$3.99** |
| Classifications (Jev) | **$0.08** |
| Median end-to-end latency | **256 ms** per paper |

The author's conclusion:

> I think this is where things are heading: different models for different parts of the workflow, instead of using one model for everything.

He also notes he was running evals on the Jev classifications before replacing the existing ones - which is the right instinct, and the one most launch-week demos skip. See [../docs/evaluating-jev.md](../docs/evaluating-jev.md).

Source: [1kpapers.com](https://1kpapers.com) by Hassan El Mghari, [thread](https://x.com/nutlope/status/2100426999546184123)

---

## The batching pattern

Do not make one request per row. Pack rows into a shared state and ask one question per row.

```python
def classify_batch(rows, labels, label_criteria, batch_size=50):
    """rows: list of dicts. labels: list of label names."""
    results = []

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]

        response = client.system_one(
            state={
                "labels": label_criteria, # sent once, shared by every question
                "rows": batch,
            },
            questions={
                f"row_{j}": Choice(
                    instructions=f"Which label applies to `rows[{j}]`?",
                    criteria=label_criteria,
                )
                for j in range(len(batch))
            },
        )

        for j, row in enumerate(batch):
            answer = response.answers[f"row_{j}"]
            results.append({
                **row,
                "label": answer.choice,
                "confidence": answer.confidence,
                "probabilities": answer.probabilities,
            })

    return results
```

**Why this is efficient:** the label criteria are sent once and shared. One request covers the whole batch, and every question evaluates in parallel. The 21-question benchmark in TypeSafe's docs makes the scale of the saving concrete: 1,709 judgments for under a cent across Every's experiments.

**Tune `batch_size` against the context limit.** 64k tokens for state plus all questions; 32k for state plus the single longest question. Larger batches amortize the shared criteria but risk context rot - accuracy falls as state grows with content unrelated to the decision. Test on your data.

Source: [realZachi/pg-jev](https://github.com/realZachi/pg-jev) uses this exact pattern, packing `jev.batch_size` rows per request with a shared `{"condition": ..., "rows": [...]}` state and one `Noul` per row.

---

## The independent benchmark result

[AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) is the first independent evaluation of Jev's classification at scale, comparing it to GLiNER2.5 on zero-shot single-label classification. Three hundred held-out examples, 100 per condition:

| Dataset | Labels | Jev accuracy | GLiNER2.5 | Jev coverage at ≤5% error |
| --- | ---: | ---: | ---: | ---: |
| AG News | 4 | **0.910** | 0.700 | **0.830** |
| Banking77/BTZSC | 72 | **0.870** | 0.610 | **0.860** |
| DAIR Emotion | 6 | 0.480 | 0.440 | 0.000 |

**Read this carefully, because it is the most honest data in the ecosystem.**

- On **news topics** and **banking intents**, Jev had a clear accuracy and calibration advantage. At a 5% error budget it could automate 83–86% of traffic.
- On **emotion**, Jev's accuracy was statistically indistinguishable from GLiNER and its calibration collapsed: Brier 0.846 vs 0.668, with zero probability on the true label for 16% of examples.

The lesson is not "Jev is good" or "Jev is bad". It is that **Jev is well calibrated on concrete, well-defined taxonomies and poorly calibrated on subjective ones.** Emotion labels are fuzzy by nature. Your label set probably sits somewhere on that spectrum, and you need to know where.

**Latency is deployment-specific.** GLiNER2.5 ran locally on an Apple M4 Max CPU; Jev was called as a hosted service from France. GLiNER was faster on the 4- and 6-label tasks (~44 ms p50 vs 236–256 ms); Jev was slightly faster on the 72-label condition (246 ms vs 296 ms p50).

---

## Large taxonomies

When the label set is large and hierarchical, do not use one flat `Choice`. Use parallel beam search over the hierarchy.

```
root
├── Finance
│   ├── Payments
│   ├── Invoicing
│   └── Payroll
├── Technology
│   └── ...
```

At each level, ask a `Choice` over the children of the candidate nodes. Keep the beam, descend, repeat. This keeps each decision small and literal - which is exactly where Jev performs best - rather than asking it to pick from 200 options at once.

Source: [hierarchical classification cookbook](https://docs.typesafe.ai/cookbooks/hierarchical_classification)

**Note on cardinality:** a single `Choice` supports up to 255 options, and each option costs a few tokens. So a flat 200-way choice is technically possible. The hierarchical version is usually better not because of a hard limit but because a large flat option set makes each option's criteria thin, and thin criteria are where the model goes wrong.

---

## Classification using confidence to climb a hierarchy

A related recipe: classify into a fine-grained group with one `Choice`, then read the answer's own confidence to decide whether to report that group or the broader division above it.

```python
answer = a["industry_group"]

if answer.confidence >= 0.8:
    report(answer.choice) # confident: report the specific group
else:
    report(parent_of(answer.choice)) # uncertain: report the broader division
```

This is a clean example of confidence as a *second axis* rather than a filter. Source: [classification using confidence cookbook](https://docs.typesafe.ai/cookbooks/classification_using_confidence)

---

## What the community built

### Classification as a library

[EdytaKucharska/ticket-quest](https://github.com/EdytaKucharska/ticket-quest) compares Jev decisions against prompted-LLM decisions on the same ticket triage task, ranked by Cost of Delay.

[Charlyhno-eng/jev-document-classification](https://github.com/Charlyhno-eng/jev-document-classification) is a focused document classifier.

### Calibration research

[FirasSX914/calibre](https://github.com/FirasSX914/calibre) measures calibration and confidence-based routing on Banking77, reporting **80.2% accuracy at $0.103 per 500 decisions**. That is a useful independent signal on a public benchmark, and Banking77 is also the dataset where the jev-benchmarks pilot showed Jev doing well.

[MongLong0214/jev-gate](https://github.com/MongLong0214/jev-gate), [iamvatsalpatel/tiershift](https://github.com/iamvatsalpatel/tiershift), and [nidhi-singh02/agent-router](https://github.com/nidhi-singh02/agent-router) apply classification to the meta-problem of routing between models.

### Open reproductions

[TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev) (839★) reproduces the interface on a frozen 4B model, and [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) does Jev-style parallel constrained decisions for any MLX model on Apple Silicon.

**Important framing from that project:** it reproduces the *interface pattern*, not Jev's model or training. If you build on an open reproduction, you get the parallelism and the typed answers but not the calibration.

---

## Design notes specific to classification at scale

### Separate "what exists" from "what is recommended"

This applies most to recommendation-style classification. Mention count rewards whatever is already popular. Rank by signal quality instead. The same discipline applies to label design: a label that describes existence is not the same as a label that recommends an action.

### Always include `other`

At scale, out-of-scope rows are guaranteed. Without an `other` label, every one of them becomes a confident misclassification that pollutes your downstream analytics.

### Batch, but watch context rot

Sharing the label criteria across a batch is what makes this cheap. But accuracy falls as state fills with irrelevant detail, so there is a real ceiling. Tune batch size on your data rather than maximizing it.

### Cache by content

Rows repeat, especially at scale. Cache judgments by row content so re-running with a different threshold or a new label set is free. [realZachi/pg-jev](https://github.com/realZachi/pg-jev) does this per session.

### Store the probabilities, not just the label

If you are going to process millions of rows, keep `.probabilities`. You may want to reinterpret them later with a different threshold, feed them to a downstream model, or analyze which labels confuse each other. Discarding them is the one mistake you cannot undo cheaply.

### Enumerate candidate labels in the state

Do not rely on the model's world knowledge for what a label means. Send the label definitions with the state so they are the same for every batch, and so you can change them without redeploying. This also lets you A/B label definitions, which is a real source of quality gains.

---

## Cost planning

| Rows | Labels | Approx. input tokens per row | Approx. cost |
| ---: | ---: | ---: | ---: |
| 10,000 | 20 | ~150 | ~$0.06 |
| 100,000 | 20 | ~150 | ~$0.63 |
| 1,000,000 | 20 | ~150 | ~$6.30 |
| 50,000,000 | 20 | ~150 | ~$315 |

Estimates assume ~150 input tokens per row including the shared label criteria amortized, at $0.042/MTok. **Verify with your own token counts** - options, criteria length, and state structure all move this materially. There is an unofficial estimator at [StefanoITA/ts-jev-cost-calculator](https://github.com/StefanoITA/ts-jev-cost-calculator).

Note that the launch coverage's "$20 for 50 million reviews" figure implies a much shorter per-row state than 150 tokens. Your own measurement is the only number that matters.

---

## Pitfalls

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| One request per row | Cost and latency explode | Batch with shared label criteria |
| No `other` label | Out-of-scope rows confidently misclassified | Always include it |
| Unbounded batch size | Accuracy drops | Tune against context rot |
| Discarding probabilities | Cannot re-threshold later | Store them |
| Flat choice over 200 labels | Thin criteria, poor accuracy | Hierarchical beam search |
| Assuming calibration transfers | Works on news, fails on emotion | [Benchmark your label set](../docs/evaluating-jev.md) |
| No caching | Redundant cost on re-runs | Cache by row content |

---

## Related

- [05-structured-data-extraction.md](05-structured-data-extraction.md) - extraction as classification over candidates
- [07-feature-extraction-for-ml.md](07-feature-extraction-for-ml.md) - turning classifications into features
- [../docs/evaluating-jev.md](../docs/evaluating-jev.md) - selective risk and calibration on your label set
