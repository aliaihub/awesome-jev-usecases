# Failure modes

Read this before you ship. Every one of these is documented by TypeSafe on their [jaggedness page](https://docs.typesafe.ai/model-jaggedness/jev-1.13) or learned the hard way by the community in the first 72 hours. The jaggedness page is unusually honest for a launch, and it will save you a week.

The honest framing: `jev-1.13` is fast, calibrated, good at common-sense judgment - and it is not perfect. It does best on System One tasks. It struggles with indirection, is quite literal, and cannot do numeric precision.

---

## 1. It reads literally

Jev answers the question you wrote, not the one you meant. Negations, scoping words, and implied conditions land at face value.

**The tell:** you look at a wrong answer and catch yourself explaining what you really meant. **That explanation is the missing half of your instruction.**

**Fix:** state the exact condition in `instructions`. Put boundary cases in `criteria`. Where interpretation is unavoidable, split into two literal questions and combine in code.

**Illustration:** a user says *"Hey, have your human support agent call me, tomorrow at 5pm."* The question *"Does the user want to speak to a human support agent?"* returns yes - technically correct, and useless. The model cannot caveat. You needed to ask *"immediately"* or add a separate question for a callback request. This is not the model failing; it is an imprecise question.

---

## 2. It is not a calculator

Jev does not count reliably. This covers characters in a word, occurrences of a term in a passage, and items in a long list. It recognizes the shape of an answer rather than tallying, and the error grows with the size of the thing being counted.

Before asking a counting question, ask why a model is needed at all. If a regex or a parser can find the unit, the count belongs in code.

**Fix:** count in code. When you want a count of items matching criteria, ask one question per item and sum yourself.

```python
items = ["typesafe", "apple", "california", "banana", "likes", "calibration", "orange", "vertex"]

result = client.system_one(
    {"items": items},
    {f"item_{i}": Noul(instructions=f"Is `items[{i}]` the name of a fruit?") for i in range(len(items))},
)

count = sum(result.answers[f"item_{i}"].noul > 0.5 for i in range(len(items)))
```

**Also:** Jev performs better on semantic representations than numeric ones. Questions about colors using English names beat the same questions using hex values. Convert in code and pass a named bucket, keeping the model for the genuinely fuzzy part.

**And:** do not use score outputs to interpolate an exact magnitude between levels. Use the score to check a threshold; the arithmetic is yours.

---

## 3. Dates are text to it, not ordered quantities

Which of two dates comes first, how far apart they are, whether one falls in a window - all unreliable. Worse with mixed formats, relative references, and domain boundaries like quarters and settlement windows.

**Fix:** split the work. Extraction is a judgment, so give it to the model. Arithmetic is not, so keep it in code.

Every part of a date is a small closed set: twelve months, thirty-one days, a bounded range of years. That turns extraction into a `Choice` over enumerated options rather than free-form parsing, and gives you somewhere to put an explicit **"not stated"** option so a missing part is reported rather than guessed. Code assembles the parts into a real date and owns ordering, duration, offset, and weekday.

See [date extraction cookbook](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook).

---

## 4. Indirection costs accuracy

Instructions carrying double negatives or complex indirection are answered less reliably. A question about a property of a property, or anything needing multiple reasoning hops, costs accuracy.

**Fix:** write instructions as directly as possible. Identify the relevant parts of state by name. When you find yourself nesting clauses, that is a signal to decompose into two questions.

---

## 5. Large noisy state causes context rot

Accuracy falls as the state grows with content unrelated to the decision. Unrelated detail acts as a distractor, and a large state makes it harder to tell which part of the input caused a wrong answer.

**Fix:** retrieve and filter in code first, and send only the fields the question needs. When filtering before the call is not possible, use a `Noul` to filter for relevance. This is [Pattern 5](patterns.md#pattern-5---retrieve-then-judge).

Also note the hard limit: 64k tokens for state plus all questions, 32k for state plus the single longest question.

---

## 6. State is not treated as hostile

Jev does not treat state as adversarial by default. Content written to steer the model - an injected instruction, a deliberately misleading framing, or text that argues for its own classification - can move the answer. TypeSafe expects to improve this; today it is your threat model.

**Fix:** be explicit in the criteria about what does *not* count. Test your integration with adversarial inputs before deploying broadly. If user-controlled text goes into state, assume it is trying to influence the answer.

This matters most for [guardrail](../usecases/02-llm-guardrails-and-verification.md) use cases, where the input you are screening is exactly the input trying to get past you.

---

## 7. Contradictory instructions and criteria confuse it

When `instructions` and `criteria` ask for different things, performance degrades. A `Noul` where `true` maps to "no" performs worse. Aim for wording the average person could read and understand.

**Fix:** treat criteria as an extension of the instruction. Align them with clear, precise language. Keep the same field names across Choice options so the model can compare them directly.

---

## 8. Structural invariants are not guaranteed

Jev is extremely consistent - expect quantitatively similar outputs for semantically similar inputs. But invariants you might assume do not hold.

**The same question as a Noul and as a yes/no Choice can disagree:**

| Noul `noul` | Choice `yes` | Choice `no` | Choice `confidence` |
| --- | --- | --- | --- |
| 0.22 | 0.01 | 0.99 | 0.97 |

Asked on the ticket *"I'm not happy with the fit. What are my options here?"*

**And a question plus its negation do not sum to 1:**

| `refund` | `not_refund` | Sum |
| --- | --- | --- |
| 0.72 | 0.47 | 1.19 |

Asked on *"I was charged twice for the same order. Can someone look into this?"*

The reason is architectural: a `Choice` is *relative* - it settles which option wins. A `Noul` is *absolute* - it can be low for all options. They answer different questions.

**Fix:** do not rely on expected structural invariance. Don't carry a threshold tuned on a `Noul` over to a `Choice`. Don't hold the model to arithmetic identities between separate questions. Word each question to mean directly what you want.

---

## 9. It does not generate

Jev is not trained to generate text. You can force it by chaining choices; it will be slow and bad.

**Fix:** when the answer space is bounded, turn extraction into a `Choice` over options rather than asking for the value. Better, extract candidates with a regex or a generative model and let Jev pick the correct one.

When you genuinely need text - a rationale, a summary, a customer reply - use a model that writes.

---

## The community's two additions

### "Can't hallucinate" is a statement about types, not truth

Jev cannot return a value outside your schema. It can absolutely return the **wrong valid** value. TypeSafe is explicit that the 0% figure is not empirical: schema matching is guaranteed, therefore 0% is added to the plot. It is the same guarantee constrained decoding already gives you.

**The consequence people miss:** if your option list has no `none of these`, the probability mass has to land on something. The model is structurally unable to abstain, so it picks the closest wrong thing and reports it with confidence.

**Fix:** always include an explicit `other` or `none of these` option where the set might not cover the input. Treat the returned confidence, not the type guarantee, as your safety mechanism.

### Every piece of free reasoning must be rebuilt

This is the real cost of Jev and the one that surprises people.

A frontier model does a lot of reasoning for free inside its forward pass - reading a date off a screenshot, comparing it to today, deciding a value is implausible, noticing a contradiction. When you replace it with Jev, **every one of those computations has to be rebuilt as deterministic state in your code.**

The author of [awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) put it plainly: the frontier model read event dates off the pixels and compared them unaided, while the Jev pipeline needed explicit date parsing built around it.

**Fix:** budget for this. Before choosing Jev, list what the LLM was doing implicitly and confirm you can compute each piece. If you cannot, Jev is the wrong tool for that step.

---

## Quick pre-ship checklist

- [ ] No question asks Jev to count, do arithmetic, or compare dates
- [ ] No question hides several judgments inside one answer
- [ ] Every `Choice` whose set might not cover the input has an `other` option
- [ ] State contains only the fields the questions need
- [ ] `instructions` and `criteria` agree; no double negatives
- [ ] No threshold assumes `P(x) + P(not x) = 1` across separate questions
- [ ] User-controlled state has been tested with adversarial input
- [ ] Thresholds are tuned on your own data, not borrowed from the docs
- [ ] The model version is pinned if thresholds are tuned
- [ ] Every implicit LLM computation the pipeline removed has been rebuilt in code

---

## Next

- [evaluating-jev.md](evaluating-jev.md) - how to test calibration on your data
- [how-to-use-jev-effectively.md](how-to-use-jev-effectively.md) - the design method these failures violate
