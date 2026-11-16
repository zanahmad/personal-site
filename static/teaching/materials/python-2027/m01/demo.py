"""Proposed 2027 day 1: original synthetic motion records, no fitted motion law."""
from pathlib import Path
from numbers import Real
import json,math
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TIMES_S=[0.,2.,4.,6.,8.]
POSITION_A_MM=[10.,14.,18.,22.,26.]
POSITION_B_MM=[0.,6.,12.,18.,24.]


def summarize(times,positions):
    if len(times)!=len(positions) or len(times)<2:raise ValueError('Use matching lists with at least two observations.')
    if not all(isinstance(v,Real) and not isinstance(v,bool) and math.isfinite(v) for v in list(times)+list(positions)):
        raise ValueError('Times and positions must be finite numbers.')
    if any(b<=a for a,b in zip(times,times[1:])):raise ValueError('Observation times must increase strictly.')
    elapsed=times[-1]-times[0];displacement=positions[-1]-positions[0]
    velocity=displacement/elapsed
    if not all(math.isfinite(v) for v in (elapsed,displacement,velocity)):
        raise ValueError('The elapsed time, displacement or velocity exceeds finite arithmetic range.')
    return {'elapsed_s':elapsed,'start_mm':positions[0],'end_mm':positions[-1],'displacement_mm':displacement,'average_velocity_mm_s':velocity}


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/(stem+'.'+ext),bbox_inches='tight')
    plt.close(fig);ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(out/(stem+'.svg'));r=tree.getroot();r.set('role','img');r.set('aria-labelledby',stem+'-title '+stem+'-desc')
    for tag,text in [('title',title),('desc',description)]:
        node=ET.Element('{'+ns+'}'+tag,id=stem+'-'+tag);node.text=text;r.insert(0,node)
    tree.write(out/(stem+'.svg'),encoding='utf-8',xml_declaration=True)


def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    a=summarize(TIMES_S,POSITION_A_MM);b=summarize(TIMES_S,POSITION_B_MM)
    assert a['end_mm']>b['end_mm'] and a['average_velocity_mm_s']<b['average_velocity_mm_s']
    shifted=summarize(TIMES_S,[p-100 for p in POSITION_A_MM]);assert shifted['average_velocity_mm_s']==a['average_velocity_mm_s']
    displacement_cm=(POSITION_A_MM[-1]-POSITION_A_MM[0])/10
    assert displacement_cm/a['elapsed_s']==a['average_velocity_mm_s']/10
    assert summarize([0,1],[5,3])['average_velocity_mm_s']==-2
    rejected=0
    for t,p in [([0,1],[2]),([0,0],[1,2]),([0,1],[1,float('nan')]),([0,1],[1,'2'])]:
        try:summarize(t,p)
        except ValueError:rejected+=1
    assert rejected==4
    plt.rcParams.update({'font.size':18, 'axes.titlesize':18, 'legend.fontsize':18,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(7.6,4.5))
    for name,p,color in [('A',POSITION_A_MM,'#176c7b'),('B',POSITION_B_MM,'#b46d27')]:ax.plot(TIMES_S,p,('o:' if name=='A' else 's:'),label='Object '+name,color=color)
    ax.set(xlabel='Recorded time (s)',ylabel='Position (mm)',title='Position and velocity differ');ax.legend(frameon=False);ax.grid(alpha=.2)
    save(fig,out,'position-records','Two synthetic position records','A starts at ten millimeters and ends at twenty-six; B starts at zero and ends at twenty-four over eight seconds. Dotted connectors show sample order only. A has the larger final position but B has the greater average displacement per second.')
    fig,axs=plt.subplots(1,2,figsize=(9.1,4.6),sharex=True)
    for name,p,color in [('A',POSITION_A_MM,'#176c7b'),('B',POSITION_B_MM,'#b46d27')]:
        change=np.asarray(p)-p[0];axs[0].plot(TIMES_S,change,('o:' if name=='A' else 's:'),label=name,color=color);axs[1].plot(TIMES_S,change/10,('o:' if name=='A' else 's:'),label=name,color=color)
    for ax,unit,title in zip(axs,['mm','cm'],['Subtract the start','Convert the units']):ax.set(xlabel='Recorded time (s)',ylabel='Displacement ('+unit+')',title=title);ax.legend(title='Object',frameon=False);ax.grid(alpha=.2)
    fig.tight_layout();save(fig,out,'displacement-units','One displacement in millimeters and centimeters','Subtracting each object’s first recorded position isolates its displacement. B advances twenty-four millimeters, or 2.4 centimeters, over eight seconds; A advances sixteen millimeters, or 1.6 centimeters. The unit conversion changes the numerical scale, not the comparison.')
    report={'object_A':a,'object_B':b,'checks':{'larger_position_not_larger_average_velocity':True,'origin_shift_preserves_velocity':True,'mm_cm_conversion_consistent':True,'negative_displacement_retained':True,'invalid_inputs_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
