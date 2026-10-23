# Experiment history and interpretation

- Fixed design: BANKING77 public benchmark; original official test retained; normalized exact-duplicate hygiene uses test text to exclude development overlaps; train/validation split seed 42.
- Defined nine-queue mapping, two feature/model candidates, calibration design and review constants before first fitting. No hyperparameter search was performed.
- Selected the word-plus-character calibrated SVM by validation macro-F1. Selected confidence threshold 0.57 by maximum validation coverage with observed error at most 5% and at least 100 accepted cases.
- Reported both candidates on the official test after selection. A text-only high-similarity audit and error analysis were performed after selection; neither changed the model or threshold.
- Re-ran the experiment for code correctness and complete notebook outputs. Corrected full-policy bookkeeping to count actual masked-input engine predictions instead of raw-model predictions; no current test texts were altered by masking, so numerical results did not change. Renamed positive sklearn log loss and clarified summary-level extractiveness metric names.
- Synthetic summary/review fixtures were authored independently before fixture inference and were never used for tuning. They remain project-authored diagnostics, not independent external validation. Failures are retained.
- Independent exploratory probes revealed out-of-domain false accepts. No heuristic was tuned to those probes. App wording and source visibility were improved, without changing predictions or policy.
- The included notebook genuinely executes all seven code cells using in-process IPython. Standard nbclient execution was unavailable because the sandbox blocks ZeroMQ interface discovery; this limitation is disclosed rather than presenting unexecuted output.
- Independent review reproduced model metrics, validation threshold, raw-data hashes and the 26-test suite. This is code/metric review, not a human summary-quality study or production certification.
