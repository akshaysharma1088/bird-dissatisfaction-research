# BIRD privacy-audit-only exploratory analysis — 2026-11-02

## Research status

The uploaded *researcher-only privacy audit* marked all **60/60** mid-dialogue
cases as \`APPROVED - RESEARCH CLEARED\`. The same generic approval note appears
for all 60 cases. This is a recorded user clearance decision, **not evidence of
independent PII review**. Fifteen cases originally had higher-priority automated
privacy flags; retain caution before releasing transcripts to anyone else.

The audit summary originally displayed **60 human reference labels**, but the
workbook contains **privacy approvals only**; it has **no human dissatisfaction
labels, customer-satisfaction surveys, evidence-turn decisions, or independent
annotator results**. The corrected consolidated workbook reports **zero human
dissatisfaction reference labels**.

The user chose to continue without completion of the two independent
annotation workbooks. This means no human-supervised evaluation claim, F1,
accuracy, inter-rater reliability or BIRD superiority can be supported.

## Reproducible, offline descriptive findings

The mid-dialogue sample contains 60 distinct conversation prefixes:
30 ASAPP ABCD + 30 Amazon Research MultiDoGO software. Screening selection
was intentionally stratified into five lexical cue buckets of 12 examples
each. It is **not prevalence-representative**.

TextBlob PatternAnalyzer v0.19.0 applied to the target customer utterance and
separately to all visible prior customer messages plus the target; cutoffs
are > +0.05 positive, < -0.05 negative, otherwise neutral. Speaker turns after
the target are excluded.

| Measurement | Count |
|---|---:|
| Target issue-related lexical cue | 24 / 60 |
| Target issue cue + nonnegative/neutral-to-positive TextBlob | 18 / 24 |
| Polite + issue cue with nonnegative/neutral-to-positive TextBlob | 11 / 12 screened cases |
| Polite target utterance after customer history containing issue cue | 12 / 60 |
| Target polarity: negative / neutral / positive | 8 / 35 / 17 |
| Customer-history polarity: negative / neutral / positive | 11 / 20 / 29 |
| Strict explicit unresolved-expression screen | 2 / 60 |

**Interpretation:** the selected examples include textual issue signals even
where a lexical sentiment analyzer does not produce a negative score. This is
only a *cue/polarity discrepancy*, not verified dissatisfaction: a refund
question can be neutral and polite, and a technical issue does not establish
that a customer is unhappy. Counts from cue-enriched sampling cannot estimate
population prevalence. No TextBlob-vs-BIRD or LLM-vs-BIRD accuracy is measured.

## Reproduction (local research artifact required)

\`\`\`bash
python -m pip install textblob==0.19.0
python scripts/explore_midpoint_no_labels.py \
  BIRD-60-midpoint-researcher-UNREVIEWED.zip \
  --output-dir data/private/exploratory
\`\`\`

The private researcher ZIP comes from [GitHub Actions run
41563966131](https://github.com/akshaysharma1088/bird-dissatisfaction-research/actions/runs/41563966131)
and is intentionally **not** checked into Git. Output is only **source-blinded
case-level numerical/lexical features**, aggregate JSON, and no raw transcript
text/source IDs. Do not redistribute unreviewed text or send it to third-party
model APIs without separate appropriate permissions.

The uploaded completed audit workbook and consolidated Excel results were
retained privately and are **not in the GitHub repository**.

Source research datasets: [ABCD](https://github.com/asappresearch/abcd)
and [MultiDoGO](https://github.com/awslabs/multi-domain-goal-oriented-dialogues-dataset).
Both are research-elicited; neither is a sample of internal Salesforce help
agents.

## Publication framing

These numbers may support an *exploratory motivation/feasibility* paragraph.
They cannot support an empirical performance claim about BIRD, multilingual
generalization, external validity, fair customer-satisfaction prediction, or a
claim that an LLM outperforms a baseline. A future independent validation
design would still be needed for that.
