"""Original ideal osmotic volume model; all parameter values are synthetic.
Water crosses; solute particles do not. Outside concentration and temperature
are held fixed, hydrostatic pressures equal, and membrane mechanics omitted.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def simulate(amount_fmol=300.,outside_mm=150.,initial_pl=1.,conductance=.002,seconds=30.,step_s=.05):
    values=np.array([amount_fmol,outside_mm,initial_pl,conductance,seconds,step_s],dtype=float)
    if not np.isfinite(values).all() or min(amount_fmol,outside_mm,initial_pl,step_s)<=0 or conductance<0 or seconds<0:
        raise ValueError('Finite positive amount, outside concentration, initial volume and step required; conductance and duration must be nonnegative')
    with np.errstate(over='ignore',divide='ignore'):equilibrium=amount_fmol/outside_mm;requested=np.divide(seconds,step_s);step_drain=step_s*conductance*outside_mm
    if not np.isfinite(equilibrium) or equilibrium<=0:raise ValueError('Equilibrium volume must be representable and positive')
    if not np.isfinite(requested) or requested>2_000_000:raise ValueError('Requested trajectory exceeds classroom computation limit')
    if step_drain>min(initial_pl,equilibrium):raise ValueError('Step exceeds the sufficient monotone-Euler bound h L c_out <= min(V0,Veq)')
    count=max(1,int(np.ceil(requested))) if seconds>0 else 0
    time=np.linspace(0,seconds,count+1);volume=np.empty(count+1);volume[0]=initial_pl
    for i,h in enumerate(np.diff(time)):
        volume[i+1]=volume[i]+h*conductance*(amount_fmol/volume[i]-outside_mm)
    if not np.isfinite(volume).all() or np.any(volume<=0):raise FloatingPointError('Nonphysical volume; inspect inputs and discretization')
    return time,volume


def save(fig,out,name,title,description):
    fig.savefig(out/(name+'.svg'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
    path=out/(name+'.svg');tree=ET.parse(path);node=tree.getroot();ns='{http://www.w3.org/2000/svg}'
    node.set('role','img');node.set('aria-labelledby','figure-title figure-description')
    for tag,ident,text in [('title','figure-title',title),('desc','figure-description',description)]:
        el=ET.Element(ns+tag,id=ident);el.text=text;node.insert(0,el)
    tree.write(path,encoding='utf-8',xml_declaration=True)


def run(output_dir=None):
    out=Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':18,'axes.titlesize':18,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    colors=['#176c7b','#677b4a','#b06838'];external=[150.,300.,450.]
    fig,ax=plt.subplots(figsize=(10,4.8));vol=np.linspace(.55,2.5,250);ax.plot(vol,300/vol,color='#18384a',lw=2.8,label='Inside: 300 fmol / volume')
    for ce,col in zip(external,colors):
        ax.axhline(ce,color=col,ls='--',lw=1.8);ax.scatter([300/ce],[ce],color=col,s=65,zorder=4);ax.text(2.47,ce+12,f'Outside {ce:g} mM',ha='right',va='bottom',fontsize=18,color=col)
    ax.set(xlabel='Volume (pL)',ylabel='Particle concentration (mM)',title='Fixed amount; concentration changes with volume',ylim=(100,570));ax.text(1.55,535,'Inside: 300 fmol / volume',ha='center',fontsize=18,color='#18384a');fig.tight_layout()
    save(fig,out,'osmotic-balance','Concentration and equilibrium volume','Inside concentration equals 300 femtomoles of impermeant solute particles divided by volume in picoliters. Horizontal external concentrations 150, 300, 450 millimolar intersect at 2, 1, and two-thirds picoliters. All hydrostatic pressure differences are set to zero in this ideal teaching model.')
    fig,axs=plt.subplots(1,2,figsize=(11,4.8));summary={}
    for ce,col in zip(external,colors):
        t,v=simulate(outside_mm=ce);summary[str(int(ce))]={'equilibrium_pl':300/ce,'final_volume_pl':float(v[-1]),'initial_flow_pl_per_s':.002*(300-ce)}
        axs[0].plot(t,v,color=col,lw=2.5,label=f'Outside {ce:g} mM');axs[1].plot(t,300/v,color=col,lw=2.5)
        axs[0].axhline(300/ce,color=col,ls=':',lw=1.3)
    axs[0].set(xlabel='Time (s)',ylabel='Volume (pL)',title='Water changes the volume');axs[0].legend(fontsize=18,loc='center right')
    axs[1].set(xlabel='Time (s)',ylabel='Inside concentration (mM)',title='Impermeant amount stays fixed');fig.tight_layout()
    save(fig,out,'volume-trajectories','Osmotic volume and concentration trajectories','Explicit Euler at step 0.05s, initial volume 1 pL, impermeant amount 300 fmol, water coefficient 0.002 pL/(s mM). External concentrations 150, 300, 450 mM produce swelling, no change, and shrinking under equal hydrostatic pressures. Dotted volume lines show equilibria. These are ideal synthetic scenarios, not predictions of cell survival or lysis.')
    for ce in external:
        _,v=simulate(outside_mm=ce);eq=300/ce
        assert np.all(v>=min(1,eq)-1e-12) and np.all(v<=max(1,eq)+1e-12)
        assert np.allclose(v*(300/v),300)
        assert np.all(np.diff(v)*(eq-1)>=-1e-13)
    assert np.all(simulate(outside_mm=300)[1]==1)
    assert np.all(simulate(conductance=0)[1]==1)
    _,one=simulate(seconds=.2,step_s=.2);assert np.isclose(one[1],1.06)
    # Scaling amount and volume by2 needs coefficient scaled by2 for the same concentration path.
    _,base=simulate();_,scaled=simulate(amount_fmol=600,initial_pl=2,conductance=.004)
    assert np.allclose(scaled,2*base)
    ends={str(h):float(simulate(seconds=10,step_s=h)[1][-1]) for h in [.2,.1,.05]};coarse=abs(ends['0.2']-ends['0.1']);fine=abs(ends['0.1']-ends['0.05']);assert fine<coarse
    rejected=0
    for fn in [lambda:simulate(outside_mm=0),lambda:simulate(amount_fmol=-1),lambda:simulate(initial_pl=0),lambda:simulate(conductance=-1),lambda:simulate(step_s=4),lambda:simulate(seconds=np.nan),lambda:simulate(seconds=1e308,step_s=1e-308)]:
        try:fn()
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid input accepted')
    report={'model':'ideal impermeant solute and water-only membrane; synthetic','amount_fmol':300,'initial_volume_pl':1,'coefficient_pl_per_s_mm':.002,'step_s':.05,'scenarios':summary,'first_0_2s_euler_volume_pl':1.06,'endpoint_refinement_gaps_pl':{'0.2_to_0.1':coarse,'0.1_to_0.05':fine},'checks':{'positive_bounded_monotone_volume':True,'constant_impermeant_amount':True,'matched_concentrations_static':True,'zero_conductance_static':True,'amount_volume_coefficient_scaling':True,'step_refinement':True,'invalid_inputs_rejected':rejected},'limitations':['no permeant solutes or ion pumps','outside concentration fixed by a large reservoir','hydrostatic pressure difference set to zero','no membrane tension elasticity or rupture','fixed water coefficient and temperature']}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
