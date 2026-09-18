"""
Example 7 - Structured extraction: pick candidates, never generate values.

Two rules that decide whether extraction works:

  1. Jev does not generate. Use a regex or a generative model to find
     candidates, then let Jev PICK the correct one.
  2. Jev does not do dates. Extract the PARTS as enums with a "not_stated"
     option; assemble and compare in code.

Run:
    python 07_extraction.py
"""

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _client import ExampleClient, banner, choice, noul, show


MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]

MONTH_NUM = {m: i + 1 for i, m in enumerate(MONTHS)}


def find_candidates(text):
    """Step 1: candidate generation - regex, not a model."""
    invoices = re.findall(r"\bINV-\d{4,6}\b", text)
    amounts = re.findall(r"\$[\d,]+\.\d{2}", text)
    return invoices, amounts


def extract(text, candidates, vendor_directory, client):
    invoices, amounts = candidates

    questions = {
        # Choice over the regex candidates, NOT a request to generate a value.
        "invoice_number": choice(
            instructions="Which candidate is the invoice number in `document.text`?",
            criteria={c: f"Candidate {c}" for c in invoices} | 
                     {"not_stated": "No invoice number is present"},
        ),
        "amount": choice(
            instructions="Which candidate is the total amount due?",
            criteria={c: f"Candidate {c}" for c in amounts} |
                     {"not_stated": "No amount is present"},
        ),
        "currency": choice(
            instructions="Which currency is the document in?",
            criteria={"usd": "US dollars", "eur": "Euros", "gbp": "Pounds sterling",
                      "other": "Some other currency", "not_stated": "Not specified"},
        ),
        # Verification against YOUR reference data, not model world knowledge.
        "vendor_is_known": noul(
            "Does `document.vendor_name` appear in `vendor_directory`?"
        ),
    }

    # --- date parts as enums; never ask for a date comparison ---------------
    questions["date_month"] = choice(
        instructions="Which month is stated in `document.text` as the invoice date?",
        criteria={m: m.capitalize() for m in MONTHS} |
                 {"not_stated": "No month is specified"},
    )
    questions["date_day"] = choice(
        instructions="Which day of the month is stated as the invoice date?",
        criteria={str(d): f"The {d}th" for d in range(1, 32)} |
                 {"not_stated": "No day is specified"},
    )
    questions["date_year"] = choice(
        instructions="Which year is stated as the invoice date?",
        criteria={str(y): str(y) for y in range(2024, 2031)} |
                 {"not_stated": "No year is specified"},
    )

    r = client.system_one(
        state={"document": {"text": text, "vendor_name": "Northwind Supply"},
               "vendor_directory": vendor_directory},
        questions=questions,
    )
    return r.answers


def main():
    client = ExampleClient()
    banner("Example 7: Structured extraction", client.mode)

    text = ("Invoice INV-48213 from Northwind Supply, dated 14 March 2026. "
            "Total amount due: $1,240.00. Payment terms net 30.")
    vendor_directory = ["Northwind Supply", "Acme Corp", "Globex"]

    invoices, amounts = find_candidates(text)
    print(f"\n  regex candidates: invoices={invoices} amounts={amounts}")

    a = extract(text, (invoices, amounts), vendor_directory, client)

    print("\n  selected fields:\n")
    show(a, only=["invoice_number", "amount", "currency", "vendor_is_known"])
    print()
    show(a, only=["date_month", "date_day", "date_year"])

    # --- assembly and arithmetic in CODE ----------------------------------
    print("\n  --- assembly in code ---\n")
    month = a["date_month"].choice
    day = a["date_day"].choice
    year = a["date_year"].choice

    if "not_stated" in (month, day, year):
        missing = [n for n, v in [("month", month), ("day", day), ("year", year)]
                   if v == "not_stated"]
        print(f"  flagged: missing date parts {missing}")
    else:
        try:
            parsed = date(int(year), MONTH_NUM[month], int(day))
            print(f"  parsed date: {parsed.isoformat()}")
            print(f"  weekday:     {parsed.strftime('%A')}  "
                  f"(computed in code, never asked of the model)")
            age = (date(2026, 9, 18) - parsed).days
            print(f"  age:         {age} days  (arithmetic in code)")
        except ValueError:
            print("  flagged: invalid date combination")

    print("\n  Note: the invoice number and amount came from regex candidates.")
    print("  Jev picked among them. The date components came as enums with a")
    print("  'not_stated' option, so a missing part is reported, not guessed.")


if __name__ == "__main__":
    main()
