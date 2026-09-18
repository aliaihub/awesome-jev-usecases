"""
Example 8 - Evaluating Jev on your own data.

This is the example to actually run against your traffic. It measures the two
things that decide your architecture:

  * selective risk - accuracy at and above each confidence threshold, with
    the coverage at that threshold. This answers "what can I automate?"
  * calibration    - whether a stated probability matches the observed rate.

It also reports a Brier score, and it works on mock data so you can see the
output shape before you have an API key.

Run:
    python 08_evaluate.py
"""

import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, Answer, banner, choice


# A small labelled set. Replace this with your own decisions and outcomes.
LABELLED = [
    {"text": "I was charged twice for order A-104", "label": "billing"},
    {"text": "Where is my order?", "label": "orders"},
    {"text": "Cannot sign in after password reset", "label": "account"},
    {"text": "Need a refund for the duplicate charge", "label": "billing"},
    {"text": "Package still not delivered after 2 weeks", "label": "orders"},
    {"text": "Please delete my account", "label": "account"},
    {"text": "Invoice shows the wrong amount", "label": "billing"},
    {"text": "Cancel my shipment please", "label": "orders"},
    {"text": "Two-factor authentication not working", "label": "account"},
    {"text": "Duplicate charge on my statement", "label": "billing"},
]


def classify_all(examples, client):
    """One call per example. In production, batch these - see example 09."""
    records = []
    for ex in examples:
        r = client.system_one(
            state={"message": ex["text"]},
            questions={
                "label": choice(
                    instructions="Which team should handle this message?",
                    criteria={
                        "billing": "Charges, invoices, refunds",
                        "orders": "Order status, delivery, cancellation",
                        "account": "Login, profile, permissions",
                    },
                ),
            },
        )
        a = r.answers["label"]
        records.append({
            "predicted": a.choice,
            "confidence": a.confidence,
            "probabilities": a.probabilities,
            "actual": ex["label"],
            "correct": a.choice == ex["label"],
            "model": r.model,
        })
    return records


def report(records):
    n = len(records)
    acc = sum(r["correct"] for r in records) / n

    print(f"\n  n = {n}")
    print(f"  overall accuracy = {acc:.3f}")

    # --- selective risk: the measurement that decides architecture --------
    print("\n  Selective risk (accuracy at confidence >= t, with coverage):\n")
    print("    threshold   accuracy   coverage   automatable")
    print("    ---------   --------   --------   -----------")
    for t in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
        kept = [r for r in records if r["confidence"] >= t]
        if not kept:
            print(f"    {t:>8.2f}        -          -            -")
            continue
        cov = len(kept) / n
        acc_t = sum(r["correct"] for r in kept) / len(kept)
        flag = "yes" if acc_t >= 0.9 else "no"
        print(f"    {t:>8.2f}   {acc_t:>8.3f}   {cov:>8.2f}   {flag:>6s}")

    print("\n  Read this as: 'at threshold T, accuracy is A and I can automate C")
    print("  of traffic.' If accuracy rises with the threshold, confidence is")
    print("  informative and your gates can work. If it is flat, do not gate.")

    # --- calibration ------------------------------------------------------
    print("\n  Calibration (predicted vs observed):\n")
    buckets = defaultdict(list)
    for r in records:
        p = r["probabilities"].get(r["predicted"], r["confidence"])
        buckets[round(p, 1)].append(r["correct"])
    print("    predicted   observed   n")
    print("    ---------   --------   --")
    for b in sorted(buckets):
        obs = sum(buckets[b]) / len(buckets[b])
        print(f"    {b:>9.1f}   {obs:>8.2f}   {len(buckets[b]):>2d}")

    # --- Brier score ------------------------------------------------------
    brier = sum(
        (r["probabilities"].get(r["predicted"], r["confidence"]) - int(r["correct"])) ** 2
        for r in records
    ) / n
    print(f"\n  Brier score = {brier:.4f}   (0.25 = always predict 0.5; lower is better)")

    # --- the comparison everyone forgets ----------------------------------
    base_rate = max(sum(r["actual"] == c for r in records) / n
                    for c in {r["actual"] for r in records})
    const_brier = sum((base_rate - int(r["correct"])) ** 2 for r in records) / n
    print(f"  Constant-baseline Brier = {const_brier:.4f}  (predict the majority class)")
    print(f"  -> Jev {'beats' if brier < const_brier else 'does NOT beat'} the constant baseline")


def main():
    client = ExampleClient()
    banner("Example 8: Evaluating Jev on your own data", client.mode)

    if client.mode == "mock":
        # In mock mode, answer correctly but with a range of confidences so
        # the selective-risk table is meaningful. Two rows are deliberately
        # misclassified so a miss is visible in the report.
        import _client as c
        for i, ex in enumerate(LABELLED):
            predicted = "orders" if i in (3, 7) else ex["label"]
            conf = 0.72 + (i % 4) * 0.08
            key = ex["text"].lower()[:20]
            c.KEYWORD_RULES.insert(0, (key, "label", predicted))
            c.CONFIDENCE_RULES.insert(0, (key, "label", conf))

    records = classify_all(LABELLED, client)

    print("\n  Per-example results:\n")
    print("    predicted   conf   actual    ok")
    print("    ---------   ----   -------   --")
    for r in records:
        ok = "ok" if r["correct"] else "MISS"
        print(f"    {r['predicted']:<9s}   {r['confidence']:.2f}   "
              f"{r['actual']:<7s}   {ok}")

    print(f"\n  model that answered: {records[0]['model']}")

    report(records)

    print("\n  Before you ship a threshold, run this on a few hundred examples")
    print("  of YOUR traffic. See docs/evaluating-jev.md.")


if __name__ == "__main__":
    main()
