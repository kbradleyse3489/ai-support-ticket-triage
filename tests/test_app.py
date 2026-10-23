from streamlit.testing.v1 import AppTest
from src.config import ROOT

def test_app_loads_and_predicts():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    assert not app.exception
    app.button[0].click().run()
    assert not app.exception
    assert len(app.metric)>=3
    assert any('Suggested category'==m.label for m in app.metric)

def test_app_off_domain_flow():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    app.selectbox[0].select('Outside supported domain').run()
    app.button[0].click().run()
    assert not app.exception
    flags=[m.value for m in app.metric if m.label=='Human-review flag']
    assert flags==['REVIEW']
