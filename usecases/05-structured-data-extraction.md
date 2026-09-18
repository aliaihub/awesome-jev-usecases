# Structured data extraction

**Decision shape:** `Choice` over pre-extracted candidates, plus `Noul` to report missing fields.

**Reach for it when:** known fields must be recovered from unstructured input, and the values come from a bounded set you can enumerate.

This is the use case where the naive approach fails hardest - and where the correct approach is genuinely different from what an LLM would do.

---

## The rule that changes everything

**Do not ask Jev to generate the value. Ask Jev to pick the value from candidates.**

Jev does not generate text. If you ask for a free-text field, you get nothing useful. Instead:

1. Use a **regex** or a **generative model** to find candidates in the text.
2. Let **Jev pick the correct candidate** with a `Choice`.
3. Normalize the result in code.

This is TypeSafe's explicit recommendation, and it is the correct architecture. A generative model is good at producing plausible values. Jev is good at selecting the right one. Use each for what it does well.

```
raw text -> regex / LLM -> candidate list -> Jev Choice -> code normalizes
```

Source: [pre-parsed value extraction cookbook](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook)

---

## The canonical example: dates

Dates are the perfect illustration because they fail in both directions - Jev cannot do date arithmetic, but it is excellent at extracting the parts.

Every part of a date is a small closed set: twelve months, thirty-one possible days, a bounded range of years. That turns extraction into a `Choice` over enumerated options **rather than free-form parsing**, and it gives you somewhere to put an explicit "not stated" option so a missing part is reported rather than guessed.

```python
questions={
    "month": Choice(
        instructions="Which month is stated in `document.effective_date`?",
        criteria={
            "january": "January", "february": "February", "march": "March",
            "april": "April", "may": "May", "june": "June",
            "july": "July", "august": "August", "september": "September",
            "october": "October", "november": "November", "december": "December",
            "not_stated": "No month is specified",
        },
    ),
    "day": Choice(
        instructions="Which day of the month is stated?",
        criteria={**{str(d): f"The {d}th" for d in range(1, 32)},
                  "not_stated": "No day is specified"},
    ),
    "year": Choice(
        instructions="Which year is stated?",
        criteria={**{str(y): str(y) for y in range(2020, 2031)},
                  "not_stated": "No year is specified"},
    ),
    "is_relative": Noul(
        "Is the date expressed relative to another date rather than absolutely?"
    ),
}

# All in ONE request - 12 + 31 + 11 + 1 options costs a few hundred tokens
# and evaluates in parallel.
```

Then code assembles and owns everything after:

```python
month, day, year = a["month"].choice, a["day"].choice, a["year"].choice

if "not_stated" in (month, day, year):
    flag_for_review(document, missing=[f for f, v in
        [("month", month), ("day", day), ("year", year)] if v == "not_stated"])
else:
    try:
        parsed = date(int(year), MONTHS[month], int(day))
        # ordering, duration, offset, weekday - all in code
    except ValueError:
        flag_for_review(document, reason="invalid_date")
```

The `not_stated` option is not optional. Without it, the model is structurally unable to abstain and will pick the closest wrong month.

Source: [date extraction cookbook](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook)

---

## The general extraction shape

```python
questions={
    # one Choice per field, over the candidate set or an enumerated domain
    "invoice_number": Choice(
        instructions="Which candidate is the invoice number in `document.text`?",
        criteria={c: f"Candidate {c}" for c in candidates.invoice_numbers},
    ),
    "currency": Choice(
        instructions="Which currency is `document.amount` expressed in?",
        criteria={"usd": "US dollars", "eur": "Euros", "gbp": "Pounds sterling",
                  "other": "Some other currency", "not_stated": "Not specified"},
    ),
    "vendor_is_known": Noul(
        "Is `document.vendor_name` present in `vendor_directory`?"
    ),
    "document_type": Choice(
        instructions="What kind of document is this?",
        criteria={
            "invoice": "A request for payment for goods or services",
            "receipt": "Proof of a completed payment",
            "statement": "A summary of account activity",
            "purchase_order": "A buyer's commitment to purchase",
            "other": "Something else",
        },
    ),
}
```

Three things to notice:

1. **The candidate-based field** (`invoice_number`) uses the extracted candidates as the option set.
2. **The enumerated-domain field** (`currency`) uses a closed vocabulary with `not_stated`.
3. **The verification field** (`vendor_is_known`) is a `Noul` against a directory you supply, not a generation.

---

## The two-stage cascade for messy documents

For hard extraction, a two-stage cascade gets most of the quality of a big reasoning model at a fraction of the cost:

