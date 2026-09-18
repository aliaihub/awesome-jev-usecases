# Feature extraction for machine learning

**Decision shape:** `Score` and `Noul` producing numeric features for a downstream classical model.

**Reach for it when:** you have a predictive task with real outcomes, and the signal lives in text that your current model cannot see.

This is one of TypeSafe's documented primary use cases and the one with the clearest research story. It is also the use case where Jev is least like a classifier and most like a feature engineering tool.

---

## The idea

A classical model predicts an outcome from features. If some of those features live in natural language - customer inquiries, sales notes, product reviews, support tickets, market reports - you have to turn text into numbers somehow.

Embeddings give you vectors but not interpretable features. A frontier LLM gives you good features but at a cost that makes training-data generation impractical.

Jev gives you **probabilistic, interpretable, named features** at a cost that makes generating a feature column for every row routine.

```
text -> Jev (Score/Noul per concept) -> numeric columns -> CatBoost / logistic regression
```

The features are named, so the downstream model is explainable in a way an embedding model is not.

---

## The concrete example

From the [use-case map](https://docs.typesafe.ai/concepts/use-case-map), for demand forecasting:

```python
questions={
    "purchase_intent": Score(
        instructions="How strong is the purchase intent in `inquiry.text`?",
        criteria=["No intent; browsing or complaining",
                  "Interested but not committed",
                  "Actively evaluating options",
                  "Ready to buy; asking about price or terms"],
    ),
    "urgency": Noul(
        "Does `inquiry.text` indicate a time-sensitive need?"
    ),
    "competitive_pressure": Noul(
        "Does `inquiry.text` mention a competing product or vendor?"
    ),
    "price_sensitivity": Score(
        instructions="How price-sensitive does the customer appear?",
        criteria=["Not price-focused", "Some price concern", "Primarily price-driven"],
    ),
    "supply_concern": Noul(
        "Does `inquiry.text` mention availability, lead time, or stock?"
    ),
}
```

Then each answer becomes a column:

```python
features = {
    "purchase_intent": a["purchase_intent"].score, # 0..3, can be fractional
    "purchase_intent_conf": a["purchase_intent"].confidence,
    "urgency": a["urgency"].noul, # 0..1
    "competitive_pressure": a["competitive_pressure"].noul,
    "price_sensitivity": a["price_sensitivity"].score,
    "supply_concern": a["supply_concern"].noul,
}
# feed into your forecasting model alongside historical time-series
```

**The `score` values are usable as continuous features** - and this is a genuine advantage over embeddings for tabular models. A gradient-boosted tree splits cleanly on an interpretable, ordered feature.

---

## The AutoResearch loop

TypeSafe published the most interesting recipe in this category: an autoresearch loop that improves the features themselves.

```
1. Propose candidate questions about the text
2. Convert free text into numeric features using those questions
3. Train a supervised model on the features against held-out ground truth
4. Use the model's errors to propose better questions
5. Repeat
```

The loop closes because you have ground truth. A question that produces a feature with no predictive value gets dropped; a question that produces a highly predictive feature gets refined. The model's errors tell you which concept you are failing to capture.

The published version trains a CatBoost regressor on Jev's probabilities.

Source: [autoresearch feature discovery cookbook](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery)

**Why this matters:** it turns Jev from a classifier into a **feature discovery engine**. You are not just labeling data, you are searching for the right questions to ask.

---

## When to use probabilities vs discrete labels

A subtle but important design choice. Jev gives you both, and they serve different purposes.

| Use | Take | Why |
| --- | --- | --- |
| Feature for a downstream model | `.noul` or `.score` (continuous) | Trees and linear models split on continuous values; thresholding throws away information |
| Routing decision | `.choice` (discrete) | You need one branch |
| Confidence gating | `.confidence` | Gate the action, not the feature |
| Training labels for a second model | `.probabilities` (full distribution) | Soft labels are richer than hard ones |

**Do not threshold before feeding a model.** If you are building features, pass the raw probability. The threshold is a decision, and decisions belong at the end of the pipeline, not the middle.

---

## The composite scoring variant

If you do not have a downstream model and just need a single score, combine the atomic scores with weights you control.

```python
composite = (
    0.40 * (a["python_depth"].score / 4)
    + 0.25 * (a["team_leadership"].score / 4)
    + 0.35 * (a["system_design"].score / 4)
)
```

Re-weighting is a code change, not a re-prompt. You can A/B it, version it, and explain it.

**The limitation:** do not interpolate between score levels to recover an exact number. The docs are explicit that `jev-1.13`'s score levels are weak in numerical calibration - you can use the expectation to check a threshold, but you cannot reconstruct an exact magnitude by interpolating between the nearest two levels.

---

## The autoresearch reproducibility angle

Two community projects push on this:

- [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) measures "whether the reported probabilities are calibrated enough to support automation, how much work can be accepted at a fixed error budget, what resources each decision uses, and how long it takes end to end" - with paired target-stratified bootstrap intervals.
- [OmniJev/awesome-jev](https://github.com/OmniJev/awesome-jev) collects papers, open reproductions, and independent evaluations behind System One models.

If you are building features that a business decision depends on, the calibration question is not academic. A feature with good *ranking* but bad *calibration* is fine for a tree and dangerous for a threshold.

---

## The open reproduction angle

Several projects reproduce the feature-extraction idea on open models:

- [TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev) reads typed option probabilities off a 4B model's logits in one forward pass.
- [kshetrajna12/reflex](https://github.com/kshetrajna12/reflex) is a small open decision model producing calibrated probabilities from state plus typed questions.
- [akash-kamat/system-one-gemma](https://github.com/akash-kamat/system-one-gemma) adds a scoring head to Gemma 3 270M for fast calibrated decisions in a single forward pass.
- [r-ms/mini-jev](https://github.com/r-ms/mini-jev) reads the option letter's logits instead of generating.

These reproduce the interface, not the training. For feature extraction especially, **calibration is the whole product**, and it is the part that is hard to reproduce. If you go the open-model route, budget extra evaluation time.

---

## Design notes specific to feature extraction

### Extract features, not labels

Resist the urge to make Jev output the final decision. Produce features and let the model or the business rules combine them. This is what makes the approach explainable and tunable.

### Name your features after the concept, not the question

`purchase_intent` is a feature. `is_the_text_about_buying` is a question. Name the output column after the concept so the downstream model is readable.

### Include the confidence as a feature

`purchase_intent_conf` is itself informative. Rows where the model is unsure behave differently, and a downstream model can learn that.

### Keep questions independent

Do not ask "how strong is the purchase intent and is it urgent". Ask two questions. The whole value of this approach over a frontier LLM is that you get separable, inspectable signals.

### Batch aggressively, cache aggressively

Feature extraction runs over your whole training set, which means millions of rows. Use [batching](06-classification-at-scale.md#the-batching-pattern) and cache by content. This is the use case where the cost advantage compounds the most.

### Keep the arithmetic out

If a feature requires a sum, a ratio, or a difference between two Jev outputs, compute it in code. Jev produces the components; your feature engineering produces the combinations.

---

## Pitfalls

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| Thresholding before the model | Discards information the model could use | Pass raw probabilities and scores |
| Asking one compound question | Inseparable signals, poor features | One question per concept |
| Interpolating between score levels | Fabricated precision | Use the score as a bucket, compute in code |
| Assuming calibration on an open reproduction | Thresholds misbehave | Evaluate calibration explicitly |
| Using Jev features without ground truth | Cannot tell if a feature helps | The loop needs outcomes to close |
| Doing arithmetic with Jev outputs | Unreliable numbers | Compute combinations in code |

---

## Related

- [06-classification-at-scale.md](06-classification-at-scale.md) - batching and cost planning
- [../docs/patterns.md](../docs/patterns.md#composite-scoring--classical-model) - the pattern summary
- [../docs/evaluating-jev.md](../docs/evaluating-jev.md) - measuring calibration before thresholds depend on it
