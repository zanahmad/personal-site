"""Original periodic Fourier-mode verification. No external data or sibling files.
Spatial error is isolated with exact evolution of the semi-discrete mode;
temporal error compares forward Euler with that same semi-discrete solution.
"""
from pathlib import Path
import html,json,time,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator, NullFormatter, FuncFormatter


def parameters(n,a,D,L,end):
    if isinstance(n,bool) or not isinstance(n,(int,np.integer)) or not 8<=n<=8192:raise ValueError('n must be an integer from8 to8192.')
    if not np.isfinite([a,D,L,end]).all() or D<0 or L<=0 or end<=0:raise ValueError('Finite coefficients, D>=0 and positive length/time required.')
    dx=L/n
    if not np.isfinite(dx) or dx<=0:raise ValueError('Cell width is outside the numerical range.')
    return dx


def eigenvalue(n,a,D,L=1.):
    dx=parameters(n,a,D,L,1.);theta=2*np.pi/n
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            lam=-abs(a)*(1-np.cos(theta))/dx-4*D*np.sin(theta/2)**2/np.float64(dx)**2-1j*a*np.sin(theta)/dx
    except (FloatingPointError,OverflowError,ZeroDivisionError) as e:raise ValueError('Mode rates exceed the numerical range.') from e
    if not np.isfinite(lam):raise ValueError('Nonfinite mode rate.')
    return lam


def exact_mode(n=64,a=.2,D=.002,L=1.,end=.5,semidiscrete=False):
    dx=parameters(n,a,D,L,end)
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            x=(np.arange(n)+.5)*dx;k=2*np.pi/L
            initial_amplitude=.3*np.sinc(1/n) # exact cell average, not midpoint sample
            lam=eigenvalue(n,a,D,L) if semidiscrete else -D*k*k-1j*a*k
            c=1+initial_amplitude*np.imag(np.exp(1j*k*x+lam*end))
    except (FloatingPointError,OverflowError,ZeroDivisionError) as e:raise ValueError('Exact-mode inputs exceed numerical range.') from e
    if not np.isfinite(c).all():raise ValueError('Nonfinite exact reference.')
    return x,c



def euler_mode(n=64,a=.2,D=.002,L=1.,end=.5,dt=.01):
    dx=parameters(n,a,D,L,end)
    if not np.isfinite(dt) or dt<=0:raise ValueError('dt must be positive and finite.')
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):rate=abs(a)/np.float64(dx)+2*D/np.float64(dx)**2
    except (FloatingPointError,OverflowError,ZeroDivisionError) as e:raise ValueError('Transport rates exceed numerical range.') from e
    if not np.isfinite(rate) or dt*rate>1+1e-13:raise ValueError('Positivity restriction is exceeded.')
    ratio=end/dt
    if not np.isfinite(ratio) or ratio>200000:raise ValueError('Teaching work limit exceeded.')
    steps=int(np.ceil(ratio))
    h=end/steps;x=(np.arange(n)+.5)*dx
    # Exact t=0 cell averages, evaluated directly.
    c=1+.3*np.sinc(1/n)*np.sin(2*np.pi*x/L)
    mass0=dx*np.sum(c)
    for _ in range(steps):
        r=np.roll(c,-1);left=np.roll(c,1)
        advection=-a*(c-left)/dx if a>=0 else -a*(r-c)/dx
        c=c+h*(advection+D*(r-2*c+left)/dx**2)
    if not np.isfinite(c).all():raise RuntimeError('Nonfinite explicit solution.')
    return x,c,h,steps,float(abs(dx*np.sum(c)-mass0))


def rms(a,b):return float(np.sqrt(np.mean((np.asarray(a)-b)**2)))

