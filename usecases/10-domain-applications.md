# Domain applications

Industry-specific applications, drawn from TypeSafe's [use-case map](https://docs.typesafe.ai/concepts/use-case-map) and the community projects. Each entry states the decision shape and where the evidence comes from.

The categories are organized by industry because the *design decisions* differ by domain - the compliance constraints, the acceptable error budget, and the explainability requirement all change.

**A general note on regulated domains.** Jev returns a probability, not a rationale. If a compliance team needs to know *why* an application was scored the way it was, a confidence number will not satisfy them. The practical pattern is to keep Jev on the high-volume routing layer and escalate flagged or low-confidence cases to a model that can produce a written explanation, or to a human. See [../docs/model-selection.md](../docs/model-selection.md).

---

## Legal and compliance

**Decision shapes:** `Choice` for classification, `Noul` for detecting missing clauses and prohibited claims.

| Use case | Shape | Notes |
| --- | --- | --- |
| Classify contracts, policies, filings, marketing claims | Choice | Enumerate the categories; add `other` |
| Detect missing clauses | Noul per required clause | One `Noul` per clause beats one "is this complete?" question |
| Detect prohibited claims | Noul per prohibition | Same decomposition principle |
| Verify against explicit requirements | Noul comparing document to requirement | Supply the requirement in state |
| Escalate high-risk findings | Confidence gate | Route uncertain findings to counsel |

**Real implementation:** [@jan__kubica](https://x.com/jan__kubica/status/2100636173249007696) tested Jev for legal use cases in stll_app:

> Jev comes from the opposite research direction: it does not generate text but is optimised for decisions instead. A few use cases below, making use of typed answers with probabilities, delivered in 0.3 s and for cents per thousand calls.

**The audit limitation is the constraint here.** Legal work often requires an explanation, and Jev does not write one. Use it to triage and route, not to make the final determination on a matter requiring a reasoned record.

---

## Financial services and financial crime

**Decision shapes:** `Choice` for classification, `Score` for risk and severity, `Noul` for fraud indicators.

| Use case | Shape | Notes |
| --- | --- | --- |
| Transaction narrative review | Noul per indicator | Suspicious characteristics as separate questions |
| KYC document evaluation | Choice + Noul | Classify document type, detect inconsistencies |
| Entity matching across inconsistent records | Choice over candidates | Same as [extraction](05-structured-data-extraction.md) |
| Alert prioritization | Score + confidence | Rank by risk, relevance, evidence quality |
| Route ambiguous cases | Confidence gate | To investigators |

**The design principle for financial crime:** decompose the suspicious characteristics. "Is this transaction suspicious?" is a bad question; "does the narrative reference an unexplained third party", "is the amount inconsistent with the account history", "does the timing pattern match structuring" are good ones - and you can weight them yourself.

**Note:** the amounts mentioned in the [classification at scale](06-classification-at-scale.md) coverage include financial use cases. As always, do not ask Jev to do the arithmetic. It classifies; code computes.

---

## Insurance

**Decision shapes:** `Choice` for claim type, `Score` for complexity and severity, `Noul` for fraud indicators and missing information.

| Use case | Shape | Notes |
| --- | --- | --- |
| Classify first-notice-of-loss reports | Choice | Enumerate claim types |
| Adjuster note classification | Choice + Noul | Type plus key facts present |
| Detect claim complexity | Score | Simple → specialist review |
| Detect missing information | Noul per required field | Decompose |
| Detect fraud indicators | Noul per indicator | Weight and combine in code |
| Prioritize for straight-through vs specialist | Confidence gate | High confidence auto, low to humans |

**Real implementation:** TypeSafe's own benchmark includes insurance-adjacent work, and the invoice processing workflow (which scored 61.8% for Jev against Terra's 74.7%) is the closest published analogue. Note that gap - extraction-heavy insurance work is where Jev is weakest relative to a frontier model. Design accordingly: use Jev for routing and triage, and be more conservative about auto-adjudication.

---

## Healthcare and life sciences

