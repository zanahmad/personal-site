"""Original fixed-output parallel network; not a Fontan or patient model.
Return oxygen contents are prescribed, not obtained from gas exchange/metabolism.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def scalar(value, name, positive=False):
    try: value=float(value)
    except (TypeError, ValueError, OverflowError) as exc: raise ValueError(name+' must be a finite scalar') from exc
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(name+' must be finite and '+('positive' if positive else 'nonnegative'))
    return value


def parallel(q_total=5, r_p=10, r_s=15, c_p=200, c_s=120):
    q=scalar(q_total,'total flow');rp=scalar(r_p,'pulmonary resistance',True);rs=scalar(r_s,'systemic resistance',True)
    cp=scalar(c_p,'pulmonary return content');cs=scalar(c_s,'systemic return content')
    # Scale the resistances before addition, avoiding overflow in rp + rs.
    scale=max(rp,rs); ap=rp/scale; ass=rs/scale
    fp=ass/(ap+ass);fs=ap/(ap+ass)
    qp=q*fp;qs=q*fs;drop=qp*rp
    cm=fp*cp+fs*cs if q>0 else None
    delivery=qs*cm if cm is not None else 0.0
    values=[qp,qs,drop,delivery]+([cm] if cm is not None else [])
    if not all(math.isfinite(v) for v in values):raise ValueError('requested quantities exceed finite arithmetic range')
    return {'q_p_L_min':qp,'q_s_L_min':qs,'common_drop_mmHg':drop,
            'mixed_content_mL_O2_L':cm,'systemic_delivery_mL_O2_min':delivery}


def save(fig,out,name,title,desc):
    fig.savefig(out/(name+'.svg'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
    path=out/(name+'.svg');tree=ET.parse(path);root=tree.getroot();ns='{http://www.w3.org/2000/svg}'
    root.set('role','img');root.set('aria-labelledby','figure-title figure-description')
    for tag,ident,txt in [('title','figure-title',title),('desc','figure-description',desc)]:
        el=ET.Element(ns+tag,id=ident);el.text=txt;root.insert(0,el)
    tree.write(path,encoding='utf-8',xml_declaration=True)


def box(ax,x,y,label,w=2.5,h=.72):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.08',facecolor='#eef4f4',edgecolor='#244c59',lw=1.6))
    ax.text(x,y,label,ha='center',va='center',fontsize=20)


def arrow(ax,a,b,rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=20,color='#244c59',linewidth=1.8,connectionstyle=f'arc3,rad={rad}'))


def run(output_dir=None):
    out=Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'legend.fontsize':20,'svg.fonttype':'none','font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(11,5.4))
    for ax in axs:ax.set(xlim=(-.2,5.7),ylim=(-.5,6.1));ax.axis('off')
    ax=axs[0];ax.set_title('Serial reference route',pad=18)
    for x,y,t in [(2.7,5.1,'Right pump'),(2.7,3.6,'Lungs'),(2.7,2.1,'Left pump'),(2.7,.6,'Body')]:box(ax,x,y,t)
    for y in [5.1,3.6,2.1]:arrow(ax,(2.7,y-.46),(2.7,y-1.04))
    arrow(ax,(1.35,.6),(1.35,5.1),rad=-.7)
    ax=axs[1];ax.set_title('Selected parallel model',pad=18)
    box(ax,2.7,5.1,'Common pump',w=2.9);box(ax,1.1,2.8,'Lungs',w=1.8);box(ax,4.3,2.8,'Body',w=1.8);box(ax,2.7,.6,'Mixed return')
    arrow(ax,(2.2,4.65),(1.1,3.26));arrow(ax,(3.2,4.65),(4.3,3.26))
    arrow(ax,(1.1,2.34),(2.2,1.05));arrow(ax,(4.3,2.34),(3.2,1.05))
    arrow(ax,(1.35,.6),(1.35,5.1),rad=-.8)
    ax.text(1.0,4.1,'Qp',ha='center',fontsize=20);ax.text(4.4,4.1,'Qs',ha='center',fontsize=20)
    ax.text(2.7,-.2,'Qp + Qs = QT',ha='center',fontsize=20)
    fig.subplots_adjust(wspace=.22,left=.02,right=.98,bottom=.04,top=.88)
    save(fig,out,'circulation-routes','Serial and selected parallel circulation routes','Original route graphs. Serial: right pump to lungs to left pump to body and return. Parallel: one common pump supplies lung and body branches, whose returns mix. The parallel model is not a Fontan circulation. Arrows are route conventions; blood is not blue.')
    rp=np.linspace(2,30,141);rows=[parallel(r_p=r) for r in rp]
    fig,axs=plt.subplots(2,1,figsize=(10,6.6),sharex=True)
    axs[0].plot(rp,[v['q_p_L_min'] for v in rows],label='Pulmonary Qp',lw=2.5,color='#126782')
    axs[0].plot(rp,[v['q_s_L_min'] for v in rows],label='Systemic Qs',lw=2.5,ls='--',color='#a34a28')
    axs[0].set(ylabel='Flow (L/min)',ylim=(0,5),yticks=[0,2,4])
    axs[1].plot(rp,[v['systemic_delivery_mL_O2_min'] for v in rows],lw=2.5,color='#244c59')
    for r in [5,10]:
        v=parallel(r_p=r);axs[1].scatter(r,v['systemic_delivery_mL_O2_min'],s=60,color='#a34a28',zorder=4)
    axs[1].set(xlabel='Pulmonary resistance (mmHg min/L)',ylabel='Delivery\n(mL O₂/min)',ylim=(0,600),yticks=[0,300,600],xticks=[5,10,20,30])
    fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.58,1.0),ncol=2,fontsize=20,frameon=False)
    fig.tight_layout(rect=(0,0,1,.9))
    save(fig,out,'flow-and-delivery','Flow division and systemic oxygen delivery','QT 5 L/min, systemic resistance 15 mmHg min/L, return contents 200 and 120 mL oxygen/L. Reducing pulmonary resistance from 10 to 5 increases mixed content from 168 to 180 but lowers systemic flow from 2 to 1.25 and delivery from 336 to 225. Delivery is not consumption; no clinical optimum is established.')
    a=parallel();b=parallel(r_p=5)
    assert np.allclose([a['q_p_L_min'],a['q_s_L_min'],a['mixed_content_mL_O2_L'],a['systemic_delivery_mL_O2_min']],[3,2,168,336])
    assert np.allclose([b['q_p_L_min'],b['q_s_L_min'],b['mixed_content_mL_O2_L'],b['systemic_delivery_mL_O2_min']],[3.75,1.25,180,225])
    for r,row in zip(rp,rows):
        assert np.isclose(row['q_p_L_min']+row['q_s_L_min'],5)
        assert np.isclose(row['q_p_L_min']*r,row['q_s_L_min']*15)
        assert 120<=row['mixed_content_mL_O2_L']<=200
    assert parallel(r_p=15)['q_p_L_min']==2.5
    zero=parallel(q_total=0);assert zero['mixed_content_mL_O2_L'] is None and zero['systemic_delivery_mL_O2_min']==0
    assert parallel(r_p=1e9)['q_s_L_min']>4.99999
    rejected=0
    for params in [{'q_total':-1},{'r_p':0},{'r_s':-2},{'c_p':float('nan')},{'c_s':-1},{'q_total':float('inf')},{'q_total':1e308,'r_p':1e308,'r_s':1e308}]:
        try:parallel(**params)
        except ValueError:rejected+=1
        else:raise AssertionError('invalid controls accepted')
    result={'model':'prescribed-output parallel branches with fixed return oxygen contents; not Fontan','worked_example':a,'reduced_pulmonary_resistance':b,'checks':{'flow_conservation':True,'equal_branch_drop':True,'mixing_bounds':True,'equal_resistances':True,'zero_output_undefined_mixture':True,'large_resistance_limit':True,'invalid_controls_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
