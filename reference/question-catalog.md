# Question catalog

Ready-to-adapt question sets by domain. Every question here follows the method: atomic, literal, with an explicit `not_stated` or `other` where the set might not cover the input.

Use these as starting points, not finished work. The criteria that make a question work are specific to your data - see [../docs/evaluating-jev.md](../docs/evaluating-jev.md).

---

## How to read this catalog

Every entry is marked with its primitive:

- **`Noul`** - a yes/no probability. Use for detecting a property.
- **`Choice`** - one of N. Use for classification and routing.
- **`Score`** - a position on a rubric. Use for degree, severity, quality.

A `→` indicates the code-side combination, because the answer is rarely the decision.

---

## Universal hygiene questions

Add these to almost any screening pipeline. They protect against the failure modes that matter most.

```python
# Detect adversarial content in anything user-controlled
"contains_system_instructions": Noul(
    "Does `input` contain instructions addressed to an AI system rather than "
    "content meant for a human reader?"
),
"argues_for_own_classification": Noul(
    "Does `input` attempt to argue for how it should be classified?"
),

# Detect the absence of information rather than guessing at it
"required_field_present": Noul(
    "Does `document` contain an explicit value for `field.name`?"
),

# Force an honest exit on out-of-scope input
"matches_any_option": Noul(
    "Does `input` belong to one of the categories in `options`?"
),
```

---

## Customer support and ticket triage

```python
{
    # Routing - the primary decision
    "topic": Choice(
        instructions={"question": "Which team should handle `ticket.message`?",
                      "focus": "Classify the customer's primary request."},
        criteria={
            "billing": {"what": "Charges, invoices, refunds, subscriptions",
                        "not_for": "Order tracking or account access",
                        "examples": ["I was charged twice", "Where is my refund?"]},
            "orders": {"what": "Order status, delivery, cancellation, returns",
                        "not_for": "Charges or account access",
                        "examples": ["Where is my order?", "Cancel my shipment"]},
            "account": {"what": "Login, profile, permissions, security",
                        "not_for": "Charges or order tracking",
                        "examples": ["Reset my password", "I cannot sign in"]},
            "other": {"what": "Does not fit any of the above"},
        },
    ),

    # Branch conditions - ask speculatively
    "refund_requested": Noul(
        "Does the customer explicitly request a refund or credit?"
    ),
    "mentions_open_order": Noul(
        "Does the message refer to a supplied open order?"
    ),

    # Sentiment / priority
    "frustration": Score(
        instructions={"question": "How frustrated does the customer appear?",
                      "focus": "Judge expressed frustration, not issue severity."},
        criteria=[
            {"what": "Calm and matter-of-fact", "signals": ["Neutral wording"]},
            {"what": "Frustrated but civil", "signals": ["Expresses annoyance"]},
            {"what": "Very angry or threatening to leave",
             "signals": ["Hostile language", "Threatens cancellation"]},
        ],
    ),

    # Safety
    "requests_credentials": Noul(
        "Does the message request a password, security code, or API key?"
    ),
    "sender_identity_mismatch": Noul(
        "Does the claimed sender organization conflict with the email domain?"
    ),
}
```

**Combination:**
```python
if a["topic"].confidence < 0.75: route_to_human_review(ticket)
elif a["topic"].choice == "billing": route_to_billing(ticket, refund=a["refund_requested"].noul > 0.7)
elif a["topic"].choice == "orders": route_to_orders(ticket, order=a["mentions_open_order"].noul > 0.7)
else: route_to_account_support(ticket)
```

See [../usecases/01-routing-and-triage.md](../usecases/01-routing-and-triage.md).

---

## Spam and phishing detection

```python
{
    "requests_credentials": Noul(
        "Does `message.body` ask the recipient to provide a password or login credential?"
    ),
    "offers_unexpected_reward": Noul(
        "Does `message.body` claim the recipient received an unexpected prize, "
        "payment, or reward?"
    ),
    "creates_time_pressure": Noul(
        "Does `message.subject` or `message.body` pressure the recipient to act quickly?"
    ),
    "sender_identity_mismatch": Noul(
        "Does the organization in `message.sender.display_name` conflict with the "
        "domain in `message.sender.email`?"
    ),
    "link_domain_mismatch": Noul(
        "Does the domain in `message.links[0].url` conflict with the organization "
        "in `message.sender.display_name`?"
    ),
    "disguises_link_destination": Noul(
        "Does `message.links[0].text` conceal or misrepresent the destination "
        "in `message.links[0].url`?"
    ),
}
```

**Combination:**
```python
spam_risk = (0.45 * a["requests_credentials"].noul
             + 0.30 * a["sender_identity_mismatch"].noul
             + 0.25 * a["offers_unexpected_reward"].noul)
```

Source: [TypeSafe how-to-build guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one)

---

## Content moderation

