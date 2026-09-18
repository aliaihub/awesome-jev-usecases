# Examples

Nine runnable Python examples, one per pattern or use-case family. They run in **mock mode** by default if you have no API key, so you can read and run them immediately.

```bash
cd examples/python
python 01_routing_triage.py
```

**Live mode** requires a TypeSafe API key:

```bash
export TYPESAFE_API_KEY="sk-..."
python 01_routing_triage.py # auto-detects the key and goes live
JEV_EXAMPLE_MODE=mock python 01_routing_triage.py # force mock
```

| # | Example | Teaches |
| --- | --- | --- |
| 01 | [routing_triage.py](python/01_routing_triage.py) | Atomic questions, one call, confidence gates |
| 02 | [composite_and_fanout.py](python/02_composite_and_fanout.py) | Speculative fan-out + composite scoring |
| 03 | [spam_screening.py](python/03_spam_screening.py) | Decomposed detection, weighted combination |
| 04 | [cascade.py](python/04_cascade.py) | Jev decides which requests deserve an expensive model |
| 05 | [retrieve_then_judge.py](python/05_retrieve_then_judge.py) | Filter before the context window; the abstain path |
| 06 | [agent_guard.py](python/06_agent_guard.py) | Agent harness guard; fails closed; rule-based deny |
| 07 | [extraction.py](python/07_extraction.py) | Pick candidates, never generate; date parts as enums |
| 08 | [evaluate.py](python/08_evaluate.py) | Selective risk, calibration, Brier score on your data |
| 09 | [batch_classify.py](python/09_batch_classify.py) | Shared criteria, one question per row, cost planning |

## What the mock does

`_client.py` provides a tiny stand-in that answers from a fixture table keyed on the question name. It exists so the surrounding **code** - the part that matters - is readable and runnable without a key. It does not simulate model quality, and unmapped questions return an obvious placeholder.

## What to run first

- **If you are new to Jev:** `01`, then `02`.
- **If you already run agents:** `06`, then `03`.
- **If you are deciding whether to adopt Jev:** `08` - it prints the selective-risk table that answers "what can I automate?".

## Notes on the live path

The live path imports `typesafe_sdk` lazily, so mock mode does not require the SDK installed. The SDK call shapes used here:

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient() # reads TYPESAFE_API_KEY, defaults to jev-latest
response = client.system_one(state=..., questions={...})
```

If the real SDK's signatures have moved since this was written, the mock mode still runs and the structure still reads correctly. Check [docs.typesafe.ai/sdk/python](https://docs.typesafe.ai/sdk/python) for the current API.

**Pin the model version if you tune thresholds.** `jev-latest` moves. Pass `model="jev-1.13.0"` and log the `model` field from every response.
