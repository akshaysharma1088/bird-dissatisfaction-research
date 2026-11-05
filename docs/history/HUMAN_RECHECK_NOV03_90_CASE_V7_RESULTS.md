# BIRD 90-case author-attested 14-case recheck and Version 7 pilot — 2026-11-03

**Status: exploratory, conditional, single-reviewer, post-flag recheck; not final independently adjudicated benchmark.** This addendum supersedes prior model-result counts for the revised reference dataset. The original source record and old labels were retained outside GitHub without modification.

## Recheck scope and provenance

- The author previously attested that all 90 reference labels were human-reviewed and that “AI-Assisted Automated Reviewer” was erroneously copied into metadata.
- On 2026-11-03 the author supplied findings for **14 previously flagged cases**. Ten `yes` dissatisfaction labels changed to `no_evidence`; one `no_evidence` changed to `yes`; three already `no_evidence` labels stayed unchanged, while their resolution state was updated.
- The resulting 90-case binary reference is **34 `yes`, 56 `no_evidence`**. Recorded resolution states: 12 `confirmed_resolved`, 34 `reported_unresolved`, 44 `unknown`.
- For rulebook compatibility, “no” from the author's recheck was encoded as `no_evidence`, “resolved” as `confirmed_resolved`, and “unresolved” as `reported_unresolved`. **`no_evidence` does not assert customer satisfaction.**
- The review was **not blinded or randomly selected**; the 14 cases were originally flagged using lexical cues similar to inputs to the BIRD-lite behavioral model. This can favor the behavior model and is an important outcome-measurement bias.
- All prior supporting-turn references remain target-only, except that the author specifically reaffirmed R005's target turn as evidence. Some “confirmed_resolved” states reflect agent promises or pending credits/refunds rather than independent customer-confirmed fulfillment. These states are **not independent validated outcomes** and were not used as input features.

## Verified rerun (fixed 5-fold out-of-fold protocol)

All 90 input records were checked against the source mapping and the earlier 30+60 cohort. We ran the same fixed evaluation script and seven synthetic tests passed. Only the reference outcome, courtesy and resolution fields specified by the author were changed. Same `StratifiedKFold(n_splits=5, shuffle=True, random_state=2026)`, logistic-regression parameters, TF-IDF preprocessing inside folds, and one held-out target per original conversation.

| Method | Macro-F1 | Yes recall | Average precision | TP / FP / FN / TN |
| --- | ---: | ---: | ---: | --- |
| Always `no_evidence` | 0.384 | 0.000 | 0.378 | 0 / 0 / 34 / 56 |
| TextBlob target | 0.526 | 0.176 | 0.476 | 6 / 3 / 28 / 53 |
| TextBlob customer history | 0.537 | 0.235 | 0.494 | 8 / 7 / 26 / 49 |
| Issue-keyword rule | **0.786** | 0.618 | 0.663 | 21 / 4 / 13 / 52 |
| **Selection category ONLY — negative control, not deployable** | **0.790** | 0.765 | 0.641 | 26 / 10 / 8 / 46 |
| TF-IDF target-only | 0.676 | 0.647 | 0.765 | 22 / 16 / 12 / 40 |
| TF-IDF naive complete thread | 0.715 | 0.559 | 0.716 | 19 / 8 / 15 / 48 |
| TF-IDF role-attributed | 0.700 | 0.529 | 0.744 | 18 / 8 / 16 / 48 |
| **BIRD-lite behavioral features** | **0.843** | 0.765 | 0.803 | 26 / 5 / 8 / 51 |
| **BIRD-lite hybrid** | **0.845** | **0.794** | 0.796 | 27 / 6 / 7 / 50 |

### Paired differences on fixed OOF predictions

- BIRD-lite hybrid − role-attributed TF-IDF Macro-F1: **+0.145**; 2,000-replicate class-stratified paired fixed-prediction interval **+0.051 to +0.245**.
- Hybrid − issue keyword: **+0.060**, interval **−0.018 to +0.147**.
- Hybrid − non-deployable selection control: **+0.056**, interval **−0.022 to +0.135**.
- Hybrid − behavior-only BIRD-lite: **+0.002**, interval **−0.058 to +0.061**.

The first comparison excludes zero in the conditional resampling calculation, but this does **not** establish unbiased significance or field performance due to selected labels, nonblind recheck, small N, two elicited English corpora and lack of independent adjudication.

### Cross-corpus diagnostic and residual QC

- Leave-one-corpus-out, pooled Macro-F1: role-TF-IDF **0.602**, behavior-only **0.806**, hybrid **0.825**. These two corpus splits are not a real production-domain test.
- Four narrower lexical-label screening flags remain: **R030, R038, R075, R079** (issue vocabulary in a `no_evidence` target). They are not automatic labeling errors.
- Several resolution-state claims lack customer-confirmed final fulfillment (especially R017, R033, R068, R079, R080, R082). Distinguish recorded author coding from verified financial/technical outcome.
- Unchanged descriptive evidence: 90 unique conversation prefixes, 1,088 speaker turns; 18/24 midpoint issue-cue targets are nonnegative by TextBlob, 11/12 polite-issue cues nonnegative, and 41/90 target-vs-customer-history polarity category shifts.

## Reproducibility and responsible disclosure

A private local package provides the revised reference CSV, original-to-revised per-field change log, out-of-fold prediction CSV, source-blind QC flags, aggregate JSON, original evaluation Python script, seven synthetic tests, Version 7 manuscript DOCX/PDF and a 6-sheet Excel analysis workbook. Inputs include redacted conversation text and must remain researcher-only. No transcript, researcher mapping or case-level annotations have been committed here.

**Judgment:** This is an improved, more coherent *exploratory controlled pilot*. It does not support claims that full BIRD or BIRD-Route was implemented, that BIRD-lite is reliably superior to the simple issue-keyword comparator, or that real-customer dissatisfaction was independently validated. Independent review of a sample of labels, a truly untouched test and a larger unselected corpus remain necessary for confirmatory claims.
