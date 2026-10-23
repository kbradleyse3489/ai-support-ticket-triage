# Demo verification

## Completed

- Streamlit AppTest loads app.py without an exception, clicks Suggest triage and verifies rendered output metrics.
- A second AppTest selects the outside-domain example, submits it and verifies the REVIEW output.
- The included Python test suite passes all 26 tests after the final UI wording/source-visibility updates.
- A local Streamlit server was started and its /_stcore/health endpoint returned a successful HTTP response. The screenshot script only proceeds to browser launch after that health check succeeds.

## Not completed here

The real Chromium launch failed because the authoring sandbox disallows a required socket operation. No browser screenshot, pixel-level UI validation or full browser end-to-end pass is claimed. The supplied app is verified through Streamlit's interaction test framework and local HTTP health, not a browser-rendered screenshot.

The optional scripts/capture_demo.py can run on an ordinary desktop after installing requirements-qa.txt and Playwright Chromium. It writes a genuine screenshot only if the browser loads the live app and the result is visible. The helper does not substitute a mockup for a failed capture.
