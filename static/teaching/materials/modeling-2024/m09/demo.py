"""Original introductory neuronal membrane experiment; no patient data."""
from pathlib import Path
import json,html,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from membrane import rates,gate_step,conductances,ionic_current,simulate,rest


def clamp(V=-20.,duration=10.,step=.05):
    if not np.isfinite([V,duration,step]).all() or not -150<=V<=100 or duration<=0 or step<=0 or duration/step>200000:
        raise ValueError('Use finite voltage -150 to100mV and positive bounded time controls.')
    t=np.linspace(0,duration,int(np.ceil(duration/step))+1);a,b=rates(V);s0=rest()[1:]
    s=a[:,None]/(a+b)[:,None]+(s0[:,None]-a[:,None]/(a+b)[:,None])*np.exp(-(a+b)[:,None]*t)
    return t,s


def save(fig,out,name,title,desc):
    fig.tight_layout()
    for ext in ('svg','pdf'):fig.savefig(out/f'{name}.{ext}',bbox_inches='tight')
    p=out/f'{name}.svg';s=p.read_text();k=s.index('>',s.index('<svg'))+1
    p.write_text(s[:k]+f'<title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc>'+s[k:]);plt.close(fig)


def run(output_dir=None):
    start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'legend.fontsize':22,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    weak=simulate(amplitude=2);strong=simulate(amplitude=10);t=strong['time'];states=strong['state']
    fig,axs=plt.subplots(1,2,figsize=(11.8,5.3))
    axs[0].plot(weak['time'],weak['state'][:,0],ls='--',lw=2.5,label='2 µA/cm²');axs[0].plot(t,states[:,0],lw=2.5,label='10 µA/cm²')
    axs[0].axvspan(1,2,color='gray',alpha=.14);axs[0].set(xlabel='Time (ms)',ylabel='Voltage (mV)',title='Same pulse duration');axs[0].legend(loc='upper right')
    for j,(name,style) in enumerate(zip(['m','h','n'],['-','--',':']),1):axs[1].plot(t,states[:,j],ls=style,lw=2.5,label=name)
    axs[1].set(xlabel='Time (ms)',ylabel='Gate fraction',title='Gates during the spike',ylim=(-.03,1.2));axs[1].legend(loc='upper right')
    save(fig,out,'pulse-and-gates','Pulse response and neuronal gate fractions','Original single-cell calculation. A 1 ms inward current-density pulse starts at 1 ms. The 2 µA/cm² case is subthreshold in this experiment; 10 µA/cm² produces a spike. Right: activation m, availability h and potassium gate n use solid, dashed, dotted curves. Gates remain in [0, 1].')
    tc,s=clamp();g=conductances(s)
    fig,axs=plt.subplots(1,2,figsize=(11.8,5.3))
    for j,(name,style) in enumerate(zip(['m','h','n'],['-','--',':'])):axs[0].plot(tc,s[j],ls=style,lw=2.5,label=name)
    axs[0].set(xlabel='Time after clamp (ms)',ylabel='Gate fraction',title='Hold voltage at −20 mV',ylim=(-.03,1.03));axs[0].legend()
    for j,(name,style) in enumerate(zip(['Na','K','Leak'],['-','--',':'])):axs[1].plot(tc,g[j],ls=style,lw=2.5,label=name)
    axs[1].set(xlabel='Time after clamp (ms)',ylabel='Conductance (mS/cm²)',title='Gates set conductances');axs[1].legend()
    save(fig,out,'voltage-clamp','Gate and conductance responses under a voltage clamp','Voltage is externally held at −20 mV; the voltage ODE is not evolved. Gates start at the original model resting state and follow the exact constant-rate solution. Sodium conductance rises then falls while potassium opens more slowly. This is a synthetic neuronal model, not a cardiac-cell calibration.')
    # Constant-rate gates have an independent scalar solution.
    s1=float(gate_step(.9,.2,.8,3));expected=.2+.7*np.exp(-3);assert abs(s1-expected)<1e-15
    eq=rest();resting=simulate(amplitude=0);assert np.max(abs(resting['state'][:,0]-eq[0]))<1e-10
    assert strong['gate_min']>=0 and strong['gate_max']<=1 and strong['peak_mV']>0 and weak['peak_mV']<0
    assert abs(strong['charge_uA_ms_cm2']-10)<1e-12
    aa,_=rates(np.array([-45.,-60.]));assert aa[0,0]==1 and aa[2,1]==.1
    fine=simulate(dt=.0025,amplitude=10);finer=simulate(dt=.00125,amplitude=10)
    gaps=[float(np.max(abs(strong['state'][:,0]-np.interp(t,fine['time'],fine['state'][:,0])))),float(np.max(abs(fine['state'][:,0]-np.interp(fine['time'],finer['time'],finer['state'][:,0]))))]
    assert gaps[1]<gaps[0]
    invalid=0
    for call in [lambda:clamp(V=np.nan),lambda:clamp(step=0),lambda:gate_step(1.1,.2,.8,1),lambda:simulate(amplitude=-1)]:
        try:call()
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid request accepted')
    result={'rest_mV':float(eq[0]),'rest_current_uA_cm2':ionic_current(eq[0],eq[1:]),'weak_peak_mV':weak['peak_mV'],'strong_peak_mV':strong['peak_mV'],'gate_range':[strong['gate_min'],strong['gate_max']],'prescribed_charge_density_uA_ms_cm2':strong['charge_uA_ms_cm2'],'gate_hand_example':s1,'voltage_refinement_max_gaps_mV':gaps,'gap_ratio':gaps[0]/gaps[1],'invalid_cases_rejected':invalid,'runtime_seconds':time.perf_counter()-start}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
