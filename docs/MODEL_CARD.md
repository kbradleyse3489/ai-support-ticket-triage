# Model card

## Purpose and intended use

Local, assistive English banking-support intent triage for educational review and demonstration. The app suggests a queue and intent, not a resolution, financial decision or authorization. A person must inspect the full source and own the next action.

## Data and model

Public BANKING77 benchmark, 77 labels, CC BY 4.0. Raw sources are pinned and hashed. The collection process is not established here as verified production tickets. Original test rows are retained; development overlap, duplicates and conflicting normalized texts are removed. The retained development set is split 80/20, stratified at seed 42.

A word-TFIDF logistic baseline is compared with a word-plus-character TFIDF linear SVM, calibrated with sigmoid cross-validation on training folds. The latter wins validation intent macro-F1 and is the shipped model. Calibration folds include their own fitted text feature pipelines. No test labels choose hyperparameters or the operating threshold.

## Outputs

- Suggested category: one of nine project-defined operational queues.
- Suggested intent: one of 77 original dataset labels.
- Confidence: maximum estimated intent probability, not queue confidence.
- Summary: a source-sentence preview, never a generated answer.
- Review flag: fixed score/margin/context/domain/multiple-issue/security/truncation checks.

Full measured scores, uncertainty, error rows and validation-selected threshold are in reports/metrics.json and README.md. Those results describe one fixed public benchmark, not target-domain production performance.

## Constraints and risks

English only; no tested cross-language or IT-domain transfer. The classifier is closed-set and can confidently assign unsupported messages. Heuristic vocabulary checks are not reliable out-of-domain detection. A review flag being false is not approval to act. Multiple intents, paraphrases and negation can confuse routing; summaries can omit required context. Full-policy accepted-error is higher than confidence-only error in this experiment, despite lower coverage.

There are no human summary ratings, longitudinal monitoring results, privacy guarantees, fairness claims, financial-account actions, priority/SLA predictions or handling-time impact estimates. Do not use the model for eligibility, fraud adjudication, credit or other consequential decisions about people.

## Security and privacy

The shipped app is localhost-only by default, disables Streamlit usage telemetry, does not call APIs and does not persist submitted tickets. It masks obvious email addresses and long digit sequences only. This is not comprehensive PII detection. JSON downloads contain copied text; use public or synthetic messages. Hosting requires a new security/privacy review. Joblib files are executable deserialization artifacts: load trusted files only.

## Reproducibility and change control

Pinned Python dependencies, seed, source hashes, saved model, executed notebook and tests are included. Keep a frozen test set for each new domain. Record every future change to mapping, data, features, calibration, threshold, extraction and rules. Re-evaluate the whole workflow, not just raw-model accuracy. Before deployment, establish lawful data access, human review, retention limits and escalation ownership.
