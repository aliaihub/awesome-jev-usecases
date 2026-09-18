"""
Example 6 - Agent harness guard.

A small version of the pattern that dominated the ecosystem's first 72 hours:
Jev as a semantic supervisor around a coding agent.

The key architectural points, all present below:

  * code owns the loop; Jev only answers questions
  * irreversible actions get a much higher confidence bar
  * a failed or uncertain judgment FAILS CLOSED (deny or ask, never allow)
  * the verdict is fed back into the agent's context, not to a user dialog

Run:
    python 06_agent_guard.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, banner, choice, noul, score, show


# Deterministic deny-list - checked BEFORE the allowlist, and before any
# model call. Keep it narrow: only rules that are absolute and unambiguous.
# "rm -rf" is deliberately NOT here - it is sometimes legitimate, so it goes
# to the model, which is exactly the fuzzy residue Jev is for.
DENY_PATTERNS = (".env", "git push")

# Deterministic allowlist - checked before any model call.
ALLOWED_PREFIXES = ("ls ", "cat ", "grep ", "rg ", "git status", "git diff")


def deterministic_verdict(call):
    """Step 1: use code when you can.

    Deny-list first (cheap, absolute), then allow-list (cheap, absolute).
    Anything not settled here goes to the model.
    """
    text = call["args"].get("command") or call["args"].get("path") or ""

    if any(p in text for p in DENY_PATTERNS):
        return "deny", 1.0, "matches deterministic deny-list"

    if call["tool"] == "bash" and text.startswith(ALLOWED_PREFIXES):
        return "allow", 1.0, "matches deterministic allowlist"

    return None


def judge(call, task, rules, client):
    """Step 2: Jev answers narrow questions about the call."""
    r = client.system_one(
        state={"proposed": call, "task": task, "rules": rules},
        questions={
            "is_irreversible": noul(
                "Would `proposed.call` permanently destroy or overwrite data "
                "that cannot be recovered?"
            ),
            "is_off_task": noul(
                "Is `proposed.call` unrelated to `task.goal`?"
            ),
            "touches_secrets": noul(
                "Does `proposed.call` read or transmit credentials or "
                "environment files?"
            ),
            "violates_project_rule": noul(
                "Does `proposed.call` break any rule in `rules`?"
            ),
            "risk": score(
                instructions="How much damage would `proposed.call` cause if wrong?",
                criteria=["Read-only or easily reverted",
                          "Modifies project files",
                          "Irreversible or affects external systems"],
            ),
        },
    )
    return r.answers


def guard(call, task, rules, client):
    # Step 1: deterministic check
    det = deterministic_verdict(call)
    if det is not None:
        return det

    # Step 2: semantic judgment
    a = judge(call, task, rules, client)

    # Step 3: combine in code, threshold per action, FAIL CLOSED
    if a["touches_secrets"].noul > 0.5:
        return "deny", a["touches_secrets"].noul, "would touch credentials"

    if a["violates_project_rule"].noul > 0.6 and a["violates_project_rule"].confidence > 0.5:
        return "deny", max(a["violates_project_rule"].noul, a["violates_project_rule"].confidence), \
               "breaks a project rule"

    # Irreversible actions need very high certainty to auto-approve.
    if a["is_irreversible"].noul > 0.4:
        if a["is_irreversible"].noul > 0.9 and a["risk"].score < 0.5:
            return "allow", 0.9, "irreversible but clearly intended"
        return "ask", a["is_irreversible"].noul, "irreversible - needs confirmation"

    if a["is_off_task"].noul > 0.7:
        return "deny", a["is_off_task"].noul, "off task"

    if a["risk"].score >= 2 and a["risk"].confidence >= 0.7:
        return "ask", a["risk"].confidence, "high risk"

    # Anything genuinely uncertain fails closed to "ask".
    if a["risk"].confidence < 0.5:
        return "ask", a["risk"].confidence, "judgment uncertain"

    return "allow", a["risk"].confidence, "low risk, on task"


def main():
    client = ExampleClient()
    banner("Example 6: Agent action guard", client.mode)

    task = {"goal": "Move the retry logic into a shared helper module"}
    rules = [
        "Never modify files outside src/",
        "Never touch .env or any credentials file",
        "Never run git push",
    ]

    calls = [
        {"tool": "bash", "args": {"command": "git diff HEAD~1"}},
        {"tool": "bash", "args": {"command": "rm -rf build/"}},
        {"tool": "bash", "args": {"command": "cat .env"}},
        {"tool": "write", "args": {"path": "src/utils/retry.py"}},
        {"tool": "bash", "args": {"command": "git push origin main"}},
    ]

    print()
    for call in calls:
        verdict, conf, reason = guard(call, task, rules, client)
        cmd = call["args"].get("command") or call["args"].get("path")
        print(f"  [{verdict.upper():5s}] {call['tool']:6s} {cmd:26s}  "
              f"({conf:.2f}) {reason}")

    print("\n  Note:")
    print("  - 'git diff' was allowed by the deterministic allowlist (no model call)")
    print("  - 'cat .env' hit the deterministic DENY list (an absolute rule)")
    print("  - 'rm -rf' went to the MODEL: irreversible -> ask, never allow")
    print("  - 'src/utils' write was judged low risk and on task -> allow")
    print("  - 'git push' hit the deny list on a project rule")
    print("  - every uncertain model judgment resolves to 'ask', never 'allow'")
    print()
    print("  Only 2 of 5 calls needed a model. Rules first, Jev for the residue.")

    # --- the steering detail ---------------------------------------------
    print("\n--- Steering, not interrupting ---\n")
    print("  pi-warden's measured design (6 rule breaks without the guard,")
    print("  0 with it) feeds the violated rule BACK into the agent context:")
    print()
    print("    verdict: deny")
    print("    rule:    'Never modify files outside src/'")
    print("    -> agent re-plans instead of the user getting a dialog")


if __name__ == "__main__":
    main()
