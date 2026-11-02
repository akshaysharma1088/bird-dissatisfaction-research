# BIRD — Behavior-Informed Recognition of Dissatisfaction

**Private academic research workspace** for behavior-aware detection of customer dissatisfaction across customer–agent conversations and social media.

## Current milestone: collect full support conversations

This repository contains a tested, standalone collector for a **30-conversation calibration pilot**:

- 15 conversations from [ASAPP ABCD](https://github.com/asappresearch/abcd), a research-elicited customer-service corpus.
- 15 software-domain conversations from [Amazon Research MultiDoGO](https://github.com/awslabs/multi-domain-goal-oriented-dialogues-dataset), another research-elicited corpus.
- Source-preserving speaker turns, deterministic selection, and automatic masking that **requires manual privacy review**.
- Two source-blinded, **unlabeled** human annotation CSVs, plus a separately held source-ID mapping.

The GitHub Actions collector runs automatically after the collection changes are merged into `main`, or manually from **Actions → BIRD - collect blinded support-dialogue pilot → Run workflow**. On success it creates two private artifacts with **3-day retention**. They are **UNREVIEWED** and must not be shared externally until a qualified researcher checks the text for sensitive details.

Full corpus files and case-to-source mapping must not be committed to Git. See [annotation and collection protocol](docs/ANNOTATION_PROTOCOL.md).

## Run it locally

Python 3.11 or newer recommended; no API keys or paid services required.

```bash
python -m pip install pytest
python -m pytest tests/test_collector.py -q
python scripts/collect_pilot.py --download --output data/private/collection
```

The collector fetches two large public data files and requires normal Internet access. `data/private/` is ignored by Git.

## Scientific integrity

**No human gold-standard labels, GPT/Haiku experimental results, multilingual performance comparisons, or proven BIRD improvements exist yet.** This 30-conversation package is designed for *annotation-guideline calibration*, not statistical evidence of BIRD superiority.

`polarity`, `expressed dissatisfaction`, `conversation resolution`, and direct customer satisfaction are distinct constructs. `thank you`/ `please` can be politeness alone; a `rejection` can be a benign refusal instead of a complaint.

Do not submit any research manuscript claiming empirical improvement until a larger independently adjudicated cross-domain benchmark and matched model evaluations have been completed.
