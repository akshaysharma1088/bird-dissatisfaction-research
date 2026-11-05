# Provisional TextBlob pilot — 2026-11-02

**Exploratory internal evidence only. NOT a validated BIRD result or an independent human gold standard.**

## Label integrity

The two user-supplied completed annotation workbooks are **byte-for-byte identical** (SHA-256 `54958655399e0c9f445c2da72d87b753c5a3d186ed014a41b71f598cdd7f6c12`). Accordingly, they are treated as **one provisional labeling source**; no independent inter-annotator agreement or Cohen's kappa can be claimed.

The private dataset contains 30 research-elicited dialogue prefixes (15 ABCD, 15 MultiDoGO), totaling 476 turns. The labels assign:

- Expressed dissatisfaction: **2 yes / 28 no**
- Polarity: **28 positive / 1 negative / 1 neutral**
- Resolution: **28 resolved**, two other statuses
- 20 evidence fields omit the target customer turn
- 17 resolved labels cite exclusively agent turns

These are review flags, not automatic corrections.

## Local-only exploratory classifier

Using TextBlob 0.19.0 PatternAnalyzer locally, no API requests or data sharing:

- Polarity **positive** when score > +0.05, **negative** when < -0.05, otherwise **neutral**.
- Final-customer-turn vs. all customer turns through the final turn evaluated separately (not including agent messages).
- For the *dissatisfaction proxy* alone, a negative TextBlob score was treated as a predicted dissatisfaction alert. This is **not** a trained dissatisfaction classifier.

### Alignment to provisional polarity

| Baseline | Accuracy | Macro-F1 (negative, neutral, positive) |
| --- | ---: | ---: |
| Always positive | **28/30 = 93.3%** | 0.322 |
| TextBlob on target customer turn | 14/30 = 46.7% | 0.251 |
| TextBlob on all previous customer turns | 19/30 = 63.3% | 0.259 |

### Dissatisfaction proxy confusion counts

| Baseline | TP | FP | FN | TN | Accuracy | Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Always not dissatisfied | 0 | 0 | 2 | 28 | **93.3%** | 0/2 |
| Negative target polarity | 0 | 1 | 2 | 27 | 90.0% | 0/2 |
| Negative full customer-history polarity | 0 | 4 | 2 | 24 | 80.0% | 0/2 |

The majority baseline **outperforms both lexical methods on accuracy solely because of class imbalance**. All methods miss the two provisionally positive dissatisfaction cases; with `n=2` positive cases the recall is far too uncertain to support any generalization.

**No BIRD, VADER, XLM-T, Twitter-RoBERTa, GPT or Claude results were produced** in this pilot. We cannot claim novelty, accuracy improvement, policy impact or cross-domain robustness from these numbers.

## Provenance, privacy and next step

All analysis was performed offline on the already-collected, automatically masked 30-case pilot. Source data and case-level outputs **were not uploaded** to GitHub. The private artifact from the original successful data-collection run remains the source of truth; manually audit every case before sharing text with annotators or third-party model APIs.

This pilot intentionally samples **conversation endings**. To test polite-but-unresolved dissatisfaction appropriately, the next study must include **mid-dialogue decision points** and genuinely independent labeling, with diverse negative examples and a held-out test set.

Code and workbook can be kept locally; the repository deliberately records only aggregate, source-blind findings. Source corpora: [ABCD](https://github.com/asappresearch/abcd), [MultiDoGO](https://github.com/awslabs/multi-domain-goal-oriented-dialogues-dataset).
