# BIRD collection and human-annotation protocol

## Collection

Run the private-repository workflow **BIRD - collect blinded support-dialogue pilot**.
The collector downloads the published, research-elicited ASAPP ABCD and Amazon
Research MultiDoGO software-domain corpora into the runner's local `data/private/`
directory. It chooses 15 eligible conversations from each corpus using
deterministic SHA-256 ordering. Model training, prompting, and gold-label
annotation are **not** part of this workflow.

The chosen prediction point is the final customer utterance. The collector
omits any future agent replies, retains preceding speaker turns, and masks
obvious email addresses, phone numbers, long numbers, account details and URLs.
This automatic masking is **not anonymization** and requires human review.

## Outputs

GitHub Actions uploads two short-lived, private artifacts:

1. **Blinded annotation pilot — UNREVIEWED**: A and B CSV sheets and a source
   manifest. Neither annotator sheet contains a source ID, model output, or
   pre-filled dissatisfaction label.
2. **Researcher-only source linkage — UNREVIEWED**: A mapping of blinded case
   IDs to exact source conversations, redacted transcript JSONL, and the
   source manifest. Never distribute this file to annotators or publish it.

The original raw source files are **not** included in artifacts or committed
to the repository. Both artifacts are retained for three days. Review
permissions and privacy *before* sharing even the masked sheets.

## Annotation rubric

Two independent human reviewers should label each transcript without
consulting the corpus's published intent labels or each other's work.

- `expressed_dissatisfaction`: yes / no / uncertain. Only explicit or
  context-supported customer dissatisfaction; politeness is not satisfaction.
- `polarity`: negative / neutral / positive / mixed / uncertain.
- `behavior_tags`: complaint, rebuttal, refusal, repeated_failure,
  escalation, gratitude, clarification, resolution_confirmation, other.
  Multiple tags allowed; annotate the *speech act*, not the perceived mood.
- `politeness`: present / absent / uncertain.
- `resolution`: resolved / unresolved / unknown. Do not infer resolution from
  an agent's polite response or from “thanks”.
- `evidence_turns`: IDs of turns supporting the decision; required for
  dissatisfaction or resolution claims.

Disagreeing reviewers must adjudicate while blinded to model predictions.
Record agreement statistics and preserve every original annotation. A
30-case pilot is for calibrating these guidelines, not establishing model
superiority. Do not call these annotations CSAT: the sources lack direct
customer self-reported satisfaction surveys.

## Source and research boundaries

- ABCD: https://github.com/asappresearch/abcd (MIT repository).
- MultiDoGO: https://github.com/awslabs/multi-domain-goal-oriented-dialogues-dataset
  (CDLA Permissive 1.0).
- Source SHA-256 digests are written into the manifest at download time.
- Research-elicited dialogue is **not** Salesforce/Amazon production support.
- No private customer records or API keys should be placed in the repo.
- Before using any source text with GPT or Haiku APIs, confirm license terms,
  the permitted data-transfer basis, and data handling expectations.
