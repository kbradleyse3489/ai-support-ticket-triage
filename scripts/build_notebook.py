"""Create and genuinely execute the review notebook; requires requirements-dev.txt."""
import os
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
nb=nbf.v4.new_notebook()
md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
nb.cells=[
md('# AI Support Ticket Triage & Quality Review System\n\n**Keisha Walker | Applied machine learning case study**\n\nThis executed notebook reproduces a local support-intent routing experiment on the public BANKING77 benchmark, then audits an assistive review workflow. It is not an IT production evaluation, financial-advice system, or autonomous agent. All summary/review fixtures are authored synthetic diagnostics, not external validation.\n\nThe notebook retrains both candidates from included data. No API keys or network calls are required after installation.'),
md('## 1. Environment and frozen decisions\n\nPython 3.12, seed 42. Word/bigram TF-IDF + logistic regression is the baseline. Word/bigram plus character 3–5-gram TF-IDF + sigmoid-calibrated LinearSVC is the richer candidate. The SVM calibrates with three training-only folds, including fold-local vocabularies. Hyperparameters, the nine-queue taxonomy, and review heuristics are defined before evaluation. Model selection uses validation intent macro-F1, not test results.'),
code("import os, sys, json, platform\nfrom pathlib import Path\nROOT = Path.cwd() if (Path.cwd() / 'src').exists() else Path.cwd().parent\nsys.path.insert(0, str(ROOT))\nos.chdir(ROOT)\nos.environ['MPLCONFIGDIR'] = '/tmp/ticket-triage-mpl'\nimport pandas as pd\nfrom IPython.display import display, Image\nfrom src.config import INTENT_TO_QUEUE\nprint('Python:', platform.python_version())\nprint('Support intents:', len(INTENT_TO_QUEUE), '| operational categories:', len(set(INTENT_TO_QUEUE.values())))"),
md('## 2. Data provenance and split hygiene\n\nSource: [PolyAI task-specific-datasets, banking_data](https://github.com/PolyAI-LDN/task-specific-datasets/tree/master/banking_data), CC BY 4.0; pinned commit and hashes are in data/DATA_PROVENANCE.md. The public corpus has 10,003 development rows and 3,080 official test rows. Collection method is not established here as verified production ticket data.\n\nOfficial test rows and labels are preserved. Test text is consulted for normalized exact-duplicate hygiene, removing overlapping development rows. Conflicting normalized development strings and repeated development rows are removed, then an 80/20 stratified train/validation split is made. This is not a claim that test content was never inspected; no test labels or scores select the model, threshold, taxonomy or rules. Near-duplicate and semantic leakage remain possible.'),
code("from src.train import main\nmetrics = main()\ndisplay(pd.DataFrame([metrics['splits']]).T.rename(columns={0:'Value'}))"),
md('## 3. Compare both candidates\n\nBoth test results are reported only after validation selection. Re-runs repair evaluation bookkeeping or documentation, not model choices. Macro-F1 gives equal weight to each of the 77 intent classes. Queue macro-F1 evaluates a separate, project-defined nine-category aggregation and must not replace intent results.'),
code("rows = []\nfor name, record in metrics['models'].items():\n    for split in ['validation', 'test']:\n        rows.append({'model': name, 'split': split, **record[split]})\ncomparison = pd.DataFrame(rows)\ndisplay(comparison[['model','split','macro_f1','accuracy','queue_macro_f1','log_loss','expected_calibration_error_10_bins']].round(4))\ndisplay(Image(filename=str(ROOT / 'reports/figures/model_comparison.png')))"),
md('## 4. Calibration and threshold selection\n\nThe confidence threshold is chosen from a 0.01 grid to maximize validation coverage while observed validation error is at most 5% and at least 100 predictions are accepted. This empirical target is not a guarantee. Confidence means estimated probability of the fine-grained intent, not the broad routing category. Top-label ECE uses 10 fixed-width bins. Wilson intervals summarize conditional test error but do not prove production reliability.'),
code("policy = metrics['policy']\nprint('Selected model:', metrics['selected_model'])\nprint('Validation-selected threshold:', policy['threshold'])\ndisplay(pd.DataFrame({'validation_score_only':policy['validation_score_only'], 'test_score_only':policy['test_score_only']}))\ndisplay(Image(filename=str(ROOT / 'reports/figures/coverage_error.png')))\ndisplay(Image(filename=str(ROOT / 'reports/figures/calibration.png')))"),
md('## 5. The actual application adds review rules\n\nThe app flags low confidence, close top-two intents, weak domain vocabulary, very short inputs, multiple-issue cues, security/dispute topics and summary truncation. Those rules reduce accepted coverage. They are workflow checks, not a calibrated out-of-domain detector and not proof of lower error. All final routing and resolution remain human decisions.'),
code("print(json.dumps(policy['test_full_review_policy'], indent=2))\nfrom src.triage import TriageEngine\nengine = TriageEngine()\nexample = 'My card has not arrived after two weeks. Can you check the delivery date?'\ndisplay(engine.predict(example))"),
md('## 6. Errors and uncertainty\n\nThe paired bootstrap resamples official test rows 500 times. Its interval is conditional on this benchmark, not a statement about future service desks. The fixed test includes normalized duplicate rows and similar paraphrases. The most frequent confusions and every per-class score are saved to CSV.'),
code("display(metrics['bootstrap'])\ndisplay(pd.read_csv(ROOT/'reports/candidate_per_class.csv',index_col=0).loc[list(INTENT_TO_QUEUE)].sort_values('f1-score').head(12))\ndisplay(pd.read_csv(ROOT/'reports/error_analysis.csv')[['text','intent','predicted_intent','confidence']].head(8))\ndisplay(Image(filename=str(ROOT/'reports/figures/queue_confusion.png')))\ndisplay(Image(filename=str(ROOT/'reports/figures/top_confusions.png')))"),
md('## 7. Summary and review diagnostics\n\nThe summary is not generated: it selects up to two source sentences using fixed issue/domain cue scores, preserves their order, and caps at 60 words. A lead-two-sentences baseline is included. The 36 synthetic messages and 99 expected phrases were authored independently before inference; these scripted expectations are not human judgements. Exact phrase retention and fully extractive output do not establish semantic quality. The 24 review challenges were also held out from tuning, but are still a small project-authored diagnostic set.'),
code("from src.evaluate_workflow import evaluate\nworkflow = evaluate()\ndisplay(pd.DataFrame(workflow['summary']).T)\ndisplay(pd.DataFrame(workflow['review_challenges']).T)\nsummary_rows=pd.read_csv(ROOT/'reports/summary_diagnostics.csv')\ndisplay(summary_rows[(summary_rows.method=='issue_focused') & ~summary_rows.all_key_phrases_retained][['id','summary','missing_phrases']].head(6))\nreview_rows=pd.read_csv(ROOT/'reports/review_diagnostics.csv')\ndisplay(review_rows[~review_rows.matches_expectation][['text','kind','expected_review','actual_review','confidence']])"),
md('## 8. Reproduce, inspect and use cautiously\n\nRun `python -m pytest -q` to verify split hygiene, saved metrics, inference, masking, extraction and Streamlit interaction. Run `streamlit run app.py` for the local demo. Models are persisted with joblib; never load untrusted pickle/joblib files.\n\nKnown failures include off-domain phrases with banking-like words, multi-issue messages without cue words, omitted summary details and overconfident mistakes. Independent exploratory probes such as “My graphics card is not working” can pass the review rules. No rules were retuned on those probes. No production deployment, real-world IT validation, human summary study or time-savings study is claimed.\n\nNext step: obtain an authorized, de-identified target-domain dataset; agree on the queue taxonomy and review cost; perform time-based and site-based validation; run a blinded human summary study; then test in shadow mode with audit logging and no automatic account actions.'),
]
nb.metadata={'kernelspec':{'display_name':'Python (ticket-triage)','language':'python','name':os.environ.get('TRIAGE_KERNEL','python3')},'language_info':{'name':'python','version':'3.12'}}
path=ROOT/'notebooks/01_support_ticket_triage.ipynb'
nbf.write(nb,path)
import sys
if '--in-process' in sys.argv:
    # Real sequential execution via IPython, without ZeroMQ / local-network sockets.
    # Useful in locked-down environments; never inject expected/canned results.
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    shell=InteractiveShell.instance()
    count=0
    for cell in nb.cells:
        if cell.cell_type != 'code': continue
        count+=1
        with capture_output() as captured:
            result=shell.run_cell(cell.source,store_history=True)
        cell.execution_count=count
        cell.outputs=[]
        if captured.stdout: cell.outputs.append(nbf.v4.new_output('stream',name='stdout',text=captured.stdout))
        if captured.stderr: cell.outputs.append(nbf.v4.new_output('stream',name='stderr',text=captured.stderr))
        for output in captured.outputs:
            cell.outputs.append(nbf.v4.new_output('display_data',data=output.data,metadata=output.metadata))
        error=result.error_before_exec or result.error_in_exec
        if error:
            nbf.write(nb,path)
            raise error
    nb.metadata['execution_method']='Sequential in-process IPython execution; outputs captured from actual execution. Standard nbclient cannot start ZeroMQ in the authoring sandbox.'
else:
    client=NotebookClient(nb,timeout=600,kernel_name=nb.metadata.kernelspec.name,resources={'metadata':{'path':str(ROOT)}})
    client.execute()
nbf.write(nb,path)
print('Executed',path,'with',sum(c.cell_type=='code' for c in nb.cells),'code cells')
