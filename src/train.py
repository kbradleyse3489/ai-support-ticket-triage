"""Reproducible train/validation/test experiment. Run: python -m src.train"""
from __future__ import annotations
import hashlib
import json
import os
import platform
import time
from datetime import datetime, timezone
os.environ.setdefault('MPLCONFIGDIR', '/tmp/ticket-triage-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib
import numpy as np
import pandas as pd
import sklearn
from scipy.sparse import csr_matrix
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, classification_report, log_loss, confusion_matrix
from sklearn.neighbors import NearestNeighbors
from .config import ROOT, SEED, VALIDATION_FRACTION, INTENT_TO_QUEUE, MAX_VALIDATION_ERROR, MIN_ACCEPTED_VALIDATION
from .triage import normalize_text, TriageEngine

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': '#ffffff', 'axes.labelcolor': '#163047'})
COLORS = ['#427c92', '#e29d47']

def dump(obj, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False))

def prepare_data():
    dev = pd.read_csv(ROOT / 'data/raw/train.csv').rename(columns={'category': 'intent'})
    test = pd.read_csv(ROOT / 'data/raw/test.csv').rename(columns={'category': 'intent'})
    for frame in (dev, test):
        assert not frame[['text','intent']].isna().any().any()
        frame['canonical'] = frame.text.map(normalize_text)
        frame['ticket_id'] = ['banking77_' + hashlib.sha256(t.encode()).hexdigest()[:12] for t in frame.text]
        frame['queue'] = frame.intent.map(INTENT_TO_QUEUE)
        assert frame.queue.notna().all()
    initial = len(dev)
    cross = dev.canonical.isin(set(test.canonical))
    overlap_rows = int(cross.sum())
    dev = dev.loc[~cross].copy()
    # Ambiguous normalized training strings are discarded, never assigned a majority label.
    conflicts = dev.groupby('canonical').intent.nunique()
    conflicting_keys = set(conflicts[conflicts > 1].index)
    conflicting_rows = int(dev.canonical.isin(conflicting_keys).sum())
    dev = dev.loc[~dev.canonical.isin(conflicting_keys)].copy()
    before = len(dev)
    dev = dev.drop_duplicates('canonical').copy()
    duplicate_rows = before - len(dev)
    train, val = train_test_split(dev, test_size=VALIDATION_FRACTION, random_state=SEED, stratify=dev.intent)
    audit = {
        'original_development_rows': initial, 'original_test_rows': len(test),
        'development_rows_removed_for_test_overlap': overlap_rows,
        'development_conflicting_rows_removed': conflicting_rows,
        'development_duplicate_rows_removed': duplicate_rows,
        'test_normalized_duplicate_rows_retained': int(test.canonical.duplicated().sum()),
        'train_rows': len(train), 'validation_rows': len(val), 'test_rows': len(test),
        'seed': SEED, 'normalization': 'lowercase, replace non-word runs with a space, strip',
        'official_test_unchanged': True,
        'note': 'Official test rows, order, and labels are retained; text-only duplicate hygiene removes development rows, not test rows. Similar paraphrases may remain.'
    }
    for name, frame in [('train',train),('validation',val),('test',test)]:
        frame.to_csv(ROOT / f'data/{name}.csv', index=False)
    assert not (set(train.canonical) & set(val.canonical))
    assert not (set(train.canonical) & set(test.canonical))
    assert not (set(val.canonical) & set(test.canonical))
    dump(audit, ROOT/'reports/split_audit.json')
    return train, val, test, audit

