# Local demo guide

Install requirements with Python 3.12, then run streamlit run app.py from the project root. The saved model is included. Read README.md for Windows and macOS/Linux setup.

Try these examples in order:

1. Card arrival: inspect the proposed category and intent, then compare the summary preview with the full masked source.
2. Pending transfer: compare the top three intents; notice that similar messages can belong to different labels.
3. Security concern: see why a specialist review flag is required even when a score is high.
4. Two issues: inspect the multiple-issue warning rather than assuming a single predicted intent is sufficient.
5. Outside supported domain: see the warning for an IT-style request and remember that not all unsupported inputs are detected.

An intentionally revealing probe is: My graphics card is not working. Banking-like vocabulary can cause an unsupported request to receive a confident prediction with no review flag. This is a documented limitation, not a supported task.

The interface retains the full source with basic masking next to the summary preview. A summary can omit important details even when the word-limit truncation flag is false. The model does not send, route, modify accounts or make financial decisions. Downloaded JSON is only a local result and can contain copied message text.

Use public or synthetic content only. Do not paste real customer records, passwords, card information, government identifiers or confidential employer tickets. A local demo is not a substitute for a production data-protection review.
