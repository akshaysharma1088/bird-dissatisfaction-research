"""Source-independent regression tests using fictional research conversations."""
import csv
import gzip
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from collect_mid_dialogue import bucket_for, candidate_turns, select_midpoints, write_outputs


def example(source, number, target='please, the software is still broken'):
    turns = [
        ('customer','hello, i need your help'),
        ('agent','sure, what is the issue'),
        ('customer', target),
        ('agent','i suggest reinstalling'),
        ('customer','okay, I will try that'),
        ('agent','anything else'),
        ('customer','will check tomorrow, thanks'),
    ]
    return {'source':source, 'source_id':str(number), 'turns':turns}


def test_bucket_categories_are_not_outcomes():
    assert bucket_for('Thank you, but the app still crashes') == 'polite_issue_cue'
    assert bucket_for('the software keeps crashing') == 'issue_cue'
    assert bucket_for('No, actually I wanted a different feature') == 'rebuttal_cue'
    assert bucket_for('Thank you, please help me') == 'polite_other_cue'
    assert bucket_for('I have a keyboard') == 'control'


def test_midpoint_is_not_final_and_excludes_future_agent():
    rec=example('ABCD','fixture')
    items=candidate_turns(rec)
    assert items
    assert all(c['target_index'] < len(rec['turns'])-2 for c in items)
    assert all(c['prefix'][-1][0]=='customer' for c in items)
    assert all(('i suggest reinstalling' not in [t for role,t in c['prefix']])
               for c in items if c['target_index'] == 2)


def test_one_selection_per_conversation_and_reproducible():
    records=[example('ABCD',i,[
        'the application still crashes','No, I need another option',
        'Thank you, please assist','I need a keyboard',
        'please, my error persists'][i % 5]) for i in range(30)]
    one,s1=select_midpoints(iter(records),'ABCD',10)
    two,s2=select_midpoints(iter(records),'ABCD',10)
    assert [(x['source_id'],x['target_index']) for x in one] == [(x['source_id'],x['target_index']) for x in two]
    assert len(set(x['source_id'] for x in one)) == 10
    assert s1==s2 and s1['eligible_conversations']==30


def test_full_pipeline_with_fake_corpora(tmp_path):
    abcd=tmp_path/'abcd_v1.1.json.gz'
    mdg=tmp_path/'software.tsv'
    payload={'train':[],'dev':[],'test':[]}
    for i in range(20):
        rec=example('ABCD',i)
        payload['train'].append({'convo_id':i, 'original':rec['turns']})
    with gzip.open(abcd,'wt',encoding='utf-8') as f:
        json.dump(payload,f)
    with mdg.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['conversationId','turnNumber','utteranceId','utterance','authorRole'])
        for i in range(20):
            for j,(role,text) in enumerate(example('MultiDoGO',i)['turns']):
                writer.writerow([f'case{i}',j,f'u{j}',text,role])
    dest=tmp_path/'out'
    manifest=write_outputs(abcd,mdg,dest,
             {'ABCD':'synthetic','MultiDoGO':'synthetic'},sample_per_source=5)
    assert manifest['sample_size']==10
    data=[json.loads(row) for row in (dest/'midpoint_cases_UNREVIEWED.jsonl').read_text().splitlines()]
    assert len(data)==10
    assert all(x['gold_labels'] is None and x['turns'][-1]['role']=='customer' for x in data)
    # Later turns must be excluded relative to each chosen prediction point.
    for case in data:
        texts=[t['text'] for t in case['turns']]
        assert 'anything else' not in texts
        assert 'will check tomorrow, thanks' not in texts
        if texts[-1]=='please, the software is still broken':
            assert 'i suggest reinstalling' not in texts
    with (dest/'annotator_A_UNREVIEWED.csv').open(encoding='utf-8-sig') as f:
        anns=list(csv.DictReader(f))
    assert len(anns)==10
    assert all(not x['expressed_dissatisfaction'] for x in anns)
    assert all('source_id' not in x and 'screening_cue' not in x for x in anns)
    with (dest/'source_linkage_RESEARCHER_ONLY.csv').open(encoding='utf-8-sig') as f:
        link=list(csv.DictReader(f))
    assert len(link)==10 and all('screening_cue_NOT_A_LABEL' in x for x in link)