def make_models():
    baseline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1,2), min_df=2, sublinear_tf=True, max_features=40000)),
        ('classifier', LogisticRegression(C=4.0, max_iter=1200, random_state=SEED, solver='lbfgs')),
    ])
    candidate = Pipeline([
        ('features', FeatureUnion([
            ('word', TfidfVectorizer(ngram_range=(1,2), min_df=2, sublinear_tf=True, max_features=40000)),
            ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5), min_df=3, sublinear_tf=True, max_features=60000)),
        ])),
        ('classifier', LinearSVC(C=1.0, random_state=SEED, max_iter=5000)),
    ])
    # Entire vectorizer + classifier is cross-fitted. No validation/test text fits a vocabulary.
    calibrated = CalibratedClassifierCV(candidate, cv=StratifiedKFold(3, shuffle=True, random_state=SEED), method='sigmoid', ensemble=False, n_jobs=1)
    return {'Word TF-IDF logistic regression': baseline, 'Word + character calibrated SVM': calibrated}

def metric_pack(y, proba, classes):
    pred = classes[np.argmax(proba, axis=1)]
    conf = proba.max(axis=1)
    correct = pred == np.asarray(y)
    ece = 0.
    for lo, hi in zip(np.arange(0,1,.1), np.arange(.1,1.01,.1)):
        ix = (conf >= lo) & ((conf < hi) if hi < .999 else (conf <= hi))
        if ix.any(): ece += ix.mean() * abs(correct[ix].mean() - conf[ix].mean())
    queues_y = [INTENT_TO_QUEUE[v] for v in y]
    queues_p = [INTENT_TO_QUEUE[v] for v in pred]
    onehot = (np.asarray(y)[:,None] == classes[None,:]).astype(float)
    return {
        'accuracy': float(accuracy_score(y,pred)),
        'macro_f1': float(f1_score(y,pred,labels=classes,average='macro',zero_division=0)),
        'weighted_f1': float(f1_score(y,pred,average='weighted',zero_division=0)),
        'queue_accuracy': float(accuracy_score(queues_y,queues_p)),
        'queue_macro_f1': float(f1_score(queues_y,queues_p,average='macro',zero_division=0)),
        'log_loss': float(log_loss(y,proba,labels=classes)),
        'multiclass_brier_sum': float(np.mean(np.sum((proba-onehot)**2,axis=1))),
        'expected_calibration_error_10_bins': float(ece),
        'mean_confidence': float(conf.mean()),
    }

def wilson(errors, n):
    if not n: return [None,None]
    z=1.96; p=errors/n; denom=1+z*z/n
    center=(p+z*z/(2*n))/denom
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return [float(max(0,center-half)),float(min(1,center+half))]

def threshold_curve(y, proba, classes):
    pred=classes[np.argmax(proba,axis=1)]; confidence=proba.max(axis=1)
    rows=[]
    for threshold in np.round(np.arange(0,1.001,.01),2):
        accept=confidence>=threshold; n=int(accept.sum()); errors=int((pred[accept]!=np.asarray(y)[accept]).sum())
        rows.append({'threshold':float(threshold),'accepted':n,'coverage':float(accept.mean()),'errors':errors,'error_rate':float(errors/n) if n else None,'error_ci_low':wilson(errors,n)[0],'error_ci_high':wilson(errors,n)[1]})
    return pd.DataFrame(rows)