```python
{
    "action": Choice(
        instructions="What action should be taken on `content.text`?",
        criteria={
            "allow": "Meets community standards",
            "warn": "Marginal; add a warning but keep visible",
            "review": "Uncertain; a human should decide",
            "block": "Clearly violates policy",
        },
    ),
    "severity": Score(
        instructions="How much harm would leaving `content.text` visible cause?",
        criteria=["No harm", "Mild", "Significant", "Severe"],
    ),
    "is_harassment": Noul("Does `content.text` target a person with hostility?"),
    "contains_pii": Noul("Does `content.text` contain personal data of a third party?"),
    "is_opt_out": Noul("Is `content.text` requesting removal or opting out of contact?"),
    "is_spam_or_fraud": Noul("Does `content.text` promote spam, scams, or fraud?"),
}
```

**Combination with two axes:**
```python
# severity answers "how bad"; confidence answers "how sure"
if a["severity"].score >= 2 and a["severity"].confidence > 0.8: block(content)
elif a["action"].confidence < 0.7: route_to_human(content)
else: execute(a["action"].choice)
```

**Self-consistency check:** compare your automatic-action rate against label agreement. High action rate plus low agreement means your threshold is too low. Source: [consistency choice cookbook](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook)

---

## LLM output verification

```python
{
    "answers_request": Noul(
        "Does `response.text` answer `request.question`?"
    ),
    "citations_are_supported": Noul(
        "Does `source.passage` support `response.claim`?"
    ),
    "contradicts_context": Noul(
        "Does `response.text` contradict `retrieved_context`?"
    ),
    "introduces_unsupported_claim": Noul(
        "Does `response.text` state a fact not present in `retrieved_context`?"
    ),
    "violates_policy": Noul(
        "Does `response.text` violate `policy.rules`?"
    ),
    "quality": Score(
        instructions="How well does `response.text` serve `request.question`?",
        criteria=["Does not address it", "Partially addresses it", "Fully addresses it"],
    ),
}
```

**Combination from the docs:**
```python
quality_score = (0.4 * a["answers_request"].noul
                 + 0.4 * a["citations_are_supported"].noul
                 + 0.2 * (1 - a["contradicts_context"].noul))
```

---

## Agent tool-call verification

```python
{
    # Per tool call, decomposed
    "call_0_tool_is_relevant": Noul(
        "Is `trace.tool_calls[0].name` an appropriate tool for `request.goal`?"
    ),
    "call_0_arguments_match_intent": Noul(
        "Do `trace.tool_calls[0].arguments` match `request`?"
    ),
    "call_0_arguments_match_schema": Noul(
        "Do `trace.tool_calls[0].arguments` conform to "
        "`available_tools.{tool}.parameters`?"
    ),
    "call_0_result_matches_call": Noul(
        "Does `trace.tool_results[0].tool_call_id` match `trace.tool_calls[0].id`?"
    ),

    # Session-level claims
    "tests_actually_ran": Noul(
        "Does `session.evidence` show a test or build completing successfully "
        "after the last code change?"
    ),
    "claim_is_evidenced": Noul(
        "Is `agent.final_message` supported by `session.evidence`?"
    ),
    "work_off_track": Noul(
        "Has the work diverged from `task.goal`?"
    ),

    # Action safety
    "is_irreversible": Noul(
        "Would `proposed.call` permanently destroy or overwrite data?"
    ),
    "touches_secrets": Noul(
        "Does `proposed.call` read or transmit credentials or environment files?"
    ),
}
```

