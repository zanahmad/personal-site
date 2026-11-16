"""Original teaching example: mass balance and explicit Euler in a mixed chamber.
Synthetic laboratory values; no patient data or dosing interpretation.
Run: python demo.py  (requires NumPy and Matplotlib)
"""
from pathlib import Path
import json, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def simulate(m0=0.0, rate_in=2.0, k=0.25, dt=1.0, end=20.0):
    """M in mg, rate_in in mg/min, k in 1/min, dt/end in min.
    Uses the OLD mass in each outflow; this is explicit Euler.
    Finite nonnegative inputs required, with positive dt/end.
    Large steps are deliberately permitted to diagnose numerical failure.
    """
    values=np.array([m0,rate_in,k,dt,end],float)
    if not np.isfinite(values).all() or min(m0,rate_in,k)<0 or min(dt,end)<=0:
        raise ValueError('Use finite nonnegative mass/input/k and positive dt/end.')
    n=int(np.ceil(end/dt))
    if n>1_000_000:raise ValueError('More than one million steps; increase dt.')
    t=np.minimum(np.arange(n+1,dtype=float)*dt,end)
    m=np.empty(n+1);m[0]=m0
    removed=np.zeros(n+1)
    for i,h in enumerate(np.diff(t)):
        loss=k*m[i]*h
        m[i+1]=m[i]+rate_in*h-loss
        removed[i+1]=removed[i]+loss
    return t,m,removed


def exact(t,m0=0.0,rate_in=2.0,k=0.25):
    t=np.asarray(t,dtype=float)
    if not np.isfinite([m0,rate_in,k]).all() or min(m0,rate_in,k)<0 or not np.isfinite(t).all() or (t<0).any():
        raise ValueError('Exact solution requires finite nonnegative time/parameters.')
    if k==0:return m0+rate_in*t
    return m0*np.exp(-k*t)+rate_in*(-np.expm1(-k*t)/k)


def checks():
    t,m,removed=simulate()
    balance=float(np.max(np.abs(m+removed-(2*t))))
    assert balance<1e-11
    _,steady,_=simulate(m0=8.)
    assert np.max(np.abs(steady-8))<1e-12
    t,closed,_=simulate(m0=3.,rate_in=0.,k=0.)
    assert np.array_equal(closed,np.full_like(closed,3.))
    t,linear,_=simulate(m0=3.,rate_in=2.,k=0.)
    assert np.allclose(linear,3+2*t)
    errors=[]
    for h in [.5,.25,.125]:
        t,m,_=simulate(dt=h,end=4.)
        errors.append(float(abs(m[-1]-exact(t[-1]))))
        assert np.min(m)>=0
    ratios=[errors[i]/errors[i+1] for i in range(2)]
    assert all(1.8<r<2.3 for r in ratios)
    _,unstable,_=simulate(dt=9.,end=27.)
    assert np.min(unstable)<0
    bad=[{'dt':0},{'k':-1},{'m0':float('nan')},{'end':float('inf')},{'dt':1e-9}]
    for kwargs in bad:
        try:simulate(**kwargs)
        except ValueError:pass
        else:raise AssertionError('Invalid input accepted: '+str(kwargs))
    return {'balance_max_mg':balance,'end4_errors_mg':errors,'refinement_ratios':ratios,'unstable_values_mg':unstable.tolist(),'invalid_cases_rejected':len(bad)}


def save(fig,stem,title,description):
    fig.tight_layout()
    fig.savefig(stem+'.svg',metadata={'Title':title,'Description':description})
    fig.savefig(stem+'.pdf',metadata={'Title':title,'Author':'Zan Ahmad'})
    # Matplotlib stores the description as metadata; put explicit accessible SVG title/desc too.
    p=Path(stem+'.svg');s=p.read_text();pos=s.index('>',s.index('<svg'))+1
    import html
    s=s[:pos]+'\n<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'+s[pos:]
    p.write_text(s);plt.close(fig)


def main():
    plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    t,m,removed=simulate();fine=np.linspace(0,20,301)
    fig,ax=plt.subplots(figsize=(7.2,4.1))
    ax.plot(fine,exact(fine),color='#18384a',lw=2.5,label='Exact continuous model')
    ax.plot(t,m,'o--',color='#087e8b',ms=4,label='Explicit Euler, step 1 min')
    ax.axhline(8,color='#754c24',ls=':',lw=2,label='Equilibrium 8 mg')
    ax.set(xlabel='Time (min)',ylabel='Stored tracer mass (mg)',ylim=(-.2,9.1))
    ax.legend(fontsize=10,loc='lower right');ax.grid(alpha=.15)
    save(fig,'filling','Approach to equilibrium','Synthetic chamber with input2 mg/min and removal rate0.25 per min. Euler with a1 minute step fills faster than the exact solution; both approach8 mg.')
    fig,axs=plt.subplots(1,2,figsize=(9,3.7))
    for ax,h,end in zip(axs,[5.,9.],[30.,27.]):
        tt,mm,_=simulate(dt=h,end=end)
        ax.plot(tt,mm,'o-',color='#087e8b',label='Explicit Euler')
        ax.plot(np.linspace(0,end,300),exact(np.linspace(0,end,300)),color='#18384a',ls='--',label='Exact')
        ax.axhline(8,color='#754c24',ls=':');ax.axhline(0,color='#666',lw=.7)
        ax.set(xlabel='Time (min)',ylabel='Mass (mg)',title=f'Step {h:g} min; k × step = {h*.25:g}')
        ax.grid(alpha=.15)
    axs[0].legend(fontsize=9)
    save(fig,'step-size','Numerical oscillations and failure','At5 minute steps Euler oscillates toward8 mg despite a monotone exact solution. At9 minute steps the error grows and the mass becomes negative. These are numerical artifacts.')
    with open('trajectory.csv','w',newline='') as f:
        w=csv.writer(f);w.writerow(['time_min','euler_mass_mg','exact_mass_mg','removed_mass_mg'])
        w.writerows(zip(t,m,exact(t),removed))
    result=checks();Path('checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
