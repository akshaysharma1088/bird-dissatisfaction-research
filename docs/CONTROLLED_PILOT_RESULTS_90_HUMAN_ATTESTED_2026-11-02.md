# BIRD 90-case controlled pilot evaluation — 2026-11-02

## Evidence status

This document records **newly measured model results**, conditional on **90 author-attested human-reviewed labels** from 90 distinct source conversation prefixes (43 `yes` expressed dissatisfaction, 47 `no_evidence`). The author explicitly clarified on November 2, 2026 that the repeated `AI-Assisted Automated Reviewer` reviewer field was an accidental copy-paste error: the case-level classifications were human-reviewed. The original CSV and its historical metadata are retained unchanged for auditing; this clarification is a separate provenance record.

This is a **single-pass human-reviewed pilot**, not independently blinded dual annotation, adjudicated gold truth, real customer CSAT, or an external representative test.

## Experimental protocol

- Source material: 30 closing and 60 mid-dialogue cases from ABCD and MultiDoGO software; 1,088 visible turns; no repeated source conversation IDs.
- Target: `expressed_dissatisfaction=yes` versus `no_evidence`. **No_evidence is not satisfaction.**
- Fixed rules: majority class, TextBlob polarity on target only, TextBlob on customer-visible history, target issue-keyword rule.
- Supervised models: TF-IDF + logistic regression with target-only, naive complete visible prefix, or speaker-role-attributed prefix; BIRD-lite behavior-only logistic regression; BIRD-lite hybrid TF-IDF + behavior indicators.
- Method: 5-fold stratified cross-validation (seed 2026), one unique source conversation per case, vectorizer vocabulary and numeric scaling fit **within the training partition only**. TF-IDF unigrams/bigrams with up to 7,000 dimensions, fixed regularization `C=1.0`, `class_weight=balanced`, 0.5 decision threshold.
- BIRD-lite is a **simplified 20-feature component study**, not the full proposed BIRD behavior/evidence/routing architecture.
- Negative control: prediction directly from lexical *selection-category metadata*, which is prohibited in a deployed model, to quantify sampling-label coupling.
- Transfer diagnostic: leave-one-corpus-out train/test (ABCD → MultiDoGO and vice versa).
- Uncertainty: 2,000 class-stratified paired resamples of **fixed out-of-fold predictions**; the interval does not represent model-refitting or population sampling uncertainty.
- No model API calls, production Salesforce data, customer surveys, or multilingual evaluation were involved.

## Out-of-fold observed results

| Method | Macro-F1 | Precision (yes) | Recall (yes) | Average precision | TP / FP / FN / TN |
|---|---:|---:|---:|---:|---|
| Always no_evidence | 0.343 | 0.000 | 0.000 | 0.478 | 0 / 0 / 43 / 47 |
| TextBlob target | 0.459 | 0.667 | 0.140 | 0.497 | 6 / 3 / 37 / 44 |
| TextBlob customer history | 0.517 | 0.667 | 0.233 | 0.543 | 10 / 5 / 33 / 42 |
| Keyword-only target | 0.693 | 0.840 | 0.488 | 0.655 | 21 / 4 / 22 / 43 |
| **Selection metadata only (bias diagnostic)** | **0.718** | 0.750 | 0.628 | 0.649 | 27 / 9 / 16 / 38 |
| TF-IDF target-only | 0.567 | 0.542 | 0.605 | 0.672 | 26 / 22 / 17 / 25 |
| TF-IDF naive-thread | 0.685 | 0.703 | 0.605 | 0.674 | 26 / 11 / 17 / 36 |
| TF-IDF role-attributed | **0.716** | 0.765 | 0.605 | 0.692 | 26 / 8 / 17 / 39 |
| BIRD-lite behavior-only | 0.683 | 0.714 | 0.581 | 0.726 | 25 / 10 / 18 / 37 |
| **BIRD-lite hybrid** | **0.729** | 0.771 | **0.628** | 0.710 | 27 / 8 / 16 / 39 |

The BIRD-lite hybrid − role-attributed TF-IDF Macro-F1 difference is **+0.012**, with paired fixed-OOF resampling interval **−0.090 to +0.115**. Thus **no statistically reliable superiority has been established**.

## Additional diagnostics

- **Close to the signal of selection itself:** non-deployable selection category alone scores Macro-F1 **0.718**, comparable to the legitimate role-attributed and BIRD-lite classifiers. This warns of sampling/label confounding, although metadata was excluded from those legitimate models.
- **Cohort differences:** BIRD-lite hybrid OOF Macro-F1 was **0.600** on 30 closing turns and **0.715** on 60 cue-enriched midpoint turns; these are not prevalence estimates.
- **Cross-corpus transfer stress test:** role-attributed TF-IDF Macro-F1 **0.579**, BIRD-lite behavior-only **0.731**, BIRD-lite hybrid **0.729**. Only two elicited corpora are available, so this cannot establish realistic domain generalization.
- **Polite positives:** the author-labeled positive class includes 22 courtesy-present cases; the fixed target TextBlob rule classified zero of them as dissatisfied. This should not be converted into a claim about actual end-user discontent without adjudication.
- **Label integrity:** all 90 evidence fields point only to the target turn; all 43 `yes` labels are coupled to `reported_unresolved`, while all 47 `no_evidence` labels are coupled to `unknown`. Consequently, resolution state is not an independent outcome variable. Fourteen higher-priority lexical/label mismatches were flagged by the refined script (earlier broader audit produced 30 flags); none was auto-corrected.
- **Descriptive evidence unchanged:** 18/24 midpoint target issue-cue messages and 11/12 polite-plus-issue targets had neutral/positive TextBlob polarity. These are lexical *signals*, not verified misclassification prevalence.

## Privacy, code and article

A downloadable **private evidence package** accompanies this research iteration, including the exact self-contained local `evaluate_bird90.py` script, seven passing synthetic unit tests, all 90 source-blind case-level OOF predictions, QC flags, aggregate JSON, a private Excel workbook, and a corrected **IET Software v6 exploratory pilot manuscript**.

The actual raw inputs (source ZIPs, case mapping, author-attested label CSV) and all private case-level predictions are **not committed to GitHub**. The full code script is distributed privately in that package and should be uploaded to this private repository separately if desired. Original-source licenses and privacy obligations remain applicable.

**Research judgment:** The pilot supports implementing and studying role-attributed customer-history features, but the sample size, selection–label coupling, unadjudicated labels, and small non-robust hybrid improvement prohibit claims of full BIRD model superiority, real-world operational validation, or journal-ready conclusive performance.
