"""
Example 2 - Speculative fan-out and composite scoring.

Shows two patterns in one pipeline:

  * fan-out  - ask branch questions that are only meaningful on some paths,
               because the marginal question costs tokens but no time
  * composite - score a fuzzy judgment on independent dimensions and combine
               them with weights you control

Run:
    python 02_composite_and_fanout.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, banner, choice, noul, score, show


def handle(message, client):
    response = client.system_one(
        state={"message": message},
        questions={
            # --- primary classification ---
            "category": choice(
                instructions="Broad category of this ticket",
                criteria={
                    "bug_report": "Something is broken or erroring",
                    "billing": "Charges, invoices, refunds",
                    "feature_request": "Asking for new functionality",
                    "account": "Login, permissions, security",
                    "other": "None of the above",
                },
            ),

            # --- only meaningful if category == bug_report. Ask anyway. ---
            "bug_severity": score(
                instructions="How severe is the reported issue?",
                criteria=["Cosmetic; no impact",
                          "Degraded feature; workaround exists",
                          "Blocking; no workaround"],
            ),
            "has_repro": noul("Does the user describe steps to reproduce?"),

            # --- only meaningful if category == billing. Ask anyway. ---
            "refund_wanted": noul(
                "Does the user explicitly ask for a refund or credit?"
            ),

            # --- always meaningful ---
            "frustration": score(
                instructions="How frustrated does the user appear?",
                criteria=["Calm", "Frustrated but civil", "Very angry"],
            ),
        },
    )
    return response.answers


def score_candidate(profile, client):
    """Composite scoring: atomic dimensions, weights owned by code."""
    response = client.system_one(
        state=profile,
        questions={
            "python_depth": score(
                instructions="Depth of Python experience shown",
                criteria=["None mentioned", "Mentioned, no detail",
                          "Used in projects", "Primary language",
                          "Deep expertise: architecture, performance"],
            ),
            "team_leadership": score(
                instructions="Experience leading engineering teams",
                criteria=["None", "Informal mentorship", "Led a small team",
                          "Managed direct reports", "Managed multiple teams"],
            ),
            "system_design": score(
                instructions="Experience designing distributed systems",
                criteria=["None mentioned", "Contributed to discussions",
                          "Designed components", "Owned a system's architecture",
                          "Designed at scale across domains"],
            ),
        },
    )
    a = response.answers

    # Re-weighting is a code change, not a re-prompt. You can A/B this.
    WEIGHTS = {"python_depth": 0.40, "team_leadership": 0.25, "system_design": 0.35}
    MAX_LEVEL = 4.0

    composite = sum(
        WEIGHTS[name] * (a[name].score / MAX_LEVEL) for name in WEIGHTS
    )
    return composite, a


def main():
    client = ExampleClient()
    banner("Example 2: Speculative fan-out and composite scoring", client.mode)

    # ---------------------------------------------------------------- fan-out
    message = ("The export button throws a 500 every time I click it. "
               "Steps: open Reports, pick Q3, click Export. "
               "I've tried three times, this is blocking my month-end close.")

    print("\n--- Speculative fan-out ---\n")
    answers = handle(message, client)
    show(answers)

    category = answers["category"]

    print("\nBranching on the primary answer, reading only what matters:\n")
    if category.confidence < 0.6:
        print("  -> human_review (low confidence)")
    elif category.choice == "bug_report":
        # bug_severity and has_repro were only meaningful here,
        # but cost almost nothing to ask upfront.
        sev, repro = answers["bug_severity"], answers["has_repro"]
        if sev.score > 1.5 and repro.noul > 0.6:
            print(f"  -> escalate_to_engineering(severity=high, "
                  f"severity_score={sev.score:.2f}, repro_p={repro.noul:.2f})")
        else:
            print("  -> add_to_bug_backlog")
    elif category.choice == "billing" and answers["refund_wanted"].noul > 0.7:
        print("  -> start_refund_flow")
    else:
        print(f"  -> route_standard({category.choice})")

    print("\n  Note: 5 questions were asked, 2 were used. That is the trade -")
    print("  speculative questions cost tokens ($0.042/MTok) and no wall time.")

    # ------------------------------------------------------------- composite
    profile = {
        "resume": ("Senior backend engineer, 8 years. Python is my primary "
                   "language; I've led the architecture for two services "
                   "handling ~50k rps. Managed a team of 5 engineers for "
                   "the last 3 years and mentored 2 juniors to mid-level."),
    }

    print("\n\n--- Composite scoring ---\n")
    composite, a = score_candidate(profile, client)
    show(a)
    print(f"\n  composite (0..1) = {composite:.3f}")
    print("  weights: python_depth=0.40, team_leadership=0.25, system_design=0.35")
    print("\n  Note: each dimension is scored separately, so you can see WHICH")
    print("  dimension is weak and re-weight without re-prompting.")


if __name__ == "__main__":
    main()
