# Streamlit application verification — 2026-10-23

**Release state: REVIEW CANDIDATE, not fully reverified. No GitHub or website publication.**

## What was executed here

- `python -m pytest -q tests/test_pipeline.py`: **24 passed** in this runtime (CPython 3.13.5, scikit-learn 1.8.0).
- `python scripts/verify_ui_without_streamlit.py`: **2 smoke scenarios passed** with the actual `app.py`, packaged saved model, classifier, and inputs. A minimal presentation stand-in was used for the `streamlit` module; it is **not** the Streamlit framework or browser.
  - **Default Card arrival:** real app script rendered a suggested category, intent confidence, human-review status, and downloadable structured JSON. No review rule fired on the selected synthetic input.
  - **Outside supported domain:** real app script rendered a human-review flag of `REVIEW` for the synthetic office-VPN request. The exported result included the banking-domain mismatch reason.
- `python -m py_compile app.py tests/test_app.py scripts/verify_ui_without_streamlit.py`: passed.
- `python scripts/verify_release.py`: see the final manifest check after packaging.

## What could *not* be executed here

`tests/test_app.py` contains **two real `streamlit.testing.v1.AppTest` tests**. Streamlit was not installed here. Attempting to install pinned `streamlit==1.50.0` failed because this runtime cannot resolve the package network endpoint. Consequently, **no new official Streamlit AppTest pass is claimed** for this session.

The archived log files in `reports/` record **26 passed** in a prior CPython 3.12.14 environment. Those are earlier results, not the October 23 rerun.

## How to finish the actual two tests

When an approved release is uploaded to GitHub, `.github/workflows/validate.yml` is configured to install dependencies under Python 3.12 and run all 26 tests, including both official Streamlit AppTest interactions. Do not declare release fully verified until GitHub Actions reports success. If it fails, correct the defect and rerun CI **before** adding the portfolio website project link.

Alternatively, use macOS/terminal in the extracted project folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -v tests/test_app.py
python scripts/verify_release.py
streamlit run app.py
```

Use public or synthetic demo text only. Loading the included `joblib` artifact is appropriate only from this trusted project source.
