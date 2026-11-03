"""No customer data, identities or outcome labels in the test fixtures."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from explore_midpoint_no_labels import analyze_case, polarity, analyze_zip

def fixture(text="Thank you, but the software still crashes"):
    return {"blind_id":"BIRD-M-FICTION","target_turn_id":"t004","gold_labels":None,
            "turns":[{"role":"customer","text":"Hello"},
                     {"role":"agent","text":"What happened?"},
                     {"role":"customer","text":"The software is broken"},
                     {"role":"agent","text":"Please try restarting"},
                     {"role":"customer","text":text}]}

def test_polite_issue_is_not_gold():
    r=analyze_case(fixture(),"ABCD","polite_issue_cue")
    assert r["target_issue_cue"]==1 and r["target_politeness_cue"]==1
    assert r["human_gold_label"]=="NOT_AVAILABLE"
    assert r["polite_after_prior_issue"]==1
    assert "text" not in r and "source_id" not in r

def test_polite_after_prior_problem():
    r=analyze_case(fixture("Thanks for your help"),"MultiDoGO","polite_other_cue")
    assert r["target_issue_cue"]==0
    assert r["prior_customer_issue_cue"]==1
    assert r["polite_after_prior_issue"]==1

def test_thresholds():
    assert polarity(0.05)=="neutral"
    assert polarity(-0.05)=="neutral"
    assert polarity(0.06)=="positive"
    assert polarity(-0.06)=="negative"

def test_rejects_human_gold():
    f=fixture()
    f["gold_labels"]={"satisfaction":"positive"}
    try: analyze_case(f,"ABCD","control")
    except ValueError: pass
    else: raise AssertionError("Expected rejection")

def test_requires_customer_target():
    f=fixture()
    f["turns"][-1]["role"]="agent"
    try: analyze_case(f,"ABCD","control")
    except ValueError: pass
    else: raise AssertionError("Expected rejection")
