# Routing and triage

**Decision shape:** `Choice` to select the destination, `Score` for priority, `Noul` for the branch conditions.

**Reach for it when:** one known category should select the next code path, and you are currently sending the whole thing to an LLM or writing brittle rules.

This is the canonical first Jev use case. It is documented by TypeSafe, demonstrated in the launch coverage, and it is the shape every other routing problem generalizes from.

---

## Why the problem is a good fit

Routing has three properties that make it ideal for a System One model:

1. **The answer space is closed.** There are four teams or there are not. You can enumerate them.
2. **The decision repeats.** Every ticket, every message, every request.
3. **The decision is a judgment, not a computation.** Rules are too brittle ("charged twice" is billing unless it's also a login problem); an LLM is too slow and too expensive per request.

That is exactly the gap Jev fills.

---

## The worked example

TypeSafe's own documentation builds a support-ticket triage workflow. It is the best single reference in the ecosystem and it demonstrates every pattern at once: deterministic code first, scoped state, atomic questions, composite spam scoring, confidence-gated routing, and speculative fan-out.

```python
from typesafe_sdk import Choice, Noul, NoulCriteria, Score, TypeSafeClient


def triage_ticket(ticket, customer):
    # Handle deterministic states without calling a model.
    if ticket["status"] == "closed":
        return "no_action"

    open_orders = [o for o in customer["orders"] if o["status"] != "delivered"]

    # Include only the structured context needed by the questions below.
    state = {
        "ticket": {
            "message": ticket["message"],
            "sender": ticket["sender"],
            "links": ticket["links"],
        },
        "customer": {"plan": customer["plan"], "open_orders": open_orders},
        "policy": {"sensitive_credentials": ["password", "security code", "API key"]},
    }

    # Ask structured, atomic questions together so they run in parallel.
    questions = {
        "topic": Choice(
            instructions={
                "question": "Which team should handle `ticket.message`?",
                "focus": "Classify the customer's primary request.",
            },
            criteria={
                "billing": {
                    "what": "Charges, invoices, refunds, or subscriptions",
                    "not_for": "Order tracking or account access",
                    "examples": ["I was charged twice", "Where is my refund?"],
                },
                "orders": {
                    "what": "Order status, delivery, cancellation, or returns",
                    "not_for": "Charges or account access",
                    "examples": ["Where is my order?", "Cancel my shipment"],
                },
                "account": {
                    "what": "Login, profile, permissions, or security",
                    "not_for": "Charges or order tracking",
                    "examples": ["Reset my password", "I cannot sign in"],
                },
            },
        ),
        "requests_credentials": Noul(
            instructions={
                "question": "Does the message request a sensitive credential?",
                "compare": ["`ticket.message`", "`policy.sensitive_credentials`"],
                "focus": "Look for a request to disclose the credential itself.",
            },
        ),
        "unexpected_reward": Noul(
            instructions={
                "question": "Does the message announce an unexpected reward?",
                "inspect": "`ticket.message`",
                "focus": "Look for an unsolicited prize, payment, or reward claim.",
            },
        ),
        "refund_requested": Noul(
            instructions={
                "question": "Does the customer explicitly request a refund or credit?",
                "inspect": "`ticket.message`",
                "focus": "Require a requested remedy, not a billing complaint alone.",
            },
        ),
        "mentions_open_order": Noul(
            instructions={
                "question": "Does the message refer to a supplied open order?",
                "compare": ["`ticket.message`", "`customer.open_orders`"],
                "focus": "Match an order id or other identifying details.",
            },
        ),
        "frustration": Score(
            instructions={
                "question": "How frustrated does the customer appear?",
                "inspect": "`ticket.message`",
                "focus": "Judge expressed frustration, not issue severity.",
            },
            criteria=[
                {"what": "Calm and matter-of-fact",
                 "signals": ["Neutral wording", "No complaint about the experience"]},
                {"what": "Frustrated but civil",
                 "signals": ["Expresses annoyance", "Remains constructive"]},
                {"what": "Very angry or threatening to leave",
                 "signals": ["Hostile language", "Threatens cancellation or churn"]},
            ],
        ),
    }

    with TypeSafeClient() as client:
        response = client.system_one(state=state, questions=questions)

    answers = response.answers
    # ... routing logic below
```

The routing logic, and this is the part that matters:

```python
    # Escalate uncertain judgments instead of guessing.
    if answers["topic"].confidence < 0.75:
        return route_to_human_review(ticket)

    # Let code decide which speculative answers matter on this path.
    if answers["topic"].choice == "billing":
        return route_to_billing(
            ticket,
            refund_requested=answers["refund_requested"].noul >= 0.7,
        )
    if answers["topic"].choice == "orders":
        return route_to_orders(
            ticket,
            mentions_open_order=answers["mentions_open_order"].noul >= 0.7,
        )

    priority = (
        "high"
        if answers["frustration"].confidence >= 0.7 and answers["frustration"].score >= 1.5
        else "normal"
    )
    return route_to_account_support(ticket, priority=priority)
```

Source: [docs.typesafe.ai/concepts/how-to-build-with-system-one](https://docs.typesafe.ai/concepts/how-to-build-with-system-one)

---

## What the community built

### Ticket triage, measured against an LLM

[EdytaKucharska/ticket-quest](https://github.com/EdytaKucharska/ticket-quest) is a playful ticket triage that shows how Jev's typed, probability-backed decisions compare with prompting an LLM, ranking by Cost of Delay. The comparison framing is the useful part: the same triage question answered both ways, with the trade visible.

### Real production routing at ~35k cases

[@aviz85](https://x.com/aviz85/status/2100150169270419572) described wiring Jev into a live claim-ops pipeline for a UK consumer-claims firm handling roughly 35,000 cases:

> Building production claim-ops agents for a UK consumer-claims firm (~35k cases): classify inbound lender/client email (info requests, appointment vs dissent, rejection reasons), then confidence-gate auto-draft vs human approval. Regex already misclassified legal intent once — need typed Choice/Noul decisions with calibrated confidence so high-confidence routes execute and low-confidence always hits a human. Ready to wire Jev into those classifiers this week.

Note the driver: **regex already misclassified once, and the fix is not a better regex.** It is a classifier with a confidence you can gate on. And note the design: high-confidence routes execute, low-confidence always hits a human - [Pattern 2](../docs/patterns.md#pattern-2---confidence-gated-routing), stated as a production requirement.

### Task, model, and exception routing

[@StrateGeee](https://x.com/StrateGeee/status/2100247334961426434) described the same pattern applied one level up:

> We'd test Jev for task/model routing, exception triage and rubric-based output verification: workflow state → typed decisions → deterministic policy gates, escalating uncertain cases to frontier models or humans.

That is the [cascade](../docs/patterns.md#pattern-4---the-cascade) in one sentence.

### Model routing as a product category

Several projects put Jev in front of other models:

- [nidhi-singh02/agent-router](https://github.com/nidhi-singh02/agent-router) picks Cursor, Claude Code, Codex, or OpenCode plus model/effort for a task, then launches it.
- [0xNatoshi/jev-codex-router](https://github.com/0xNatoshi/jev-codex-router) does per-turn model and reasoning routing for Codex - picks the model, thinking depth, and speed mode for every turn.
- [iamvatsalpatel/tiershift](https://github.com/iamvatsalpatel/tiershift) shifts every LLM call to the cheapest model that can handle it, decided by Jev in ~280 ms with no training data.
- [tylerjharden/ailerix](https://github.com/tylerjharden/ailerix) is a type-safe model router where Jev banks each request to a typed catalogue route.
- [MongLong0214/jev-gate](https://github.com/MongLong0214/jev-gate) - "not every coding task needs your best model."

The repetition of this idea across independent authors is the strongest signal in the routing category.

---

## Design notes specific to routing

### Always include an `other` option

Without one, the probability mass lands on the closest wrong team. The model cannot abstain. Add `other` or `unclassified` explicitly, and route it to human review.

### Confidence gates belong on the route, not the request

A wrong routing decision costs a re-route. A wrong *action* (issuing a refund, closing an account) costs more. Use a lower confidence bar for routing and a higher one for any side effect downstream.

### Ask the branch conditions speculatively

`refund_requested` and `mentions_open_order` are only meaningful on one branch each. Ask them anyway - they cost tokens and almost no time. See [Pattern 1](../docs/patterns.md#pattern-1---speculative-fan-out).

### Score the priority separately from the category

Do not ask "which team and how urgent" as one question. They are independent judgments, and combining them hides the decision. Ask them separately and combine in code, where the weighting is visible and tunable.

### Do not route on a score without a confidence check

A `Score` gives you degree, not certainty. For priority, check `confidence >= 0.7` *and* `score >= 1.5` before escalating, as the worked example does.

---

## Pitfalls

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| Broad category question | The model picks a plausible wrong team | Add contrastive `not_for` criteria and examples |
| No `other` option | Forced false classification on out-of-scope input | Add an explicit `other`, route it to review |
| Routing on a score alone | Erratic priority | Gate on confidence as well |
| Sending whole customer record | Accuracy drops as irrelevant detail grows | Send only the fields the questions need |
| No confidence gate | Confidently misrouted tickets | Escalate below threshold; tune per route |
| Thresholds copied from docs | Works on demo, not on your traffic | [Evaluate on your data](../docs/evaluating-jev.md) |

---

## Adapting this template

Replace `topic` options with your destinations, replace the `Noul` branch conditions with your branch questions, and keep everything else. The structure transfers to:

- **Sales lead routing** (SDR vs AE vs partner vs nurture)
- **Support escalation** (tier 1 vs tier 2 vs engineering vs management)
- **Legal intake** (contract review vs litigation vs compliance vs outside counsel)
- **Insurance claim triage** (straight-through vs adjuster vs specialist vs fraud)
- **Content moderation queues** (allow vs warn vs review vs block)
- **Security alert triage** (auto-close vs investigate vs escalate)

See [reference/question-catalog.md](../reference/question-catalog.md) for ready-made question sets by domain.

---

## Related

- [../docs/patterns.md](../docs/patterns.md) - cascade and confidence-gated routing
- [10-domain-applications.md](10-domain-applications.md) - industry-specific routing
- [02-llm-guardrails-and-verification.md](02-llm-guardrails-and-verification.md) - screening inputs before they reach the router
