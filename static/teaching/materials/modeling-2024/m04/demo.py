"""Read a pulsatile circulation and audit its closed-volume account.
Original 2026 teaching wrapper and figures; synthetic parameters, no clinical use.
The reusable implicit hydraulic solver is supplied locally in hydraulic_core.py.
"""
from pathlib import Path
import json, html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from circulation import baseline
from hydraulic_core import compliance, VD, EDGES


def ideal_valve(upstream, downstream, resistance):
    x=np.array([upstream,downstream,resistance],float)
    if not np.isfinite(x).all() or resistance<=0:
        raise ValueError('Use finite pressures and a finite positive resistance.')
    return max(upstream-downstream,0.)/resistance


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();i=s.index('>',s.index('<svg'))+1
    p.write_text(s[:i]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    r=baseline();t=r['time_s'];p=r['pressure_mmHg'];v=r['volume_L'];q=r['flow_L_min']
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    tail=t>=13.5
    fig,axes=plt.subplots(2,1,figsize=(10.5,6.5),sharex=True,constrained_layout=True)
    axes[0].plot(t[tail],p[tail,0],label='Left ventricle',color='#087e8b',lw=2)
    axes[0].plot(t[tail],p[tail,1],label='Systemic artery',color='#b16a20',lw=2,ls='--')
    axes[0].set(ylabel='Pressure (mmHg)',ylim=(0,155));axes[0].legend(loc='upper right',ncol=2)
    axes[1].plot(t[tail],q[tail,1],color='#18384a',lw=2)
    axes[1].set(xlabel='Time (s)',ylabel='Aortic valve flow\n(L/min)');axes[1].set_ylim(bottom=-1)
    for ax in axes:ax.grid(alpha=.15)
    save(fig,out,'pressure-and-valve','An ideal valve responds to a pressure difference','The final 1.5 seconds of the 15-second synthetic fixed-rate run show left ventricular and systemic arterial pressures and forward aortic-valve flow. Flow is zero when ventricular pressure does not exceed arterial pressure. The displayed startup calculation is not asserted to be exactly periodic.')
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.8),constrained_layout=True)
    axes[0].plot(t[tail],1000*v[tail,0],label='Left ventricle',color='#087e8b',lw=2)
    axes[0].plot(t[tail],1000*v[tail,3],label='Right ventricle',color='#b16a20',ls='--',lw=2)
    axes[0].set(xlabel='Time (s)',ylabel='Stored volume (mL)',ylim=(20,130));axes[0].legend(loc='upper right')
    axes[1].plot(t,v.sum(axis=1),color='#18384a',lw=2)
    axes[1].set(xlabel='Time (s)',ylabel='Six-region total (L)',ylim=(5.10,5.18));axes[1].ticklabel_format(axis='y',useOffset=False,style='plain')
    for ax in axes:ax.grid(alpha=.15)
    save(fig,out,'changing-storage','Changing compartments can share a conserved total','Left and right ventricular volumes change during the final two cycles, while the sum over all six regions remains at its initialized 5.13616 liters across the complete 15-second calculation. All values are synthetic; total conservation does not prove clinical validity or time-step accuracy.')
    # Check accounting directly from exported states and flows.
    rates=np.zeros_like(v)
    for j,(a,b) in enumerate(EDGES):rates[:,a]-=q[:,j];rates[:,b]+=q[:,j]
    balance=(v[1:]-v[:-1])/np.diff(t)[:,None]*60-rates[1:]
    balance_error=float(abs(balance).max());assert balance_error<1e-7
    reconstruction=np.array([VD+compliance(ph)*pr for ph,pr in zip(r['phase'],p)])
    assert np.max(abs(reconstruction-v))<1e-12
    valve=np.array([ideal_valve(a,b,.01) for a,b in zip(p[:,0],p[:,1])]);assert np.max(abs(valve-q[:,1]))<1e-10
    assert np.max(abs(v.sum(axis=1)-v[0].sum()))<1e-9
    assert ideal_valve(90,110,2)==0 and ideal_valve(110,90,2)==10 and ideal_valve(90,90,2)==0
    a=baseline(duration_s=1.5,dt_s=.001875);b=baseline(duration_s=1.5,dt_s=.0009375)
    refinement=float(np.max(abs(a['pressure_mmHg'][-1]-b['pressure_mmHg'][-1])))
    bad=[(1,0,0),(1,0,-1),(np.nan,0,1),(1,np.inf,1),(1,0,np.inf)]
    for args in bad:
        try:ideal_valve(*args)
        except ValueError:pass
        else:raise AssertionError('Invalid input accepted')
    results={**r['diagnostics'],'independent_balance_residual_L_min':balance_error,'coarse_fine_pressure_gap_mmHg':refinement,'forward_valve_formula_pass':True,'matched_phase_storage_pass':True,'invalid_valve_inputs_rejected':len(bad),'first_step_transfer_example_mL':10*.06/60*1000}
    np.savez_compressed(out/'circulation.npz',**{k:z for k,z in r.items() if k!='diagnostics'})
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n');return results

if __name__=='__main__':print(json.dumps(run(),indent=2))
