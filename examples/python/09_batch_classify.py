"""
Example 9 - Classification at scale: batching with shared label criteria.

The rule: do not make one request per row. Pack rows into a shared state and
ask one question per row. The label criteria are sent ONCE and shared by every
question in the batch.

This is what makes the 50-million-row economics work.

Run:
    python 09_batch_classify.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, banner, choice


LABEL_CRITERIA = {
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
    "other": {"what": "None of the above"},
}

ROWS = [
    "I was charged twice for order A-104",
    "Where is my package?",
    "Cannot reset my password",
    "Refund the duplicate please",
    "Cancel order B-220",
    "Enable two-factor auth",
    "Invoice amount looks wrong",
    "Delivery is 3 weeks late",
    "Locked out of my account",
    "Why was I charged a subscription fee?",
    "Change my shipping address",
    "Delete my profile data",
]


def classify_batch(rows, label_criteria, client, batch_size=50):
    """Shared state, one question per row, one request per batch."""
    results = []

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]

        state = {
            "labels": label_criteria,   # sent once, shared by every question
            "rows": batch,
        }
        questions = {
            f"row_{j}": choice(
                instructions=f"Which label applies to `rows[{j}]`?",
                criteria=label_criteria,
            )
            for j in range(len(batch))
        }

        r = client.system_one(state=state, questions=questions)

        for j, row in enumerate(batch):
            a = r.answers[f"row_{j}"]
            results.append({
                "row": row,
                "label": a.choice,
                "confidence": a.confidence,
                "probabilities": a.probabilities,
            })

    return results


def main():
    client = ExampleClient()
    banner("Example 9: Classification at scale (batched)", client.mode)

    print(f"\n  rows: {len(ROWS)}   label criteria sent once, shared across rows\n")

    t0 = time.perf_counter()
    results = classify_batch(ROWS, LABEL_CRITERIA, client)
    elapsed = time.perf_counter() - t0

    print("    row                              label      conf")
    print("    ------------------------------   --------   ----")
    for r in results:
        print(f"    {r['row'][:30]:30s}   {r['label']:<8s}   {r['confidence']:.2f}")

    # --- keep the probabilities -------------------------------------------
    print("\n  One row's full distribution (store these, do not discard them):\n")
    sample = results[0]
    print(f"    row: {sample['row']}")
    for label, p in sorted(sample["probabilities"].items(), key=lambda kv: -kv[1]):
        bar = "#" * int(p * 40)
        print(f"    {label:<8s} {p:>5.3f}  {bar}")

    # --- cost planning ----------------------------------------------------
    print("\n  --- cost planning ---\n")
    # Assume ~150 input tokens per row including amortized label criteria.
    # MEASURE YOUR OWN - options, criteria length and state shape all move this.
    TOKENS_PER_ROW = 150
    PRICE_PER_MTOK = 0.042

    print("    rows        approx cost")
    print("    ---------   -----------")
    for n in [10_000, 100_000, 1_000_000, 10_000_000]:
        cost = n * TOKENS_PER_ROW / 1_000_000 * PRICE_PER_MTOK
        print(f"    {n:>9,d}   ${cost:>8.2f}")

    print(f"\n    (assumes {TOKENS_PER_ROW} input tokens/row at "
          f"${PRICE_PER_MTOK}/MTok)")
    print("    Verify with your own token counts before planning a budget.")

    print(f"\n  {len(ROWS)} rows classified in {elapsed:.2f}s "
          f"({len(ROWS)/max(elapsed,1e-6):.0f} rows/s in mock mode)")
    print("\n  Note: the marginal question is nearly free in wall time because")
    print("  all questions are evaluated in parallel over the same state.")


if __name__ == "__main__":
    main()
