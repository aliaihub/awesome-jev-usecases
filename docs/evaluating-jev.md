# Evaluating Jev

The calibration claim is the load-bearing claim of the entire product. Without it, the confidence number is decoration and every threshold in your code is a guess. It is also the claim with the least independent evidence.

This page is how to verify it on your own traffic.

---

## Why you must evaluate it yourself

- **No independent reproduction of the full benchmark exists.** TypeSafe designed the workflows, built the harness, and ran the eval.
- **"Accuracy" in the vendor eval means agreement with two frontier models**, not correctness against human labels. That proxy quietly rewards agreeing with frontier-model mistakes.
- **No calibration curves have been published.** Calibration has a precise meaning - among answers given at probability 0.8, about 80% should be true - and it is not demonstrated in the documentation.
- **The first independent benchmark found a mixed result.** [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) compared Jev to GLiNER2.5 on zero-shot single-label classification across three datasets of 100 held-out examples each:

| Dataset | Labels | Jev accuracy | GLiNER accuracy | Jev coverage at ≤5% error |
| --- | ---: | ---: | ---: | ---: |
| AG News | 4 | **0.910** | 0.700 | **0.830** |
| Banking77/BTZSC | 72 | **0.870** | 0.610 | **0.860** |
| DAIR Emotion | 6 | 0.480 | 0.440 | 0.000 |

Jev had a clear accuracy and Brier-score advantage on AG News and Banking77. On DAIR Emotion the accuracy difference was unresolved and **Jev was substantially worse calibrated**: Brier 0.846 vs 0.668, and zero probability on the true label for 16% of examples.

That is the right shape of result. Jev is not uniformly calibrated, and the failure is on the domain where the categories are subjective and emotion-like. Your domain may resemble any of those three.

- **The one independent measurement in the launch window was positive but small.** Every's Mike Taylor made 777 judgments across 37 documents in under 0.7 seconds and 1,709 judgments for under a cent, and on a 7-defect test Jev caught 6 where Fable 5.1 caught 7. One person's afternoon is not a benchmark, but it matches the vendor's latency and price and shows the expected accuracy gap ([every.to](https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds)).

---

## The three things to measure

### 1. Accuracy on a label set you trust

Collect a few hundred examples your team has already decided. Run Jev on them. Compare to your labels.

For a `Choice`, accuracy is the share where `.choice` matches. For a `Noul`, you need to pick a threshold first (0.5 is the default assumption; test others). For a `Score`, bucket the scores and treat it as a classification of levels.

The number that matters is not the headline accuracy. It is the accuracy **at the confidence threshold you intend to ship**.

### 2. Selective risk - the curve that actually decides your architecture

This is the measurement to prioritize. It answers the real production question:

> At what confidence threshold do I get 90% accuracy, and what fraction of traffic can I automate at that bar?

Plot confidence on the x-axis and accuracy on the y-axis. A well-calibrated model produces a monotonic curve: higher confidence, higher accuracy. Then read off the operating point.

```
accuracy
  1.0 |                              ●●●
      |                        ●●●
  0.9 |                  ●●●
      |            ●●●
  0.8 |      ●●●
      |  ●●●
  0.7 |
      +--------------------------------------  confidence
        0.5   0.6   0.7   0.8   0.9   1.0
```

If the curve is flat, confidence carries no information and your thresholds are noise. If the curve is monotonic and steep, Jev is doing what you paid for.

**Report the pair.** "90% accuracy at 0.82 confidence, which covers 61% of traffic" is an architectural decision. "87% accuracy" is not.

### 3. Calibration specifically

Calibration is distinct from accuracy. A model can be accurate and badly calibrated, and the DAIR Emotion result shows Jev can be.

Use **Brier score** for `Noul` questions and probability outputs:

```python
# For a Noul question where outcome is 1 (true) or 0 (false)
brier = sum((p - outcome) ** 2 for p, outcome in zip(predictions, outcomes)) / len(outcomes)
```

Lower is better. 0.25 is the score of always predicting 0.5. Compare against the base rate: predicting the constant base rate is the honest baseline.

For `Choice`, compute the Brier score across the full probability distribution, not just the selected label. This is what penalizes confident-but-wrong answers.

**Also check the reliability diagram.** Bucket predictions by probability (0.5–0.6, 0.6–0.7, …) and plot the observed true rate in each bucket against the predicted rate. A perfectly calibrated model lies on the diagonal.

```python
buckets = {}
for p, outcome in zip(predictions, outcomes):
    b = round(p, 1)
    buckets.setdefault(b, []).append(outcome)

for b in sorted(buckets):
    observed = sum(buckets[b]) / len(buckets[b])
    print(f"predicted {b:.1f} -> observed {observed:.2f} (n={len(buckets[b])})")
```

If predicted 0.9 buckets observe at 0.6, your threshold is lying to you.

---

## Practical methodology

