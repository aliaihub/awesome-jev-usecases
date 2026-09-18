"""
Shared helpers for the Jev examples in this directory.

Every example runs in one of two modes:

  * live  - calls the real TypeSafe API (requires TYPESAFE_API_KEY)
  * mock  - returns deterministic fixture answers, so you can run and read
            the examples without an API key

Set JEV_EXAMPLE_MODE=live to force live, =mock to force mock. Default is
live if TYPESAFE_API_KEY is set, otherwise mock.

The mock is deliberately simple: it answers from a small table keyed on the
question name. Its purpose is to let the surrounding *code* be read and run,
not to simulate model quality.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any


# --------------------------------------------------------------------------
# Answer types - these mirror the shape of the real SDK's responses.
# --------------------------------------------------------------------------


@dataclass
class Answer:
    """One typed answer from Jev."""
    kind: str                      # "choice" | "score" | "noul"
    choice: str | None = None
    score: float | None = None
    noul: float | None = None
    probabilities: dict[str, float] = field(default_factory=dict)
    confidence: float = 1.0

    def __repr__(self) -> str:
        if self.kind == "choice":
            return f"<choice={self.choice!r} conf={self.confidence:.2f}>"
        if self.kind == "score":
            return f"<score={self.score:.2f} conf={self.confidence:.2f}>"
        return f"<noul={self.noul:.2f}>"


@dataclass
class Response:
    answers: dict[str, Answer]
    model: str = "mock"


# --------------------------------------------------------------------------
# Question builders - thin wrappers so examples read the same in both modes.
# --------------------------------------------------------------------------


def choice(instructions: Any, criteria: dict[str, Any]) -> dict:
    return {"kind": "choice", "instructions": instructions, "criteria": criteria}


def score(instructions: Any, criteria: list[Any]) -> dict:
    return {"kind": "score", "instructions": instructions, "criteria": criteria}


def noul(instructions: Any) -> dict:
    return {"kind": "noul", "instructions": instructions}


# --------------------------------------------------------------------------
# Mock: a small keyword heuristic so the examples demonstrate the intended
# behaviour without an API key.
# --------------------------------------------------------------------------
# This is NOT a model. It is a lookup table keyed on the text found in the
# state, existing only so the surrounding code is readable and runnable.
# In live mode this entire section is bypassed.

KEYWORD_RULES: list[tuple[str, str, Any]] = [
    # (substring found in state text, question name, value)
    ("charged twice", "topic", "billing"),
    ("refund", "topic", "billing"),
    ("invoice", "topic", "billing"),
    ("subscription fee", "topic", "billing"),
    ("where is my", "topic", "orders"),
    ("delivery", "topic", "orders"),
    ("cancel", "topic", "orders"),
    ("shipping", "topic", "orders"),
    ("package", "topic", "orders"),
    ("order", "topic", "orders"),
    ("password", "topic", "account"),
    ("sign in", "topic", "account"),
    ("locked out", "topic", "account"),
    ("two-factor", "topic", "account"),
    ("delete my", "topic", "account"),
    ("profile", "topic", "account"),

    # cascade intent (example 04)
    ("where is my", "intent", "order_status"),
    ("order a-104", "intent", "order_status"),
    ("order status", "intent", "order_status"),
    ("support sso", "intent", "product_question"),
    ("does the pro plan", "intent", "product_question"),
    ("return these", "intent", "return_exchange"),
    ("wrong size", "intent", "return_exchange"),
    ("unacceptable", "intent", "complaint"),
    ("third time contacting", "intent", "complaint"),

    ("charged twice", "department", "billing"),
    ("refund", "department", "billing"),
    ("invoice", "department", "billing"),
    ("where is my", "department", "orders"),
    ("delivery", "department", "orders"),
    ("reset my password", "department", "account"),

    # detection - SPECIFIC needles first, generic ones later
    ("confirm your payroll password", "requests_credentials", 0.93),
    ("claim your", "requests_credentials", 0.88),
    ("selected for", "offers_unexpected_reward", 0.84),
    ("bonus", "offers_unexpected_reward", 0.89),
    ("claim-bonus.example", "sender_identity_mismatch", 0.87),
    ("claim-bonus.example", "link_domain_mismatch", 0.83),
    ("urgent", "creates_time_pressure", 0.81),
    ("charged twice", "refund_requested", 0.91),
    ("refund the duplicate", "refund_requested", 0.94),
    ("please refund", "refund_requested", 0.88),
    ("a-104", "mentions_open_order", 0.88),
    ("a-104", "refund_wanted", 0.83),
    ("northwind", "vendor_is_known", 0.96),
    ("$", "currency", "usd"),
    ("14 march 2026", "date_month", "march"),
    ("14 march 2026", "date_day", "14"),
    ("14 march 2026", "date_year", "2026"),
    ("500", "category", "bug_report"),
    ("blocking", "category", "bug_report"),
    ("blocking", "bug_severity", 2.0),
    ("steps:", "has_repro", 0.91),
    ("steps:", "bug_severity", 2.0),
    ("export button", "category", "bug_report"),
    ("reset my password", "topic", "account"),
    ("reset my password", "requests_credentials", 0.03),

    # retrieval
    ("randomised, double-blind", "is_rct", 0.94),
    ("randomised controlled trial", "is_rct", 0.91),
    ("major adverse cardiovascular", "reports_mace", 0.93),
    ("major adverse cardiovascular", "evidence_strength", 2.0),
    ("narrative review", "is_rct", 0.03),
    ("narrative review", "evidence_strength", 0.4),
    ("mice", "is_rct", 0.05),
    ("preclinical", "evidence_strength", 0.2),
    ("narrative review", "document_contains_answer", 0.14),
    ("narrative review", "answers_question", 0.11),
    ("narrative review", "relevance", 0.5),
    ("randomised, double-blind", "document_contains_answer", 0.93),

    # guard / agent - needles chosen so they appear ONLY in the proposed
    # call, never in the rules text that is also part of the state.
    ("rm -rf", "is_irreversible", 0.94),
    ("rm -rf", "risk", 2.6),
    ("git push origin", "is_irreversible", 0.71),
    ("git push origin", "risk", 1.8),
    ("git push origin", "violates_project_rule", 0.94),
    ("cat .env", "touches_secrets", 0.92),
    ("cat .env", "risk", 2.4),
    ("cat .env", "violates_project_rule", 0.88),
    ("src/utils", "risk", 0.3),
    ("src/utils", "is_off_task", 0.05),
    ("src/utils", "is_irreversible", 0.04),
    ("git diff head", "risk", 0.2),

    # review / agent claims
    ("no test", "tests_actually_ran", 0.11),
    ("no test", "claim_is_evidenced", 0.13),
    ("tests pass", "tests_actually_ran", 0.94),

    # recruiter / composite
    ("python is my primary", "python_depth", 3.4),
    ("primary language", "python_depth", 3.2),
    ("managed a team of 5", "team_leadership", 3.1),
    ("mentored", "team_leadership", 2.2),
    ("50k rps", "system_design", 3.3),
    ("architecture for two services", "system_design", 3.0),

    # generic label questions (examples 08 and 09)
    ("charged twice", "label", "billing"),
    ("refund", "label", "billing"),
    ("invoice", "label", "billing"),
    ("subscription fee", "label", "billing"),
    ("duplicate", "label", "billing"),
    ("where is my", "label", "orders"),
    ("delivery", "label", "orders"),
    ("cancel", "label", "orders"),
    ("package", "label", "orders"),
    ("shipping", "label", "orders"),
    ("order b-220", "label", "orders"),
    ("password", "label", "account"),
    ("sign in", "label", "account"),
    ("locked out", "label", "account"),
    ("two-factor", "label", "account"),
    ("delete my", "label", "account"),
    ("profile", "label", "account"),
]


def _state_text(state: Any) -> str:
    """Flatten the state into lowercase text for the keyword heuristics."""
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, str):
            parts.append(node)
        elif isinstance(node, dict):
            for k, v in node.items():
                parts.append(str(k))
                walk(v)
        elif isinstance(node, (list, tuple)):
            for item in node:
                walk(item)
        elif node is not None:
            parts.append(str(node))

    walk(state)
    return " ".join(parts).lower()


def _mock_lookup(name: str, state_text: str) -> Any:
    """Find the first keyword rule matching this question name + state."""
    # Batched questions ("row_3") are judged on the row text, which is the
    # state_text passed in - fall through to the generic "label" rules.
    lookup_name = "label" if re.fullmatch(r"row_\d+", name) else name
    for needle, qname, value in KEYWORD_RULES:
        if qname == lookup_name and needle in state_text:
            return value
    return None

def _mock_answer(name: str, spec: dict, state_text: str = "") -> Answer:
    value = _mock_lookup(name, state_text)

    # Sensible fallbacks when no keyword rule fires.
    if value is None:
        if spec["kind"] == "noul":
            value = 0.12 if not name.startswith("is_") else 0.08
        elif spec["kind"] == "score":
            value = 1.0
        else:
            value = 0.5  # handled below: pick the first option

    conf = CONFIDENCE_OVERRIDE.get(name)
    if conf is None:
        for needle, qname, c_val in CONFIDENCE_RULES:
            if qname in (name, "label") and re.fullmatch(r"row_\d+", name):
                if needle in state_text:
                    conf = c_val
                    break
            elif qname == name and needle in state_text:
                conf = c_val
                break
    if conf is None:
        conf = 0.86 if value is not None else 0.5

    # Noul answers are probabilities - the value IS the answer.
    if spec["kind"] == "noul" and isinstance(value, (int, float)) and 0 <= value <= 1:
        return Answer(kind="noul", noul=float(value))

    kind = spec["kind"]

    if kind == "choice":
        options = list(spec["criteria"].keys())
        chosen = value if value in options else options[0]
        # Spread a little probability mass over the other options.
        probs = {o: round(0.02, 3) for o in options}
        probs[chosen] = 0.9
        total = sum(probs.values())
        probs = {k: round(v / total, 3) for k, v in probs.items()}
        return Answer(kind="choice", choice=chosen, probabilities=probs,
                      confidence=conf if conf is not None else 0.9)

    if kind == "score":
        n = len(spec["criteria"])
        s = float(value) if value is not None else 0.0
        return Answer(kind="score", score=max(0.0, min(float(n - 1), s)),
                      confidence=conf if conf is not None else 0.75)

    return Answer(kind="noul", noul=float(value) if value is not None else 0.5)


def set_fixture(name: str, value: Any) -> None:
    """Override a mock answer. Used by the evaluation example."""
    KEYWORD_RULES.insert(0, ("", name, value))


# Optional per-row confidence, keyed the same way as KEYWORD_RULES.
CONFIDENCE_RULES: list[tuple[str, str, float]] = []
CONFIDENCE_OVERRIDE: dict[str, float] = {}


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------


class ExampleClient:
    """A Jev client that works in both live and mock mode."""

    def __init__(self, model: str | None = None) -> None:
        forced = os.environ.get("JEV_EXAMPLE_MODE", "").strip().lower()
        has_key = bool(os.environ.get("TYPESAFE_API_KEY"))

        if forced == "mock":
            self.mode = "mock"
        elif forced == "live":
            if not has_key:
                sys.exit("JEV_EXAMPLE_MODE=live but TYPESAFE_API_KEY is not set.")
            self.mode = "live"
        else:
            self.mode = "live" if has_key else "mock"

        self.model = model or "jev-latest"
        self._client = None
        if self.mode == "live":
            from typesafe_sdk import TypeSafeClient  # imported lazily
            self._client = TypeSafeClient(model=self.model)

    def system_one(self, state: Any, questions: dict[str, dict]) -> Response:
        if self.mode == "mock":
            answers = {}
            for name, spec in questions.items():
                # Batched questions ("row_3") must be judged against that row
                # ALONE. The shared label criteria in the state would otherwise
                # match every row.
                m = re.fullmatch(r"row_(\d+)", name)
                if m and isinstance(state, dict) and "rows" in state:
                    idx = int(m.group(1))
                    rows = state["rows"]
                    text = _state_text(rows[idx]) if idx < len(rows) else ""
                else:
                    text = _state_text(state)
                answers[name] = _mock_answer(name, spec, text)
            return Response(answers=answers, model="mock")
        return self._live(state, questions)

    # -- live path ---------------------------------------------------------

    def _live(self, state: Any, questions: dict[str, dict]) -> Response:
        from typesafe_sdk import Choice, Noul, Score

        built = {}
        for name, spec in questions.items():
            if spec["kind"] == "choice":
                built[name] = Choice(instructions=spec["instructions"],
                                     criteria=spec["criteria"])
            elif spec["kind"] == "score":
                built[name] = Score(instructions=spec["instructions"],
                                    criteria=spec["criteria"])
            else:
                built[name] = Noul(instructions=spec["instructions"])

        raw = self._client.system_one(state=state, questions=built)

        answers: dict[str, Answer] = {}
        for name, spec in questions.items():
            r = raw.answers[name]
            if spec["kind"] == "choice":
                answers[name] = Answer(
                    kind="choice", choice=r.choice,
                    probabilities=dict(getattr(r, "probabilities", {}) or {}),
                    confidence=r.confidence)
            elif spec["kind"] == "score":
                answers[name] = Answer(
                    kind="score", score=float(r.score),
                    confidence=getattr(r, "confidence", 1.0))
            else:
                answers[name] = Answer(kind="noul", noul=float(r.noul))

        return Response(answers=answers,
                        model=getattr(raw, "model", self.model))


# --------------------------------------------------------------------------
# Presentation helpers
# --------------------------------------------------------------------------


def banner(title: str, mode: str) -> None:
    print("=" * 72)
    print(f"  {title}")
    print(f"  mode: {mode}")
    print("=" * 72)


def show(answers: dict[str, Answer], only: list[str] | None = None) -> None:
    for name, a in answers.items():
        if only and name not in only:
            continue
        if a.kind == "choice":
            print(f"  {name:28s} {a.choice:<14s} conf={a.confidence:.2f}")
        elif a.kind == "score":
            print(f"  {name:28s} {a.score:<14.2f} conf={a.confidence:.2f}")
        else:
            print(f"  {name:28s} p={a.noul:<13.2f}")
