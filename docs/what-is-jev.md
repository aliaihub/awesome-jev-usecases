# What is Jev?

Jev is TypeSafe AI's flagship model and the first **System One model**: a frontier model trained to produce fast, structured, calibrated decisions that software can consume directly, rather than text for a human to read.

- Announcement: [Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) (15 September 2026)
- Documentation: [docs.typesafe.ai](https://docs.typesafe.ai/introduction)
- Model page: [docs.typesafe.ai/models](https://docs.typesafe.ai/models)

## The core idea

An LLM answers a question by generating tokens one at a time. When your code needs a judgment - *which queue does this ticket go to?*, *is this invoice suspicious?*, *does this citation support this claim?* - you have to coax that answer out of a text generator and then parse it back into something your program can branch on. That coercion is the mismatch Jev removes.

Jev takes unstructured **state** plus typed **questions** and returns typed **answers with probability distributions**. Nothing is generated, so nothing has to be parsed. The vendor's framing is a "frontier-intelligence function call": unstructured state in, typed probabilistic decisions out.

## The three primitives

Everything Jev does is one of three question types. They can be mixed freely in a single call, and every question is evaluated in parallel and in isolation over the same state.

| Primitive | Question shape | You declare | You get back |
| --- | --- | --- | --- |
| `Choice` | One option should win | Options (up to 255) + criteria | `choice`, `probabilities`, `confidence` |
| `Score` | The answer sits on an ordered scale | 2–10 described levels | `score`, `probabilities`, `confidence` |
| `Noul` | Is this statement true? | A statement about the state | `noul` (0–1) |

`Noul` is TypeSafe's coinage for the yes/no primitive. It has no separate confidence field because the probability *is* the belief.

Confidence is not a second model output. It is a statistic computed from the probability distribution the answer already returns - high when the distribution is concentrated, low when it is spread out. You also get the raw probabilities and can define your own uncertainty measure from them.

Source: [docs.typesafe.ai/primitives](https://docs.typesafe.ai/primitives), [docs.typesafe.ai/confidence](https://docs.typesafe.ai/confidence)

## What makes it different

| | Frontier LLM | Jev |
| --- | --- | --- |
| Output | Generated strings, must be parsed | Typed values, schema-guaranteed |
| Sampling | Sequential, one token at a time | Parallel, single pass |
| Latency | 3–329 s | 70–500 ms |
| Input price | ~$0.20–$10 per MTok | $0.042 per MTok |
| Output price | ~5x input | Free |
| Confidence | Overconfident, inconsistent | Calibrated per output *(vendor claim)* |
| Structured-output errors | 0.58%–45.5% *(vendor test)* | 0% by construction |
| Text generation | Yes | No |
| Counting, arithmetic, date math | Unreliable but possible | Unreliable and not intended |

The last two rows matter as much as the first ones. Jev cannot write you a paragraph, and it cannot count or do arithmetic. Both are features, not bugs - see [failure-modes.md](failure-modes.md).

## The trade, stated honestly

**What is solid:**
- The latency and price are directly measurable and have been measured by a third party. Every's Mike Taylor ran 777 judgments across 37 documents in under 0.7 seconds, and 1,709 judgments for under a cent, during early access ([every.to](https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds)).
- The type guarantee is real. Output cannot fall outside the schema you declared. TypeSafe says the 0% error figure is not empirical because schema matching is guaranteed by construction.
- The parallel evaluation is real. Independent developers reproduced the interface on open models within hours ([TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev)).

**What to hold loosely:**
- **The multipliers are picked, not typical.** "193.6x faster, 444.6x cheaper" comes from TypeSafe's own eval against the single slowest and priciest baseline. Against Terra - the model TypeSafe names as its intelligence peer - the same arithmetic gives roughly 25x faster and 76x cheaper, which is still remarkable but a long way from the poster ([pearpages.com](https://pearpages.com/blog/2026/09/16/jev-sorted-what-typesafes-system-one-model-actually-is-and-what-is-still-just-a-claim)).
- **"Accuracy" means agreement with two other models.** There is no human ground truth in the eval. The reference labels are the average of GPT-6 Astra and Claude Fable 5.1 at high thinking. Jev's 67.8% means it agrees with that consensus about two thirds of the time, and so does Terra.
- **The average hides a gap on the hardest task.** On invoice processing Jev scored 61.8% against Terra's 74.7% and Opus 5's 78.4%. Its best workflow was customer service at 76.0%.
- **"Can't hallucinate" is a statement about types, not truth.** Jev cannot return a category you did not declare. It can still select the wrong one, confidently. As Sean Goedecke put it, the model constrains the shape of the output, not the judgment ([seangoedecke.com](https://www.seangoedecke.com/jev-means-structured-output-is-interesting-again/)).
- **"Calibrated" is asserted, not demonstrated.** Calibration has a precise meaning: among answers given at probability 0.8, about 80% should be true. No calibration curves, Brier scores, or reliability diagrams have been published, and the first independent benchmark found Jev well calibrated on two of three datasets and substantially worse on the third ([AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)).
- **The pricing may be subsidized.** TypeSafe says so themselves and expects prices to fall rather than rise.

None of this makes Jev a bad tool. It makes the first paragraph of your own evaluation notebook the most important part of your integration.

## Where it fits architecturally

TypeSafe describes three software architectures:

1. **Traditional software** - a decision tree of reliable primitives.
2. **LLM agents** - a model chooses its own next step; works well with a human watching, and every loop is another chance to go off the rails.
3. **AI-powered software** - code owns the workflow and the model appears only where the system needs programmable common sense or has to interpret unstructured data. Each AI task stays atomic and constrained.

Jev is built for architecture 3. If you are writing an agent loop and hoping the model behaves, you are solving a different problem.

Source: [docs.typesafe.ai/concepts/how-to-build-with-system-one](https://docs.typesafe.ai/concepts/how-to-build-with-system-one)

## When *not* to use Jev

- **Generating anything.** Text, code, summaries, emails, rationales. Jev is not trained for it and forcing it through chained choices is slow and bad.
- **Arithmetic, counting, or date comparison.** Keep it in code. This is their own documentation's advice.
- **Decisions that need a written rationale for an auditor.** Jev gives you a number, not an explanation. Route the flagged cases to a model that can write.
- **One-off complex reasoning.** Use a reasoning model.
- **Genuinely open answer spaces.** If you cannot enumerate the options, you cannot ask the question. Extract candidates first, then let Jev pick.

## Next

- [getting-started.md](getting-started.md) - make a call
- [how-to-use-jev-effectively.md](how-to-use-jev-effectively.md) - the design method
- [model-selection.md](model-selection.md) - Jev vs LLM vs a fine-tuned classifier
