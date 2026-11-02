#!/usr/bin/env python3
"""Collect 15+15 research-elicited dialogues. No customer satisfaction labels are inferred.

Source files are downloaded solely in the running worker's local workspace. Only
best-effort-redacted research excerpts are exported; human privacy review is required.
"""
import argparse
import csv
import gzip
import hashlib
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

SOURCES = {
    'ABCD': ('https://raw.githubusercontent.com/asappresearch/abcd/master/data/abcd_v1.1.json.gz', 30_000_000),
    'MultiDoGO': ('https://raw.githubusercontent.com/awslabs/multi-domain-goal-oriented-dialogues-dataset/master/data/unannotated/software.tsv', 10_000_000),
}
ROLES = {'customer':'customer','user':'customer','caller':'customer','client':'customer',
         'agent':'agent','assistant':'agent','representative':'agent','operator':'agent'}
FIELDS = ['blind_id','transcript','expressed_dissatisfaction','polarity',
          'behavior_tags','politeness','resolution','evidence_turns','notes']


def fetch(url, path, minimum):
    path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent':'BIRD academic data pilot v1'})
    with urllib.request.urlopen(req, timeout=150) as resp, path.open('wb') as out:
        while chunk := resp.read(1 << 20):
            out.write(chunk)
    if path.stat().st_size < minimum:
        raise ValueError(f'Incomplete download for {path.name}: {path.stat().st_size} bytes')
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def redacted(s):
    s = str(s)
    s = re.sub(r'https?://\S+', '[URL]', s, flags=re.I)
    s = re.sub(r'\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b', '[EMAIL]', s, flags=re.I)
    s = re.sub(r'\b(?:password|passcode|username|account id|user id|order id|my name|my address|my phone)\b\s*(?:is|:|=)?\s*[^.!?;,\n]+', '[REDACTED PERSONAL DETAIL]', s, flags=re.I)
    s = re.sub(r'(?<!\w)\+?\d[\d()\s.-]{7,}\d(?!\w)', '[PHONE_OR_NUMBER]', s)
    s = re.sub(r'\b\d{4,}\b', '[NUMBER]', s)
    return s


def sample_prefix(cid, turns, source):
    clean = [(role, text.strip()) for role, text in turns if role in ('agent','customer') and text.strip()]
    last_customer = max((i for i,(role,_) in enumerate(clean) if role == 'customer'), default=-1)
    if last_customer < 3: return None
    prefix = clean[:last_customer+1]
    if sum(role=='agent' for role,_ in prefix) < 2 or sum(role=='customer' for role,_ in prefix) < 2:
        return None
    if len(prefix[-1][1]) < 4: return None
    return {'source':source,'source_id':str(cid),'turns':prefix}


def parse_abcd(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data,dict) or not {'train','dev','test'}.intersection(data):
        raise ValueError('Unexpected ABCD format')
    for split, conversations in data.items():
        if split not in ('train','dev','test'):continue
        for conv in conversations:
            raw = [(str(role).lower().strip(),str(text)) for role,text in conv['original']]
            row = sample_prefix(conv['convo_id'],raw,'ABCD')
            if row: yield row


def parse_multidogo(path):
    groups = defaultdict(list)
    expected = ['conversationId', 'turnNumber', 'utteranceId', 'utterance', 'authorRole']
    with path.open(encoding='utf-8-sig', newline='') as f:
        for row_number, cells in enumerate(csv.reader(f, delimiter='\t'), start=1):
            if not cells or not any(v.strip() for v in cells):
                continue  # An empty line is not a malformed dialogue row.
            if cells[:5] == expected:
                continue  # Some releases include a column-name header.
            if len(cells) == 1 and cells[0].count(r'\t') >= 4:
                cells = cells[0].split(r'\t')
            if len(cells) < 5:
                # Do not print raw source text into a GitHub Actions log.
                first = cells[0] if cells else ''
                raise ValueError(
                    f'MultiDoGO unexpected row {row_number}: fields={len(cells)}, '
                    f'chars={len(first)}, literal_tabs={first.count(chr(92)+"t")}, '
                    f'commas={first.count(",")}, pipes={first.count("|")}')
            cid, turn_number, _ = cells[:3]
            # If text contains unquoted tabs, preserve them rather than silently
            # shifting the final speaker column.
            utterance = '\t'.join(cells[3:-1])
            raw = cells[-1].strip().lower()
            if raw not in ROLES:
                raise ValueError(f'Unrecognized MultiDoGO role at row {row_number}: {raw}')
            groups[cid].append((int(turn_number), ROLES[raw], utterance))
    for cid, turns in groups.items():
        ordered = [(role, text) for _,role,text in sorted(turns,key=lambda x:x[0])]
        row = sample_prefix(cid, ordered, 'MultiDoGO')
        if row: yield row


