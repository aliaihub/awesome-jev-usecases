# Research notes

How this repository was assembled, what its evidence base is, and what its limits are.

**Snapshot date:** 2026-09-18. Jev launched 15 September 2026, so this repo is a three-day-old picture of a very fast-moving ecosystem. Expect it to go stale quickly.

---

## Method

Two research passes.

### 1. Social and ecosystem sweep (last30days skill)

Ran a multi-source research sweep over a 30-day window (2026-08-19 to 2026-09-18) across Reddit, X, YouTube, Hacker News, GitHub, and Polymarket, using a custom query plan with resolved handles, subreddits, and repositories.

| Source | Items | Engagement |
| --- | ---: | --- |
| Reddit | 18 threads | 10,127 upvotes, 2,498 comments |
| X | 19 posts | 903 likes, 157 reposts |
| YouTube | 10 videos | 1,536,895 views (5 with transcripts) |
| Hacker News | 8 stories | 1,885 points, 493 comments |
| GitHub | 1 repo | 80 reactions |

Raw output: `~/Documents/Last30Days/typesafe-jev-system-one-model-use-cases-raw-v3.md` (local, not committed).

Notable single items:
- The [launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev) on Hacker News: 1,861 points, 490 comments, with founder Diogo Almeida replying in-thread as @CompleteSkeptic.
- [Syntax](https://www.youtube.com/watch?v=QbYBRjOaGOo): 25,544 views, 988 likes.
- [@npaka123](https://x.com/npaka123/status/2100202335104598393): 801 likes, 137 reposts - the most-shared explainer, in Japanese.

### 2. GitHub ecosystem census

```
gh search repos "jev typesafe" --limit 60
gh search repos --topic=jev --limit 60
gh search repos --topic=typesafe-ai --limit 50
gh search repos "jev system one" --limit 60
gh search repos "jev" language:Python --limit 60
gh search repos "jev" language:TypeScript --limit 60
```

**306** repositories match "jev typesafe". The 55 most relevant were inspected in detail via `gh api` for metadata and READMEs. Results are in [../reference/ecosystem.md](../reference/ecosystem.md).

### 3. Primary source reading

Every claim in this repository traces to a primary source:

- [TypeSafe docs](https://docs.typesafe.ai/introduction) - introduction, models, primitives, confidence, state, patterns, the design guide, the use-case map, the jaggedness page, and the full cookbook list
- [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [Workflow evals](https://evals.typesafe.ai/)
- The individual project READMEs for everything cited

### 4. Independent and critical analysis

Deliberately included, because the vendor material alone would be one-sided:

- [Pere Pages](https://pearpages.com/blog/2026/09/16/jev-sorted-what-typesafes-system-one-model-actually-is-and-what-is-still-just-a-claim) - decodes the headline claims
- [Sean Goedecke](https://www.seangoedecke.com/jev-means-structured-output-is-interesting-again/) - technical argument that the moat is thin
- [Every / Mike Taylor](https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds) - the only independent measurement in the window
- [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) - the only independent calibration benchmark
- The [Hacker News thread](https://news.ycombinator.com/item?id=49717558) - 490 comments of pushback, including from the founder

---

## Evidence standards used

Every factual claim in this repo is one of four types, and the type is stated inline:

| Label | Meaning |
| --- | --- |
| **Vendor-reported** | TypeSafe's own numbers. Labeled as such wherever used. |
| **Independently measured** | Measured by someone other than TypeSafe. Named. |
| **Self-reported by the author** | A project author's own claim about their project. Named. |
| **Launch-week artifact** | Built in the first 72 hours. A proof of concept, not a production case study. |

Where a number appears without a label, it is from a primary source and linked.

---

## Known limitations

### The evidence base is three days old

Every project in [reference/ecosystem.md](../reference/ecosystem.md) was created on or after 15 September 2026. Nothing here is a production case study. The two strongest measurements are:

- [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden): 150 paired headless runs, 6 rule violations without the guard and 0 with it
- [AbdelStark/jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks): 300 held-out examples across 3 datasets with paired bootstrap intervals

Both are small. Both are honest. Nothing larger exists yet.

### Vendor benchmarks are self-run

TypeSafe designed the four benchmark workflows, built the harness, ran the eval, and published the results. The reference labels are an average of two frontier models, not human ground truth. There is no independent reproduction of the full suite. This is stated wherever the numbers appear.

### The calibration claim is unverified at scale

Jev's core value proposition is that confidence is meaningful. No calibration curves, Brier scores, or reliability diagrams had been published as of the snapshot date. The first independent benchmark found Jev well calibrated on two datasets and substantially worse on a third (emotion classification).

### Star counts are volatile

Every star count was live from the GitHub API at collection time. In a launch week, these move fast. Treat them as directionally informative, not exact.

### The mock in the examples is not a model

`examples/python/_client.py` uses a keyword lookup table so the examples run without an API key. It exists to make the surrounding code readable. It does not simulate model behavior and should never be used to evaluate anything.

### Selection bias in the project census

The census was assembled from GitHub search, which favors projects with descriptive names and topics. Projects that use Jev without naming it in the repo name, description, or topics are underrepresented.

---

## What would change the picture

These have not happened as of the snapshot date and each would materially change this repository:

1. **A calibration curve from someone other than TypeSafe**, on human-labelled data, far from the four launch workflows. This is the single most valuable missing result.
2. **An eval with human ground truth.** Agreement with two frontier models rewards agreement with their mistakes.
3. **A paper or technical report on RLCD**, so "calibrated" in the method name is verifiable rather than aspirational.
4. **General availability with published limits**, so latency and price can be measured under real load.
5. **A single-token logprobs baseline in TypeSafe's own table.** The current comparison forces LLMs to generate full structured answers, which is the slowest fair comparison.
6. **A production case study at volume.** Everything here is launch-week.
7. **A cost or latency regression** as the service scales, which TypeSafe warns is possible while GPU capacity lands.

---

## Reproducing this research

```bash
# Ecosystem census
gh search repos "jev typesafe" --limit 60 --json fullName,description,stargazersCount,language
gh search repos --topic=jev --limit 60 --json fullName,description,stargazersCount

# Repository details
gh api repos/{owner}/{repo}
gh api repos/{owner}/{repo}/readme -H "Accept: application/vnd.github.raw"

# Primary sources
# See the URL list in ../reference/ecosystem.md
```

For the social sweep, re-run the `last30days` skill against `TypeSafe Jev System One model use cases` with the subreddits `LocalLLaMA,LLMDevs,MachineLearning,artificial,OpenAI,AI_Agents,ChatGPTCoding,singularity` and the handles `typesafeai` (primary), `CompleteSkeptic` (founder).

---

## Corrections

If a claim here is wrong, stale, or missing its label, that is the most valuable contribution you can make. See [../CONTRIBUTING.md](../CONTRIBUTING.md).
