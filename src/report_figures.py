"""Additional diagnostic figures, generated only from saved measured outputs."""
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/ticket-triage-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .config import ROOT

def make_extra_figures():
    m=json.loads((ROOT/'reports/metrics.json').read_text())
    w=json.loads((ROOT/'reports/workflow_metrics.json').read_text())
    score=m['policy']['test_score_only'];full=m['policy']['test_full_review_policy']
    fig,axes=plt.subplots(1,2,figsize=(9,4.6))
    labels=['Confidence\nthreshold only','Full app\nreview policy']
    for ax,key,title in [(axes[0],'coverage','Accepted without review flag (%)'),(axes[1],'error_rate','Error among accepted (%)')]:
        vals=[score[key]*100,full[key]*100]
        bars=ax.bar(labels,vals,color=['#427c92','#e29d47'],width=.6)
        ax.bar_label(bars,labels=[f'{v:.2f}%' for v in vals],padding=5)
        ax.set_title(title,fontsize=11)
        ax.set_ylim(0,105 if key=='coverage' else 7)
        ax.spines[['right','top']].set_visible(False)
    fig.suptitle('Actual app policy reduces coverage, not observed accepted-error',fontweight='bold',fontsize=12)
    fig.text(.5,.01,'3,080 official test rows | fixed validation-selected threshold 0.57 | not a production guarantee',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.05,1,.92]);fig.savefig(ROOT/'reports/figures/review_policy_comparison.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.5,4.5))
    names=['lead_two','issue_focused'];vals=[w['summary'][name]['micro_key_phrase_recall']*100 for name in names]
    bars=ax.bar(['Lead two sentences','Issue-focused extraction'],vals,color=['#427c92','#e29d47'],width=.55)
    ax.bar_label(bars,labels=['51 / 99 phrases','82 / 99 phrases'],padding=5)
    ax.set(ylim=(0,100),ylabel='Authored key-phrase recall (%)',title='Summary diagnostics on 36 synthetic messages')
    ax.spines[['right','top']].set_visible(False)
    fig.text(.5,.01,'Not human judgement or external validation. Complete retention: 7/36 versus 19/36.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(ROOT/'reports/figures/summary_diagnostics.png',dpi=180);plt.close(fig)

if __name__=='__main__': make_extra_figures()
