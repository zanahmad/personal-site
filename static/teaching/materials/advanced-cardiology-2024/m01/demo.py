"""Original question-to-observable example: mean flow cannot identify rate and stroke volume.
Synthetic teaching inputs; no patient data. Run: python demo.py.
"""
from pathlib import Path
import json, html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def mean_observables(rate_bpm,stroke_volume_ml,pressure_drop_mmHg=90.):
    values=np.array([rate_bpm,stroke_volume_ml,pressure_drop_mmHg],float)
    if not np.isfinite(values).all() or np.any(values<=0):
        raise ValueError('Use finite positive rate, stroke volume and pressure drop.')
    with np.errstate(over='raise',invalid='raise',divide='raise'):
        try:
            q=float(np.float64(rate_bpm)*np.float64(stroke_volume_ml)/1000.)
            resistance=float(np.float64(pressure_drop_mmHg)/q)
        except FloatingPointError as e:raise ValueError('Inputs exceed numerical range.') from e
    if not np.isfinite([q,resistance]).all() or min(q,resistance)<=0:raise ValueError('Inputs exceed numerical range.')
    return {'flow_L_min':q,'resistance_mmHg_min_L':resistance}


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1
    p.write_text(s[:j]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(exist_ok=True,parents=True)
    plt.rcParams.update({'font.size':16,'axes.titlesize':18,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,5));ax.set(xlim=(-1.2,7.2),ylim=(-1.3,3.3));ax.axis('off')
    xy=[(0,2),(3,2),(6,2),(6,0),(3,0),(0,0)]
    labels=['Left ventricle','Systemic\narteries','Systemic\nveins','Right ventricle','Pulmonary\narteries','Pulmonary\nveins']
    for (x,y),label in zip(xy,labels):
        ax.add_patch(FancyBboxPatch((x-.94,y-.35),1.88,.7,boxstyle='round,pad=.04',fc='#e7f2f2',ec='#18384a',lw=1.6));ax.text(x,y,label,ha='center',va='center',fontsize=14)
    names=['aortic valve','systemic bed','tricuspid\nvalve','pulmonic valve','pulmonary bed','mitral\nvalve']
    for i,label in enumerate(names):
        a=np.array(xy[i]);b=np.array(xy[(i+1)%6]);d=(b-a)/np.linalg.norm(b-a);cut=.42 if i in (2,5) else 1.
        ax.annotate('',b-cut*d,a+cut*d,arrowprops={'arrowstyle':'->','lw':1.8,'color':'#087e8b'})
        mid=(a+b)/2;ax.text(mid[0]+(.52 if i==2 else -.52 if i==5 else 0),mid[1]+(.62 if i<2 else -.64 if i in (3,4) else 0),label,ha='center',va='center',fontsize=14,rotation=90 if i in (2,5) else 0)
    ax.text(3,1,'Anatomy motivates the grouping.\nA box represents a storage region,\nnot an extra heart chamber.',ha='center',va='center',fontsize=14)
    ax.text(3,-1,'Closed boundary: blood moves through two pumps and two vascular beds.',ha='center',fontsize=14)
    save(fig,out,'circulation-map','From circulation anatomy to six storage regions','Original functional diagram: left ventricle, systemic arteries, systemic veins, right ventricle, pulmonary arteries and pulmonary veins form a closed loop. Four valve links and two vascular resistance beds are labeled.')
    rates=np.linspace(50,150,201);q=6.;stroke=q*1000/rates
    fig,ax=plt.subplots(figsize=(7.6,4.8));ax.plot(rates,stroke,lw=2.4,color='#087e8b',label='All pairs give 6 L/min')
    pairs=[(60,100),(80,75),(120,50)]
    for f,sv in pairs:ax.plot(f,sv,'o',color='#b16a20');ax.annotate(f'({f}, {sv})',(f,sv),xytext=(6,8),textcoords='offset points',fontsize=16)
    ax.set(xlabel='Heart rate (beats/min)',ylabel='Stroke volume (mL/beat)',title='One mean-flow observation\nleaves many possibilities',xlim=(48,153),ylim=(35,130));ax.legend();ax.grid(alpha=.18)
    save(fig,out,'flow-identifiability','Mean flow does not separate rate and stroke volume','An inverse curve contains three highlighted rate/stroke-volume pairs:60 and100,80 and75,120 and50. All yield6 liters per minute, so this measurement alone cannot identify both factors.')
    cases=[mean_observables(*pair) for pair in pairs];assert all(abs(x['flow_L_min']-6)<1e-12 for x in cases)
    assert all(abs(x['resistance_mmHg_min_L']-15)<1e-12 for x in cases)
    # Product-preserving perturbation and dimensional rescaling are independent checks.
    a=mean_observables(72,80);b=mean_observables(72*1.2,80/1.2);assert np.isclose(a['flow_L_min'],b['flow_L_min'])
    rejected=0
    for args in [(0,75,90),(80,-1,90),(80,75,float('nan')),(1e308,1e308,90)]:
        try:mean_observables(*args)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid input accepted')
    result={'model':'illustrative mean-flow observation map','pairs_rate_bpm_stroke_ml':pairs,'observables':cases,'checks':{'equal_products_equal_flow':True,'product_preserving_perturbation':True,'invalid_cases_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
