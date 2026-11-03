# BIRD mid-conversation candidate pilot

## Scientific purpose

The initial 30 ABCD/MultiDoGO cases were sampled at the final customer utterance, where
courtesy closings dominated and provisional labels were severely imbalanced. The new
**60-decision-point calibration sample** targets customer turns during dialogues, before
later agent/customer responses, to reduce closure bias and study prospective alerts.

This is **cue-enriched sampling**, not a representative sample or a dissatisfaction
reference dataset. It is explicitly designed to find ambiguous, informative language
while also retaining ordinary requests and control utterances. The lexical cues used
to *select* examples are not supervision, predictions, or ground-truth labels.

## Sample construction

- 30 unique ABCD conversations; 30 unique MultiDoGO software-domain conversations.
- At most one selected target per conversation (no conversation-level duplication).
- A candidate must be a customer utterance after at least one prior agent turn
  and one other customer turn. Another agent and customer turn must occur later.
- Transcript includes all customer and agent turns up to **and including** the
  selected customer utterance. Any later response is withheld.
- Candidate cues (in descending precedence): polite issue mention, issue mention,
  rebuttal/contradiction, other polite message, other/control.
- Per source, target six candidates from each of five cue groups; stable SHA-256
  sampling fills shortages and the manifest reports actual category counts.
- Candidate cues remain **only** in the private source mapping; annotators see
  neither the source identity nor the cue used to select the example.
- The initial 30 closing-turn dataset is a **different screening sample**; do not
  assume that conversation IDs do not overlap without a researcher-only linkage audit.

## Researcher workflow

1. Review private-run GitHub Actions outputs, confirm source hashes, inclusion counts
   and no exposed future agent responses.
2. Perform human privacy review and revise/redact or exclude problematic cases.
   Automated masks are best-effort and do **not** certify anonymity.
3. Distribute redacted A and B workbooks to **two distinct human annotators**.
   Independent review must be verifiable; identical copied files cannot establish
   inter-annotator reliability.
4. Label target-turn **expressed dissatisfaction**, polarity, behavior, politeness,
   and issue-resolution evidence. Use uncertain/unknown when unsupported.
   Polite language alone is not evidence of resolution.
5. Preserve initial labels, adjudicate with cited turn IDs, and publish agreement
   and disagreement statistics only after independent rating.
6. Compare baselines and BIRD only after labels are frozen, separately reporting
   the calibration and held-out evaluation sets.

## Data provenance and privacy

Sources: ASAPP ABCD and Amazon Research MultiDoGO, both research-elicited;
**neither is a sample of actual Salesforce production-agent conversations**.
Only the two private GitHub Actions artifacts contain excerpts. They expire in
three days. Source corpora and private linkage files stay out of Git history.
Do not upload case text into GitHub issues, public repositories or external LLM
services without privacy review and license/permitted-transfer assessment.

Run with Python 3.11+:

\`\`\`bash
python scripts/collect_mid_dialogue.py --download --n-per-source 30
\`\`\`

No model keys, simulated outcome labels, or paid inference are needed for collection.
