"""
Example 4 - The cascade.

Jev decides which requests deserve an expensive model. One branch never
touches a model at all, one branch is pure code, two load specialists, one
escalates to a human.

This is the pattern that saves money on a workflow you already run at volume.

Run:
    python 04_cascade.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, Answer, banner, choice, score, show


# Stand-ins for the downstream handlers. In a real system these would call
# specialist models or deterministic services.
def lookup_order(message):
    return "[code] looked up order status - no model call"


def handle_with_llm(message, persona):
    return f"[llm:{persona}] generated a reply"


def route_to_human(message):
    return "[human] routed to a person"


def handle(message, client):
    r = client.system_one(
        state={"message": message},
        questions={
            "intent": choice(
                instructions="Primary intent of this message",
                criteria={
                    "order_status": "Asking about an existing order",
                    "product_question": "Asking about a product",
                    "return_exchange": "Wants to return or exchange",
                    "complaint": "Unhappy, wants resolution",
                    "other": "None of the above",
                },
            ),
            "complexity": score(
                instructions="How complex is this to resolve?",
                criteria=["Simple lookup or standard procedure",
                          "Requires judgment or multiple steps",
                          "Unusual edge case, escalation needed"],
            ),
        },
    )
    intent, complexity = r.answers["intent"], r.answers["complexity"]

    # --- the cascade ---
    if intent.confidence < 0.5:
        return route_to_human(message), intent, complexity

    if intent.choice == "order_status":
        # pure code, no model at all
        return lookup_order(message), intent, complexity

    if intent.choice == "product_question":
        return handle_with_llm(message, "PRODUCT_SPECIALIST"), intent, complexity

    if intent.choice == "return_exchange":
        return handle_with_llm(message, "RETURNS_SPECIALIST"), intent, complexity

    if intent.choice == "complaint":
        if complexity.score > 1 or complexity.confidence < 0.5:
            return route_to_human(message), intent, complexity
        return handle_with_llm(message, "COMPLAINT_RESOLUTION"), intent, complexity

    return route_to_human(message), intent, complexity


def expected_cost(tiers, n=1_000_000):
    """Rough cost model using TypeSafe's reported per-case figures."""
    per_case = {"jev": 0.0004, "llm": 0.0304, "human": 3.00}
    return sum(tiers.get(k, 0) * per_case[k] * n for k in per_case)


def main():
    client = ExampleClient()
    banner("Example 4: The cascade", client.mode)

    examples = [
        "Where is my order A-104?",
        "Does the Pro plan support SSO?",
        "I want to return these boots, wrong size.",
        "Third time contacting you. This is unacceptable and I want it fixed.",
    ]

    for message in examples:
        result, intent, complexity = handle(message, client)
        print(f"\n  message   : {message[:58]}")
        print(f"  intent    : {intent.choice} (conf {intent.confidence:.2f})")
        print(f"  complexity: {complexity.score:.2f}")
        print(f"  -> {result}")

    print("\n\nCost shape on 1,000,000 tickets (using TypeSafe's per-case figures):")
    print("  all-to-frontier-LLM : $%.0f" % expected_cost({"llm": 1.0}))
    print("  cascaded            : ~$6,480 (Jev on all, LLM on the minority)")
    print("\n  The saving comes from routing, not from making the model cheaper.")
    print("  One branch never touched a model at all.")


if __name__ == "__main__":
    main()
