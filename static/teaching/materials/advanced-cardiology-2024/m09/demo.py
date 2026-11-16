"""Original single neuronal HH membrane lesson; not a cardiac-cell model.
Rate/voltage convention: Ahmad, current Action Potential Propagation report,
section2 and Table1. mV,ms,uF/cm²,mS/cm²,uA/cm². Outward ionic current positive.
Exact frozen-rate gates then exact frozen-conductance voltage: first-order
coupled splitting, not the report's staggered Crank–Nicolson method.
"""
from pathlib import Path
import html,json,time
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from membrane import C,GMAX,EREV,vtrap,rates,gate_step,conductances,ionic_current,rest,rhs,timeline,simulate


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+f'<title>{html.escape(title)}</title><desc>{html.escape(description)}</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'legend.fontsize':22,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    cases=[simulate(amplitude=a) for a in (2,5,10)];active=cases[-1]
    fig,axs=plt.subplots(1,2,figsize=(11.5,5.8),constrained_layout=True)
    for a,r,style in zip((2,5,10),cases,['-','--',':']):axs[0].plot(r['time'],r['state'][:,0],lw=2.8,ls=style,label=f'{a} µA/cm²')
    axs[0].axvspan(1,2,color='#dde4e9',zorder=-2);axs[0].set(xlabel='Time (ms)',ylabel='Neuronal voltage (mV)',title='Equal-duration neuronal pulses');axs[0].legend(loc='upper right');axs[0].grid(alpha=.15)
    for j,(name,style) in enumerate(zip(['m','h','n'],['-','--',':'])):axs[1].plot(active['time'],active['state'][:,j+1],lw=2.8,ls=style,label=name)
    axs[1].set(xlabel='Time (ms)',ylabel='Gate fraction',title='Bounded gate fractions',ylim=(0,1));axs[1].legend(loc='upper right',fontsize=22);axs[1].grid(alpha=.15)
    save(fig,out,'neuronal-cell','A labeled neuronal membrane and its gates','Original single-cell calculations using the current public report’s HH voltage convention. One-millisecond pulses start at1ms; shaded region marks the pulse. These are neuronal model outputs, not cardiac action potentials. The split exponential updates keep gates within0and1.')
    initial=rest();initial[0]=-55.;reference=solve_ivp(rhs,[0,1],initial,method='DOP853',rtol=2e-12,atol=2e-13)
    if not reference.success:raise RuntimeError(reference.message)
    hs=[.01,.005,.0025,.00125];errors=[]
    for h in hs:errors.append(float(abs(simulate(dt=h,end=1,amplitude=0,initial=initial)['state'][-1,0]-reference.y[0,-1])))
    orders=np.log2(np.array(errors[:-1])/errors[1:]);assert np.all((orders>.95)&(orders<1.05))
    fig,axs=plt.subplots(1,2,figsize=(11.5,5.8),constrained_layout=True)
    axs[0].loglog(hs,errors,'o-',lw=2.5);axs[0].set_xticks([.00125,.005,.01],['1.25e-3','5e-3','1e-2']);axs[0].set_yticks([.3,1.,3.],['0.3','1','3']);axs[0].minorticks_off();axs[0].set(xlabel='Time step (ms)',ylabel='Voltage error at 1 ms (mV)',title='First-order coupled error');axs[0].grid(alpha=.15)
    t=np.linspace(0,5,151);alpha=.2;beta=.3;s0=.9;exact=alpha/(alpha+beta)+(s0-alpha/(alpha+beta))*np.exp(-(alpha+beta)*t)
    axs[1].plot(t,exact,lw=2.5,label='Exact gate');points=np.arange(6);values=[s0]
    for _ in range(5):values.append(float(gate_step(values[-1],alpha,beta,1.)))
    axs[1].plot(points,values,'o',ms=7,label='1 ms steps');axs[1].set(xlabel='Time (ms)',ylabel='Gate fraction',title='Frozen-rate gate check');axs[1].legend(fontsize=22);axs[1].grid(alpha=.15)
    save(fig,out,'gate-and-time-checks','Independent gate and coupled-membrane checks','Left: the coupled first-order split method approaches an independent DOP853 reference for an unforced non-equilibrium cell at1ms. Right: fixed opening and closing rates admit an exact exponential gate solution, matched by the substep for any step size. Substep exactness does not remove coupled-system error.')
    np.testing.assert_allclose(values,alpha/(alpha+beta)+(s0-alpha/(alpha+beta))*np.exp(-.5*points),atol=2e-15,rtol=0)
    np.testing.assert_allclose([rates(-45)[0][0],rates(-60)[0][2]],[1.,.1],atol=1e-15,rtol=0)
    for center,index,target in [(-45,0,1.),(-60,2,.1)]:
        for eps in [-1e-8,1e-8]:assert abs(rates(center+eps)[0][index]-target)<1e-8
    equilibrium=rest();quiet=simulate(amplitude=0);assert np.max(abs(quiet['state']-equilibrium))<1e-10
    event=simulate(dt=.037,end=4,amplitude=7,on=.113,duration=.829);assert abs(event['charge_uA_ms_cm2']-7*.829)<1e-12
    # Inward current raises voltage slope under the stated sign convention.
    assert abs(rhs(0,equilibrium,3)[0]-3)<1e-10
    invalid=0
    for kw in [{'dt':0},{'amplitude':-1},{'initial':[-70,1.1,.5,.3]}]:
        try:simulate(**kw)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid membrane input accepted')
    result={'model':'neuronal HH, current Ahmad report convention; not cardiac','rest_state':equilibrium.tolist(),'rest_current_residual_uA_cm2':ionic_current(equilibrium[0],equilibrium[1:]),'stimulus_amplitudes_uA_cm2':[2,5,10],'peaks_mV':[r['peak_mV'] for r in cases],'gate_min':active['gate_min'],'gate_max':active['gate_max'],'reference_voltage_at_1ms':float(reference.y[0,-1]),'dt_values_ms':hs,'voltage_errors_mV':errors,'observed_orders':orders.tolist(),'checks':{'rest_preserved':True,'removable_singularities':True,'exact_frozen_gate':True,'non_grid_pulse_charge':event['charge_uA_ms_cm2'],'invalid_cases_rejected':invalid},'runtime_seconds':time.perf_counter()-start}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