def main():
    start=time.perf_counter()
    for p in ['models','reports/figures','data']: (ROOT/p).mkdir(parents=True,exist_ok=True)
    train,val,test,audit=prepare_data()
    dump(INTENT_TO_QUEUE,ROOT/'data/intent_to_queue.json')
    models=make_models(); scores={}; predictions={}; fitted={}
    for name,model in models.items():
        print('Fitting:',name,flush=True)
        t=time.perf_counter(); model.fit(train.text,train.intent); fit_seconds=time.perf_counter()-t
        valproba=model.predict_proba(val.text)
        scores[name]={'validation':metric_pack(val.intent,valproba,model.classes_),'fit_seconds':fit_seconds}
        fitted[name]=model; predictions[name]={'validation':valproba}
        print(name, scores[name],flush=True)
    winner=max(scores, key=lambda n:scores[n]['validation']['macro_f1'])
    # Select model + threshold using validation ONLY, before examining test model scores.
    chosen=fitted[winner]; classes=chosen.classes_
    valcurve=threshold_curve(val.intent,predictions[winner]['validation'],classes)
    eligible=valcurve[(valcurve.error_rate<=MAX_VALIDATION_ERROR)&(valcurve.accepted>=MIN_ACCEPTED_VALIDATION)]
    threshold=float(eligible.sort_values(['coverage','threshold'],ascending=[False,True]).iloc[0].threshold) if len(eligible) else 1.01
    policy={'selected_model':winner,'selection_metric':'validation intent macro-F1','threshold':threshold,
            'validation_error_target':MAX_VALIDATION_ERROR,'minimum_accepted_validation':MIN_ACCEPTED_VALIDATION,
            'selection_rule':'Maximum validation coverage among 0.01-grid thresholds with empirical error <= 5% and at least 100 accepted; ties use lower threshold. If none qualifies, review all.',
            'no_guarantee':'5% is a validation selection target, not a guaranteed test or production error bound.',
            'extra_rules':'Margin <0.10, weak domain cues, <2 known terms, <4 words, possible multiple issues, security/dispute topics, or summary truncation trigger review independently.'}
    dump(policy, ROOT/'reports/operating_policy.json')
    vocab=set(fitted['Word TF-IDF logistic regression'].named_steps['tfidf'].vocabulary_)
    joblib.dump({'model':chosen,'vocabulary':vocab,'threshold':threshold,'policy':policy,'version':'1.0'},ROOT/'models/triage_model.joblib',compress=3)
    for name,model in fitted.items():
        t=time.perf_counter(); p=model.predict_proba(test.text); elapsed=time.perf_counter()-t
        predictions[name]['test']=p
        scores[name]['test']=metric_pack(test.intent,p,model.classes_)
        scores[name]['batch_test_inference_seconds']=elapsed
        slug='baseline' if name.startswith('Word TF-IDF') else 'candidate'
        pred=model.classes_[np.argmax(p,axis=1)]
        pd.DataFrame(classification_report(test.intent,pred,labels=model.classes_,output_dict=True,zero_division=0)).T.to_csv(ROOT/f'reports/{slug}_per_class.csv')
        print('Test:',name,scores[name]['test'],flush=True)
    p=predictions[winner]['test']; pred=classes[np.argmax(p,axis=1)]
    testcurve=threshold_curve(test.intent,p,classes)
    valcurve.to_csv(ROOT/'reports/threshold_validation.csv',index=False)
    testcurve.to_csv(ROOT/'reports/threshold_test.csv',index=False)
    threshold_selected=threshold
    def at_policy(frame):
        if threshold_selected>1: return {'threshold':threshold_selected,'accepted':0,'coverage':0.,'errors':0,'error_rate':None,'error_ci_low':None,'error_ci_high':None}
        return frame.loc[frame.threshold==threshold_selected].iloc[0].to_dict()
    policy['validation_score_only']=at_policy(valcurve); policy['test_score_only']=at_policy(testcurve)
    # Full end-to-end policy is evaluated separately from confidence-only coverage.
    engine=TriageEngine(); outputs=[]
    for text in test.text: outputs.append(engine.predict(text))
    accepted=np.array([not r['human_review'] for r in outputs]); workflow_pred=np.array([r['suggested_intent'] for r in outputs]); errors=int((workflow_pred[accepted]!=test.intent.to_numpy()[accepted]).sum()); n=int(accepted.sum())
    policy['test_full_review_policy']={'accepted':n,'coverage':float(accepted.mean()),'errors':errors,'error_rate':float(errors/n) if n else None,'error_wilson_95':wilson(errors,n)}
    dump(policy,ROOT/'reports/operating_policy.json')
    result=test[['ticket_id','text','intent','queue']].copy()
    result['predicted_intent']=pred; result['predicted_queue']=[INTENT_TO_QUEUE[v] for v in pred]
    result['confidence']=p.max(axis=1); result['correct']=pred==test.intent
    result['workflow_predicted_intent']=workflow_pred
    result['workflow_confidence']=[r['confidence'] for r in outputs]
    result['workflow_correct']=workflow_pred==test.intent.to_numpy()
    result['human_review']=[r['human_review'] for r in outputs]
    result['review_reasons']=['; '.join(r['review_reasons']) for r in outputs]
    result['summary']=[r['summary'] for r in outputs]
    result.to_csv(ROOT/'reports/test_predictions.csv',index=False)
    result.loc[~result.correct].sort_values('confidence',ascending=False).to_csv(ROOT/'reports/error_analysis.csv',index=False)
    # Text-only near-duplicate diagnostic, never used to tune model or policy.
    diagnostic=fitted['Word TF-IDF logistic regression'].named_steps['tfidf']
    nearest=NearestNeighbors(n_neighbors=1,metric='cosine',algorithm='brute').fit(diagnostic.transform(train.text))
    distances,indices=nearest.kneighbors(diagnostic.transform(test.text))
    near=result[['ticket_id','text','intent']].copy();near['nearest_train_text']=train.iloc[indices[:,0]].text.to_numpy();near['cosine_similarity']=1-distances[:,0]
    near.loc[near.cosine_similarity>=.95].to_csv(ROOT/'reports/near_duplicate_audit.csv',index=False)
    audit['test_rows_with_train_word_tfidf_cosine_ge_0_95']=int((near.cosine_similarity>=.95).sum())
    dump(audit,ROOT/'reports/split_audit.json')
    # Paired fixed-test bootstrap: uncertainty of the difference, not independent model CIs.
    basepred=fitted['Word TF-IDF logistic regression'].classes_[predictions['Word TF-IDF logistic regression']['test'].argmax(axis=1)]
    candpred=fitted['Word + character calibrated SVM'].classes_[predictions['Word + character calibrated SVM']['test'].argmax(axis=1)]
    rng=np.random.default_rng(SEED); diffs=[]; winner_f1=[]; y=test.intent.to_numpy()
    for _ in range(500):
        ix=rng.integers(0,len(y),len(y))
        b=f1_score(y[ix],basepred[ix],labels=classes,average='macro',zero_division=0)
        c=f1_score(y[ix],candpred[ix],labels=classes,average='macro',zero_division=0)
        diffs.append(c-b);winner_f1.append(c if winner=='Word + character calibrated SVM' else b)
    bootstrap={'replicates':500,'seed':SEED,'selected_model_macro_f1_percentile_95':[float(v) for v in np.quantile(winner_f1,[.025,.975])],
               'candidate_minus_baseline_macro_f1_percentile_95':[float(v) for v in np.quantile(diffs,[.025,.975])],
               'caveat':'Paired row bootstrap on this fixed benchmark; does not capture domain shift, training variability or correlated paraphrases.'}
    dump(bootstrap,ROOT/'reports/bootstrap.json')
    summary={'created_at_utc':datetime.now(timezone.utc).isoformat(),'dataset':'BANKING77 public banking intent benchmark','models':scores,'selected_model':winner,'splits':audit,'policy':policy,'bootstrap':bootstrap,
             'python':platform.python_version(),'sklearn':sklearn.__version__,'seed':SEED,'total_run_seconds':time.perf_counter()-start}
    dump(summary,ROOT/'reports/metrics.json')
    make_charts(scores,result,valcurve,testcurve,threshold,outputs)
    print(json.dumps(summary,indent=2),flush=True)
    return summary

