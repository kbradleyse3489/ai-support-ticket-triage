"""Build the README from measured results, avoiding copied/stale headline numbers."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'reports/metrics.json').read_text());w=json.loads((R/'reports/workflow_metrics.json').read_text())
p=m['policy'];s=m['splits'];base=m['models']['Word TF-IDF logistic regression'];cand=m['models']['Word + character calibrated SVM'];full=p['test_full_review_policy'];score=p['test_score_only'];summary=w['summary']['issue_focused']
text=f'''# AI Support Ticket Triage & Quality Review System

**Keisha Walker · Applied machine learning · Assistive support operations**

A complete, locally runnable case study that turns an English support message into a suggested operational category, fine-grained intent, confidence estimate, extractive summary preview, and human-review flag. A Streamlit demo makes the result inspectable; a reproducible experiment measures where it works and where it fails.

> **Scope matters:** this is a public BANKING77 banking-support intent benchmark, not an employer IT-ticket dataset or a production deployment. The source does not establish verified production provenance. No private tickets, paid APIs, API keys, account access, financial advice, or account actions are used. Summary and review diagnostics are synthetic, project-authored checks, not real-world or human validation.

## Start here

- Read the [PDF case study](docs/Keisha_Walker_AI_Support_Ticket_Triage_Case_Study.pdf) or [editable Word report](docs/Keisha_Walker_AI_Support_Ticket_Triage_Case_Study.docx) for the narrative and tradeoffs; the report builder source is included.
- Open `notebooks/01_support_ticket_triage.ipynb` for genuinely executed training, evaluation and diagnostic outputs.
- Launch `app.py` for the local workflow; `docs/DEMO_GUIDE.md` walks through useful examples.
- Inspect `reports/error_analysis.csv`, `reports/review_diagnostics.csv` and `reports/summary_diagnostics.csv` to see actual failures.

## What this demonstrates

The support-operations problem is repetitive first-pass categorization and inconsistent review of short customer messages. This project demonstrates an **AI-assisted workflow**, not an autonomous agent: it proposes a route, previews source text, and makes uncertain or sensitive cases easier to inspect. A person still owns every routing and resolution decision. The project connects classification, calibration, abstention, extraction, testing and service-desk quality checks in one usable application.

The technical patterns can inform an IT support project, but BANKING77 performance cannot establish IT helpdesk performance. Target-domain data and a validated local taxonomy are required before transfer. No time-savings or business-impact claim is made because no timed comparison or deployment study was performed.

## Measured results

Model selection used **validation intent macro-F1**. Both fixed candidates' test results are reported after that choice.

| Model | Validation intent macro-F1 | Official-test intent macro-F1 | Official-test queue macro-F1 |
|---|---:|---:|---:|
| Word/bigram TF-IDF + logistic regression | {base['validation']['macro_f1']:.4f} | {base['test']['macro_f1']:.4f} | {base['test']['queue_macro_f1']:.4f} |
| Word/bigram + character TF-IDF + calibrated linear SVM | {cand['validation']['macro_f1']:.4f} | {cand['test']['macro_f1']:.4f} | {cand['test']['queue_macro_f1']:.4f} |

The selected candidate's intent macro-F1 is **{cand['test']['macro_f1']:.4f}**. A paired 500-resample fixed-test bootstrap estimates the candidate-minus-baseline macro-F1 difference at a 95% percentile interval of **{m['bootstrap']['candidate_minus_baseline_macro_f1_percentile_95'][0]:.4f} to {m['bootstrap']['candidate_minus_baseline_macro_f1_percentile_95'][1]:.4f}**. This is conditional on this benchmark; it does not account for domain shift or all paraphrase dependence. The richer candidate won this experiment, not a universal model comparison.

### Actual application policy versus confidence-only experiment

| Evaluation on 3,080 official test rows | Accepted without review flag | Error among accepted | 95% Wilson interval for error |
|---|---:|---:|---:|
| Confidence threshold alone, t = {p['threshold']:.2f} | {int(score['accepted']):,} / {score['coverage']:.2%} | {int(score['errors']):,} / {score['error_rate']:.2%} | {score['error_ci_low']:.2%}–{score['error_ci_high']:.2%} |
| **Actual app: threshold plus review rules** | **{full['accepted']:,} / {full['coverage']:.2%}** | **{full['errors']:,} / {full['error_rate']:.2%}** | **{full['error_wilson_95'][0]:.2%}–{full['error_wilson_95'][1]:.2%}** |

“Accepted” means **no automatic review rule fired**, not approval to route or act. The app flags **{1-full['coverage']:.2%}** of the benchmark for review. The additional rules reduce coverage but do **not** lower observed accepted-error here: {score['error_rate']:.2%} becomes {full['error_rate']:.2%}. They are workflow protections, not proven accuracy improvements.

The threshold maximizes validation coverage over a 0.01 grid, subject to observed validation error ≤ 5% and at least 100 accepted examples. Validation accepted {int(p['validation_score_only']['accepted']):,} examples with {p['validation_score_only']['error_rate']:.2%} error. The 5% target is not a test or production guarantee. Score thresholds and queue mapping were not tuned on test outcomes.

![Model comparison](reports/figures/model_comparison.png)
![Coverage and error](reports/figures/coverage_error.png)
![Actual application policy](reports/figures/review_policy_comparison.png)

## Quick start

Tested on **CPython 3.12.14**, scikit-learn 1.8.0. Use Python 3.12 and the pinned dependencies for the saved model.

```bash
# macOS/Linux, from the extracted project folder
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

```powershell
# Windows PowerShell
py -3.12 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The included `.streamlit/config.toml` binds the app to `127.0.0.1` and disables Streamlit usage telemetry. Open the local URL printed by Streamlit, normally `http://127.0.0.1:8501`. The trained model is included, so initial use does not require retraining. If activation is blocked on Windows, call `.venv\\Scripts\\python.exe -m pip ...` and `.venv\\Scripts\\python.exe -m streamlit run app.py` directly instead of changing security policy.

**Privacy:** use public or synthetic text only. The code makes no external API calls and does not save submitted tickets. Best-effort email/long-number masking is not complete de-identification. Hosting this app changes who can receive inputs. The JSON download can contain copied message text. Never enter secrets, payment details, identity documents or confidential customer data.

**Model security:** joblib/pickle loading can execute code. Only load the model shipped in a trusted copy of this project or one you train yourself. Do not upload arbitrary models into this app.

## Reproduce the experiment

```bash
python -m pip install -r requirements-dev.txt
python -m src.train
python -m src.evaluate_workflow
python -m pytest -q
python scripts/build_notebook.py --in-process
python scripts/write_readme.py
```

Training and evaluation are CPU-only and use the included licensed data. Measured training/evaluation runtime varies by hardware; no end-user handling-time claim follows from model speed. Training writes the model, split audit, per-class reports, predictions, policy, bootstrap and figures. The notebook also retrains and recomputes workflow diagnostics, rather than merely displaying canned scores.

The distributed notebook was executed **sequentially through in-process IPython**, capturing actual outputs. The authoring environment blocks the ZeroMQ interface-discovery step required by standard `nbclient`; the in-process route avoids that dependency. All seven code cells completed. On a normal desktop, the notebook can also run in a Python 3.12 Jupyter/VS Code kernel. `scripts/build_notebook.py` without `--in-process` uses standard nbclient and a `python3` kernel; `TRIAGE_KERNEL` can choose another installed kernel.

A fresh isolated environment installed `requirements-dev.txt` successfully, `pip check` found no broken requirements, and all tests passed there. `requirements-lock.txt` records that complete resolved environment. The verified automated suite includes **26 passing tests**, including two actual Streamlit `AppTest` interactions, inference, probability validity, split hygiene, source/test preservation, review logic, summary extraction, and metric recomputation. See `reports/test_run.txt`. These checks do not certify production quality. A local HTTP health check also succeeded. Full browser screenshot capture was blocked by the authoring sandbox's Chromium socket restriction; no visual browser end-to-end test or screenshot is claimed. The optional `scripts/capture_demo.py` requires `requirements-qa.txt` and `python -m playwright install chromium`; `CHROMIUM_PATH` can specify an existing browser on a normal desktop.

## Data and leakage controls

- **Source:** [PolyAI BANKING77](https://github.com/PolyAI-LDN/task-specific-datasets/tree/master/banking_data), 10,003 development messages and 3,080 official test messages across 77 intents. License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Authors: Iñigo Casanueva, Tadas Temčinas, Daniela Gerz, Matthew Henderson and Ivan Vulić. See [the 2020 paper](https://arxiv.org/abs/2003.04807).
- The official test's text, order and labels are preserved. **Test text is used for exact-duplicate hygiene**, not label-based fitting or selection: {s['development_rows_removed_for_test_overlap']} overlapping development rows, {s['development_conflicting_rows_removed']} conflicting development rows and {s['development_duplicate_rows_removed']} repeated development rows are removed.
- The retained development data is split stratifiably at seed 42: **{s['train_rows']:,} train / {s['validation_rows']:,} validation / {s['test_rows']:,} official test**. Canonical normalization lowercases and replaces non-word runs with a space. No normalized exact strings cross the resulting splits.
- Every vectorizer is fit on training only. SVM sigmoid calibration cross-fits the entire pipeline within three training folds. Validation chooses only the model and score threshold.
- Leakage is reduced, not eliminated: **{s['test_normalized_duplicate_rows_retained']} normalized duplicate test rows are retained**; **{s['test_rows_with_train_word_tfidf_cosine_ge_0_95']} test rows** have training word-TFIDF cosine similarity ≥ 0.95. This text-only diagnostic is not proof that the remaining rows are independent.
- Nine operational queues are a **project-defined, a priori mapping** of the original 77 intents. They are not BANKING77 ground-truth team assignments. See `src/config.py` and `data/intent_to_queue.json`.
- Raw files are pinned to a Git commit and SHA-256 hashes in `data/raw/SOURCE_MANIFEST.json`; attribution, modifications and source details are in `data/DATA_PROVENANCE.md`.

## Model and workflow design

1. **Baseline:** word/bigram TF-IDF (min_df 2, sublinear term frequency, maximum 40,000 features), logistic regression C=4.
2. **Candidate:** the same word features plus character-boundary 3–5 grams (min_df 3, maximum 60,000 features), linear SVM C=1; three-fold training-only sigmoid calibration. Character features can represent spelling fragments, but no dedicated typo-robustness claim is measured here.
3. **Confidence:** maximum predicted probability over 77 intents, not a queue probability. The selected model's test top-label ECE is {cand['test']['expected_calibration_error_10_bins']:.4f} across ten fixed-width bins; calibration remains imperfect.
4. **Review rules:** score below {p['threshold']:.2f}; top-two probability margin below 0.10; fewer than two known terms or no banking cue; fewer than four words; multiple-issue cue; security/dispute topic; or summary truncation. Rules are fixed, inspectable heuristics, not verified risk detectors.
5. **Summary preview:** deterministic extraction of at most two sentences using issue/domain cues plus bounded sentence length. Selected sentences remain in source order; a 60-word cap is explicitly marked. No LLM, generated resolution or paid judge is used. The full masked source stays visible in the demo.
6. **Human control:** the app has no “send,” “route,” account mutation or transaction tools. Suggestions and summaries must be checked against the original.

## Summary quality and challenge results

The 36 synthetic summary messages contain 99 authored essential phrases. The fixtures were written without inspecting model/extractor outputs and were not used to tune the extractor, but they are still small **project-authored diagnostics**, not independent external validation or human-rated summaries.

| Diagnostic | Lead two sentences | Issue-focused extraction |
|---|---:|---:|
| Essential phrase recall | 51 / 99 (51.52%) | 82 / 99 (82.83%) |
| All essential phrases retained | 7 / 36 (19.44%) | 19 / 36 (52.78%) |
| Entire summary copied from source sentences | 36 / 36 (100%) | 36 / 36 (100%) |
| Mean summary/input word ratio | 51.73% | 57.58% |

The extractor retains more diagnostic phrases but uses more words than the lead-two baseline. **Seventeen of 36 extracted summaries still omit at least one expected detail.** Copied wording does not prove factuality, intent preservation, completeness or usefulness; it can preserve a mistaken user statement or lose negation/context. The app always labels the output a preview and displays the full masked source.

Review checks flagged **7/8 off-domain** and **5/8 ambiguous/multiple-issue** fixtures; **1/8 clear in-domain** fixtures were also flagged. The ambiguous group combines insufficient-context and multi-issue cases. The straightforward mismatch is a lost-card message, for which the fixed security rule overrides the authored no-review expectation; it is a policy disagreement, not necessarily a harmful escalation. Four challenge cases expected to be reviewed slipped through. These fixtures are not representative enough to estimate a production false-negative rate. See the failure rows in the CSVs and `data/FIXTURES.md`.

## Known failure modes

- Closed-set prediction always proposes one of 77 intents, even for unsupported content. A high score is not reliable proof of relevance.
- Exploratory checks found that “My graphics card is not working” can be classified as a banking card issue with no review flag; “I want to verify my account on Facebook” can also pass the heuristics. No rules were retuned on these examples.
- Short or overlapping intents are hard to distinguish, particularly transfer timing, card status and refunds. All 77 per-class scores and high-confidence errors are included.
- Multi-issue cues are incomplete; lexical overlap is not a genuine out-of-domain detector. Review flags do not reliably catch every risky message.
- English-only benchmark data, no chronological holdout, no real routing teams, and no demonstrated transfer to IT incidents, multilingual requests or long ticket threads.
- No priority/SLA prediction, customer-satisfaction model, fraud decision, credit/eligibility decision, financial action, production monitoring or business-impact result is claimed.

## What to validate next

Before a real pilot: obtain authorized, de-identified target-domain tickets; agree on the taxonomy with support staff; label multiple intents and out-of-scope cases; split by time/customer/thread; evaluate a semantic text candidate on the same frozen splits; calibrate to actual review costs; and conduct blinded human assessment of summary omissions and misleading context. Start in shadow mode, retain source messages, log decisions with a defined retention policy, and measure handling time with a controlled comparison before claiming savings. See `docs/VALIDATION_PLAN.md`.

## Project layout

```text
app.py                         Local Streamlit workflow
src/config.py                  Frozen queue mapping and policy constants
src/train.py                   Train, select, evaluate, chart and persist
src/triage.py                  Inference, masking, extraction and review checks
src/evaluate_workflow.py        Synthetic diagnostic scoring
notebooks/                     Executed, inspectable experiment
models/triage_model.joblib      Saved selected model
reports/                       Metrics, all predictions, errors, charts, tests
data/raw/                     Licensed original data and provenance manifest
data/*fixtures.json           Clearly marked synthetic checks
docs/                         Case study, model card and validation plan
tests/                        Unit, integration and Streamlit tests
scripts/                      Reproduction, notebook and artifact builders
```

## Attribution and license

Project-authored code, documentation and synthetic fixtures are provided under the MIT license in `LICENSE`. BANKING77 data and original source material retain **CC BY 4.0**, with attribution and modification notices in `data/DATA_PROVENANCE.md`; the full license is included. Project additions are the normalized split hygiene, queue mapping, models, evaluation, extraction/review logic and app. No endorsement by PolyAI or the dataset authors is implied. Third-party dependencies retain their own licenses.
'''
(R/'README.md').write_text(text)
print('README refreshed from measured results.')
