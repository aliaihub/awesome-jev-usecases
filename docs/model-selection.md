# Jev vs LLM vs classifier: when to use which

Jev is not competing with your chat model for the same jobs. It competes with the three ways teams already get typed decisions out of software. This page is the honest comparison.

---

## The full landscape

| Approach | Needs your labelled data | Latency | Cost per decision | Probabilities | Retrain to change |
| --- | --- | --- | --- | --- | --- |
| **Rules / regex / parser** | No | Microseconds | ~Zero | No | No |
| **Fine-tuned classifier** (BERT-style) | Thousands of examples | Milliseconds | Near zero | Native; calibration is your job | Yes |
| **LLM, single constrained token + logprobs** | No | Hundreds of ms - seconds | Prompt-sized | Token logprobs, crude | No |
| **LLM, structured output (JSON schema)** | No | Seconds - minutes | Prompt + output | Self-reported, unreliable | No |
| **Jev** | No | 70–500 ms | Input only, $0.042/MTok | Native; calibration asserted but unverified | No |

The row that deserves more attention than it gets is **LLM with a single constrained token**. If you prefill an LLM's response so the only thing left to generate is one token from a fixed set, you get one forward pass, a probability per option from the logprobs, and no parsing. Sean Goedecke reports a 2–3x speedup over ordinary structured output on a small open model doing exactly this ([seangoedecke.com](https://www.seangoedecke.com/jev-means-structured-output-is-interesting-again/)). It does not reach Jev's latency, because a general LLM still processes the whole prompt through a much larger network - but it is available this afternoon, on the model you already have, with no waitlist.

That is also why the community reproduced Jev's *interface* on open models within hours:

- [TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev) (839★) reads typed option probabilities directly off a 4B model's logits in one forward pass.
- [r-ms/mini-jev](https://github.com/r-ms/mini-jev) reads the option letter's logits instead of generating.
- [kshetrajna12/reflex](https://github.com/kshetrajna12/reflex) is a small open decision model on Qwen3.5.

These reproduce the interface pattern, not Jev's model or training. The interface is the easy part. The calibration is the part nobody has reproduced.

---

## When to reach for each

### Reach for **code** when
The answer is computable exactly. Comparisons, arithmetic, counting, regex matches, date ordering, schema validation. This is not a cop-out - it is step 1 of the design method. Jev's own documentation says to avoid asking the model anything code can compute.

### Reach for **Jev** when
- The decision is **repeated** and **high-volume**
- The possible answers are **known in advance**
- It is a **judgment** rather than a computation - classify, route, score, detect, rank, verify
- You need it **fast** (sub-second, inside a request handler or a control loop)
- You need a **probability you can threshold on**
- You need a **type guarantee** because a malformed value several layers deep is a deal-breaker

### Reach for a **frontier LLM** when
- You need **generated text**: code, emails, summaries, explanations
- You need a **written rationale** for a human or an auditor
- It is **one-off complex reasoning** with no repetition
- The answer space is **genuinely open**
- **Peak accuracy** matters more than cost on a low-volume task

### Reach for a **fine-tuned classifier** when
- You have **thousands of labelled examples**
- Latency requirements are extreme (milliseconds, on-device)
- The task is stable and not going to change
- You want zero per-call cost at very high volume

### Keep a **human** in the loop when
- Being wrong is expensive and confidence is below your threshold
- The decision has legal or regulatory weight requiring a rationale

---

## The composition is the answer

In practice the right architecture uses all of them:

```
incoming request
      │
      ▼
  [rules / regex]  ─── handles what code can compute exactly
      │
      ▼
  [Jev]  ─── classifies intent, scores complexity, gates confidence
      │
      ├── pure-code branch   -> no model at all
      ├── specialist LLM     -> handles the generated-text work
      ├── reasoning model    -> handles the hard minority
      └── human              -> handles the uncertain minority
```

Jev classifies and routes cheaply. Code handles what it can. A frontier model takes the hard minority. This is [Pattern 4, the cascade](patterns.md#pattern-4---the-cascade).

**The evidence is strongest when it is hybrid.** Hassan El Mghari's paper classifier used DeepSeek V4 Flash for summaries at $3.99 and Jev for classification at $0.08 - 1,018 papers, median 256 ms each. The generative model wrote; the decision model decided.

---

## The honest scorecard

On TypeSafe's four-workflow evaluation, all numbers vendor-run:

| Model | Agreement | Cost per case | Seconds per case |
| --- | --- | --- | --- |
| **Jev** | 67.8% | **$0.0004** | **0.4** |
| GPT-5.6 Terra | 67.9% | $0.0304 | 10.1 |
| GPT-5.6 Sol | 74.1% | $0.0836 | 23.3 |
| Claude Opus 5 | 73.1% | $0.1761 | 37.8 |
| Claude Sonnet 5 | 67.8% | $0.1174 | 78.1 |
| Claude Haiku 4.5 | 53.6% | $0.0195 | 12.5 |

Four things to hold onto:

1. **"Agreement" is not accuracy.** There is no human ground truth. Reference labels are the average of GPT-6 Astra and Claude Fable 5.1 at high thinking. It measures agreement with two frontier models, which is why neither appears in the results.
2. **It is self-run.** TypeSafe designed the workflows, built the harness, and ran it. No independent reproduction of the full suite exists. Evaluate on your own traffic.
3. **The mean hides a real gap.** On invoice processing Jev scored 61.8% against Terra's 74.7% and Opus 5's 78.4%. "Terra-level" is true of the mean across four chosen tasks and false on the one that looks most like extracting structured facts from a messy document.
4. **The headline multipliers are picked.** "193.6x / 444.6x" is Jev against the slowest and priciest baseline in that table. Against Terra - TypeSafe's named intelligence peer - it is about 25x faster and 76x cheaper.

**Where Jev actually loses:** peak accuracy on hard extraction. If you need 74–78% and can pay 200x more for 10–30x the latency, the LLM still wins on that task.

**Where Jev actually wins:** any decision you need to run more times than you could previously afford, and any decision that has to complete inside a request handler or a control loop.

**Price the fallback, not just the call.** [YTAL](https://ytal.io/blog/typesafe-jev-entity-resolution-production-replay/) replayed production entity-resolution logs through Jev (525 new nodes, candidate Choice, 0.85 confidence threshold). The model stage cost about $0.032 against $0.787 for the existing process, roughly 96% cheaper. Sending uncertain cases back to that process pushed the projected total to $0.819, a **4.1% increase**, so they did not adopt it. They attribute this to their own aggregation rules rather than the model: the same responses gave a 13.0% holdout rate per pair and 39.6% per node. Self-reported by the company, on private data.

---

## A note on "frontier model"

The launch title originally read *"Jev: New frontier model 40-400x cheaper and 20-200x faster"* and was changed within the hour after pushback. The objection was not that Jev is bad, but that "frontier model" implies general capability comparable to GPT-6 Astra, and a schema-constrained decision model with no test-time compute is a different thing.

Both framings are defensible. Jev is frontier in the sense that it explores an unexplored domain and owns the speed/cost Pareto frontier for structured decisions. It is not a general-purpose reasoning model and does not claim to be - the launch post says plainly that it gives up string generation.

Read the claim for what it is: **the fastest, cheapest way to get a calibrated typed judgment from a frontier-trained model.** That is a genuinely new primitive. It is not a smaller GPT.

---

## Next

- [evaluating-jev.md](evaluating-jev.md) - how to verify the accuracy and calibration claims on your own data
- [what-is-jev.md](what-is-jev.md) - the model, the claim, and the trade
