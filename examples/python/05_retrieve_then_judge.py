"""
Example 5 - Retrieve, then judge.

The retrieval layer decides what Jev is allowed to know. Two rules matter:

  1. filter before the expensive context window
  2. ask a document-level question so the system can ABSTAIN

This example simulates a small paper screen - the shape used in the ecosystem
to screen 20 papers on four dimensions for well under a cent.

Run:
    python 05_retrieve_then_judge.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, banner, noul, score, show


PAPERS = [
    {
        "title": "Semaglutide and Cardiovascular Outcomes in Type 2 Diabetes",
        "year": 2024,
        "content": ("A randomised, double-blind, placebo-controlled trial of 3,297 "
                    "patients with type 2 diabetes and high cardiovascular risk. "
                    "The primary composite outcome of major adverse cardiovascular "
                    "events occurred in 6.6% of the semaglutide group vs 8.9% of "
                    "placebo (HR 0.74, 95% CI 0.58-0.95)."),
    },
    {
        "title": "GLP-1 Receptor Agonists: A Narrative Review",
        "year": 2023,
        "content": ("A narrative review summarising existing literature on GLP-1 "
                    "receptor agonists, their mechanisms, and clinical adoption. "
                    "No new experimental data is presented."),
    },
    {
        "title": "A Mouse Model of GLP-1 Signalling in Aortic Tissue",
        "year": 2025,
        "content": ("Preclinical study in C57BL/6 mice examining aortic expression "
                    "of GLP-1 receptor mRNA. No human participants."),
    },
]


def judge(paper, client):
    r = client.system_one(
        state={"title": paper["title"], "year": paper["year"],
               "content": paper["content"]},
        questions={
            "is_rct": noul("This paper reports a randomised controlled trial"),
            "reports_mace": noul(
                "The paper reports major adverse cardiovascular events as an outcome"
            ),
            "evidence_strength": score(
                instructions="How strong is the causal evidence presented?",
                criteria=["Anecdotal or preclinical",
                          "Observational",
                          "Single randomised trial",
                          "Meta-analysis of randomised trials"],
            ),
        },
    )
    return r.answers


def main():
    client = ExampleClient()
    banner("Example 5: Retrieve, then judge", client.mode)

    print("\nScreening %d candidate papers (in a real pipeline: 20+).\n" % len(PAPERS))

    shortlist = []
    for paper in PAPERS:
        a = judge(paper, client)
        keep = a["is_rct"].noul > 0.7 and a["evidence_strength"].score > 1.5
        mark = "KEEP" if keep else "drop"
        print(f"  [{mark}] {paper['title'][:60]}")
        print(f"         is_rct={a['is_rct'].noul:.2f}  "
              f"reports_mace={a['reports_mace'].noul:.2f}  "
              f"evidence={a['evidence_strength'].score:.2f}")
        if keep:
            shortlist.append((paper, a["evidence_strength"].confidence))

    print(f"\n  shortlist: {len(shortlist)} of {len(PAPERS)}")

    # --- the abstain path -------------------------------------------------
    print("\n--- The abstain path ---\n")
    print("  A retrieval system that cannot say 'not here' always returns")
    print("  the least-bad passage. Add a document-level question:\n")

    r = client.system_one(
        state={"document": PAPERS[1]["content"],
               "question": "Does semaglutide reduce cardiovascular events?"},
        questions={
            "document_contains_answer": noul(
                "Does `document` contain an answer to `question`?"
            ),
        },
    )
    p = r.answers["document_contains_answer"].noul
    print(f"  document_contains_answer = {p:.2f}")
    print(f"  -> {'answer from this document' if p > 0.6 else 'NOT FOUND - do not fabricate'}")

    print("\n  Note the ordering: filter BEFORE the expensive context window,")
    print("  and never let the least-bad passage win by default.")


if __name__ == "__main__":
    main()
