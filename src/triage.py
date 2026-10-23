"""Inference, conservative review rules, and deterministic extractive summaries.

No API calls, account actions, generated advice, or hidden ticket writes.
Only load pickle/joblib files you trust: deserialization can execute code.
"""
from __future__ import annotations
import re
from pathlib import Path
import joblib
import numpy as np
from .config import ROOT, MAX_INPUT_CHARS, INTENT_TO_QUEUE, MIN_MARGIN, MIN_KNOWN_TERMS

ISSUE_CUES = re.compile(r"\b(not|cannot|can't|unable|missing|lost|stolen|failed|declined|pending|wrong|charged|refund|blocked|forgot|forgotten|where|when|how|why|never|haven't|didn't|hasn't|doesn't)\b", re.I)
DOMAIN_CUES = re.compile(r"\b(card|cards|bank|banking|payment|payments|transfer|transfers|cash|atm|atms|refund|top.?up|deposit|debit|account|pin|passcode|currency|exchange|verify|verification|identity|balance|money|transaction|transactions|beneficiary|withdrawal|contactless)\b", re.I)
SECURITY_CUES = re.compile(r"\b(stolen|fraud|fraudulent|compromised|hacked|unauthori[sz]ed|not recogni[sz]e|don't recogni[sz]e|didn't authori[sz]e)\b", re.I)
MULTI_CUES = re.compile(r"\b(also|another issue|separate issue|second issue|as well as)\b", re.I)

def normalize_text(text: str) -> str:
    return re.sub(r'\W+', ' ', text.lower()).strip()

def redact_obvious_identifiers(text: str) -> str:
    """Best-effort masking, NOT a production DLP or de-identification guarantee."""
    text = re.sub(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '[EMAIL]', text, flags=re.I)
    text = re.sub(r'(?<!\w)(?:\d[ -]?){12,19}(?!\w)', '[LONG_NUMBER]', text)
    return text

def sentences(text: str) -> list[str]:
    # A simple splitter deliberately preserves source spans. Abbreviations can mis-split.
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text.strip()) if s.strip()]

def extractive_summary(text: str, max_sentences: int = 2, max_words: int = 60) -> dict:
    """Rank sentences by issue cues + domain cues + bounded length; preserve order.

    Output is copied from the redacted input. No new facts or resolution are generated.
    Quality measurements are diagnostic lexical tests, not human judgements.
    """
    parts = sentences(text)
    if not parts:
        return {'text': '', 'method': 'rule-based extractive', 'source_indices': [], 'truncated': False}
    def score(sentence):
        return 3 * len(ISSUE_CUES.findall(sentence)) + 2 * len(DOMAIN_CUES.findall(sentence)) + min(len(sentence.split()), 20) / 20
    ranked = sorted(range(len(parts)), key=lambda i: (-score(parts[i]), i))
    # Keep at most two sentences; short one-sentence queries are intentionally unchanged.
    chosen = sorted(ranked[:max_sentences])
    summary = ' '.join(parts[i] for i in chosen)
    words = summary.split()
    truncated = len(words) > max_words
    if truncated:
        # The cap preserves the selected prefix; the ellipsis explicitly marks omission.
        summary = ' '.join(words[:max_words]) + ' ...'
    return {'text': summary, 'method': 'rule-based extractive', 'source_indices': chosen, 'truncated': truncated}

class TriageEngine:
    def __init__(self, bundle_path: str | Path | None = None):
        self.bundle = joblib.load(bundle_path or ROOT / 'models' / 'triage_model.joblib')
        self.model = self.bundle['model']
        self.vocabulary = self.bundle['vocabulary']
        self.threshold = float(self.bundle['threshold'])

    def predict(self, text: str) -> dict:
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Enter a non-empty support message.')
        if len(text) > MAX_INPUT_CHARS:
            raise ValueError(f'Input is limited to {MAX_INPUT_CHARS:,} characters. Split long threads before triage.')
        clean = redact_obvious_identifiers(text.strip())
        probabilities = self.model.predict_proba([clean])[0]
        order = np.argsort(probabilities)[::-1]
        intent = str(self.model.classes_[order[0]])
        confidence = float(probabilities[order[0]])
        margin = float(confidence - probabilities[order[1]])
        known_terms = len(set(re.findall(r'\b\w\w+\b', clean.lower())) & self.vocabulary)
        summary = extractive_summary(clean)
        reasons = []
        if confidence < self.threshold: reasons.append('Confidence below validation-selected threshold')
        if margin < MIN_MARGIN: reasons.append('Top two intents are close')
        if known_terms < MIN_KNOWN_TERMS or not DOMAIN_CUES.search(clean): reasons.append('Weak evidence that this is in the supported banking domain')
        if len(clean.split()) < 4: reasons.append('Too little context')
        if MULTI_CUES.search(clean): reasons.append('Possible multiple issues; confirm the intended queue')
        if SECURITY_CUES.search(clean) or INTENT_TO_QUEUE[intent] == 'Security and disputes': reasons.append('Security or dispute topic requires human handling')
        if summary['truncated']: reasons.append('Summary was truncated; read the full message')
        return {
            'suggested_category': INTENT_TO_QUEUE[intent],
            'suggested_intent': intent,
            'confidence': confidence,
            'confidence_definition': 'Estimated probability of the suggested intent, not of the broad category; not a correctness guarantee',
            'threshold': self.threshold,
            'top_two_margin': margin,
            'summary': summary['text'],
            'summary_method': summary['method'],
            'summary_truncated': summary['truncated'],
            'human_review': bool(reasons),
            'review_reasons': reasons or ['No automatic review rule fired; a person still owns routing and resolution'],
            'alternatives': [{'intent': str(self.model.classes_[i]), 'probability': float(probabilities[i])} for i in order[:3]],
            'scope': 'BANKING77 English support-intent demonstration only; no account or financial actions',
        }