**Decision shapes:** `Choice` for classification, `Noul` for inclusion/exclusion and evidence checks.

| Use case | Shape | Notes |
| --- | --- | --- |
| Screen papers against inclusion/exclusion criteria | Noul per criterion | One question per criterion, combine in code |
| Label passages in transcripts and field notes | Choice over themes | Enumerate the theme set |
| Check citations support claims | Noul | See [guardrails](02-llm-guardrails-and-verification.md) |
| Flag missing methodological details | Noul per detail | Controls, dataset, settings - one each |
| Build research knowledge graphs | Choice for entity types and relations | |

**Real implementation:** the [retrieve-then-judge](04-search-reranking-and-rag.md#the-retrieve-then-judge-pattern) example screens 20 PubMed and arXiv papers on four dimensions for well under a cent, against primary literature.

**Independent benchmark in a medical context:** [mahlernim/jev-korean-benchmark](https://github.com/mahlernim/jev-korean-benchmark) is a reproducible early-access evaluation of Jev on Korean understanding and medical text, with runtime and cost evidence. Relevant because Jev's language support is uneven - English is the primary training language and other languages are "handled but not equally well".

**Compliance caveat:** health decisions have hard explainability requirements. Keep Jev on the screening and routing layer.

---

## Recruiting

**Decision shapes:** `Score` per competency, `Choice` for match and routing.

| Use case | Shape | Notes |
| --- | --- | --- |
| Evaluate resumes against job criteria | Score per criterion | One `Score` per competency, combine in code |
| Score evidence for required competencies | Score | "Depth of experience shown", not "is this a good candidate" |
| Match candidates to roles | Choice over roles | Enumerate roles |
| Route to hiring managers | Choice + confidence | Gate uncertain cases |

**Real implementation:** the [composite scoring](../docs/patterns.md#pattern-3--composite-scoring) example scores `python_depth`, `team_leadership`, and `system_design` separately and combines with explicit weights. That is the correct shape - and the weight visibility is what makes it defensible.

**Important:** this is a regulated domain in many jurisdictions. Scoring each competency separately against explicit, job-related criteria is not just better modeling, it is the more auditable approach. Avoid any question that asks for a holistic judgment of a person.

---

## E-commerce and marketplaces

**Decision shapes:** `Choice` for classification, `Noul` for policy violations.

| Use case | Shape | Notes |
| --- | --- | --- |
| Classify and normalize product listings | Choice over categories | Hierarchical if large |
| Extract product attributes | Choice over candidates | See [extraction](05-structured-data-extraction.md) |
| Detect prohibited listings | Noul per policy | One question per policy |
| Detect counterfeit signals | Noul per signal | Weight and combine |
| Detect review abuse | Noul + Score | |
| Rank products | Score | |
| Route uncertain listings for review | Confidence gate | |

**The scale story:** this is where the 50-million-row economics example comes from. Classifying a huge catalogue becomes affordable when a per-row decision is a fraction of a cent.

---

## Moderation and trust and safety

**Decision shapes:** `Choice` for action, `Score` for severity, `Noul` per hazard.

| Use case | Shape | Notes |
| --- | --- | --- |
| Moderate user content | Choice: allow/warn/review/block | |
| Detect toxicity, harassment, spam, fraud | Noul per category | Decompose by hazard |
| Detect personal-data exposure | Noul | |
| Detect opt-out requests | Noul | |
| Combine severity and confidence | Score + confidence | Two axes: how bad, how sure |

**Real implementation:** [brainstormity/Jev-Moderation-Bot](https://github.com/brainstormity/Jev-Moderation-Bot) is a Jev-based moderation bot.

**Self-consistency pattern from the docs:** add an explicit uncertain outcome to moderation decisions and compare label agreement with the share of automatic actions. If your automatic-action rate is high but your agreement is low, your threshold is too low. Source: [consistency choice cookbook](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook)

**The adversarial warning applies here most of all.** The content you are moderating is exactly the content trying to get past you. Test with adversarial inputs.

---

## Advertising

**Decision shapes:** `Choice` for brand safety and suitability, `Noul` for compliance.

| Use case | Shape | Notes |
| --- | --- | --- |
| Brand safety classification | Choice | Enumerate the safety tiers |
| Audience suitability | Choice + Score | |
| Regulatory compliance checks | Noul per regulation | |
| Creative quality evaluation | Score per dimension | |
| Ad-to-landing-page alignment | Noul | |

---

## Gaming

**Decision shapes:** `Choice` per tick (see [real-time](08-real-time-and-games.md)).

| Use case | Shape | Notes |
| --- | --- | --- |
| Moderate chat and player reports | Choice + Noul | |
| Detect abuse and suspicious behavior | Noul per signal | |
| Score frustration or engagement | Score | |
| Detect churn signals | Noul + Score | |
| Route player-support requests | Choice | |

The most mature gaming use case is the real-time agent loop, covered in its own page.

---

## Customer support

Covered in depth in [routing and triage](01-routing-and-triage.md). The domain-specific additions:

| Use case | Shape | Notes |
| --- | --- | --- |
| Extract customer issues from call transcripts | Noul per issue | |
| Extract commitments and follow-up actions | Noul per item | |
| Detect urgency, frustration, churn risk | Score + Noul | |
| Verify support responses against policy | Noul | |
| Verify response against the customer's request | Noul | |

**Repeated implementation:** [Obrais-cloud/ticket-rerank](https://github.com/Obrais-cloud/ticket-rerank) is a FastAPI service that reranks support tickets by urgency.

---

## Risk assessment (cross-industry)

A general pattern applicable across insurance, lending, vendor management, and operations.

```
incident reports, claims notes, transaction descriptions, vendor assessments
        |
        v
Jev: probabilistic risk indicators
        |
        v
classify risk types, detect suspicious characteristics, score severity,
prioritize review, extract features for a broader risk model
```

The last step - extracting features for a broader model - connects this page to [feature extraction](07-feature-extraction-for-ml.md). Risk indicators are features; the decision comes later.

---

## Graphs and knowledge graphs

| Use case | Shape | Notes |
| --- | --- | --- |
| Classify relationship and entity types | Choice | |
| Detect contradictions between records | Noul | |
| Verify knowledge graph annotations | Noul | |
| Probabilistic traversal | Choice over neighbors | |

**Real implementation:** [jexp/neo4jev](https://github.com/jexp/neo4jev) navigates a Neo4j graph using a classifier over neighbouring relationships. [TypeSafe's entity alignment cookbook](https://docs.typesafe.ai/cookbooks/entity_alignment) decides which of 450 candidate pairs from two beer catalogues describe the same product, using one `Score` question whose three levels are the three things you can do with a pair: merge it, leave it unlinked, or hand it to a curator.

**That cookbook is worth studying for the design.** A three-level `Score` encoding the three possible *actions* is a clean way to make the model's output directly actionable, with no threshold to fit.

---

## Choosing a domain starting point

| If your constraint is… | Start with |
| --- | --- |
| Regulatory explainability | Routing only; escalate for rationale |
| High volume, low error tolerance | [Extraction](05-structured-data-extraction.md) + conservative gates |
| Adversarial input | [Guardrails](02-llm-guardrails-and-verification.md) with adversarial testing |
| Deep taxonomies | [Classification](06-classification-at-scale.md) with hierarchical search |
| A downstream predictive model | [Feature extraction](07-feature-extraction-for-ml.md) |
| Real-time constraints | [Real-time](08-real-time-and-games.md) |

---

## Related

- [01-routing-and-triage.md](01-routing-and-triage.md) - the canonical triage template
- [02-llm-guardrails-and-verification.md](02-llm-guardrails-and-verification.md) - verification patterns
- [../reference/question-catalog.md](../reference/question-catalog.md) - ready-made questions by domain
- [TypeSafe use-case map](https://docs.typesafe.ai/concepts/use-case-map) - the vendor's own category list
