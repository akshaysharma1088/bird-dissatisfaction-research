# Verified BIRD mid-dialogue candidate collection — November 2, 2026

**Live GitHub Actions run:** https://github.com/akshaysharma1088/bird-dissatisfaction-research/actions/runs/41563966131

## Status: collection SUCCESS, human labels NONE

- 60 distinct customer-turn decision points from research-elicited customer/agent dialogues.
- 30 cases from ASAPP ABCD; 30 from Amazon Research MultiDoGO's software domain.
- 60 distinct source conversations **within this second sample**. Potential source overlap with the earlier 30-ending sample has **not** been independently cross-checked.
- All cases are **mid-conversation**. The selected customer turn has at least one subsequent agent turn and one later customer turn in the upstream corpus, but neither is included in the case's prediction-time prefix.
- Annotators receive two unfilled, source-blinded CSVs. Researcher-only linkage and screening categories are in a separate private artifact.
- All automatically masked excerpts are **UNREVIEWED**. Downloaded source corpora were not uploaded or committed.

### Candidate screening mix (per source)

| Lexical screen (NOT a human label) | ABCD | MultiDoGO | Total |
|---|---:|---:|---:|
| Polite + issue cue | 6 | 6 | 12 |
| Issue cue | 6 | 6 | 12 |
| Rebuttal cue | 6 | 6 | 12 |
| Polite-other cue | 6 | 6 | 12 |
| Control/other | 6 | 6 | 12 |
| **Total** | **30** | **30** | **60** |

Source-eligible conversation pool, based on the predefined mid-turn eligibility rules:
ABCD **9,143** conversations; MultiDoGO **4,445** conversations. These numbers do **not** represent dissatisfaction prevalence or any labels.

### Official-source checksums

| Source | SHA-256 |
|---|---|
| ABCD `abcd_v1.1.json.gz` | `2bdf53ac359543dcdc38d55bc6513e78df120363f8f44870716e909f4606de15` |
| MultiDoGO `software.tsv` | `3f90adc3c6c4f81edad4227e020d669c36c8f963061216b845ab5f853132de47` |

These are the same downloaded source checksums as the prior full-conversation collection.

### Private artifacts — short-lived

The successful GitHub Actions run created:

- `BIRD-60-midpoint-annotators-UNREVIEWED` (blinded A and B CSVs; manifest)
- `BIRD-60-midpoint-researcher-UNREVIEWED` (masked case JSONL, source linkage, privacy-review queue, manifest)

Both have **3-day retention** from the run (approximately November 5, 2026). Download and retain securely before they expire. Neither is cleared for sharing, third-party model input, or public publication.

### Required quality gates

1. Check source IDs for overlap against the first 30-case ending pilot. Deduplicate at **conversation** level before train/test splitting.
2. Perform manual case-by-case privacy and license review (automated redaction is imperfect).
3. Independently annotate two copies by **different human reviewers**, without source intent labels or screening cues. The first pilot's A/B files were byte-identical and do not constitute independent reliability evidence.
4. Adjudicate with target-turn evidence and report agreement; avoid assuming `please`/`thank you` indicate satisfaction or that a polite agent reply indicates issue resolution.
5. Report the cue-enriched sample as an **annotation development sample**, not a population-prevalence estimate or unbiased held-out test.
6. Obtain a sufficiently large, independently labeled, source- and conversation-grouped held-out benchmark before comparing BIRD, transformers, VADER, GPT and Claude.

**No human gold standards, model improvements or statistically robust empirical comparisons are claimed in this report.**
