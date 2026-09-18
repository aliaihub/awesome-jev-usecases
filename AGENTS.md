# AGENTS.md

Instructions for AI agents working in this repository.

## What this repo is

A curated collection of Jev use cases and guidance. It is documentation-first: most of the value is in the Markdown, not the code.

- `docs/` - conceptual and methodological guides
- `usecases/` - one page per use-case category
- `reference/` - question catalog and ecosystem census
- `examples/python/` - nine runnable examples

## House style (enforced)

- **No em-dashes or en-dashes in prose.** Use ` - ` (hyphen with spaces). The only exception is quoted source material inside blockquotes (`> `). En-dashes are acceptable *only* in numeric ranges like `70-500 ms`.
- **Cite inline with markdown links.** `[name](url)` at first mention. No trailing "Sources:" blocks.
- **Label the evidence.** Every factual claim is one of: vendor-reported, independently measured, self-reported by the author, or launch-week artifact. State which.
- **Tables and ASCII diagrams must stay aligned.** Do not run a whitespace-collapsing formatter over this repo. It will destroy the diagrams.
- **Preserve quoted material verbatim**, including its punctuation.

## Evidence rules

When adding or editing a claim:

1. Find the primary source. Link it.
2. If the number is TypeSafe's own, write "vendor-reported" or "TypeSafe's own eval".
3. If it is a project author's claim, name the author and say it is self-reported.
4. If it is a launch-week artifact (created on or after 2026-09-15), say so.
5. Never present a vendor benchmark as independent.

The most common mistake in this space is repeating TypeSafe's headline multipliers without noting that they compare against the single slowest and priciest baseline. Do not do that.

## Running the examples

```bash
cd examples/python
python 01_routing_triage.py          # mock mode if no API key
```

All examples run without an API key by default. `_client.py` provides a keyword-heuristic mock so the surrounding code is runnable and readable. It is not a model and must never be used to evaluate anything.

Live mode: set `TYPESAFE_API_KEY`, or force with `JEV_EXAMPLE_MODE=live`.

## Verifying a change

Before committing:

```bash
# 1. Examples still run
cd examples/python && for f in 0*.py; do python "$f" > /dev/null || echo "FAILED: $f"; done

# 2. No broken relative links
# 3. No em-dashes outside blockquotes
```

The examples print to stdout and exit 0. If a change to `_client.py` breaks one, the others usually break too.

## Do not

- Do not add a project that does not actually use Jev.
- Do not add promotional or course content.
- Do not reformat code blocks or diagram whitespace.
- Do not turn this into a link dump. Every entry states what was measured and by whom.
- Do not add emojis to the Markdown unless the user asks.

## When adding a use case

A new page in `usecases/` needs: a distinct decision shape, at least one real implementation or a documented vendor recipe, and specific pitfalls a reader would not guess. Otherwise add to `reference/question-catalog.md` or `reference/ecosystem.md` instead.

Update the table in `usecases/README.md` and the catalog table in the root `README.md`.
