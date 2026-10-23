"""Offline functional smoke check for app.py when Streamlit isn't available.

IMPORTANT: This is NOT Streamlit's AppTest and does not test browser/widget state.
It executes the REAL app.py module and REAL saved classifier using a minimal
stand-in for Streamlit's presentation functions. Two documented paths:
 - default card arrival, check UI metrics and downloadable JSON
 - unsupported office VPN request, check human-review flag and reasons.
Run: python scripts/verify_ui_without_streamlit.py
"""
import contextlib
import json
import runpy
import sys
import types
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

class CaptureUI(types.ModuleType):
    def __init__(self, selected_example):
        super().__init__('streamlit')
        self.selected_example = selected_example
        self.sidebar = contextlib.nullcontext()
        self.metrics = {}
        self.download_payload = None
        self.input_text = None
        self.alerts = []

    def cache_resource(self, func):
        return func

    def set_page_config(self, **kwargs):
        pass

    def __getattr__(self, name):
        # Presentation methods unrelated to the two smoke assertions.
        if name in {'title','caption','header','write','info','subheader','success','divider','dataframe'}:
            return lambda *args, **kwargs: None
        raise AttributeError(name)

    def warning(self, text, **kwargs):
        self.alerts.append(str(text))

    def error(self, text, **kwargs):
        raise AssertionError(f'Application displayed error: {text}')

    def stop(self):
        raise AssertionError('Application stopped before making a prediction')

    def selectbox(self, label, options, **kwargs):
        assert label == 'Try an example'
        assert self.selected_example in options
        return self.selected_example

    def text_area(self, label, value, **kwargs):
        assert label == 'Support message'
        assert isinstance(value, str) and value
        self.input_text = value
        return value

    def button(self, label, **kwargs):
        assert label == 'Suggest triage'
        return True

    def metric(self, label, value, **kwargs):
        self.metrics[label] = str(value)

    def columns(self, widths, **kwargs):
        count = len(widths) if not isinstance(widths,int) else widths
        return [self] * count

    def expander(self, label, **kwargs):
        return contextlib.nullcontext()

    def download_button(self, label, data, **kwargs):
        assert label == 'Download this result as JSON'
        self.download_payload = json.loads(data)

def run_case(selection):
    ui = CaptureUI(selection)
    with patch.dict(sys.modules, {'streamlit': ui}):
        runpy.run_path(str(ROOT/'app.py'), run_name='__main__')
    assert 'Suggested category' in ui.metrics
    assert 'Intent confidence' in ui.metrics
    assert 'Human-review flag' in ui.metrics
    assert ui.download_payload is not None
    assert ui.download_payload['suggested_category'] == ui.metrics['Suggested category']
    return ui

def main():
    card = run_case('Card arrival')
    assert card.metrics['Human-review flag'] == 'NO RULE FIRED'
    print('PASS offline app flow 1: default banking example renders prediction and export')

    outside = run_case('Outside supported domain')
    assert 'office VPN' in outside.input_text
    assert outside.metrics['Human-review flag'] == 'REVIEW'
    assert outside.download_payload['human_review'] is True
    assert any('supported banking domain' in r for r in outside.download_payload['review_reasons'])
    print('PASS offline app flow 2: non-banking message triggers human review')
    print('Note: Streamlit AppTest tests/test_app.py remains unexecuted in this runtime.')

if __name__ == '__main__':
    main()
