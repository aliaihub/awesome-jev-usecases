"""
Example 3 - LLM guardrail: decomposed spam/phishing screening.

Shows the decompose-then-combine pattern for detection. Instead of one broad
question ("is this spam?"), ask one atomic question per hazard and combine the
probabilities with weights you own.

Run:
    python 03_spam_screening.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, banner, noul, show


def screen(message, credentials_policy, client):
    response = client.system_one(
        state={"message": message, "policy": credentials_policy},
        questions={
            "requests_credentials": noul(
                "Does `message.body` ask the recipient to provide a password "
                "or other login credential?"
            ),
            "offers_unexpected_reward": noul(
                "Does `message.body` claim the recipient received an unexpected "
                "prize, payment, or reward?"
            ),
            "creates_time_pressure": noul(
                "Does `message.subject` or `message.body` pressure the recipient "
                "to act quickly?"
            ),
            "sender_identity_mismatch": noul(
                "Does the organization in `message.sender.display_name` conflict "
                "with the domain in `message.sender.email`?"
            ),
            "link_domain_mismatch": noul(
                "Does the domain in `message.links[0].url` conflict with the "
                "organization in `message.sender.display_name`?"
            ),
            "disguises_link_destination": noul(
                "Does `message.links[0].text` conceal or misrepresent the "
                "destination in `message.links[0].url`?"
            ),
        },
    )
    return response.answers


def main():
    client = ExampleClient()
    banner("Example 3: Decomposed spam/phishing screening", client.mode)

    message = {
        "sender": {
            "display_name": "Acme Payroll",
            "email": "rewards@claim-bonus.example",
        },
        "subject": "Urgent: claim your employee bonus",
        "body": ("You have been selected for a $1,000 bonus. Confirm your payroll "
                 "password today to receive it."),
        "links": [{"text": "Claim bonus", "url": "http://claim-bonus.example/acme"}],
    }
    policy = {"sensitive_credentials": ["password", "security code", "API key"]}

    a = screen(message, policy, client)
    show(a)

    # Combine independent signals with weights owned by code.
    WEIGHTS = {
        "requests_credentials": 0.45,
        "sender_identity_mismatch": 0.30,
        "unexpected_reward": 0.25,
    }
    spam_risk = (
        WEIGHTS["requests_credentials"] * a["requests_credentials"].noul
        + WEIGHTS["sender_identity_mismatch"] * a["sender_identity_mismatch"].noul
        + WEIGHTS["unexpected_reward"] * a["offers_unexpected_reward"].noul
    )

    print(f"\n  spam_risk = {spam_risk:.3f}")
    print("    = 0.45*requests_credentials + 0.30*sender_mismatch "
          "+ 0.25*unexpected_reward")

    # Escalate the uncertain band rather than guessing.
    if 0.4 < spam_risk < 0.6:
        decision = "human_review"
    elif spam_risk >= 0.6:
        decision = "quarantine_as_spam"
    else:
        decision = "deliver"

    print(f"\n  Decision: {decision}")
    print("\nWhy this beats one broad question:")
    print("  - you can see WHICH hazard fired, not just a score")
    print("  - you can re-weight without re-prompting")
    print("  - the uncertain band (0.4..0.6) is handled explicitly")
    print("  - the model never had to answer an unfalsifiable 'is this spam?'")


if __name__ == "__main__":
    main()
