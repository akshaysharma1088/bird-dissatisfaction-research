#!/usr/bin/env python3
"""Select mid-dialogue decision points for blinded, human-led BIRD annotation.

The selection buckets are lexical *screening signals*, never satisfaction,
dissatisfaction, sentiment, or resolution labels. All transcripts require
manual privacy review. Source data stay in the runner's ignored directory.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from collect_pilot import SOURCES, fetch, redacted, parse_abcd, parse_multidogo

SEED = 'bird-midpoint-screen-2026-11-v1'
BUCKETS = ('polite_issue_cue', 'issue_cue', 'rebuttal_cue',
           'polite_other_cue', 'control')
ISSUE = re.compile(
    r"\b(?:issue|issues|problem|problems|error|errors|broken|"
    r"crash(?:es|ed|ing)?|fail(?:ed|ure|s|ing)?|refund|return|"
    r"delay(?:ed|s)?|wrong|missing|cannot|can't|couldn't|"
    r"won't|doesn't|didn't|unable|stopped|still|again|"
    r"not working|not open|unresolved|not fixed)\b", re.I)
REBUTTAL = re.compile(
    r"^\s*(?:no|nah|not really|actually|but|however)\b|"
    r"\b(?:but|however|already|i tried|that's not|that is not)\b", re.I)
POLITE = re.compile(
    r"\b(?:please|thanks|thank you|appreciate|sorry|"
    r"could you|would you|if you don't mind)\b", re.I)
ANNOTATION_FIELDS = [
    'blind_id', 'transcript', 'expressed_dissatisfaction', 'polarity',
    'behavior_tags', 'politeness', 'resolution_at_target',
    'evidence_turns', 'confidence', 'notes',
]


def bucket_for(text):
    """A non-gold candidate-selection signal; never use it as an outcome."""
    issue, polite = bool(ISSUE.search(text)), bool(POLITE.search(text))
    if issue and polite:
        return 'polite_issue_cue'
    if issue:
        return 'issue_cue'
    if REBUTTAL.search(text):
        return 'rebuttal_cue'
    if polite:
        return 'polite_other_cue'
    return 'control'


def stable_key(source, cid, index):
    return hashlib.sha256(
        f'{SEED}:{source}:{cid}:{index}'.encode('utf-8')
    ).hexdigest()


def candidate_turns(record):
    """Yield at most one candidate per lexical bucket per conversation.

    Context ends at a customer turn *before* a later agent response and a
    subsequent customer turn. This avoids both terminal-closure bias and
    leakage of future support-agent messages.
    """
    full = record['turns']
    if len(full) < 6:
        return []
    choices = {}
    for j, (role, text) in enumerate(full):
        if role != 'customer' or j >= len(full)-2 or len(text.strip()) < 7:
            continue
        prefix = full[:j+1]
        if sum(r == 'customer' for r,_ in prefix) < 2:
            continue
        if sum(r == 'agent' for r,_ in prefix) < 1:
            continue
        future = full[j+1:]
        if not any(r == 'agent' for r,_ in future) or not any(r == 'customer' for r,_ in future):
            continue
        category = bucket_for(text)
        item = {
            'source':record['source'],
            'source_id':record['source_id'],
            'target_index':j,
            'prefix':prefix,
            'bucket':category,
            'sort_key':stable_key(record['source'], record['source_id'], j),
        }
        if category not in choices or item['sort_key'] < choices[category]['sort_key']:
            choices[category] = item
    return list(choices.values())


def select_midpoints(records, source, sample_size=30):
    """Stratified cue enrichment, with stable fallback and no repeated chats."""
    pool = defaultdict(list)
    eligible_ids = set()
    for record in records:
        if record['source'] != source:
            raise ValueError('Unexpected corpus identity')
        candidates = candidate_turns(record)
        if candidates:
            eligible_ids.add(record['source_id'])
        for item in candidates:
            pool[item['bucket']].append(item)
    if len(eligible_ids) < sample_size:
        raise ValueError(f'{source}: only {len(eligible_ids)} eligible conversations, need {sample_size}')
    for bucket in BUCKETS:
        pool[bucket].sort(key=lambda x:x['sort_key'])
    selected, used = [], set()
    # Intentional equal target per cue bucket (screening, not balanced labels).
    base, remainder = divmod(sample_size, len(BUCKETS))
    quotas = {b:base + (i < remainder) for i,b in enumerate(BUCKETS)}
    for bucket in BUCKETS:
        for c in pool[bucket]:
            if quotas[bucket] <= 0:
                break
            if c['source_id'] in used:
                continue
            selected.append(c);used.add(c['source_id'])
            quotas[bucket] -= 1
    if len(selected) < sample_size:
        rest = sorted((x for items in pool.values() for x in items),
                      key=lambda x:x['sort_key'])
        for c in rest:
            if c['source_id'] not in used:
                selected.append(c);used.add(c['source_id'])
                if len(selected) == sample_size:
                    break
    if len(selected) != sample_size:
        raise ValueError(f'{source}: unable to select {sample_size} unique eligible conversations')
    return selected, {
        'eligible_conversations':len(eligible_ids),
        'screening_pool_by_cue':{b:len(pool[b]) for b in BUCKETS},
        'selected_by_cue':dict(sorted(Counter(x['bucket'] for x in selected).items())),
        'quota_shortfall_before_fallback':{b:n for b,n in quotas.items() if n},
    }


def csv_safe(text):
    """Protect future spreadsheet display, not a substitute for PII masking."""
    return "'"+text if text[:1] in ('=', '+', '-', '@') else text


def write_outputs(abcd_path, multidogo_path, dest, sha, sample_per_source=30):
    abc, a_stats = select_midpoints(parse_abcd(abcd_path), 'ABCD', sample_per_source)
    mdg, m_stats = select_midpoints(parse_multidogo(multidogo_path), 'MultiDoGO', sample_per_source)
    # Alternate by source to avoid making source recoverable from case IDs.
    chosen = [item for pair in zip(abc, mdg) for item in pair]
    assert len(chosen) == sample_per_source * 2
    assert len({(x['source'], x['source_id']) for x in chosen}) == len(chosen)
    dest.mkdir(parents=True,exist_ok=True)
    cases, linkage, annotation_rows, qc_rows = [], [], [], []
    for n,c in enumerate(chosen, 1):
        blind_id = f'BIRD-M-{n:04d}'
        turns = [{'turn_id':f't{j:03d}', 'role':role, 'text':redacted(text)}
                 for j,(role,text) in enumerate(c['prefix'])]
        # Every candidate is a customer utterance; last is the prediction point.
        assert turns[-1]['role'] == 'customer' and len(turns) >= 3
        transcript = '\n'.join(f'[{t["turn_id"]} | {t["role"]}] {t["text"]}' for t in turns)
        cases.append({
            'blind_id':blind_id, 'target_turn_id':turns[-1]['turn_id'],
            'turns':turns, 'gold_labels':None,
            'privacy_status':'UNREVIEWED_AUTOMATIC_MASKING_ONLY',
        })
        linkage.append({
            'blind_id':blind_id, 'source':c['source'], 'source_id':c['source_id'],
            'source_target_index':c['target_index'], 'screening_cue_NOT_A_LABEL':c['bucket'],
        })
        annotation_rows.append({'blind_id':blind_id, 'transcript':csv_safe(transcript)})
        qc_rows.append({
            'blind_id':blind_id, 'turns':len(turns),
            'has_masked_tokens':any('[' in x['text'] and ']' in x['text'] for x in turns),
            'reviewed_by_human':'NO',
        })
    (dest/'midpoint_cases_UNREVIEWED.jsonl').write_text(
        ''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in cases),encoding='utf8')
    for filename,columns,rows in [
        ('source_linkage_RESEARCHER_ONLY.csv',list(linkage[0]),linkage),
        ('privacy_review_RESEARCHER_ONLY.csv',list(qc_rows[0]),qc_rows),
        ('annotator_A_UNREVIEWED.csv',ANNOTATION_FIELDS,annotation_rows),
        ('annotator_B_UNREVIEWED.csv',ANNOTATION_FIELDS,annotation_rows),
    ]:
        with (dest/filename).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=columns)
            writer.writeheader();writer.writerows(rows)
    manifest={
        'study_phase':'mid_conversation_lexically_enriched_annotation_pilot',
        'sample_size':len(chosen),
        'by_source':{'ABCD':sample_per_source,'MultiDoGO':sample_per_source},
        'source_sha256':sha,
        'source_selection_summary':{'ABCD':a_stats,'MultiDoGO':m_stats},
        'sampling_seed':SEED,
        'selection_is_a_label':'NO',
        'gold_labels':'NONE',
        'privacy_status':'NOT REVIEWED — do not share with external reviewers or API vendors',
        'future_turn_policy':'Only turns through target customer utterance; later agent/customer replies excluded',
        'sampling_bias':'Lexical cue enrichment, not prevalence-representative',
    }
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    return manifest


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-dir',default='data/private/source')
    ap.add_argument('--output',default='data/private/midpoint')
    ap.add_argument('--download',action='store_true')
    ap.add_argument('--n-per-source',type=int,default=30)
    args=ap.parse_args()
    if args.n_per_source < 1:
        raise SystemExit('n-per-source must be at least 1')
    raw=Path(args.source_dir);dest=Path(args.output)
    paths={'ABCD':raw/'abcd_v1.1.json.gz','MultiDoGO':raw/'software.tsv'}
    sha={}
    for label,(url,min_bytes) in SOURCES.items():
        path=paths[label]
        if args.download:
            sha[label]=fetch(url,path,min_bytes)
        else:
            if not path.is_file() or path.stat().st_size<min_bytes:
                raise SystemExit('Official source missing or incomplete; use --download')
            with path.open('rb') as f:
                sha[label]=hashlib.file_digest(f,'sha256').hexdigest()
    manifest=write_outputs(paths['ABCD'], paths['MultiDoGO'], dest, sha, args.n_per_source)
    print(json.dumps(manifest,indent=2))


if __name__ == '__main__':
    main()