def select(rows, source, n=15):
    unique = {r['source_id']:r for r in rows}
    eligible = sorted(unique.values(), key=lambda r:hashlib.sha256(
        f'bird-2026-11-calibration:{source}:{r["source_id"]}'.encode()).hexdigest())
    if len(eligible) < n:raise ValueError(f'{source}: {len(eligible)} eligible conversations, need {n}')
    return eligible[:n]


def create_outputs(abcd, multidogo, root, hashes):
    selected = select(parse_abcd(abcd),'ABCD') + select(parse_multidogo(multidogo),'MultiDoGO')
    assert len(selected)==30 and len(set((r['source'],r['source_id']) for r in selected))==30
    root.mkdir(parents=True,exist_ok=True)
    blind, linkage, annot = [], [], []
    for i,r in enumerate(selected,1):
        blind_id = f'BIRD-P-{i:04d}'
        turns = [{'turn_id':f't{j:03}', 'role':role, 'text':redacted(text)}
                 for j,(role,text) in enumerate(r['turns'])]
        transcript = '\n'.join(f'[{t["turn_id"]} | {t["role"]}] {t["text"]}' for t in turns)
        if transcript.lstrip().startswith(('=','+','-','@')):transcript="'"+transcript
        blind.append({'blind_id':blind_id,'target_turn_id':turns[-1]['turn_id'],
                      'turns':turns,'human_gold_labels':None,
                      'privacy':'automated_redaction_only_review_required'})
        linkage.append({'blind_id':blind_id,'source':r['source'],'source_id':r['source_id']})
        annot.append({'blind_id':blind_id,'transcript':transcript})
    (root/'pilot_redacted_REVIEW_REQUIRED.jsonl').write_text(
        ''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in blind),encoding='utf-8')
    with (root/'source_linkage_PRIVATE.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=['blind_id','source','source_id']);w.writeheader();w.writerows(linkage)
    for name in ('annotator_A.csv','annotator_B.csv'):
        with (root/name).open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(annot)
    manifest={'source_datasets':{k:{'url':v[0],'sha256':hashes[k]} for k,v in SOURCES.items()},
              'sample_size':len(blind),'sample_by_source':{'ABCD':15,'MultiDoGO':15},
              'human_labels':'NONE','status':'Privacy review required before annotation or API submission',
              'sampling':'Deterministic SHA256 order on eligible conversations; calibration only',
              'transcript_context':'Truncated at final customer utterance; no future agent leakage'}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='data/private/collection')
    p.add_argument('--source-dir',default='data/private/source')
    p.add_argument('--download',action='store_true')
    a=p.parse_args();raw=Path(a.source_dir);out=Path(a.output)
    paths={'ABCD':raw/'abcd_v1.1.json.gz','MultiDoGO':raw/'software.tsv'}
    sha={}
    for src,(url,minsize) in SOURCES.items():
        path=paths[src]
        if a.download:sha[src]=fetch(url,path,minsize)
        else:
            if not path.is_file() or path.stat().st_size<minsize:
                raise SystemExit(f'Missing/incomplete official source: {path}')
            with path.open('rb') as f:sha[src]=hashlib.file_digest(f,'sha256').hexdigest()
    manifest=create_outputs(paths['ABCD'],paths['MultiDoGO'],out,sha)
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
