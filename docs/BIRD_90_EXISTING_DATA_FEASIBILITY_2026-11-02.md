# BIRD existing-data feasibility analysis — 90 conversations (2 Nov 2026)

**Status:** exploratory and label-free. These are source-verified, English-language, research-elicited support conversations—not production Salesforce/Amazon messages, direct CSAT records, or a validated dissatisfaction benchmark.

## Grounded research materials

- 30 ending-turn prefixes (15 ASAPP ABCD, 15 Amazon Research MultiDoGO software)
- 60 separate cue-enriched mid-dialogue prefixes (30 ABCD, 30 MultiDoGO), selected at a customer turn before subsequent responses
- **0 overlap** between the 30 and 60 source conversation identities
- **90 distinct source conversations; 1,088 observed speaker turns** (476 closing + 612 midpoint)

All private source ZIP files and identifying linkages remain outside Git. Source hashes and collection runs are recorded in `docs/VERIFIED_COLLECTION_2026-11-02.md` and `docs/VERIFIED_MID_DIALOGUE_COLLECTION_2026-11-02.md`.

Datasets: [ABCD (Chen et al., 2021)](https://aclanthology.org/2021.naacl-main.239/) and [MultiDoGO (Peskov et al., 2019)](https://aclanthology.org/D19-1460/).

## Methodology

1. The prediction target is the **last customer message in each saved chronological prefix**. This is a conversation ending in the 30-case cohort and a mid-conversation decision point in the 60-case cohort. Later agent/customer responses were withheld at both points.
2. Only the customer's message or observed customer-message history was scored; agent text was not mixed into the target sentiment.
3. TextBlob PatternAnalyzer lexical polarity: negative if score < -0.05, positive if score > 0.05, otherwise neutral. Two inputs were compared: target only vs all observed customer turns through the target.
4. An explicit, fixed lexical screen looked for issue-related terms (including *issue, broken, failed, still, error, refund, return*) and separate politeness/gratitude/rebuttal cues.
5. The 60-case cohort was deliberately stratified by five cue screens (12 cases per screen). Therefore screening prevalence and any cross-cohort contrasts are **not population estimates**.
6. The 30-case completed annotation workbooks were byte-identical; they cannot support independent agreement. The 60-case completed audit sheet records privacy approvals rather than dissatisfaction labels; usable independently verified dissatisfaction gold standards = **0**.

**Important:** The lexical issue screen may fire on ordinary procedural requests. Neither lexical issues nor neutral/positive scores establish a customer's satisfaction state.

## Verified aggregate counts

| Group | Distinct conversations | Visible turns | Target issue cues | Issue cues with neutral/positive polarity | Target polarity negative/neutral/positive | Target-vs-history polarity-category difference |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| Ending-turn pilot | 30 | 476 | 1 | 1 | 1 / 16 / 13 | 17 |
| Mid-dialogue pilot | 60 | 612 | 24 | 18 | 8 / 35 / 17 | 24 |
| ABCD midpoint (within 60) | 30 | 365 | 12 | 7 | 6 / 16 / 8 | 14 |
| MultiDoGO midpoint (within 60) | 30 | 247 | 12 | 11 | 2 / 19 / 9 | 10 |
| Combined convenience material | **90** | **1,088** | **25** | **19** | **9 / 51 / 30** | **41** |

Further **mid-dialogue-only** descriptive checks:

- 12 selected *polite + issue-cue* targets; 11 were neutral/positive by TextBlob.
- 27 midpoint targets tripped a predeclared broad behavioral alert cue (issue mention, explicit unresolved phrase, or rebuttal after prior customer issue); 21 of these were not negative by TextBlob. This broad cue is **not a BIRD classifier or ground-truth satisfaction decision**.
- Midpoint target-history polarity categories differed in 24/60 messages (40.0%).
- The 18/24 issue-cue/nonnegative-polarity fraction is 75.0% *within the intentionally enriched subset*; an approximate Wilson interval is 55.1%–88.0%, **not a generalization interval for support traffic**.
- Closing vs midpoint issue-cue counts (1/30 vs 24/60) are confounded by sampling strategy. Do not interpret as a causal effect of conversational position.

## What can and cannot be concluded

**Supported observation:** In this selected English-language support-dialogue material, an issue-related lexical cue can coexist with nonnegative TextBlob sentiment. Customer-history input changes TextBlob output categories on some cases. These observations motivate exploration of behavior-aware features.

**Not supported:** Whether the customer was actually dissatisfied; superiority of BIRD, GPT, Claude, VADER, or transformer models; recall, precision, F1, AUROC, calibration, or false-negative rate for customer dissatisfaction; multilingual or social-media transfer; deployment impact; general support-traffic prevalence.

A separate 30-case provisional annotation comparison (2 putative positive cases) exists but is **not a validated benchmark**. It is not pooled with these label-free findings.

## Decision and manuscript framing

The user elected to proceed with existing materials **without requesting licensed MSDialog data and without completing two new independent annotation workbooks**. MSDialog work is therefore out of scope (Issue #10 closed). We can continue drafting this as an **exploratory methodological feasibility study**. It should not be submitted as a validated BIRD performance-comparison article unless independently trustworthy reference labels and matched model experiments become available.

**Privacy:** The 60-case audit records user approval but includes repeated generic notes; 15 cases were previously flagged for priority manual inspection. These text records are not published here and were not sent to hosted LLM inference APIs. Only aggregated counts, methodology, and source bibliography are committed.