```
stage 1 (mini model): extract candidate fields from raw text
stage 2 (Jev): verify / select / score confidence on each field
stage 3 (reasoning): only for the fields that failed stage 2
```

Source: [SDE cascade cookbook](https://docs.typesafe.ai/cookbooks/sde_cascade)

The economics work because stage 3, the expensive stage, only sees the residue.

---

## Where extraction fits in a real pipeline

Extraction is rarely the whole job. The pattern is:

```
document -> extract fields (Choice over candidates)
          -> verify fields (Noul against reference data)
          -> score confidence (already returned)
          -> route (auto-post / review / reject)
```

A concrete version from the [invoice processing workflow](https://docs.typesafe.ai/concepts/use-case-map):

```python
answers = r.answers

auto_post = (
    answers["invoice_number"].confidence > 0.9
    and answers["currency"].choice != "not_stated"
    and answers["vendor_is_known"].noul > 0.9
    and answers["amount_matches_po"].noul > 0.85
)

if auto_post:
    post_invoice(invoice)
elif answers["vendor_is_known"].noul < 0.5:
    route_to_vendor_management(invoice)
else:
    route_to_human_review(invoice, reason="low_confidence_extraction")
```

The `amount_matches_po` check is a `Noul` comparing two supplied values, not an arithmetic comparison. If the amounts need summing or matching exactly, do it in code - but if the question is "does this vendor's reference format match", that is a judgment.

---

## Important: what not to extract with Jev

| Do not ask Jev to | Why | Do instead |
| --- | --- | --- |
| Count occurrences | It does not count reliably; error grows with size | Regex or code |
| Sum or average amounts | It is not a calculator | Code |
| Compare two dates | Dates are text to it, not ordered quantities | Extract parts, compare in code |
| Generate a free-text summary | It does not generate | A writing model |
| Produce a field value from nothing | It selects, it does not invent | Regex or generative model for candidates |
| Recover a value between two score levels | Score levels are weak in numerical calibration | Bucket the score, keep arithmetic in code |

Every one of these is documented on the [jaggedness page](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

---

## What the community built

### Computer-use extraction at $0.0002 a step

[awlevin/typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) OCRs the screen and asks Jev which action comes next, calling a writing model only when a text field genuinely needs free text. The author's caveat is the most instructive line in the project: the frontier model read event dates off the pixels and compared them unaided, while the Jev pipeline needed explicit date parsing built around it.

> Every piece of reasoning the frontier model does for free has to be rebuilt here as deterministic state.

### Invoice and claim processing

TypeSafe's own use-case map lists invoice processing as one of its four benchmark workflows, and the domain applications page collects the broader claim-ops and insurance patterns.

---

## Design notes specific to extraction

### Give the model candidates, never a blank page

This is the single most important rule in the category. `Choice` over candidates, never a request to generate a value.

### Provide `not_stated` for every field

The model cannot abstain unless you give it an option to. A missing field must be reportable, or it becomes a guess.

### Do the arithmetic in code

Assembly, ordering, duration, offsets, sums, comparisons, validation. The `Choice` gives you the parts; code owns everything after.

### Score fields independently, then gate as a group

Extract each field as its own question so you know *which* field is uncertain. Then combine into an overall confidence for routing. Do not ask one question that extracts all fields at once - you lose the per-field signal.

### Enumerate the domain whenever it is closed

Months, currencies, document types, statuses, countries. An enumerated `Choice` beats free-text extraction on accuracy, and it gives you a typed value to branch on with no normalization step.

### Verify against your own reference data

Do not ask the model whether a vendor name is valid. Ask whether the extracted name appears in the directory you pass in the state. That is a judgment about a match, which Jev is good at, and it uses your data rather than model weights.

---

## Pitfalls

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| Asking for a generated field value | Empty or useless output | Extract candidates, use `Choice` |
| No `not_stated` option | Confident wrong value on a missing field | Always include it |
| Date comparison in the model | Unreliable ordering | Extract parts, compare in code |
| One question for all fields | No per-field confidence | One question per field |
| Free-text domain not enumerated | Normalization hell downstream | Enumerate the closed sets |
| Assuming exact amounts match | Wrong arithmetic | Supply both values, ask about format match; compute in code |

---

## Related

- [04-search-reranking-and-rag.md](04-search-reranking-and-rag.md) - retrieving the candidates to extract from
- [../docs/failure-modes.md](../docs/failure-modes.md#3-dates-are-text-to-it-not-ordered-quantities) - the date failure mode in full
- [10-domain-applications.md](10-domain-applications.md) - insurance, legal, and finance extraction
