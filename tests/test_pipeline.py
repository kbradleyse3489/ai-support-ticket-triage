import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.config import ROOT, INTENT_TO_QUEUE, MAX_INPUT_CHARS
from src.triage import TriageEngine, normalize_text, redact_obvious_identifiers, extractive_summary, sentences

@pytest.fixture(scope='session')
def engine(): return TriageEngine()

def test_taxonomy_covers_every_label():
    labels=json.loads((ROOT/'data/raw/categories.json').read_text())
    assert set(labels)==set(INTENT_TO_QUEUE)
    assert len(set(INTENT_TO_QUEUE.values()))==9

def test_disjoint_normalized_splits():
    splits=[set(pd.read_csv(ROOT/f'data/{name}.csv').canonical) for name in ['train','validation','test']]
    assert not splits[0]&splits[1]
    assert not splits[0]&splits[2]
    assert not splits[1]&splits[2]

def test_original_test_unchanged():
    raw=pd.read_csv(ROOT/'data/raw/test.csv')
    processed=pd.read_csv(ROOT/'data/test.csv')
    assert raw.text.tolist()==processed.text.tolist()
    assert raw.category.tolist()==processed.intent.tolist()

def test_every_label_present_in_all_splits():
    for name in ['train','validation','test']:
        assert set(pd.read_csv(ROOT/f'data/{name}.csv').intent)==set(INTENT_TO_QUEUE)

def test_training_vocabulary_does_not_include_unique_test_sentinel():
    from src.train import make_models
    model=make_models()['Word TF-IDF logistic regression']
    model.set_params(tfidf__min_df=1)
    model.fit(['card never arrived','card delivery missing','cash withdrawal declined','cash not dispensed'],['card_arrival','card_arrival','declined_cash_withdrawal','declined_cash_withdrawal'])
    model.predict(['uniquetestsentinel card missing'])
    assert 'uniquetestsentinel' not in model.named_steps['tfidf'].vocabulary_

@pytest.mark.parametrize('invalid',['','  ',None,123])
def test_empty_invalid_inputs(engine,invalid):
    with pytest.raises(ValueError): engine.predict(invalid)

def test_length_limit(engine):
    with pytest.raises(ValueError): engine.predict('x'*(MAX_INPUT_CHARS+1))

def test_schema_and_probabilities(engine):
    out=engine.predict('My card has not arrived after two weeks.')
    assert out['suggested_intent'] in INTENT_TO_QUEUE
    assert out['suggested_category']==INTENT_TO_QUEUE[out['suggested_intent']]
    assert 0<=out['confidence']<=1
    assert 0<=out['top_two_margin']<=1
    assert isinstance(out['human_review'],bool)
    assert len(out['alternatives'])==3
    assert out['summary']

def test_probability_distribution(engine):
    p=engine.model.predict_proba(['My bank transfer is pending.'])[0]
    assert np.all(np.isfinite(p))
    assert np.all(p>=0)
    assert p.sum()==pytest.approx(1)

def test_masking():
    out=redact_obvious_identifiers('Email me at sample@example.com and use 4111 1111 1111 1111.')
    assert 'sample@example.com' not in out
    assert '4111' not in out
    assert '[EMAIL]' in out and '[LONG_NUMBER]' in out

def test_summary_empty():
    assert extractive_summary('')['text']==''

def test_summary_exact_copy_and_limit():
    text='Hello there. My card has not arrived. The delivery estimate was yesterday. Thank you.'
    result=extractive_summary(text)
    assert len(result['source_indices'])<=2
    assert all(s in sentences(text) for s in sentences(result['text']))

def test_summary_truncation():
    out=extractive_summary('Card '+('payment '*100)+'.')
    assert out['truncated']
    assert out['text'].endswith(' ...')
    assert len(out['text'].split())==61

def test_out_of_domain_review(engine):
    result=engine.predict('My printer cannot connect to the office network.')
    assert result['human_review']
    assert any('supported banking domain' in s for s in result['review_reasons'])

def test_security_review(engine):
    result=engine.predict('My card was stolen and my account has a fraudulent payment.')
    assert result['human_review']
    assert any('Security' in s for s in result['review_reasons'])

def test_multiple_issues_review(engine):
    result=engine.predict('My card is missing. Also, my bank transfer failed.')
    assert result['human_review']
    assert any('multiple issues' in s for s in result['review_reasons'])

def test_too_little_context_review(engine):
    assert engine.predict('card')['human_review']

def test_operating_threshold_matches_validation_selection(engine):
    curve=pd.read_csv(ROOT/'reports/threshold_validation.csv')
    eligible=curve[(curve.error_rate<=.05)&(curve.accepted>=100)]
    expected=float(eligible.sort_values(['coverage','threshold'],ascending=[False,True]).iloc[0].threshold) if len(eligible) else 1.01
    assert engine.threshold==expected

def test_frozen_fixtures_valid():
    summary=json.loads((ROOT/'data/summary_fixtures.json').read_text())
    assert len(summary)==36
    assert all(f['synthetic'] for f in summary)
    for f in summary:
        assert all(p.lower() in f['text'].lower() for p in f['expected_key_phrases'])
    challenge=json.loads((ROOT/'data/review_fixtures.json').read_text())
    assert len(challenge)==24
    assert all(f['synthetic'] for f in challenge)

def test_metrics_recompute_from_predictions():
    from sklearn.metrics import f1_score
    metrics=json.loads((ROOT/'reports/metrics.json').read_text())
    rows=pd.read_csv(ROOT/'reports/test_predictions.csv')
    actual=f1_score(rows.intent,rows.predicted_intent,average='macro')
    assert actual==pytest.approx(metrics['models'][metrics['selected_model']]['test']['macro_f1'])

def test_review_policy_error_is_end_to_end():
    metrics=json.loads((ROOT/'reports/metrics.json').read_text())
    frame=pd.read_csv(ROOT/'reports/test_predictions.csv')
    accepted=frame.loc[~frame.human_review]
    assert len(accepted)==metrics['policy']['test_full_review_policy']['accepted']
    assert int((~accepted.workflow_correct).sum())==metrics['policy']['test_full_review_policy']['errors']
