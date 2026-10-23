# Review before GitHub and portfolio publication

**AI Support Ticket Triage & Quality Review — Project 3**

- **Publication status:** local review candidate. No files from this package have been pushed to your public AI Ticket Triage repository or added to keishawalker.tech.
- **Review the work:** start with `docs/Keisha_Walker_AI_Support_Ticket_Triage_Case_Study.pdf`, then `README.md`, `app.py`, `docs/MODEL_CARD.md` and `docs/DEMO_GUIDE.md`.
- **Data:** public BANKING77 English banking-intent examples plus explicitly synthetic QA fixtures. This is not a Colorado/myColorado service desk system and has no confidential employer data intentionally included.
- **Reported test metric:** intent macro-F1 **0.9033** against baseline **0.8766** (from existing saved evaluation, not recalculated in this review).
- **Current test status:** 24 non-UI tests passed, two framework-free app smoke scenarios passed. Prior archived runs reported all 26 tests passed. The two **official Streamlit AppTest** checks could not rerun here due to missing package/network. See `reports/STREAMLIT_TEST_STATUS_2026-10-23.md`.
- **Planned final gate:** after your publication approval, GitHub Actions runs 26 tests in CPython 3.12. Only after that passes should the portfolio site be updated with the verified repository, case-study and demo instructions.
- **Website scope:** link to the repository and case study and describe it as a *local Streamlit demo*, not a hosted live app unless separately deployed and privacy-reviewed.
- **Approval requested:** review the actual model/results, presentation, limitations, source files and the website writeup before giving permission for any external update.
