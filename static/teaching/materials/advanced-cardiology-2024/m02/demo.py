"""Fixed-rate six-compartment baseline workshop using local hydraulic_core.py.
No feedback controller is run.
"""
from pathlib import Path
import json,html,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hydraulic_core import Parameters,compliance,pressure_step,edge_flows,NAMES,VD,P_INITIAL


def baseline(duration_s=15.,dt_s=.001875,rate_bpm=80.,rs=17.86):
    values=np.array([duration_s,dt_s,rate_bpm,rs],float)
    if not np.isfinite(values).all() or np.any(values<=0):raise ValueError('Use finite positive duration, step, rate and resistance.')
    if duration_s/dt_s>250000:raise ValueError('Baseline workshop limit:250000 steps.')
    p=Parameters(f0=rate_bpm,rs_rest=rs);p.validate()
    n=math.ceil(duration_s/dt_s);times=np.minimum(np.arange(n+1)*dt_s,duration_s)
    c=compliance(0);pressure=P_INITIAL.copy();valves=np.zeros(4,bool);pressures=[pressure.copy()];volumes=[VD+c*pressure];flows=[edge_flows(pressure,rs,p)];max_residual=0.;max_solves=0
    for old,new in zip(times[:-1],times[1:]):
        cn=compliance(rate_bpm*new/60.)
        pressure,valves,q,residual,solves=pressure_step(pressure,c,cn,(new-old)/60.,rs,p,valves)
        c=cn;pressures.append(pressure.copy());volumes.append(VD+c*pressure);flows.append(q)
        max_residual=max(max_residual,float(np.max(abs(residual))));max_solves=max(max_solves,solves)
    pressures=np.array(pressures);volumes=np.array(volumes);flows=np.array(flows);total=volumes.sum(axis=1)
    return {'time_s':times,'phase':rate_bpm*times/60.,'pressure_mmHg':pressures,'volume_L':volumes,'flow_L_min':flows,'total_volume_L':total,'diagnostics':{'max_total_drift_L':float(np.max(abs(total-total[0]))),'max_balance_residual_L_min':max_residual,'max_solves':max_solves,'initial_total_L':float(total[0]),'rate_bpm':rate_bpm,'rs_mmHg_min_L':rs,'dt_s':dt_s}}


def cycle_difference(result,period_s=.75):
    if not np.isfinite(period_s) or period_s<=0:
        raise ValueError('Cycle comparison period must be finite and positive.')
    t=result['time_s'];p=result['pressure_mmHg']
    if t[-1]<2*period_s:raise ValueError('Need at least two periods.')
    sample=np.linspace(t[-1]-period_s,t[-1],301)
    last=np.stack([np.interp(sample,t,p[:,j]) for j in range(6)],axis=1)
    prev=np.stack([np.interp(sample-period_s,t,p[:,j]) for j in range(6)],axis=1)
    return float(np.max(abs(last-prev)))


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(exist_ok=True,parents=True)
    result=baseline();t=result['time_s'];v=result['volume_L'];p=result['pressure_mmHg'];plt.rcParams.update({'font.size':20,'axes.titlesize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(2,1,figsize=(10.5,6.2),sharex=True,constrained_layout=True)
    for j,label in [(0,'Left ventricle'),(1,'Systemic artery'),(4,'Pulmonary artery')]:axs[0].plot(t,p[:,j],label=label,lw=1.3)
    axs[0].set(ylabel='Pressure (mmHg)',ylim=(0,150));axs[0].legend(loc='upper right',ncol=3,fontsize=20,handlelength=1.2,columnspacing=.8,handletextpad=.4)
    axs[1].plot(t,v[:,0]*1000,label='Left ventricle',color='#087e8b');axs[1].plot(t,v[:,3]*1000,label='Right ventricle',color='#b16a20',ls='--');axs[1].set(xlabel='Time (s)',ylabel='Ventricular volume\n(mL)',ylim=(25,125));axs[1].legend(ncol=2)
    for ax in axs:ax.grid(alpha=.15)
    save(fig,out,'baseline-state','Startup and repeated pulsatile states','A newly implemented closed six-compartment circulation at80 beats per minute and systemic resistance17.86. Three pressures and both ventricular volumes are shown over15 seconds. Individual compartments change despite constant total volume.')
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.8),constrained_layout=True)
    axs[0].plot(t,result['total_volume_L'],color='#18384a');tot=result['total_volume_L'][0];axs[0].set(xlabel='Time (s)',ylabel='Total blood volume\n(L)',ylim=(tot-.04,tot+.04));axs[0].ticklabel_format(axis='y',style='plain',useOffset=False)
    axs[1].plot(t,(result['total_volume_L']-tot)*1e9,color='#087e8b');axs[1].set(xlabel='Time (s)',ylabel='Total-volume drift\n(nL)')
    for ax in axs:ax.grid(alpha=.15)
    save(fig,out,'volume-audit','A conserved total can coexist with changing compartments','The total is plotted on an absolute-liter scale and its small floating-point drift on a nanoliter scale. Conservation is audited independently of whether the initial waveform has reached a repeatable cycle.')
    assert result['diagnostics']['max_total_drift_L']<1e-9
    assert result['diagnostics']['max_balance_residual_L_min']<1e-7
    assert np.min(v)>=0 and np.min(result['flow_L_min'][:,:4])>=0
    assert np.allclose(result['phase'],80*t/60.,atol=1e-13,rtol=0)
    # Reconstruct all volumes independently from stored pressures and known phase.
    independent=np.array([VD+compliance(ph)*pr for ph,pr in zip(result['phase'],p)])
    assert np.max(abs(independent-v))<1e-12
    # A wrong fixed compliance in a volume audit must be detectable.
    wrong=(VD+compliance(0)*p).sum(axis=1);wrong_drift=float(np.max(abs(wrong-wrong[0])));assert wrong_drift>.01
    short=baseline(duration_s=1.5,dt_s=.001875);fine=baseline(duration_s=1.5,dt_s=.0009375)
    refinement=float(np.max(abs(short['pressure_mmHg'][-1]-fine['pressure_mmHg'][-1])))
    original_rs=baseline(duration_s=1.5,rs=8.)
    assert original_rs['diagnostics']['max_total_drift_L']<1e-9
    checks={**result['diagnostics'],'last_cycle_pressure_difference_mmHg':cycle_difference(result),'wrong_fixed_compliance_audit_drift_L':wrong_drift,'coarse_fine_endpoint_pressure_difference_mmHg':refinement,'rs8_short_volume_drift_L':original_rs['diagnostics']['max_total_drift_L'],'volume_reconstruction_pass':True,'ideal_valves_nonnegative':True,'constant_shared_phase_pass':True}
    np.savez_compressed(out/'baseline.npz',**{k:v for k,v in result.items() if k!='diagnostics'})
    (out/'results.json').write_text(json.dumps(checks,indent=2)+'\n');return checks

if __name__=='__main__':print(json.dumps(run(),indent=2))
