"""Original threshold analysis using functions, branches and explicit loops.
None marks a missing reading; no value is invented in its place.
"""
from pathlib import Path
import math,json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TIMES_MIN=[0.,1.,2.,3.,4.,5.,6.,7.,8.]
TEMPERATURES_C=[80.,62.,48.,40.,35.,None,28.,25.,23.]

def classify(temperature_c,target_c):
    if not isinstance(target_c,(int,float)) or isinstance(target_c,bool) or not math.isfinite(target_c):
        raise ValueError('Target must be a finite number in degrees Celsius.')
    if temperature_c is None:return 'missing'
    if not isinstance(temperature_c,(int,float)) or isinstance(temperature_c,bool) or not math.isfinite(temperature_c):
        raise ValueError('A reading must be a finite number or None.')
    if temperature_c < -273.15:raise ValueError('Temperature cannot be below absolute zero.')
    if temperature_c <= target_c:return 'at_or_below'
    return 'above'

def analyze(times_min,temperatures_c,target_c=40.):
    if len(times_min)!=len(temperatures_c) or len(times_min)==0:
        raise ValueError('Use equally sized, nonempty time and reading lists.')
    if any(not isinstance(t,(int,float)) or isinstance(t,bool) or not math.isfinite(t) for t in times_min):
        raise ValueError('Times must be finite numbers.')
    if times_min[0]<0 or any(b<=a for a,b in zip(times_min,times_min[1:])):
        raise ValueError('Times must be nonnegative and strictly increasing.')
    counts={'above':0,'at_or_below':0,'missing':0};first=None;states=[]
    for time,temperature in zip(times_min,temperatures_c):
        state=classify(temperature,target_c);states.append(state);counts[state]+=1
        if state=='at_or_below' and first is None:first=time
    known=counts['above']+counts['at_or_below']
    fraction=counts['at_or_below']/known if known else None
    return {'target_C':target_c,'counts':counts,'known_readings':known,
            'fraction_of_known_at_or_below':fraction,'first_recorded_time_min':first,'states':states}

def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/(stem+'.'+ext),bbox_inches='tight')
    plt.close(fig);ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(out/(stem+'.svg'));r=tree.getroot();r.set('role','img');r.set('aria-labelledby',stem+'-title '+stem+'-desc')
    for tag,value in [('title',title),('desc',desc)]:
        e=ET.Element('{'+ns+'}'+tag,id=stem+'-'+tag);e.text=value;r.insert(0,e)
    tree.write(out/(stem+'.svg'),encoding='utf-8',xml_declaration=True)

def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    report=analyze(TIMES_MIN,TEMPERATURES_C)
    assert classify(40,40)=='at_or_below' and classify(40.01,40)=='above'
    assert report['counts']=={'above':3,'at_or_below':5,'missing':1}
    assert report['first_recorded_time_min']==3 and report['fraction_of_known_at_or_below']==.625
    assert analyze([0,1],[None,None])['fraction_of_known_at_or_below'] is None
    assert analyze([0],[40])['first_recorded_time_min']==0
    rejected=0
    for fn in [lambda:classify(float('nan'),40),lambda:classify('40',40),lambda:analyze([0,0],[40,39]),lambda:analyze([],[])]:
        try:fn()
        except ValueError:rejected+=1
    assert rejected==4
    plt.rcParams.update({'font.size':14,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8,4.6));values=[np.nan if x is None else x for x in TEMPERATURES_C]
    ax.plot(TIMES_MIN,values,':',color='#9aa4a8')
    for state,color,label in [('above','#a56320','Above target'),('at_or_below','#146f7e','At or below target')]:
        ids=[i for i,s in enumerate(report['states']) if s==state]
        ax.scatter([TIMES_MIN[i] for i in ids],[values[i] for i in ids],color=color,s=55,label=label,zorder=3)
    ax.axhline(40,color='#555',ls='--',label='Target = 40 °C')
    ax.annotate('Missing at 5 min\nNo temperature invented',xy=(5,52),xytext=(3.1,60),arrowprops={'arrowstyle':'->','color':'#666'},fontsize=14)
    ax.set(xlabel='Recorded time (min)',ylabel='Temperature (°C)',title='Equality and a missing observation',ylim=(20,90));ax.legend(frameon=False,loc='upper right',fontsize=14);ax.grid(alpha=.2)
    save(fig,out,'threshold-record','Classifying a synthetic temperature record','The 40-degree observation at 3 minutes is included by the at-or-below rule. One observation at 5 minutes is missing; the line is interrupted there. Five of eight known readings satisfy the rule. This is a recorded-time decision, not an exact continuous crossing time.')
    targets=np.arange(20,66);counts=[analyze(TIMES_MIN,TEMPERATURES_C,float(t))['counts']['at_or_below'] for t in targets]
    fig,ax=plt.subplots(figsize=(7.4,4.4));ax.step(targets,counts,where='post',color='#146f7e',lw=2);ax.scatter([35,40],[4,5],color='#a56320',zorder=3)
    ax.set(xlabel='Chosen target (°C)',ylabel='At or below target\n(known readings)',title='One record, changing target',ylim=(-.2,8.5));ax.set_yticks(range(9));ax.grid(alpha=.2)
    save(fig,out,'threshold-counts','Threshold and count for eight known readings','A step plot shows how the at-or-below count changes as the target increases. A target of 35 degrees includes four readings; 40 degrees includes five. The missing reading is excluded from every known-reading denominator, not replaced by zero.')
    report['checks']={'equality_included':True,'all_missing_fraction_is_None':True,'zero_first_time_preserved':True,'invalid_inputs_rejected':rejected}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
