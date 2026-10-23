"""Launch locally: streamlit run app.py"""
import json
import streamlit as st
import pandas as pd
from src.config import ROOT, MAX_INPUT_CHARS
from src.triage import TriageEngine, redact_obvious_identifiers

st.set_page_config(page_title='Support Ticket Triage',page_icon='📨',layout='wide')

@st.cache_resource
def load_engine():
    return TriageEngine()

st.title('AI Support Ticket Triage & Quality Review')
st.caption('Keisha Walker | Applied machine learning and assistive support operations')
st.warning('Demonstration, not a production service desk. Trained on the public BANKING77 English banking-intent benchmark, not employer IT tickets. It cannot access accounts, route tickets, or perform financial actions.')

with st.sidebar:
    st.header('How to read the output')
    st.write('1. Paste a de-identified banking-support message.\n2. Review the proposed queue and intent.\n3. Check the source message before accepting the extractive summary.\n4. A person decides the next step.')
    st.info('Do not enter passwords, card numbers, identity documents or private customer data. Basic masking is not a privacy guarantee.')
    st.caption('The model runs in this Python process. This app contains no API calls or ticket persistence. Hosting it elsewhere changes who can receive the input.')
    st.caption('Model files use joblib. Load only the trusted model included with this project or one you train yourself.')

try:
    engine=load_engine()
except FileNotFoundError:
    st.error('Model missing. Run python -m src.train in the project folder, then restart this app.')
    st.stop()
except Exception as exc:
    st.error(f'Model could not be loaded: {exc}. Use the pinned requirements and Python 3.12, or retrain locally.')
    st.stop()

examples={
    'Card arrival': 'My new card has not arrived after two weeks. Can you check when it will be delivered?',
    'Pending transfer': 'I sent a bank transfer yesterday and it is still pending. The recipient has not received the money.',
    'Security concern': 'I do not recognize a card payment on my account. I think my card has been compromised.',
    'Two issues': 'My card is not working at the shop. Also, I want to change the address on my account.',
    'Outside supported domain': 'My laptop cannot connect to the office VPN. I need help joining a meeting.',
}
example=st.selectbox('Try an example',list(examples))
text=st.text_area('Support message',value=examples[example],height=150,max_chars=MAX_INPUT_CHARS,help='Maximum 5,000 characters. Use public or synthetic content only.')
if st.button('Suggest triage',type='primary'):
    try:
        result=engine.predict(text)
    except ValueError as exc:
        st.error(str(exc))
    else:
        a,b,c=st.columns([1.5,1,1])
        a.metric('Suggested category',result['suggested_category'])
        b.metric('Intent confidence',f"{result['confidence']:.1%}")
        c.metric('Human-review flag','REVIEW' if result['human_review'] else 'NO RULE FIRED')
        st.write('Suggested intent: '+result['suggested_intent'].replace('_',' '))
        st.caption(f"Confidence is for the 77-class intent, not the broader category. Validation-selected threshold: {result['threshold']:.2f}. It is not a correctness guarantee.")
        st.subheader('Summary preview')
        st.write(result['summary'])
        st.warning('A summary can omit important details even when it is not truncated. Never use it as the only evidence for a routing or resolution decision.')
        st.caption('Word-limit truncation: ' + ('YES' if result['summary_truncated'] else 'NO, but omission is still possible'))
        st.subheader('Full source message with basic masking')
        st.write(redact_obvious_identifiers(text.strip()))
        st.caption('Rule-based sentence selection, not generative AI. Copies up to two sentences from the masked input; may omit important context. Always compare with the original.')
        if result['human_review']: st.warning(' • '.join(result['review_reasons']))
        else: st.success('No automatic review rule fired. This is still a suggestion, not approval to act.')
        with st.expander('Alternative intents and quality-review checklist'):
            st.dataframe(pd.DataFrame(result['alternatives']),hide_index=True,width='stretch')
            for check in ['Does the suggested queue fit the actual issue?', 'Does the summary preserve negation, timing and affected transaction?', 'Are there multiple issues or a security concern?', 'Should a specialist inspect the original message?']:
                st.write('□ '+check)
        st.download_button('Download this result as JSON',json.dumps(result,indent=2),file_name='triage_result.json',mime='application/json')

st.divider()
st.subheader('Evidence and boundaries')
metrics_path=ROOT/'reports/metrics.json'
if metrics_path.exists():
    metrics=json.loads(metrics_path.read_text()); selected=metrics['models'][metrics['selected_model']]['test']
    col1,col2,col3=st.columns(3)
    col1.metric('Official test intent macro-F1',f"{selected['macro_f1']:.3f}")
    col2.metric('Test examples',f"{metrics['splits']['test_rows']:,}")
    col3.metric('Routing categories','9')
    st.caption('Model selection and threshold tuning used validation only. These are benchmark results, not a measured reduction in handling time, production validation, or evidence of IT-domain performance.')
with st.expander('Sources and limitations'):
    st.write('BANKING77 by PolyAI: https://github.com/PolyAI-LDN/task-specific-datasets/tree/master/banking_data')
    st.write('Dataset license: CC BY 4.0. Operational queues, review rules and diagnostic fixtures are project-defined additions. Source collection method is not established here as verified production data.')
    st.write('Known limitations: English only, closed-set intents, possible paraphrase overlap, heuristic out-of-domain screening, unvalidated queue taxonomy, summaries not human-rated. Do not use for credit, fraud adjudication, eligibility, account changes, or emergency support.')
