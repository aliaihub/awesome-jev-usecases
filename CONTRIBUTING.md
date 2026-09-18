# Contributing

This repository is a research snapshot of the Jev ecosystem and a practical guide to using it. Corrections and additions are welcome.

## What belongs here

- **Use cases that use Jev.** A generic classifier that resembles the pattern without using Jev does not qualify.
- **Guidance derived from evidence.** If you add a claim, link the source, and label vendor-reported numbers as vendor-reported.
- **Projects with a working artifact.** A repository, a notebook, a reproducible write-up. Launch-hype commentary without a concrete practice does not qualify.
- **Corrections.** If a number here is wrong or has gone stale, that is the most valuable PR you can send.

## What does not belong

- Pure opinion without a concrete practice
- Summaries of projects with no working artifact
- Anything that does not actually call Jev (or a documented Jev port/derivative)
- Promotional content for a bootcamp, course, or paid product
- Long write-ups embedded in the list rather than linked

## How to contribute

1. Open an issue describing the addition or correction, or open a PR directly for small fixes.
2. For a new use case, include: the decision shape (Choice/Score/Noul), what it does, what was measured, who measured it, and a link.
3. For a new project, state explicitly whether the result is **measured** or **claimed**, and by whom.
4. For a correction, link the primary source that contradicts the current text.

## Style

- **No em-dashes.** Use ` - ` (hyphen with spaces). This is a house rule, not a grammatical preference.
- **Cite inline.** Every factual claim gets a link.
- **Label the evidence.** "Vendor-reported", "independently measured", "launch-week artifact", "self-reported by the author".
- **Prefer short sentences.** The reader is here for the signal.

## Reviewing evidence claims

When you add a number, answer these questions in the PR:

- **Who measured it?** The vendor, an independent party, or the author of the project?
- **On what data?** Public benchmark, private dataset, synthetic set?
- **Is it reproducible?** Is there a script, a harness, or committed raw results?
- **Is it vendor-reported?** If so, say so.

The community's best work is labeled this way. [AbdelStark/awesome-typesafe](https://github.com/AbdelStark/awesome-typesafe) labels which results rest on private data or single runs. [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) commits raw machine-readable metrics and paired bootstrap intervals. Match that standard.

## Scope notes

This repository focuses on **use cases and guidance**. For pure project indexes, contribute to:

- [AbdelStark/awesome-typesafe](https://github.com/AbdelStark/awesome-typesafe) - curated with research labeling
- [yibie/awesome-jev](https://github.com/yibie/awesome-jev) - category-organized
- [Anil-matcha/awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe) - evidence-backed use cases
- [AnotiaWang/awesome-jev](https://github.com/AnotiaWang/awesome-jev)
- [OmniJev/awesome-jev](https://github.com/OmniJev/awesome-jev) - research and reproductions

## The bar for "use case"

A use case earns a page in `usecases/` when it has:

1. A distinct **decision shape** that differs from the existing pages
2. At least one **real implementation** or a documented vendor recipe
3. **Specific pitfalls** that a reader would not guess

Otherwise it belongs in [reference/question-catalog.md](reference/question-catalog.md) or [reference/ecosystem.md](reference/ecosystem.md).
