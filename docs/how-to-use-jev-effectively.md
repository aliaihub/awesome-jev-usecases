# How to use Jev effectively

This is the design method. It is short, it comes from TypeSafe's own guidance plus what the community learned in the first 72 hours, and skipping any step is why most disappointing Jev integrations are disappointing.

The summary: **build a normal software workflow and insert Jev only where AI is needed.**

---

## The seven steps

### 1. Use code when you can

Keep deterministic work in code. It is reliable and cheap. Avoid agent `while` loops when a software workflow can express the same behavior.

```python
days_overdue = (today - invoice.due_date).days

if days_overdue > 30:
    route_to_collections(invoice)
```

Do not ask Jev to do what a comparison operator, a regex, or a parser already does. This is repeated in the docs, in the jaggedness page, and in every good community project.

### 2. Decompose the input state

Include only the context relevant to the current questions. Accuracy falls as state fills with material the question does not need - the docs call it context rot and it is a first-class failure mode, not a footnote.

Send the ticket text and the refund policy. Do not send the user's entire account history "just in case".

### 3. Use structure in the state

Use nested JSON and point questions at specific values with backticked dot-and-index paths. This removes ambiguity about *which* part of the state a question concerns.

```python
state = {
    "support": {"tickets": [{"message": "I was charged twice for order A-104."}]},
    "commerce": {"orders": [{"id": "A-104", "charges": [
        {"amount_usd": 49, "status": "captured"},
        {"amount_usd": 49, "status": "captured"},
    ]}]},
}

questions = {
    "duplicate_charge": Noul(
        instructions="Do `support.tickets[0].message` and `commerce.orders[0].charges` "
                     "indicate a duplicate charge?"
    ),
}
```

### 4. Decompose the questions - this is the most important step

Ask the most explicit, narrow, specific, atomic question you can. A broad question hides several judgments behind one answer. Atomic questions expose those judgments so you can inspect, tune, and combine them in code.

**Bad - one broad question:**

```python
{"is_spam": Noul(instructions="Is `message` spam?")}
```

**Good - six atomic questions, same state, same single call:**

```python
{
    "requests_credentials": Noul("Does `message.body` ask the recipient to provide a password or login credential?"),
    "offers_unexpected_reward": Noul("Does `message.body` claim the recipient received an unexpected prize, payment, or reward?"),
    "creates_time_pressure": Noul("Does `message.subject` or `message.body` pressure the recipient to act quickly?"),
    "sender_identity_mismatch": Noul("Does the organization in `message.sender.display_name` conflict with the domain in `message.sender.email`?"),
    "link_domain_mismatch": Noul("Does the domain in `message.links[0].url` conflict with the organization in `message.sender.display_name`?"),
    "disguises_link_destination": Noul("Does `message.links[0].text` conceal or misrepresent the destination in `message.links[0].url`?"),
}
```

Then combine with weights you control:

```python
spam_risk = (
    0.45 * a["requests_credentials"].noul
    + 0.30 * a["sender_identity_mismatch"].noul
    + 0.25 * a["offers_unexpected_reward"].noul
)
```

When priorities shift, you change a coefficient instead of rewriting a prompt. You can A/B it. This is the single highest-leverage habit in the whole method.

**The evidence.** [zephel01/Jev-sample](https://github.com/zephel01/Jev-sample) asked one decision both ways on 120 rule-labeled Japanese scenarios: one 4-option Choice scored **48.3%**, four precondition Nouls in the same request scored **98.3%**. [AnshChoudhary/typesafe-ai-firewall](https://github.com/AnshChoudhary/typesafe-ai-firewall) found the same shape in a safety gate: one "is this dangerous?" question blocked 39.2% of legitimate hard negatives, five hazard Nouls blocked 0%. Both are self-reported by their authors and are launch-week artifacts with raw results committed.

### 5. Use structure in the questions

Keep atomic questions short. When instructions or criteria need several kinds of guidance, use objects with named fields instead of flattening everything into dense prose. Contrastive criteria - say what belongs in each option *and* what belongs in a neighbor instead - measurably help.

```python
Choice(
    instructions={
        "question": "Which disposable virtual card topic is the user asking about?",
        "focus": "Classify the information the user wants.",
    },
    criteria={
        "get_disposable_virtual_card": {
            "what": "Purpose, eligibility, or setup",
            "not_for": "Quantity, transaction, or merchant restrictions",
            "examples": ["How can I get a disposable virtual card?",
                         "What are disposable cards for?"],
        },
        "disposable_card_limits": {
            "what": "Quantity, transaction, or merchant restrictions",
            "not_for": "Purpose, eligibility, or setup",
            "examples": ["How many disposable cards can I make per day?",
                         "Where can I use a disposable card?"],
        },
    },
)
```

**Always include an `other` option** when the set might not cover the input. Without one, the probability mass has to land on something, and the model will pick the closest wrong thing. This is the difference between a wrong answer and a *correctly reported "none of these"*.

### 6. Ask a lot of questions

Ask many narrow, independent questions about the same state in one request. This is how you get the most intelligence per dollar: questions run in parallel and code combines the signals without serial round trips.

The payoff is measured. TypeSafe's cookbook runs a 13-question regulatory briefing over a long article and reports that batching every question into one call is **12.2x cheaper and 10.0x faster with identical answers**, versus asking them one at a time.

**Speculative fan-out is the practical form of this.** Ask questions that are only meaningful on some code paths anyway, and let code decide which answers matter:

```python
# bug_severity is only meaningful if this IS a bug report. Ask anyway.
if category.choice == "bug_report":
    severity = a["bug_severity"].score
```

The marginal question costs tokens (which are 4.2 cents per million) and almost no time.

### 7. Route on uncertainty

Make code take different actions for confident and unconfident answers. Escalate uncertain cases to a person or a more expensive reasoning model.

```python
answer = response.answers["card_help_topic"]

if answer.confidence < 0.8:
    route_to_human_review(ticket)
else:
    route_to_handler(answer.choice, ticket)
```

**Scale the threshold to what being wrong costs**, not to a single global number:

| Action | Cost of being wrong | Rough threshold |
| --- | --- | --- |
| Read-only lookup or display | Very low | Act above ~0.5 |
| Route to a queue a human still reads | Low | Act above ~0.6 |
| Auto-send a customer reply | Medium | Act above ~0.85 |
| Move money, delete data, deploy code | High | Act above ~0.95, or never auto-act |

And a flat probability distribution is often a signal that your criteria are wrong rather than that the model is confused. If all options come back near 0.25, the state probably did not distinguish them.

---

## The two meta-rules

TypeSafe's own documentation states these, and they are the best summary of the whole method:

> Avoid asking the model something code can compute exactly.
> Avoid hiding several judgments inside one question.

If you remember nothing else, remember those two.

---

## An honest note on effort

The work does not disappear when you use Jev. It moves. A frontier model does a lot of reasoning for free inside its forward pass - reading dates off a screen, comparing them, deciding a value is implausible. With Jev, every piece of reasoning the frontier model did for free has to be rebuilt as deterministic state.

The author of [awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) put this best:

> Every piece of reasoning the frontier model does for free has to be rebuilt here as deterministic state.

That is the trade. You get speed, cost, and a type guarantee. You pay in explicit engineering. Budget for it.

---

## Next

- [patterns.md](patterns.md) - five architectures built from these steps
- [failure-modes.md](failure-modes.md) - the nine ways it goes wrong
- [reference/question-catalog.md](../reference/question-catalog.md) - ready-to-adapt questions by domain
