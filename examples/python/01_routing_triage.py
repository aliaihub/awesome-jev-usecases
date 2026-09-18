"""
Example 1 - Routing and triage.

Shows the canonical first Jev use case: four atomic questions in ONE call,
combined in code with explicit confidence gates.

Run:
    python 01_routing_triage.py

Works without an API key (mock mode). Set TYPESAFE_API_KEY for live mode.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, banner, choice, noul, score, show


def triage(ticket, customer, client):
    # STEP 1: use code when you can. A closed ticket needs no model call.
    if ticket["status"] == "closed":
        return "no_action", {}

    # Only the fields the questions actually need.
    open_orders = [o for o in customer["orders"] if o["status"] != "delivered"]
    state = {
        "ticket": {
            "message": ticket["message"],
            "sender": ticket["sender"],
            "links": ticket["links"],
        },
        "customer": {"plan": customer["plan"], "open_orders": open_orders},
        "policy": {"sensitive_credentials": ["password", "security code", "API key"]},
    }

    # STEP 2-4: atomic, literal, structured questions. One call.
    questions = {
        "topic": choice(
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
                "other": {"what": "Does not fit any of the above"},
            },
        ),
        # Branch conditions. Only meaningful on one path - ask them anyway.
        "refund_requested": noul(
            "Does the customer explicitly request a refund or credit?"
        ),
        "mentions_open_order": noul(
            "Does the message refer to a supplied open order?"
        ),
        # Safety, checked on every ticket.
        "requests_credentials": noul(
            "Does `ticket.message` ask the recipient to disclose a password, "
            "security code, or API key from `policy.sensitive_credentials`?"
        ),
        "sender_identity_mismatch": noul(
            "Does `ticket.sender.display_name` conflict with the domain in "
            "`ticket.sender.email`?"
        ),
        # Degree, scored on a rubric.
        "frustration": score(
            instructions={
                "question": "How frustrated does the customer appear?",
                "focus": "Judge expressed frustration, not issue severity.",
            },
            criteria=[
                {"what": "Calm and matter-of-fact",
                 "signals": ["Neutral wording", "No complaint"]},
                {"what": "Frustrated but civil",
                 "signals": ["Expresses annoyance", "Remains constructive"]},
                {"what": "Very angry or threatening to leave",
                 "signals": ["Hostile language", "Threatens cancellation"]},
            ],
        ),
    }

    response = client.system_one(state=state, questions=questions)
    a = response.answers

    # STEP 5: combine in code. Thresholds are yours, and they are visible.
    if a["requests_credentials"].noul > 0.7:
        return "quarantine_phishing", a

    if a["sender_identity_mismatch"].noul > 0.8:
        return "quarantine_spoofed_sender", a

    if a["topic"].confidence < 0.75:
        return "human_review", a

    if a["topic"].choice == "billing" and a["refund_requested"].noul > 0.7:
        return "billing_refund_queue", a

    if a["topic"].choice == "orders" and a["mentions_open_order"].noul > 0.7:
        return "orders_priority_queue", a

    if a["frustration"].confidence >= 0.7 and a["frustration"].score >= 1.5:
        return f"{a['topic'].choice}_priority_queue", a

    return f"{a['topic'].choice}_standard_queue", a


def main():
    client = ExampleClient()
    banner("Example 1: Routing and triage", client.mode)

    ticket = {
        "status": "open",
        "message": ("I was charged twice for order A-104 this month. "
                    "Please refund the duplicate charge."),
        "sender": {"display_name": "Jamie Ortiz", "email": "jamie@example.com"},
        "links": [],
    }
    customer = {
        "plan": "pro",
        "orders": [{"id": "A-104", "status": "shipped"}],
    }

    route, answers = triage(ticket, customer, client)

    print("\nState sent:\n")
    print(f"  ticket.message  : {ticket['message'][:64]}...")
    print(f"  customer.plan   : {customer['plan']}")
    print(f"  open orders     : {[o['id'] for o in customer['orders']]}")

    print("\nAnswers (all from ONE request, evaluated in parallel):\n")
    show(answers)

    print(f"\nDecision: {route}")
    print("\nNote the shape:")
    print("  - 6 questions, 1 network call")
    print("  - safety checks run on every ticket, in parallel with routing")
    print("  - refund_requested was asked speculatively (only used on the billing path)")
    print("  - the decision is code, not the model's answer")


if __name__ == "__main__":
    main()
