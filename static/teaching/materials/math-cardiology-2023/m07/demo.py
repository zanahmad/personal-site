"""Original static fetal-route bookkeeping and local shunt laws.
Pressures/selected flows are supplied, not solved; no birth-transition kinetics.
The foramen law is a finite-resistance directional surrogate, not flap mechanics.
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


def finite(value,name):
    try:value=float(value)
    except (TypeError,ValueError,OverflowError) as exc:raise ValueError(name+' must be a finite scalar') from exc
    if not math.isfinite(value):raise ValueError(name+' must be finite')
    return value


def ductus_flow(p_pa,p_ao,resistance=.1,conducting=True):
    pa=finite(p_pa,'pulmonary pressure');ao=finite(p_ao,'aortic pressure');r=finite(resistance,'ductus resistance')
    if r<=0:raise ValueError('resistance must be positive')
    if not isinstance(conducting,(bool,np.bool_)):raise ValueError('conducting must be a boolean')
    if not conducting:return 0.0
    q=(pa-ao)/r
    if not math.isfinite(q):raise ValueError('ductus flow exceeds finite arithmetic range')
    return q


def foramen_flow(p_ra,p_la,resistance=.05):
    ra=finite(p_ra,'right atrial pressure');la=finite(p_la,'left atrial pressure');r=finite(resistance,'forward resistance')
    if r<=0:raise ValueError('forward resistance must be positive')
    drop=ra-la
    if not math.isfinite(drop):raise ValueError('pressure difference exceeds finite range')
    q=max(drop,0.0)/r
    if not math.isfinite(q):raise ValueError('foramen flow exceeds finite arithmetic range')
    return q


def balanced_flows(q_p,q_d,q_f):
    p=finite(q_p,'pulmonary flow');d=finite(q_d,'signed ductus flow');f=finite(q_f,'foramen flow')
    if p<0 or f<0:raise ValueError('pulmonary and foramen flows must be nonnegative')
    right=p+d;left=p+f;systemic=left+d
    if not all(math.isfinite(v) and v>=0 for v in [right,left,systemic]):
        raise ValueError('assigned flows violate finite forward-pump/systemic-flow assumptions')
    if not np.isclose(systemic,right+f,rtol=1e-12,atol=1e-12):raise ValueError('floating-point junction mismatch')
    return {'Qp':p,'Qd':d,'Qf':f,'QR':right,'QL':left,'Qs':systemic}


def save(fig,out,name,title,desc):
    fig.savefig(out/(name+'.svg'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
    path=out/(name+'.svg');tree=ET.parse(path);root=tree.getroot();ns='{http://www.w3.org/2000/svg}'
    root.set('role','img');root.set('aria-labelledby','figure-title figure-description')
    for tag,ident,txt in [('title','figure-title',title),('desc','figure-description',desc)]:
        el=ET.Element(ns+tag,id=ident);el.text=txt;root.insert(0,el)
    tree.write(path,encoding='utf-8',xml_declaration=True)


def box(ax,x,y,text,w=2.5,h=.9):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.06',facecolor='#eef4f4',edgecolor='#244c59',lw=1.6))
    ax.text(x,y,text,ha='center',va='center',fontsize=20)


def arrow(ax,a,b,rad=0,style='-'):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=21,linewidth=1.9,color='#244c59',linestyle=style,connectionstyle=f'arc3,rad={rad}'))


def run(output_dir=None):
    out=Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'legend.fontsize':20,'svg.fonttype':'none','font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,6.8));ax.set(xlim=(-.9,10.5),ylim=(-.2,7.4));ax.axis('off')
    box(ax,2,6.3,'Right atrium');box(ax,8,6.3,'Left atrium')
    box(ax,2,3.1,'Right ventricle\n→ pulmonary artery',w=3.4,h=1.2)
    box(ax,8,3.1,'Left ventricle\n→ aorta',w=2.8,h=1.2)
    box(ax,5,4.7,'Lungs',w=1.9);box(ax,5,.7,'Body + placenta',w=3.6)
    arrow(ax,(2,5.78),(2,3.77));ax.text(2.25,4.7,'QR',va='center',fontsize=20)
    arrow(ax,(8,5.78),(8,3.77));ax.text(8.25,4.7,'QL',va='center',fontsize=20)
    arrow(ax,(3.35,6.3),(6.65,6.3));ax.text(5,6.62,'FO: Qf ≥ 0',ha='center',fontsize=20)
    arrow(ax,(3.77,3.1),(6.53,3.1));ax.text(5.15,2.5,'DA: signed Qd',ha='center',fontsize=20)
    arrow(ax,(3.35,3.77),(4.3,4.19));ax.text(3.5,4.25,'Qp',ha='center',fontsize=20)
    arrow(ax,(5.65,5.23),(6.75,5.91))
    arrow(ax,(8,2.43),(6.65,1.22));ax.text(7.75,1.65,'Qs',ha='center',fontsize=20)
    ax.plot([3.12,.05,.05,.66],[.7,.7,6.3,6.3],color='#244c59',lw=1.9);arrow(ax,(.25,6.3),(.66,6.3))
    ax.text(-.5,3.7,'Systemic return',rotation=90,va='center',fontsize=20)
    ax.set_title('Grouped fetal routes — not anatomical geometry',pad=10)
    fig.tight_layout()
    save(fig,out,'fetal-routes','Grouped fetal circulation routes','Foramen ovale connects right and left atria. Ductus arteriosus connects pulmonary artery to aorta; the chosen positive direction is pulmonary to aortic. Lungs receive a nonzero branch flow. Right and left ventricles are grouped with their arterial outlets; body and placenta are grouped. Umbilical vessels and ductus venosus are discussed in notes but not separately resolved. The graph is not anatomical geometry.')
    drops=np.linspace(-10,10,161)
    fig,axs=plt.subplots(1,2,figsize=(11,4.9))
    axs[0].plot(drops,[ductus_flow(d,0) for d in drops],lw=2.5,label='Open',color='#126782')
    axs[0].plot(drops,np.zeros_like(drops),lw=2.5,ls='--',label='Closed',color='#a34a28')
    axs[0].set(xlabel='Ppa − Pao (mmHg)',ylabel='Qd (mL/min)',title='Ductus: signed flow',yticks=[-100,0,100],xticks=[-10,0,10]);axs[0].legend(loc='upper left',fontsize=20)
    axs[1].plot(drops,[foramen_flow(d,0) for d in drops],lw=2.5,color='#244c59')
    axs[1].set(xlabel='PRA − PLA (mmHg)',ylabel='Qf (mL/min)',title='Foramen: one-way rule',yticks=[0,100,200],xticks=[-10,0,10],ylim=(-10,225))
    for ax in axs:ax.axvline(0,color='#888888',lw=1,alpha=.5)
    fig.tight_layout(w_pad=1.5)
    save(fig,out,'shunt-rules','Local ductus and foramen surrogate laws','Ductus resistance 0.1 mmHg min/mL permits signed flow; declared closure gives zero conductance. Foramen forward resistance 0.05 permits only right-to-left nonnegative flow, with zero for a reversed or zero pressure difference. Pressures are supplied, not solved. Zero flow does not establish anatomical closure.')
    states={'pre_transition_example':balanced_flows(100,50,40),'reversed_ductus_example':balanced_flows(300,-100,0),'closed_shunts_example':balanced_flows(200,0,0)}
    assert ductus_flow(30,25)==50 and ductus_flow(20,30)==-100
    assert ductus_flow(30,30)==0 and ductus_flow(20,30,conducting=False)==0
    assert foramen_flow(6,4)==40 and foramen_flow(4,7)==0 and foramen_flow(4,4)==0
    assert all(foramen_flow(d,0)>=0 for d in drops)
    for v in states.values():
        assert np.isclose(v['QR'],v['Qp']+v['Qd']) and np.isclose(v['QL'],v['Qp']+v['Qf'])
        assert np.isclose(v['Qs'],v['QL']+v['Qd']) and np.isclose(v['Qs'],v['QR']+v['Qf'])
    rejected=0
    for call in [lambda:ductus_flow(1,0,0),lambda:ductus_flow(float('nan'),0),lambda:ductus_flow(1,0,conducting='false'),lambda:foramen_flow(1,0,-1),lambda:balanced_flows(-1,0,0),lambda:balanced_flows(10,-11,0),lambda:balanced_flows(10,0,-1),lambda:balanced_flows(10,float('inf'),0),lambda:ductus_flow(1e308,-1e308),lambda:foramen_flow(1e308,-1e308)]:
        try:call()
        except ValueError:rejected+=1
        else:raise AssertionError('invalid controls accepted')
    report={'model':'static prescribed states; no closure timing, gas exchange or coupled pressure solver','flow_units':'mL/min','static_states':states,'checks':{'ductus_sign_and_zero':True,'declared_closure':True,'one_way_foramen':True,'four_junction_balances':True,'invalid_controls_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
