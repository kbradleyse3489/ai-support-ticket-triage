# Validation before a service desk pilot

1. Define the actual routing problem with support staff. Agree on queues, multiple-issue handling, unsupported topics and the cost of a wrong suggestion. Do not copy the benchmark taxonomy into an organization without validation.
2. Obtain authorized, de-identified target-domain records. Exclude credentials and protected content not required for routing. Specify retention, access controls and who may label data. Do not use employer tickets without permission.
3. Label representative cases with an adjudication process. Include rare intents, terse requests, spelling variants, long threads, mixed issues and out-of-domain messages. Track agreement; do not treat model-generated labels as ground truth.
4. Split by time and, where relevant, customer/conversation/site. Freeze a final evaluation set and prevent cross-thread paraphrases from appearing in both training and test. Fit vocabularies/calibrators inside the appropriate training folds.
5. Compare lexical and semantic candidates under identical splits and compute budget. Report macro/per-class scores, calibration, queue confusion, slices and high-confidence errors. Do not choose winners using final test results.
6. Choose the review policy on validation according to actual error costs. Evaluate confidence-only and complete app behavior separately. Include meaningful out-of-domain detection and uncertainty intervals. Report review burden and missed risky cases, not only coverage.
7. Run a blinded human summary study with the original message visible to evaluators. Predefine omission, negation, misleading emphasis, actionability and privacy criteria. Use independent raters and report agreement. Synthetic phrase checks are only an early diagnostic.
8. Start in shadow mode. No automatic ticket routing, messages, account changes or financial actions. Compare suggestions with staff decisions and inspect overrides. Design audit logging with minimal data and explicit retention limits.
9. Measure any proposed time savings with a controlled, timed comparison. Record accuracy and rework alongside speed; do not infer benefits from inference latency alone.
10. Establish release gates, rollback and monitoring. Track label drift, confidence shifts, review load, error slices and unsafe suggestions. Retrain/recalibrate only with authorized data and a documented review process.

These are proposed validation steps, not work already completed or commitments to deploy.
