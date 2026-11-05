# BIRD: polite but unresolved

**Detecting customer dissatisfaction that sentiment scores miss, in technical-support dialogues.**

A customer writes "Thanks for checking, but it still doesn't work." A sentiment lexicon reads
"thanks" and scores the message neutral or positive. This repository holds the code and protocol
for a pilot study that measures how often that happens, and whether simple behavioural cues
(repeated failures, rebuttals, politeness next to an issue) catch what polarity misses.

> **Paper.** A. Sharma, *Beyond Sentiment Polarity: Evaluating Behavior-Informed Customer
> Dissatisfaction Signals in Technical-Support Dialogues: An Exploratory Pilot Study.*
> Submitted to IET Software, 2026.

## What the pilot found

90 dialogue prefixes (1,088 turns) from two public, research-elicited corpora:
30 conversation endings and 60 midpoints chosen to over-represent ambiguous turns.
Reference labels: 34 `yes`, 56 `no_evidence` (expressed dissatisfaction), from a single annotator.

| Method | Macro-F1 | Recall (yes) |
| --- | ---: | ---: |
| TextBlob, target turn | 0.526 | 17.6% |
| VADER, target turn | 0.746 | 50.0% |
| Twitter-RoBERTa (off the shelf), target turn | 0.830 | 73.5% |
| TF-IDF + logistic regression, speaker-tagged prefix | 0.700 | 52.9% |
| Issue-keyword rule (control) | 0.786 | 61.8% |
| Sampling-stratum only (negative control, not deployable) | 0.790 | 76.5% |
| **BIRD-lite, 20 behavioural cues** | **0.843** | **76.5%** |
| **BIRD-lite hybrid (cues + speaker-tagged text)** | **0.845** | **79.4%** |

Supervised rows use five-fold out-of-fold predictions (seed 2026), one prefix per conversation.

- **Polarity masking.** Of 24 midpoint issue reports, TextBlob scored 75% neutral or positive,
  VADER 37.5% and Twitter-RoBERTa 16.7%.
- **A CPU model matches a transformer.** BIRD-lite beats speaker-tagged TF-IDF by +0.145
  Macro-F1 (95% paired bootstrap interval +0.051 to +0.245) and is level with Twitter-RoBERTa
  (+0.015, interval -0.023 to +0.062).
- **The controls matter.** A single keyword rule and a classifier that sees only the sampling
  stratum come within 0.06 of BIRD-lite. We recommend reporting both controls on any
  cue-enriched benchmark.

## Limits, stated plainly

- One annotator labelled all 90 prefixes; 14 flagged cases were rechecked by the same person,
  not blind. There is no inter-annotator agreement yet.
- The 60 midpoints were selected by keyword screens, so labels correlate with the sampling
  strata (the negative control shows how much).
- Both corpora are research-elicited English dialogues, not production support traffic, and
  carry no customer satisfaction ratings.

These are pilot estimates. A second, independent annotator is the first piece of future work.

## Repository layout

```
scripts/collect_pilot.py             30 conversation endings (15 ABCD, 15 MultiDoGO software)
scripts/collect_mid_dialogue.py      60 midpoints, 5 keyword strata x 6 per corpus
scripts/explore_midpoint_no_labels.py label-free descriptive screens
tests/                               15 tests on fictional fixtures only
docs/ANNOTATION_PROTOCOL.md          collection and labelling protocol (conversation endings)
docs/MID_DIALOGUE_PROTOCOL.md        midpoint selection protocol
docs/history/                        dated working notes, kept for provenance
.github/workflows/                   unit tests and the two collection jobs
```

## Reproduce the sample

Python 3.11 or newer. No API keys or paid services.

```bash
python -m pip install pytest textblob==0.19.0
python -m pytest tests -q
python scripts/collect_pilot.py --download --output data/private/collection
python scripts/collect_mid_dialogue.py --download --output data/private/midpoint
```

Selection is deterministic (SHA-256 ordering of conversation IDs), so the same 90 prefixes are
rebuilt from the same public releases. Each run records the SHA-256 digest of every source file
in its manifest, so you can confirm you used the same releases. Everything written to
`data/private/` is git-ignored.

**Not in this repository:** dialogue text, the case-to-source mapping and case-level labels.
They are kept out to respect the source licences and because automatic masking is not
anonymisation.

## Data sources

| Corpus | Use here | Licence |
| --- | --- | --- |
| [ABCD](https://github.com/asappresearch/abcd) (Chen et al., NAACL 2021) | 45 conversations | MIT |
| [MultiDoGO](https://github.com/awslabs/multi-domain-goal-oriented-dialogues-dataset), software domain (Peskov et al., EMNLP 2019) | 45 conversations | CDLA-Permissive-1.0 |

## Cite

See [`CITATION.cff`](CITATION.cff). A versioned archive with a DOI will be added on the first
release.

## Licence

Code: MIT ([LICENSE](LICENSE)). The source corpora keep their own licences.
