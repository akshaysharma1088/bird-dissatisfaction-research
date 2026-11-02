import gzip
import json
from pathlib import Path
from scripts.collect_pilot import sample_prefix, redacted, parse_abcd, parse_multidogo, select, create_outputs


def test_redaction():
    msg='my password is hunter2, call 312-555-1234 or a@b.com: order id 12345678'
    out=redacted(msg)
    assert 'hunter2' not in out and '312-555-1234' not in out
    assert 'a@b.com' not in out and '12345678' not in out


def test_prefix_excludes_future_agent():
    turns=[('customer','hello'),('agent','hello'),('customer','something broke'),
           ('agent','try reboot'),('customer','still not working'),('agent','future resolution')]
    rec=sample_prefix('x',turns,'ABCD')
    assert rec is not None and rec['turns'][-1][1]=='still not working'
    assert all('future' not in x[1] for x in rec['turns'])


def test_end_to_end_fixture(tmp_path):
    raw=tmp_path/'s';raw.mkdir()
    fake={'train':[],'dev':[],'test':[]}
    for i in range(20):
        fake['train'].append({'convo_id':i,'original':[
            ['customer','hello'],['agent','hello there'],['customer','software problem'],
            ['agent','try this'],['customer','thank you but issue persists'],['agent','goodbye']]})
    with gzip.open(raw/'abcd_v1.1.json.gz','wt') as f:json.dump(fake,f)
    with (raw/'software.tsv').open('w') as f:
        f.write('conversationId\tturnNumber\tutteranceId\tutterance\tauthorRole\n')
        for i in range(20):
            for j,(role,text) in enumerate([('customer','hello'),('agent','hello there'),
                 ('customer','my software crashed'),('agent','try rebooting'),
                 ('customer','thank you but it still crashes'),('agent','bye')]):
                f.write(f'{i}\t{j}\t{i}_{j}\t{text}\t{role}\n')
    out=tmp_path/'out'
    manifest=create_outputs(raw/'abcd_v1.1.json.gz',raw/'software.tsv',out,{'ABCD':'test','MultiDoGO':'test'})
    assert manifest['sample_size']==30
    for name in ('annotator_A.csv','annotator_B.csv'):
        t=(out/name).read_text(encoding='utf-8-sig')
        assert 'source_id' not in t and 'thank you but issue persists' in t
        assert 'expressed_dissatisfaction' in t
    assert len((out/'pilot_redacted_REVIEW_REQUIRED.jsonl').read_text().splitlines())==30
    assert len({x['source_id'] for x in parse_abcd(raw/'abcd_v1.1.json.gz')})==20
    assert len({x['source_id'] for x in parse_multidogo(raw/'software.tsv')})==20
    assert len(select(parse_abcd(raw/'abcd_v1.1.json.gz'),'ABCD'))==15
