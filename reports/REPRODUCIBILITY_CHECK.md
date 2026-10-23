# Reproducibility checks for version 1.0

Completed on October 18, 2026 with CPython 3.12.14:

- Installed requirements-dev.txt in a fresh virtual environment without inherited system packages.
- Ran pip check: no broken requirements found.
- Ran all 26 tests successfully in that clean environment, including both Streamlit interactions.
- Built the release archive, verified ZIP CRC integrity, extracted it into a separate directory, and checked every SHA-256 entry in its manifest.
- Ran all 26 tests from the extracted project directory using the clean environment; all passed. The extracted application uses its own included data, model and report files.
- Validated the notebook structure: seven sequentially executed code cells and no error outputs. The notebook documents its real in-process IPython execution method.
- The report contains eight pages and was rendered and visually checked page by page. PDF and editable DOCX are included; rendering intermediates are not packaged.

Raw numerical checks and limitations remain in README.md, reports/DEMO_VERIFICATION.md and reports/EXPERIMENT_NOTES.md. Reproducing a benchmark and passing tests do not establish production performance.
