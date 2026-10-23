"""Verify the included release file hashes without loading a pickle or contacting the network."""
from pathlib import Path
from hashlib import sha256
import sys
ROOT = Path(__file__).resolve().parents[1]
manifest = ROOT / "MANIFEST.sha256"
errors = []
lines = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
for line in lines:
    if len(line) < 67 or line[64:66] != "  ":
        errors.append("Malformed manifest entry")
        continue
    expected, relative = line[:64], line[66:]
    candidate = (ROOT / relative).resolve()
    if not candidate.is_relative_to(ROOT.resolve()):
        errors.append("Path escapes project: " + relative)
    elif not candidate.is_file():
        errors.append("Missing: " + relative)
    elif sha256(candidate.read_bytes()).hexdigest() != expected:
        errors.append("Mismatch: " + relative)
for relative in ("app.py", "requirements.txt", "src/train.py", "src/triage.py",
                 "data/raw/SOURCE_MANIFEST.json", "models/triage_model.joblib",
                 "reports/metrics.json", "docs/MODEL_CARD.md", "tests/test_pipeline.py"):
    if not (ROOT / relative).is_file():
        errors.append("Required file missing: " + relative)
print(f"Release integrity: {len(lines)} manifest entries; {len(errors)} errors")
for item in errors:
    print("ERROR:", item)
sys.exit(1 if errors else 0)
