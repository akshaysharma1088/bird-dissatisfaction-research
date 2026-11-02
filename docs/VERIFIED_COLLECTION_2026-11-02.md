# BIRD complete-dialogue calibration collection — verified 2026-11-02

**GitHub Actions run:** https://github.com/akshaysharma1088/bird-dissatisfaction-research/actions/runs/41509778593

## Verified outcome

- Workflow status: completed successfully.
- 30 unique dialogue prefixes collected: **15 ABCD** plus **15 MultiDoGO software**.
- Context truncated after the final customer utterance, so no later agent answer can leak into classification.
- Two source-blinded, blank annotation sheets and a researcher-only source mapping were uploaded to **private** GitHub Actions artifacts; neither artifact contains the complete downloaded raw corpora.
- **No human ground-truth labels** were created. The calibration sample is not yet a model-comparison benchmark.

## Source provenance

| Dataset | Public upstream source | SHA-256 of downloaded bytes |
| --- | --- | --- |
| ABCD | https://raw.githubusercontent.com/asappresearch/abcd/master/data/abcd_v1.1.json.gz | `2bdf53ac359543dcdc38d55bc6513e78df120363f8f44870716e909f4606de15` |
| MultiDoGO software | https://raw.githubusercontent.com/awslabs/multi-domain-goal-oriented-dialogues-dataset/master/data/unannotated/software.tsv | `3f90adc3c6c4f81edad4227e020d669c36c8f963061216b845ab5f853132de47` |

## Artifacts (private repository; retention three days)

- `BIRD-30-blinded-annotation-pilot-UNREVIEWED`
- `BIRD-30-researcher-only-UNREVIEWED`

Both were confirmed created and accessible to the repository's authorized users. Download them from the run's **Artifacts** section. **Human privacy review is required before sharing these files, even with annotators.** Never commit these artifacts or submit the text to third-party LLM services without authorization.

## Next evidence gates

1. Manually inspect redaction, source permissions and participant identifiers.
2. Have two independent human annotators label the same cases while blinded to source intent tags and model predictions.
3. Measure agreement and adjudicate disagreements with evidence-turn IDs.
4. Run a larger, held-out cross-domain sample; the 30-case pilot is for rubric calibration.
5. Separately evaluate models on this annotated dataset. Do not claim BIRD superiority from collection success alone.
