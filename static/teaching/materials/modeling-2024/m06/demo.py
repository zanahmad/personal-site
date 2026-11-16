"""Original closed-population SIR teaching example with synthetic rates.
No real epidemic data, medical guidance or fitted forecast. Explicit Euler
uses the same transfer in each donor/recipient update and rejects unsafe steps.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate(initial=(990.,10.,0.),beta_per_day=.3,gamma_per_day=.1,days=120.,step_days=.1):
    initial=np.asarray(initial,dtype=float)
    params=np.array([beta_per_day,gamma_per_day,days,step_days],dtype=float)
    if initial.shape!=(3,) or not np.isfinite(initial).all() or np.any(initial<0) or not np.isfinite(params).all():raise ValueError('Three finite nonnegative initial compartments and finite parameters required')
    if beta_per_day<0 or gamma_per_day<0 or days<0 or step_days<=0:raise ValueError('Nonnegative rates and duration, positive step required')
    with np.errstate(over='ignore'):population=float(initial.sum());bound=step_days*max(beta_per_day,gamma_per_day)
    if not np.isfinite(population) or population<=0:raise ValueError('Finite positive total population required')
    if bound>1:raise ValueError('Step too large for this positivity-preserving Euler condition: step × max(rate) must be <= 1')
    with np.errstate(over='ignore',divide='ignore'):requested_steps=np.divide(days,step_days)
    if not np.isfinite(requested_steps) or requested_steps>2_000_000:raise ValueError('Requested trajectory exceeds classroom computation limit')
    count=max(1,int(np.ceil(requested_steps))) if days>0 else 0
    times=np.linspace(0,days,count+1);states=np.empty((count+1,3));states[0]=initial
    for k,h in enumerate(np.diff(times)):
        s,i,r=states[k]
        new_infections=(h*beta_per_day)*(i/population)*s
        recoveries=(h*gamma_per_day)*i
        states[k+1]=[s-new_infections,i+new_infections-recoveries,r+recoveries]
    if not np.isfinite(states).all() or states.min() < -1e-12*population:raise FloatingPointError('State bounds failed; inspect the numerical method')
    return times,states

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
    from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
    fig,ax=plt.subplots(figsize=(10.5,4.6));ax.set(xlim=(0,12),ylim=(0,5));ax.axis('off')
    for x,label,col in [(0.3,'S\nSusceptible','#dcebf1'),(4.8,'I\nInfectious','#f1dfd2'),(9.3,'R\nRecovered','#d9eae2')]:
        ax.add_patch(FancyBboxPatch((x,1.5),2.4,1.8,boxstyle='round,pad=.1',facecolor=col,edgecolor='#18384a',lw=2));ax.text(x+1.2,2.4,label,ha='center',va='center',fontsize=20)
    for a,b in [(2.8,4.7),(7.3,9.2)]:ax.add_patch(FancyArrowPatch((a,2.4),(b,2.4),arrowstyle='->',mutation_scale=22,lw=2,color='#18384a'))
    ax.text(3.75,3.7,'β S I / N',ha='center',fontsize=20);ax.text(8.25,3.7,'γ I',ha='center',fontsize=20)
    ax.text(6,.65,'Same transfer leaves one group and enters the next',ha='center')
    ax.set_title('Closed population: S + I + R = N',pad=12);fig.tight_layout()
    save(fig,out,'population-transfers','Transfers in a closed SIR population','Original schematic with susceptible, infectious and recovered categories. Infection transfers beta times S times I divided by N per day from S to I. Recovery transfers gamma times I per day from I to R. No births, deaths, migration, latent stage or return to susceptibility is modeled.')
    time,state=simulate();other_time,other=simulate(beta_per_day=.08)
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.9))
    for k,label,col,style in [(0,'Susceptible','#176c7b','-'),(1,'Infectious','#ad5f2f','--'),(2,'Recovered','#51795a',':')]:axs[0].plot(time,state[:,k],label=label,color=col,ls=style,lw=2.5)
    axs[0].set(xlabel='Time (days)',ylabel='People (continuous model)',title='Transfers change composition');axs[0].legend(fontsize=17,loc='center right')
    axs[1].plot(time,state[:,1],label='β = 0.30/day',color='#ad5f2f',lw=2.5);axs[1].plot(other_time,other[:,1],'--',label='β = 0.08/day',color='#176c7b',lw=2.5)
    axs[1].set(xlabel='Time (days)',ylabel='Infectious people',title='Change one synthetic rate');axs[1].legend(fontsize=17,loc='upper right')
    fig.tight_layout();save(fig,out,'population-trajectories','Closed-population trajectories and two contact-rate scenarios','Left: explicit-Euler SIR trajectory at step 0.1 day with N = 1000, initial S = 990, I = 10, R = 0, beta = 0.3 per day and gamma = 0.1 per day. Total population is conserved while group sizes change. Right: infectious counts for beta = 0.3 versus 0.08 with the same other inputs. These are synthetic scenarios, not fitted forecasts or intervention estimates.')
    _,one=simulate(days=1,step_days=1);assert np.allclose(one[1],[987.03,11.97,1.])
    assert np.max(np.abs(state.sum(axis=1)-1000))<1e-9 and state.min()>=0
    assert np.allclose(simulate(initial=(1000,0,0))[1],[1000,0,0])
    assert np.allclose(simulate(beta_per_day=0,gamma_per_day=0)[1],[990,10,0])
    t0,s0=simulate(beta_per_day=0,days=10,step_days=.1)
    assert np.allclose(s0[:,0],990) and np.allclose(s0[:,1],10*(1-.1*.1)**np.arange(len(t0)))
    assert np.all(np.diff(state[:,0])<=0) and np.all(np.diff(state[:,2])>=0)
    assert np.all(np.diff(other[:,1])<=0)
    # Compare Euler trajectories at common final time under step refinement.
    endpoints={str(h):simulate(days=40,step_days=h)[1][-1].tolist() for h in [.2,.1,.05]}
    coarse_gap=float(np.max(np.abs(np.array(endpoints['0.2'])-endpoints['0.1'])));fine_gap=float(np.max(np.abs(np.array(endpoints['0.1'])-endpoints['0.05'])))
    assert fine_gap<coarse_gap
    rejected=0
    for call in [lambda:simulate(initial=(0,0,0)),lambda:simulate(initial=(-1,2,0)),lambda:simulate(beta_per_day=-1),lambda:simulate(step_days=4),lambda:simulate(days=np.nan)]:
        try:call()
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid input accepted')
    peak=int(np.argmax(state[:,1]));report={'model':'synthetic closed homogeneous SIR; explicit Euler with nonnegative-transfer step bound','parameters':{'N':1000,'beta_per_day':.3,'gamma_per_day':.1,'step_days':.1},'first_one_day_Euler_state':[987.03,11.97,1.],'initial_infectious_net_rate_people_per_day':1.97,'sampled_peak':{'day':float(time[peak]),'infectious':float(state[peak,1])},'population_drift_max':float(np.max(np.abs(state.sum(axis=1)-1000))),'endpoint_step_refinement_gaps':{'0.2_to_0.1':coarse_gap,'0.1_to_0.05':fine_gap},'checks':{'closed_population':True,'nonnegative_states':True,'no_seed_no_outbreak':True,'zero_rates_static':True,'pure_recovery_discrete_reference':True,'susceptible_nonincreasing':True,'recovered_nondecreasing':True,'low_beta_infectious_declines':True,'invalid_inputs_rejected':rejected},'limitations':['all rates synthetic and fixed','homogeneous mixing','no exposed stage or waning immunity','no births deaths or migration','no individual stochastic events','not a forecast for an actual population']}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
