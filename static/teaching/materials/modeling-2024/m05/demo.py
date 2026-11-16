"""Original two-state attachment illustration; fixed force per attached head.
This is not a strain-resolved crossbridge model, a force-velocity law or a
cardiac mechanics prediction. Run python demo.py with NumPy/Matplotlib.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def advance(attached, duration_s, attach_per_s, detach_per_s):
    a=float(attached);t=np.asarray(duration_s,dtype=float);f=float(attach_per_s);g=float(detach_per_s)
    if not np.isfinite([a,f,g]).all() or not np.isfinite(t).all() or not 0<=a<=1 or np.any(t<0) or f<0 or g<0:
        raise ValueError('Fraction in [0,1], time and rates nonnegative, all inputs finite required')
    total=f+g
    if not np.isfinite(total):raise ValueError('Combined rate exceeds finite numeric range')
    if total==0:return np.full_like(t,a,dtype=float)
    equilibrium=f/total
    with np.errstate(over='ignore'):
        progress=-np.expm1(-total*t)
    return a+(equilibrium-a)*progress

def force_pn(attached, heads=1000, force_per_attached_pn=2.):
    a=np.asarray(attached,dtype=float)
    if not np.isfinite(a).all() or np.any((a<0)|(a>1)) or not np.isfinite([heads,force_per_attached_pn]).all() or heads<0 or force_per_attached_pn<0:
        raise ValueError('Fractions in [0,1], nonnegative finite head count and force required')
    with np.errstate(over='ignore',invalid='ignore'):result=a*heads*force_per_attached_pn
    if not np.isfinite(result).all():raise ValueError('Force exceeds finite numeric range')
    return result

def protocol():
    """Three exact constant-rate intervals; rates change but state is continuous."""
    times=[0.];values=[.5];state=.5
    for start,f in [(0.,1.),(1.,3.),(2.,0.)]:
        local=np.linspace(0,1,101)
        segment=advance(state,local,f,1.)
        times.extend((start+local[1:]).tolist());values.extend(segment[1:].tolist());state=float(segment[-1])
    return np.array(times),np.array(values)

def save(fig,out,name,title,description):
    fig.savefig(out/(name+'.svg'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
    path=out/(name+'.svg');tree=ET.parse(path);node=tree.getroot();ns='{http://www.w3.org/2000/svg}'
    node.set('role','img');node.set('aria-labelledby','figure-title figure-description')
    for tag,ident,text in [('title','figure-title',title),('desc','figure-description',description)]:
        el=ET.Element(ns+tag,id=ident);el.text=text;node.insert(0,el)
    tree.write(path,encoding='utf-8',xml_declaration=True)

def run(output_dir=None):
    out=Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':17,'axes.titlesize':17,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
    fig,ax=plt.subplots(figsize=(9.6,4.6));ax.set(xlim=(0,10),ylim=(0,5));ax.axis('off')
    for x,label in [(0.6,'Detached\nfraction 1 − A'),(6.,'Attached\nfraction A')]:
        ax.add_patch(FancyBboxPatch((x,1.6),3.3,1.8,boxstyle='round,pad=.1',facecolor='#e4f1f2',edgecolor='#18384a',lw=2))
        ax.text(x+1.65,2.5,label,ha='center',va='center',fontsize=19)
    ax.add_patch(FancyArrowPatch((4,3.25),(6,3.25),arrowstyle='->',mutation_scale=22,lw=2,color='#087e8b'))
    ax.add_patch(FancyArrowPatch((6,1.7),(4,1.7),arrowstyle='->',mutation_scale=22,lw=2,color='#a54e2c'))
    ax.text(5,3.85,'Attachment flux: f (1 − A)',ha='center');ax.text(5,1.,'Detachment flux: g A',ha='center')
    ax.set_title('Two categories; one conserved population',pad=10)
    fig.tight_layout();save(fig,out,'state-balance','Attached and detached fractions','Original two-state model. Attachment takes fraction from detached 1 minus A at rate f times 1 minus A; detachment returns fraction at rate g times A. Both fluxes have units per second. Total fraction is one.')
    t,a=protocol();fig,axs=plt.subplots(1,2,figsize=(10.5,4.8))
    axs[0].plot(t,a,color='#087e8b',lw=2.5)
    for boundary in [1,2]:axs[0].axvline(boundary,color='#777',ls=':',lw=1)
    axs[0].set(xlabel='Time (s)',ylabel='Attached fraction A',ylim=(0,1),title='Rates change; state stays continuous')
    axs[0].text(.5,.88,'f = 1',ha='center');axs[0].text(1.5,.88,'f = 3',ha='center');axs[0].text(2.5,.88,'f = 0',ha='center')
    axs[0].text(1.5,.07,'g = 1/s throughout',ha='center')
    constant_t=np.linspace(0,1.5,151)
    axs[1].plot(constant_t,advance(0,constant_t,3,1),label='f = 3/s, g = 1/s',lw=2.5,color='#087e8b')
    axs[1].plot(constant_t,advance(0,constant_t,6,2),'--',label='Both rates doubled',lw=2.5,color='#a54e2c')
    axs[1].axhline(.75,color='#777',ls=':',lw=1);axs[1].set(xlabel='Time (s)',ylabel='Attached fraction A',ylim=(0,1),title='Same endpoint; different timescale');axs[1].legend(loc='lower right',fontsize=17)
    fig.tight_layout();save(fig,out,'occupancy-traces','Attachment protocols and timescale comparison','Left: initial fraction 0.5, detachment 1 per second, attachment 1 then 3 then 0 per second on consecutive one-second intervals; the state remains continuous at rate changes. Right: initial zero, rates 3 and 1 versus 6 and 2 per second. Both approach attached fraction 0.75; doubling both rates halves the relaxation time.')
    assert np.all((a>=0)&(a<=1));assert np.array_equal(advance(.3,[0,1,1e6],0,0),[.3,.3,.3])
    assert np.allclose(advance(.75,[0,.1,1],3,1),.75)
    assert np.allclose(advance(0,constant_t,6,2),advance(0,2*constant_t,3,1))
    assert np.isclose(advance(float(advance(.2,.3,2,3)),.4,2,3),advance(.2,.7,2,3))
    assert np.allclose(advance(.7,[0,1],0,2),.7*np.exp(-2*np.array([0,1])))
    assert force_pn(.75)==1500
    rejected=0
    for call in [lambda:advance(1.1,1,1,1),lambda:advance(.5,-1,1,1),lambda:advance(.5,1,-1,1),lambda:advance(.5,np.nan,1,1),lambda:force_pn(.5,heads=-1)]:
        try:call()
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid input accepted')
    report={'model':'two-state occupancy; fixed per-head force is a separate illustrative readout','equilibrium_for_f3_g1':.75,'relaxation_time_s':.25,'force_for_1000_heads_2pN_each_at_equilibrium_pN':1500,'protocol_fraction_at_0_1_2_3_seconds':a[::100].tolist(),'checks':{'bounds':True,'zero_rates_preserve_state':True,'equilibrium_preserved':True,'rate_time_scaling':True,'semigroup':True,'pure_detachment':True,'invalid_cases_rejected':rejected},'limitations':['no strain distribution','no sliding or shortening speed','no ATP consumption model','no calcium activation dynamics','not a ventricular force prediction']}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
