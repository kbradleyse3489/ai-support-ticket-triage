"""Capture the real local Streamlit UI, not a fabricated mockup. Optional QA tool."""
import os, subprocess, sys, time
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
proc=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port','8512','--server.address','127.0.0.1'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
try:
    for _ in range(60):
        try:
            if requests.get('http://127.0.0.1:8512/_stcore/health',timeout=1).ok: break
        except requests.RequestException: pass
        time.sleep(.5)
    else: raise RuntimeError('Local Streamlit HTTP health endpoint was not reachable.')
    with sync_playwright() as p:
        options={'headless':True}
        if os.environ.get('CHROMIUM_PATH'): options['executable_path']=os.environ['CHROMIUM_PATH']
        browser=p.chromium.launch(**options)
        page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
        page.goto('http://127.0.0.1:8512',wait_until='networkidle')
        page.get_by_role('button',name='Suggest triage',exact=True).click()
        page.get_by_text('Summary preview',exact=True).wait_for(timeout=30000)
        page.screenshot(path=str(ROOT/'reports/figures/demo_screenshot.png'),full_page=True)
        print('Real Streamlit screenshot saved.')
        browser.close()
finally:
    proc.terminate()
    try: proc.wait(timeout=5)
    except subprocess.TimeoutExpired: proc.kill()
