# Getting started

Everything you need for a first useful Jev call. Roughly five minutes.

## 1. Get access

Jev is in early access behind a waitlist.

- Sign up and get pulled off the waitlist at [typesafe.ai](https://typesafe.ai/)
- Create an API key at [console.typesafe.ai/settings/keys](https://console.typesafe.ai/settings/keys)
- Alternative route: Jev is also reachable through the [Vercel AI Gateway](https://vercel.com/ai-gateway/models/jev)

```bash
export TYPESAFE_API_KEY="sk-..."
```

## 2. Install an SDK

**Python** (3.10+):

```bash
pip install typesafe-sdk
# or
uv add typesafe-sdk
```

**JavaScript / TypeScript** (Node 20+):

```bash
npm install @typesafe-ai/sdk
```

Both SDKs read `TYPESAFE_API_KEY` from the environment and default to the `jev-latest` alias.

## 3. One endpoint, if you prefer raw HTTP

```
POST https://api.typesafe.ai/v1/systemone
```

```python
import requests

response = requests.post(
    "https://api.typesafe.ai/v1/systemone",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "jev-latest",
        "state": {"ticket": "I was charged twice for order A-104. Please refund the duplicate."},
        "questions": {
            "department": {
                "type": "choice",
                "instructions": "Which team should handle this?",
                "criteria": {
                    "billing": "Payment, invoices, refunds, subscriptions",
                    "technical": "Bugs or integration problems",
                    "sales": "Pricing or account questions",
                },
            },
            "wants_refund": {
                "type": "noul",
                "instructions": "The customer is explicitly asking for a refund",
            },
        },
    },
)
print(response.json())
```

## 4. The real first call

The state can be a string, a JSON object, or an array of text. Use an object when there is more than one piece of context. Use backticked dot-and-index paths in questions to point at specific values.

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient() # reads TYPESAFE_API_KEY, defaults to jev-latest

response = client.system_one(
    state={
        "ticket": {
            "subject": "Duplicate charge",
            "messages": [
                {
                    "from": "customer",
                    "text": "I was charged twice for order A-104. Please refund the duplicate.",
                }
            ],
        },
        "order": {
            "id": "A-104",
            "charges": [
                {"amount_usd": 49, "status": "captured"},
                {"amount_usd": 49, "status": "captured"},
            ],
        },
        "refund_policy": "Duplicate charges are eligible for a refund.",
    },
    questions={
        "department": Choice(
            instructions="Which team should handle `ticket.messages[0].text`?",
            criteria={
                "billing": "Payment or subscription issues",
                "technical": "Bugs or integration problems",
                "sales": "Pricing or account questions",
            },
        ),
        "frustration": Score(
            instructions="How frustrated does the customer appear?",
            criteria=[
                "Calm, just stating facts",
                "Frustrated but civil",
                "Very angry, strong language",
            ],
        ),
        "refund_requested": Noul(
            instructions="The customer is explicitly asking for a refund or credit"
        ),
        "policy_supports_refund": Noul(
            instructions="Does `refund_policy` cover this situation?"
        ),
    },
)

dept = response.answers["department"]
print(dept.choice, round(dept.confidence, 3))
print(round(response.answers["frustration"].score, 2))
print(round(response.answers["refund_requested"].noul, 3))
print(round(response.answers["policy_supports_refund"].noul, 3))
```

Notice four things, because they are the whole method:

1. **Four questions, one network call.** They run in parallel, so the tenth costs tokens but almost no time.
2. **Every question is atomic.** "Should we refund?" is not asked. Two separate questions establish that a refund was requested *and* that policy covers it. Your code combines them.
3. **State is structured and scoped.** The questions only need the ticket text, the order charges, and the policy - so that is what is sent.
4. **Nothing was asked that code could compute.** The duplicate charge is already visible in `order.charges`. Jev is not asked to count anything.

## 5. Combine the answers in code

This is the step most first integrations skip, and it is the point.

```python
answers = response.answers

refundable = (
    answers["refund_requested"].noul > 0.7
    and answers["policy_supports_refund"].noul > 0.7
)

if answers["department"].confidence < 0.75:
    route_to_human_review(ticket)
elif answers["department"].choice == "billing" and refundable:
    start_refund_flow(ticket)
elif answers["frustration"].score >= 1.5 and answers["frustration"].confidence >= 0.7:
    route_priority(ticket, answers["department"].choice)
else:
    route_standard(ticket, answers["department"].choice)
```

The thresholds are yours. They live in code, so re-weighting is a code change and not a re-prompt. Start with the vendor's suggested defaults (escalate below 0.5, act above 0.9) and tune on your own data - see [evaluating-jev.md](evaluating-jev.md).

## 6. Operational facts to know before you ship

**Pin the version if you tune thresholds.** `jev-latest` currently resolves to `jev-1.13.0` and will move when a new release ships, which changes answers under you. The response's `model` field reports the versioned ID that answered, so log it.

```python
client = TypeSafeClient(model="jev-1.13.0") # pin
```

**Context limits work differently from an LLM.** State is ingested once and questions run in parallel over it:
- 64k tokens for state plus all questions together
- 32k tokens for state plus the single longest question

**Rate limits** for `jev-1.13` are 250,000 tokens/second and 1,200 requests/minute. Over either returns `429`. Both SDKs retry with backoff and honor `retry-after`. TypeSafe warns these limits are moving without notice while GPU capacity lands.

**Billing is input-only.** Output tokens are free. This is why speculative fan-out is cheap and why adding options to a `Choice` costs almost nothing.

**Input is text only.** No images, audio, or video. Pre-process non-text inputs into text or structured fields first. See [usecases/09-browser-and-computer-use.md](../usecases/09-browser-and-computer-use.md) for how projects handle this with OCR and classical CV.

**There is an official agent skill** if you build with a coding agent:

```bash
claude plugin marketplace add typesafe-ai/skills
claude plugin install typesafe@typesafe-ai
# or, for other agents:
npx skills add typesafe-ai/skills --skill typesafe-ai
```

## Next

- [how-to-use-jev-effectively.md](how-to-use-jev-effectively.md) - the design method in seven steps
- [patterns.md](patterns.md) - five architectures worth stealing
- [failure-modes.md](failure-modes.md) - read this before you ship