### Start from existing decisions, not new ones

Go to your backlog. Find decisions your team already made and recorded the outcome for. Tickets that were routed, claims that were approved or denied, moderation actions taken. This is free labelled data and it reflects your actual distribution.

Do not build a synthetic evaluation set first. Synthetic sets measure your imagination, not your traffic.

### Test the threshold, not just the model

Your integration has a threshold. Evaluate the *pipeline* at that threshold. The question is not "how good is Jev" but "how good is my system".

### Test shift deliberately

A model calibrated on TypeSafe's four workflows may be badly calibrated on your tickets. Include:

- Your **rare but important** cases, not just the common ones
- Inputs from the **edges** of your distribution
- **Adversarial** inputs, especially for guardrail and screening use cases

### Version-pin during evaluation

`jev-latest` moves. Pin the versioned ID so your evaluation is reproducible, and log the `model` field from every response.

```python
client = TypeSafeClient(model="jev-1.13.0")
```

### Instrument production

Run the eval on your own data before launch, then keep measuring. Sample live decisions, route a slice to human review, and compare. This is how you catch drift when the model version changes under you.

---

## A minimal evaluation harness

```python
import json
from pathlib import Path
from typesafe_sdk import Choice, TypeSafeClient

def evaluate(examples, question_builder, label_key, model="jev-1.13.0"):
    """examples: list of {"state": ..., "label": ...}"""
    client = TypeSafeClient(model=model)
    records = []

    for ex in examples:
        response = client.system_one(state=ex["state"], questions=question_builder())
        answer = response.answers["label"]
        records.append({
            "predicted": answer.choice,
            "confidence": answer.confidence,
            "probabilities": answer.probabilities,
            "actual": ex[label_key],
            "correct": answer.choice == ex[label_key],
            "model": response.model, # log the versioned ID that answered
        })

    return records


def report(records):
    n = len(records)
    acc = sum(r["correct"] for r in records) / n
    print(f"overall accuracy: {acc:.3f} (n={n})")

    # selective risk: accuracy at and above each confidence threshold
    for t in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
        kept = [r for r in records if r["confidence"] >= t]
        if not kept:
            continue
        cov = len(kept) / n
        acc_t = sum(r["correct"] for r in kept) / len(kept)
        print(f" confidence >= {t:.2f}: accuracy {acc_t:.3f} coverage {cov:.2f}")

    # calibration buckets
    buckets = {}
    for r in records:
        buckets.setdefault(round(r["confidence"], 1), []).append(r["correct"])
    print("calibration:")
    for b in sorted(buckets):
        obs = sum(buckets[b]) / len(buckets[b])
        print(f" predicted {b:.1f} -> observed {obs:.2f} (n={len(buckets[b])})")

    # Brier score on the selected label's probability
    brier = sum(
        (r["probabilities"][r["predicted"]] - int(r["correct"])) ** 2 for r in records
    ) / n
    print(f"brier score: {brier:.4f} (0.25 = always predict 0.5)")
```

**How to read the output:**

- If the selective-risk rows show accuracy **rising** with confidence, Jev's confidence is informative and your thresholds can work.
- If they are flat, do not ship a confidence gate. Either the task is below Jev's capability or your criteria are not distinguishing the options.
- If calibration buckets are far off the diagonal, recalibrate in code (fit a simple mapping from Jev's confidence to your observed rate) or lower your thresholds and accept a human-review slice.

---

## The comparison baseline everyone forgets

TypeSafe's own eval has an unintentional finding that is worth acting on regardless of whether you adopt Jev:

**Every LLM in the table scored higher, cost less, and ran faster in decomposed workflow mode than when given the same policy as a single prompt.** Claude Haiku 4.5 went from 18.1% as a prompt to 53.6% as a decision graph.

That means the highest-value experiment you can run is not "Jev vs GPT". It is **your current prompt as a single call vs the same policy decomposed into small typed questions**. Decomposition is a technique you can apply today with whatever model you already pay for. TypeSafe's own data says it is worth doing whether or not Jev exists.

---

## What to watch for as the ecosystem matures

These have not happened yet and would change the picture:

1. **A calibration curve from someone other than TypeSafe**, on human-labelled data, ideally far from the four launch workflows. This is the single most valuable result.
2. **An eval with human ground truth.** Agreement with two frontier models is a proxy that rewards agreement with their mistakes.
3. **A paper or technical report on RLCD**, so "calibrated" in the method name stops being a promise about intent.
4. **General availability with published limits**, so latency and price can be measured under real load.
5. **A single-token logprobs baseline in TypeSafe's own table.** The current comparison forces LLMs to generate full structured answers, which is the slowest fair comparison. The cheapest fair one is missing.

---

## Next

- [failure-modes.md](failure-modes.md) - what breaks when you skip this
- [patterns.md](patterns.md) - where thresholds live in the architecture
