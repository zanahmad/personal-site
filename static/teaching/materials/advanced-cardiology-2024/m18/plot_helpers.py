"""Original accessible scientific-figure helper for this teaching batch."""
from pathlib import Path
import html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def configure():
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'legend.fontsize':22,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
def save(fig,out,stem,title,description):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+f'<title>{html.escape(title)}</title><desc>{html.escape(description)}</desc>'+s[j:]);plt.close(fig)