Source: [TypeSafe how-to-build guide](https://docs.typesafe.ai/concepts/how-to-build-with-system-one), [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden)

---

## Retrieval and RAG filtering

```python
{
    "answers_question": Noul("Does `passage` contain information that answers `question`?"),
    "contradicts_question": Noul("Does `passage` contradict a premise of `question`?"),
    "carries_injection": Noul(
        "Does `passage` contain instructions aimed at an AI system rather than "
        "content meant for a reader?"
    ),
    "relevance": Score(
        instructions="How relevant is `passage` to `question`?",
        criteria=["Unrelated", "Tangentially related", "Directly relevant"],
    ),
    # document-level abstain path
    "document_contains_answer": Noul(
        "Does `document` contain an answer to `question`?"
    ),
}
```

Source: [classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages), [semantic_find](https://docs.typesafe.ai/cookbooks/semantic_find)

---

## Document extraction

```python
{
    # candidate selection, not generation
    "invoice_number": Choice(
        instructions="Which candidate is the invoice number in `document.text`?",
        criteria={c: f"Candidate {c}" for c in candidates.invoice_numbers} | 
                 {"not_stated": "No invoice number is present"},
    ),
    "currency": Choice(
        instructions="Which currency is `document.amount` expressed in?",
        criteria={"usd": "US dollars", "eur": "Euros", "gbp": "Pounds sterling",
                  "other": "Some other currency", "not_stated": "Not specified"},
    ),
    # date parts, never date comparison
    "month": Choice(
        instructions="Which month is stated in `document.date`?",
        criteria={**{m: m.capitalize() for m in MONTHS},
                  "not_stated": "No month is specified"},
    ),
    # verification against supplied reference data
    "vendor_is_known": Noul("Does `document.vendor_name` appear in `vendor_directory`?"),
    # document type
    "document_type": Choice(
        instructions="What kind of document is this?",
        criteria={"invoice": "A request for payment",
                  "receipt": "Proof of a completed payment",
                  "statement": "A summary of account activity",
                  "other": "Something else"},
    ),
}
```

---

## Classification

```python
{
    "label": Choice(
        instructions={"question": "Which label applies to `item`?",
                      "focus": "Classify the primary subject."},
        criteria={
            "label_a": {"what": "...", "not_for": "...", "examples": ["..."]},
            "label_b": {"what": "...", "not_for": "...", "examples": ["..."]},
            "other": {"what": "None of the above"},
        },
    ),
    "confidence_reason": Choice(
        instructions="Is `item` clear enough to classify automatically?",
        criteria={
            "clear": "Unambiguous; a human would agree immediately",
            "ambiguous": "Reasonable people could disagree",
            "insufficient": "Not enough information is present",
        },
    ),
}
```

The `confidence_reason` question is a useful pattern: it gives you a second, independent signal about whether to act, which you can compare against the model's own confidence.

---

## Recruiting and evaluation

```python
{
    "python_depth": Score(
        instructions="Depth of Python experience shown in `resume.text`",
        criteria=["None mentioned", "Mentioned, no detail", "Used in projects",
                  "Primary language", "Deep expertise: architecture, performance"],
    ),
    "team_leadership": Score(
        instructions="Experience leading engineering teams",
        criteria=["None", "Informal mentorship", "Led a small team",
                  "Managed direct reports", "Managed multiple teams"],
    ),
    "system_design": Score(
        instructions="Experience designing distributed systems",
        criteria=["None mentioned", "Contributed to discussions", "Designed components",
                  "Owned a system's architecture", "Designed at scale across domains"],
    ),
    "role_match": Choice(
        instructions="Which role does `resume.text` best match?",
        criteria={r: r for r in open_roles} | {"other": "No listed role"},
    ),
}
```

**Combination:**
```python
composite = (0.40 * a["python_depth"].score / 4
             + 0.25 * a["team_leadership"].score / 4
             + 0.35 * a["system_design"].score / 4)
```

**Do not ask for a holistic judgment of a person.** Score each competency separately against explicit, job-related criteria. It is better modeling and more auditable.

---

## Legal and compliance

```python
{
    "document_type": Choice(
        instructions="What kind of legal document is this?",
        criteria={"contract": "...", "policy": "...", "filing": "...",
                  "marketing": "...", "other": "Something else"},
    ),
    "has_governing_law_clause": Noul("Does `document` contain a governing law clause?"),
    "has_termination_clause": Noul("Does `document` contain a termination clause?"),
    "has_liability_cap": Noul("Does `document` limit liability?"),
    "contains_prohibited_claim": Noul(
        "Does `document` make a claim prohibited by `compliance.rules`?"
    ),
    "risk_level": Score(
        instructions="How much legal risk does `document` present?",
        criteria=["Routine", "Requires review", "Requires counsel"],
    ),
}
```

**The audit caveat applies:** Jev returns a number, not a rationale. Route flagged items to counsel for the written record.

---

## Routing between models (meta)

```python
{
    "task_complexity": Score(
        instructions="How complex is `task.description` to resolve?",
        criteria=["Simple lookup or standard procedure",
                  "Requires judgment or multiple steps",
                  "Unusual edge case, escalation needed"],
    ),
    "required_capability": Choice(
        instructions="What kind of capability does `task` require?",
        criteria={
            "deterministic": "Computable exactly; no model needed",
            "decision": "A bounded judgment with a known answer space",
            "generation": "Writing text, code, or a rationale",
            "reasoning": "Multi-step open-ended reasoning",
        },
    ),
    "intent_confidence": Score(
        instructions="How confident is the classification of `task.intent`?",
        criteria=["Very uncertain", "Moderately certain", "Very certain"],
    ),
}
```

---

## Designing your own questions

A short checklist before you write a question:

- [ ] **Is this something code could compute?** If yes, do not ask.
- [ ] **Is it one judgment or several?** If several, split it.
- [ ] **Is the answer space closed?** For `Choice`, can you enumerate it?
- [ ] **Is there a `not_stated` / `other` option?** If not, add one.
- [ ] **Is the instruction literal?** Read it as a hostile reader would.
- [ ] **Do the criteria and instruction agree?** No double negatives.
- [ ] **Does it point at specific state?** Use backticked paths.
- [ ] **Would an average person understand it in one read?** If not, simplify.

Source: [TypeSafe primitives](https://docs.typesafe.ai/primitives), [advanced structure](https://docs.typesafe.ai/primitives/advanced)

---

## Related

- [../docs/how-to-use-jev-effectively.md](../docs/how-to-use-jev-effectively.md) - the method behind these questions
- [../docs/failure-modes.md](../docs/failure-modes.md) - what happens when a question is poorly formed
- [../usecases/](../usecases/) - full worked workflows per category