def make_charts(scores,result,valcurve,testcurve,threshold,outputs):
    f=ROOT/'reports/figures'
    fig,ax=plt.subplots(figsize=(8,4.6));x=np.arange(2);w=.33
    names=list(scores)
    for k,split in enumerate(['validation','test']):
        vals=[scores[n][split]['macro_f1'] for n in names]
        bars=ax.bar(x+(k-.5)*w,vals,w,label=split.title(),color=COLORS[k])
        ax.bar_label(bars,labels=[f'{v:.3f}' for v in vals],padding=4)
    ax.set_xticks(x,['Word TF-IDF\nLogistic regression','Word + character TF-IDF\nCalibrated SVM']);ax.set_ylim(0,1);ax.set_ylabel('Intent macro-F1 (77 classes)');ax.set_title('Validate first; report on the official test set',loc='left',fontweight='bold');ax.legend(loc='lower right');fig.tight_layout();fig.savefig(f/'model_comparison.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.8))
    for frame,label,col in [(valcurve,'Validation',COLORS[0]),(testcurve,'Official test',COLORS[1])]:
        valid=frame[frame.accepted>0];ax.plot(valid.coverage*100,valid.error_rate*100,label=label,color=col,linewidth=2)
        if threshold<=1:
            row=frame[frame.threshold==threshold].iloc[0];ax.scatter([row.coverage*100],[row.error_rate*100],s=55,color=col,zorder=3)
    ax.axhline(5,linestyle='--',color='#87929c',label='5% validation selection target')
    ax.set(xlabel='Confidence-only coverage (%)',ylabel='Error among accepted predictions (%)',title=f'Coverage versus error at score thresholds | chosen t = {threshold:.2f}')
    ax.legend();ax.grid(alpha=.15);fig.tight_layout();fig.savefig(f/'coverage_error.png',dpi=180);plt.close(fig)
    queues=sorted(set(result.queue));cm=confusion_matrix(result.queue,result.predicted_queue,labels=queues);norm=cm/cm.sum(axis=1,keepdims=True)
    fig,ax=plt.subplots(figsize=(9,7));im=ax.imshow(norm,cmap='Blues',vmin=0,vmax=1)
    for i in range(len(queues)):
        for j in range(len(queues)): ax.text(j,i,str(cm[i,j]),ha='center',va='center',fontsize=8,color='white' if norm[i,j]>.5 else '#163047')
    ax.set_xticks(range(len(queues)),queues,rotation=42,ha='right',fontsize=8);ax.set_yticks(range(len(queues)),queues,fontsize=8);ax.set(xlabel='Suggested queue',ylabel='Reference queue',title='Operational queues | official test counts')
    fig.colorbar(im,ax=ax,fraction=.045,pad=.04,label='Share of reference queue');fig.tight_layout();fig.savefig(f/'queue_confusion.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.5));rows=[]
    for lo in np.arange(0,1,.1):
        mask=(result.confidence>=lo)&(result.confidence<(lo+.1) if lo<.9 else result.confidence<=1)
        if mask.any(): rows.append((result.loc[mask,'confidence'].mean(),result.loc[mask,'correct'].mean(),int(mask.sum())))
    ax.plot([0,1],[0,1],'--',color='#9ba3aa',label='Perfect calibration');ax.plot([r[0] for r in rows],[r[1] for r in rows],marker='o',color=COLORS[0],label='Selected model')
    for x,y,n in rows: ax.annotate(str(n),(x,y),xytext=(3,6),textcoords='offset points',fontsize=8)
    ax.set(xlim=(0,1),ylim=(0,1.05),xlabel='Mean predicted intent confidence',ylabel='Observed intent accuracy',title='Reliability on official test | labels show bin counts');ax.legend(loc='lower right');fig.tight_layout();fig.savefig(f/'calibration.png',dpi=180);plt.close(fig)
    conf=result.loc[~result.correct].groupby(['intent','predicted_intent']).size().sort_values(ascending=False).head(8)
    fig,ax=plt.subplots(figsize=(9,5)); labels=[a.replace('_',' ')+' → '+b.replace('_',' ') for a,b in conf.index]
    ax.barh(range(len(conf)),conf.values,color=COLORS[1]);ax.set_yticks(range(len(conf)),labels,fontsize=8);ax.invert_yaxis();ax.set(xlabel='Number of official test errors',title='Most frequent intent confusions');fig.tight_layout();fig.savefig(f/'top_confusions.png',dpi=180);plt.close(fig)

if __name__=='__main__': main()
