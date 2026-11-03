#!/usr/bin/env python3
"""Privacy-audit-only exploratory BIRD analysis. Never emits gold labels or accuracy.

Input: researcher-only zip from private GitHub Actions collection run.
Output: case-level lexical features keyed by blinded ID (NO transcript text
or source conversation ID), plus descriptive aggregate counts.
Run locally: pip install textblob==0.19.0
"""
import argparse
import csv
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from textblob import TextBlob
from collect_mid_dialogue import ISSUE, POLITE, REBUTTAL

GRAT = re.compile(r"\b(?:thanks|thank you|appreciate|grateful)\b",re.I)
EXPLICIT = re.compile(
    r"\b(?:still (?:not|doesn't|cannot|can't|broken|crash|fail)|"
    r"doesn't work|not working|never fixed|not resolved|unresolved|"
    r"keeps (?:crashing|failing)|again and again)\b",re.I)

def polarity(score,threshold=0.05):
    return "positive" if score>threshold else "negative" if score< -threshold else "neutral"

def analyze_case(case, corpus, cue):
    if case.get("gold_labels") is not None:
        raise ValueError("Unexpected human labels in screening artifact")
    turns=case["turns"]
    if not turns or turns[-1]["role"] != "customer":
        raise ValueError("Prediction point must be customer")
    utterance=turns[-1]["text"]
    customer=[t["text"] for t in turns if t["role"]=="customer"]
    target=round(float(TextBlob(utterance).sentiment.polarity),6)
    history=round(float(TextBlob(" ".join(customer)).sentiment.polarity),6)
    issue=bool(ISSUE.search(utterance))
    polite=bool(POLITE.search(utterance))
    prior_issue=bool(ISSUE.search(" ".join(customer[:-1])))
    return dict(
        blind_id=case["blind_id"], corpus=corpus,
        selection_cue_NOT_GOLD_LABEL=cue,
        target_turn=case["target_turn_id"], turns=len(turns),
        target_TextBlob_polarity=target, target_sentiment=polarity(target),
        customer_history_TextBlob_polarity=history, history_sentiment=polarity(history),
        target_issue_cue=int(issue), target_politeness_cue=int(polite),
        target_gratitude_cue=int(bool(GRAT.search(utterance))),
        target_rebuttal_cue=int(bool(REBUTTAL.search(utterance))),
        explicit_unresolved_phrase=int(bool(EXPLICIT.search(utterance))),
        prior_customer_issue_cue=int(prior_issue),
        issue_cue_with_nonnegative_polarity=int(issue and target>=-0.05),
        polite_issue_with_nonnegative_polarity=int(issue and polite and target>=-0.05),
        polite_after_prior_issue=int(polite and prior_issue),
        human_gold_label="NOT_AVAILABLE"
    )

def analyze_zip(path):
    with zipfile.ZipFile(path) as z:
        cases=[json.loads(s) for s in z.read("midpoint_cases_UNREVIEWED.jsonl").decode().splitlines()]
        links=list(csv.DictReader(z.read("source_linkage_RESEARCHER_ONLY.csv").decode("utf-8-sig").splitlines()))
    byid={r["blind_id"]:r for r in links}
    if len(byid)!=len(links) or len(cases)!=len(links) or set(byid)!={c["blind_id"] for c in cases}:
        raise ValueError("Missing or duplicated blinded case / source mapping")
    rows=[analyze_case(c,byid[c["blind_id"]]["source"],
            byid[c["blind_id"]]["screening_cue_NOT_A_LABEL"]) for c in cases]
    c=lambda field:sum(int(r[field]) for r in rows)
    summary=dict(
        conversations=len(rows), human_gold_labels=0,
        target_polarity_counts=dict(Counter(r["target_sentiment"] for r in rows)),
        history_polarity_counts=dict(Counter(r["history_sentiment"] for r in rows)),
        target_issue_cue=c("target_issue_cue"),
        target_politeness_cue=c("target_politeness_cue"),
        target_gratitude_cue=c("target_gratitude_cue"),
        prior_customer_issue_cue=c("prior_customer_issue_cue"),
        issue_cue_with_nonnegative_polarity=c("issue_cue_with_nonnegative_polarity"),
        polite_issue_with_nonnegative_polarity=c("polite_issue_with_nonnegative_polarity"),
        polite_after_prior_issue=c("polite_after_prior_issue"),
        explicit_unresolved_phrase=c("explicit_unresolved_phrase"),
        selection_buckets=dict(Counter(r["selection_cue_NOT_GOLD_LABEL"] for r in rows)),
        interpretation="Lexical cue-enriched exploratory screening; no dissatisfaction ground truth, no accuracy, no prevalence estimate."
    )
    return rows,summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("researcher_zip",type=Path)
    p.add_argument("--output-dir",type=Path,default=Path("data/private/exploratory"))
    args=p.parse_args()
    rows,summary=analyze_zip(args.researcher_zip)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with (args.output_dir/"case_features_PRIVATE.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir/"summary_DESCRIPTIVE_ONLY.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