def save(fig,out,stem,title,description):
    description=re.sub(r'(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])', ' ', description)
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+f'<title>{html.escape(title)}</title><desc>{html.escape(description)}</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'legend.fontsize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    ns=[20,40,80,160];spatial={}
    for label,a,D in [('Upwind advection',.2,0.),('Centered diffusion',0.,.01)]:
        errors=[]
        for n in ns:
            _,truth=exact_mode(n,a,D,end=.5);_,sem=exact_mode(n,a,D,end=.5,semidiscrete=True);errors.append(rms(sem,truth))
        spatial[label]={'errors':errors,'orders':np.log2(np.array(errors[:-1])/errors[1:]).tolist()}
    steps=[.04,.02,.01,.005];temporal=[]
    _,reference=exact_mode(64,.1,.001,end=.4,semidiscrete=True)
    for h in steps:
        _,c,_,_,_=euler_mode(64,.1,.001,end=.4,dt=h);temporal.append(rms(c,reference))
    fig,axs=plt.subplots(1,2,figsize=(11.5,5.8),constrained_layout=True)
    for (label,row),style in zip(spatial.items(),['o-','s--']):axs[0].loglog(1/np.array(ns),row['errors'],style,lw=2.3,label=label)
    axs[0].set(xlabel='Cell width (m)',ylabel='RMS concentration error',title='Space: time error removed');axs[0].set_xticks([.01,.02,.04],['0.01','0.02','0.04']);axs[0].xaxis.set_minor_locator(NullLocator());axs[0].legend(loc='center',bbox_to_anchor=(.5,.62));axs[0].grid(which='both',alpha=.15)
    axs[1].loglog(steps,temporal,'s-',lw=2.3,color='#007e83',label='Euler vs. fixed-grid reference');axs[1].set(xlabel='Time step (s)',ylabel='RMS concentration error',title='Time: Euler at fixed grid');axs[1].set_xticks([.005,.01,.02,.04],['0.005','0.01','0.02','0.04']);axs[1].xaxis.set_minor_locator(NullLocator());axs[1].grid(which='both',alpha=.15)
    for a in axs:
        a.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:.0e}'.replace('e-0','e-').replace('e+0','e+')))
        a.yaxis.set_minor_formatter(NullFormatter())
    axs[1].set_yticks([1e-4,2e-4,4e-4,6e-4])
    save(fig,out,'separate-errors','Independent spatial and temporal refinement','A periodic cell-average sine mode provides an exact continuum reference. Exact semi-discrete evolution isolates first-order upwind advection and second-order centered diffusion. Forward Euler at fixed64cells approaches its semi-discrete reference with first-order time error.')
    # A checkerboard is the highest-frequency mode; the inadmissible example is an analytic diagnostic, never an accepted solve.
    mus=[.4,.6];k=np.arange(13);fig,ax=plt.subplots(figsize=(10.2,5.6))
    for mu,style in zip(mus,['o-','s--']):ax.plot(k,np.abs(1-4*mu)**k,style,lw=2.3,label=f'D dt/dx² = {mu:g}')
    ax.set(yscale='log',xlabel='Number of explicit updates',ylabel='Checkerboard amplitude / initial',title='Unstable diffusion steps amplify noise');ax.legend();ax.grid(alpha=.15)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:g}'));ax.yaxis.set_minor_formatter(NullFormatter())
    save(fig,out,'stability-mode','A high-frequency stability diagnostic','For pure diffusion the alternating-cell mode has amplification1−4mu per Euler step. At mu0.4 its magnitude decays; at mu0.6 it grows. The production solver rejects the latter time step.')
    assert .9<spatial['Upwind advection']['orders'][-1]<1.1
    assert 1.95<spatial['Centered diffusion']['orders'][-1]<2.05
    orders=np.log2(np.array(temporal[:-1])/temporal[1:]);assert np.all((orders>.95)&(orders<1.05))
    checks=[]
    for a in [-.2,0,.2]:
        x,c,h,m,drift=euler_mode(64,a,.002,dt=.005)
        amplification=(1+h*eigenvalue(64,a,.002))**m
        prediction=1+.3*np.sinc(1/64)*np.imag(np.exp(2j*np.pi*x)*amplification)
        error=float(np.max(abs(c-prediction)));assert error<2e-14 and drift<2e-14;checks.append({'a':a,'amplification_check_error':error,'mass_drift':drift})
    rejected=False
    try:euler_mode(64,0,.01,dt=.6*(1/64)**2/.01)
    except ValueError:rejected=True
    assert rejected
    for kw in [{'a':1e308},{'L':1e-308},{'D':float('nan')}]:
        try:exact_mode(**kw)
        except ValueError:pass
        else:raise AssertionError('Invalid reference inputs accepted')
    result={'n_values':ns,'spatial':spatial,'dt_values':steps,'temporal_errors':temporal,'temporal_orders':orders.tolist(),'independent_amplification_checks':checks,'unstable_step_rejected':True,'invalid_exact_reference_cases_rejected':3,'runtime_seconds':time.perf_counter()-start}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
