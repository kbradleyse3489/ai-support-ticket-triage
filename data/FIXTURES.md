# Synthetic diagnostic fixtures

These fixtures are hand-authored synthetic examples composed by an AI assistant for this project. They are not real customer records, sampled Banking77 messages, human-evaluated data, or independently adjudicated ground truth. No real names, account numbers, addresses, credentials, or other private identifiers are included. Banking77's 77 intent names were consulted only to keep the banking-support scenarios relevant; fixture text was written independently. No classifier predictions, generated summaries, or review-threshold decisions were consulted during authoring.

## Files and counts

- `summary_fixtures.json`: 36 messages, each 3–5 sentences. Each record contains `id`, `text`, `expected_key_phrases`, `rationale`, and `synthetic: true`. There are 1–3 case-insensitive, contiguous source spans per message. Messages vary issue placement and include greetings, unrelated details, negated alternatives, multiple issues, and vague follow-ups clarified later in the same input.
- `review_fixtures.json`: 24 challenges, with eight records in each `kind`: `in_domain_straightforward`, `off_domain`, and `ambiguous_multiple_issues`. Fields are `id`, `text`, `kind`, `expected_review`, `expected_reason`, `rationale`, and `synthetic: true`. The eight straightforward cases expect `false`; the sixteen other cases expect `true`. Expected reasons are author judgments about desired routing, not observed detector outputs.

The review examples are diagnostic holdouts: do not use them for classifier training, hyperparameter selection, vocabulary fitting, calibration, review-threshold tuning, or choosing a rejection rule. The summary examples likewise should not be used to tune sentence selection or summary rules. If a system is adjusted after inspecting results, disclose that exposure and create a fresh, independent fixture set before claiming another held-out result.

## Summary checks and interpretation

Use case-insensitive exact lexical recall of the authored key phrases as a diagnostic: a phrase counts as retained only if that same contiguous span occurs in the summary. Specify whether the reported overall result is macro-averaged across messages or micro-averaged across all phrases. Do not call this semantic recall, factual accuracy, human-rated quality, or summarization validation.

Also report the fraction of output sentences copied from source sentences and a clearly defined compression measure, such as summary word count divided by source word count. State tokenization and sentence-matching rules. Copied-sentence rate is largely a construction check for an extractive method, not independent evidence of correctness. A lower length ratio is not necessarily better: it can reflect loss of essential details. These scores should be viewed together, with per-fixture failures available for inspection.

Exact phrase recall can penalize a correct paraphrase and reward superficial copying. It may miss a dropped negation, changed implication, incorrect issue priority, or unresolved reference unless the chosen phrase exposes that error. Multiple-issue and vague-follow-up cases deliberately challenge summary completeness. The phrases are selected essentials, not an exhaustive reference summary.

## Review checks and limitations

Report routing results separately for the three challenge groups and retain individual predictions, expected routing, and explanatory reason fields. Report any mismatch as a diagnostic failure rather than changing the labels or thresholds to match the result. Off-domain examples include both ordinary non-banking requests and lexical traps involving a river bank, playing cards, plant transfers, and a graphics card. The ambiguous group contains four insufficient-context cases and four clearly multi-intent cases.

This small, intentionally balanced set is not representative of production prevalence or the full range of Banking77 intents. Its routing expectations express a conservative support workflow, not a claim that Banking77 includes an out-of-domain class or that confidence alone detects multiple intents. It cannot establish calibrated uncertainty, robust out-of-domain detection, safety, customer satisfaction, or real-world performance. Broader, independently collected and reviewed evaluation data are needed for those claims.

## Structural validation performed

JSON parsing, unique IDs, record counts, summary sentence counts, 1–3 phrase counts, case-insensitive phrase containment, `synthetic: true`, review group counts, and expected review flags were checked programmatically. These structural checks do not substitute for human semantic evaluation.
