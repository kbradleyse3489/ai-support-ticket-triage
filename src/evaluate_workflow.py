"""One-shot diagnostics. Fixtures are never used to select the model or threshold."""
import json
import re
import pandas as pd
from .config import ROOT
from .triage import TriageEngine, extractive_summary, sentences
from .train import dump

def evaluate():
    summary_fixtures=json.loads((ROOT/'data/summary_fixtures.json').read_text())
    rows=[]
    for f in summary_fixtures:
        for method in ['lead_two','issue_focused']:
            output=' '.join(sentences(f['text'])[:2]) if method=='lead_two' else extractive_summary(f['text'])['text']
            found=[phrase.lower() in output.lower() for phrase in f['expected_key_phrases']]
            source_parts=sentences(f['text']); output_parts=sentences(output)
            copied=all(s in source_parts for s in output_parts)
            rows.append({'id':f['id'],'method':method,'summary':output,'matched_key_phrases':sum(found),'total_key_phrases':len(found),'key_phrase_recall':sum(found)/len(found),'all_key_phrases_retained':all(found),'exact_sentence_copy':copied,'word_ratio':len(output.split())/len(f['text'].split()),'missing_phrases':'; '.join(p for p,ok in zip(f['expected_key_phrases'],found) if not ok)})
    frame=pd.DataFrame(rows);frame.to_csv(ROOT/'reports/summary_diagnostics.csv',index=False)
    summary={}
    for method,group in frame.groupby('method'):
        summary[method]={'fixtures':len(group),'matched_key_phrases':int(group.matched_key_phrases.sum()),'total_key_phrases':int(group.total_key_phrases.sum()),'micro_key_phrase_recall':float(group.matched_key_phrases.sum()/group.total_key_phrases.sum()),'complete_key_phrase_retention':float(group.all_key_phrases_retained.mean()),'fully_extractive_summary_rate':float(group.exact_sentence_copy.mean()),'mean_summary_to_input_word_ratio':float(group.word_ratio.mean())}
    engine=TriageEngine();challenge=json.loads((ROOT/'data/review_fixtures.json').read_text()); review_rows=[]
    for f in challenge:
        r=engine.predict(f['text'])
        review_rows.append({'id':f['id'],'text':f['text'],'kind':f['kind'],'expected_review':f['expected_review'],'expected_reason':f['expected_reason'],'actual_review':r['human_review'],'matches_expectation':f['expected_review']==r['human_review'],'confidence':r['confidence'],'predicted_intent':r['suggested_intent'],'review_reasons':'; '.join(r['review_reasons']),'rationale':f['rationale']})
    reviews=pd.DataFrame(review_rows);reviews.to_csv(ROOT/'reports/review_diagnostics.csv',index=False)
    bykind={kind:{'examples':len(group),'flagged_for_review':int(group.actual_review.sum()),'matches_authored_expectation':int(group.matches_expectation.sum())} for kind,group in reviews.groupby('kind')}
    result={'summary':summary,'review_challenges':bykind,'notes':['All fixtures are project-authored synthetic diagnostics, not real customer tickets.','Expected phrases and review flags were frozen independently before inference, not supplied by human raters.','Lexical retention is not semantic correctness, actionability, or professional summary quality.','Copying a sentence prevents newly generated words, but can still omit critical context or preserve a false user statement.','Challenge results are observations only; no model, threshold, extractor, or review rules were retuned after viewing fixture scores.']}
    dump(result,ROOT/'reports/workflow_metrics.json')
    from .report_figures import make_extra_figures
    make_extra_figures()
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__': evaluate()
