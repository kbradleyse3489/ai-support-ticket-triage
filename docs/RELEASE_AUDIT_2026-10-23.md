# October 23, 2026 — project release integrity review

## Scope and provenance

This project is based on the public **BANKING77** benchmark and authored synthetic checks. No State of Colorado/myColorado data, internal Jira tickets, customer data, confidential records, or employer-specific process artifacts were included in this verified archive. The model is a **local demonstration**, not a production ticket-handling system. Full source attribution and license text remain in `data/DATA_PROVENANCE.md` and `data/raw/`.

## Current-turn verification (not the original experimental run)

- Extracted the complete previously packaged source, demo, data, report, saved model, and notebook.
- Verified every original `MANIFEST.sha256` entry before adding this release audit and script; **76 entries matched**.
- Ran the environment-independent pipeline test suite: **24 tests passed** on CPython 3.13 with scikit-learn 1.8.0.
- Ran the saved model locally on three synthetic banking/off-domain inputs; inference succeeded. A high-confidence out-of-domain false positive remains possible and is documented in the model card.
- The two Streamlit `AppTest` tests could **not** run here because Streamlit 1.50.0 is unavailable and installation failed due to unavailable package networking. The original archived logs record **26 passed** on CPython 3.12.14; this is prior evidence, **not a 26-test rerun on October 23**.
- Static scan across 63 original readable source/data/text files found **no recognized private-key headers, GitHub/Slack/AWS/Stripe credential signatures, or candidate application-secret assignments**. Two `sample@example.com` strings appear in tests and are synthetic. Static scans are not a guarantee against all sensitive content.
- No substantive retraining or performance re-estimation was performed; the published macro-F1 and policy metrics remain those recorded in the dated experiment reports.

## Verify on your own machine

1. Use CPython **3.12**. Create and activate a virtual environment; install `requirements-dev.txt`.
2. Run `python scripts/verify_release.py` to verify release files against the included SHA-256 manifest.
3. Run `python -m pytest -q` and confirm all 26 tests pass in the pinned compatible environment.
4. Run `streamlit run app.py` locally, use public/synthetic messages only, and verify demo text manually.
5. Inspect `reports/metrics.json`, `reports/operating_policy.json`, `reports/error_analysis.csv`, `docs/MODEL_CARD.md`, and `docs/VALIDATION_PLAN.md` before making any new performance claims.

## Publication safety

Do not upload private tickets or post a public Streamlit demo before evaluating input privacy. Do not treat BANKING77 as a sample of Colorado state support tickets. Never load an untrusted `joblib` file. Please give dataset authors credit under CC BY 4.0 and keep existing licenses.

## GitHub release status

As of this local verification, the remote GitHub repository contained only a one-line README. This release archive is **publish-ready for code review/upload**, but do not claim that the files are on GitHub until remote verification confirms them.
