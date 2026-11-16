"""New conservative 1D transport teaching code; no historical source code copied.
Concentration is dimensionless, x in m, t in s, a in m/s, D in m^2/s.
Periodic boundaries identify x=0 and x=L; this is not a blood-flow solver.
"""
from pathlib import Path
import html,json,time,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def scalar(value,name,positive=False,nonnegative=False):
    if not np.isscalar(value) or not np.isfinite(value):raise ValueError(f'{name} must be a finite scalar.')
    if positive and value<=0 or nonnegative and value<0:raise ValueError(f'Invalid {name}.')
    return float(value)


def conservative_step(c,face_flux,dx,dt):
    """One update; face_flux[j] is the rightward flux at face j, including both ends."""
    c=np.asarray(c,dtype=float);f=np.asarray(face_flux,dtype=float)
    if c.ndim!=1 or f.shape!=(len(c)+1,) or len(c)<2 or not np.isfinite(c).all() or not np.isfinite(f).all():raise ValueError('Finite cell and face vectors with N and N+1 entries required.')
    dx=scalar(dx,'dx',positive=True);dt=scalar(dt,'dt',positive=True)
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):new=c-dt/dx*np.diff(f)
    except FloatingPointError as e:raise ValueError('Update overflows the numerical range.') from e
    if not np.isfinite(new).all():raise ValueError('Nonfinite update.')
    return new


def periodic_flux(c,a,D,dx):
    c=np.asarray(c,float)
    if c.ndim!=1 or len(c)<3 or not np.isfinite(c).all():raise ValueError('Finite cell vector required.')
    a=scalar(a,'a');D=scalar(D,'D',nonnegative=True);dx=scalar(dx,'dx',positive=True)
    right=np.roll(c,-1)
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):f=a*(c if a>=0 else right)-D*(right-c)/dx
    except FloatingPointError as e:raise ValueError('Flux overflows the numerical range.') from e
    return np.r_[f[-1],f]


def solve(c0,a=.2,D=.002,L=1.,end=.5,dt=None):
    c=np.asarray(c0,float).copy()
    if c.ndim!=1 or not 3<=len(c)<=4096 or not np.isfinite(c).all() or np.min(c)<0:raise ValueError('Use 3–4096 finite nonnegative cell averages.')
    a=scalar(a,'a');D=scalar(D,'D',nonnegative=True);L=scalar(L,'L',positive=True);end=scalar(end,'end',positive=True);dx=L/len(c)
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):rate=abs(a)/dx+2*D/dx**2
    except FloatingPointError as e:raise ValueError('Transport rates overflow.') from e
    if not np.isfinite(rate):raise ValueError('Transport rates overflow.')
    chosen=scalar(dt,'dt',positive=True) if dt is not None else (min(end,.85/rate) if rate else end)
    if chosen*rate>1+1e-13:raise ValueError('Positivity restriction violated: |a| dt/dx + 2 D dt/dx^2 > 1.')
    ratio=end/chosen
    if not np.isfinite(ratio) or ratio>200000:raise ValueError('Requested run exceeds the teaching work limit.')
    nsteps=int(np.ceil(ratio))
    h=end/nsteps;mass0=dx*np.sum(c);maxdrift=0.
    for _ in range(nsteps):
        c=conservative_step(c,periodic_flux(c,a,D,dx),dx,h)
        maxdrift=max(maxdrift,abs(dx*np.sum(c)-mass0))
    if np.min(c)<-1e-12:raise RuntimeError('A stable update produced an inadmissible negative concentration.')
    return {'c':c,'x':(np.arange(len(c))+.5)*dx,'dt':h,'steps':nsteps,'courant':abs(a)*h/dx,'diffusion_number':D*h/dx**2,'mass_initial':float(mass0),'mass_final':float(dx*np.sum(c)),'max_mass_drift':float(maxdrift)}


def save(fig,out,stem,title,description):
    description=re.sub(r'(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])', ' ', description)
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+f'<title>{html.escape(title)}</title><desc>{html.escape(description)}</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    n=100;x=(np.arange(n)+.5)/n;c0=np.exp(-((x-.25)/.07)**2);cases=[solve(c0,.2,0),solve(c0,0,.002),solve(c0,.2,.002)]
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'legend.fontsize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10.2,5.6));ax.plot(x,c0,color='#283b4b',lw=2.5,label='Initial pulse')
    for r,label,color,style in zip(cases,['Advection only','Diffusion only','Both'],['#a55216','#4d639b','#007e83'],['--',':','-.']):ax.plot(x,r['c'],lw=2.5,label=label,color=color,linestyle=style)
    ax.set(xlabel='Position x (m)',ylabel='Concentration (relative units)',title='Transport redistributes a conserved amount');ax.legend(loc='upper right');ax.grid(alpha=.15)
    save(fig,out,'transport-pulse','Conservative pulse transport','Periodic length1m,100cells,0.5s. Advection0.2m/s translates and upwind discretization also smears; diffusion0.002m²/s broadens. All three runs conserve total amount.')
    # A general finite-volume budget, with boundary fluxes intentionally unequal.
    before=np.array([1.,2.,1.]);f=np.array([.3,.5,.2,.1]);after=conservative_step(before,f,.5,.2)
    fig,axs=plt.subplots(1,2,figsize=(11.5,5.5),constrained_layout=True)
    k=np.arange(3);axs[0].bar(k-.18,before*.5,.35,label='Before');axs[0].bar(k+.18,after*.5,.35,label='After',hatch='//');axs[0].set(xticks=k,xticklabels=['Cell 1','Cell 2','Cell 3'],ylabel='Amount per unit area (m)',title='Internal transfers cancel');axs[0].set_ylim(0,1.5);axs[0].legend(loc='upper left')
    axs[1].bar(['In','Out','Change'],[.2*.3,.2*.1,.2*(.3-.1)],color=['#007e83','#a55216','#4d639b']);axs[1].set(ylabel='Integrated boundary amount (m)',title='Boundary flux sets the change');axs[1].grid(axis='y',alpha=.15)
    save(fig,out,'flux-budget','Cell and boundary conservation budget','Three0.5m cells start with concentrations1,2,1. During0.2s, rightward face fluxes are0.3,0.5,0.2,0.1m/s. New concentrations0.92,2.12,1.04 give total amount2.04m: initial2m plus0.04m net boundary input.')
    np.testing.assert_allclose(after,[.92,2.12,1.04],rtol=0,atol=2e-15)
    assert abs(.5*sum(after-before)-.2*(f[0]-f[-1]))<1e-14
    assert max(r['max_mass_drift'] for r in cases)<1e-12
    constant=solve(np.full(40,2.),-.3,.01);np.testing.assert_allclose(constant['c'],2.,rtol=0,atol=1e-14)
    still=solve(c0,0,0);np.testing.assert_array_equal(still['c'],c0)
    # Courant1 pure advection is an exact one-cell translation in either direction.
    for a in [1.,-1.]:
        shifted=solve(c0,a,0,L=1,end=.01,dt=.01);np.testing.assert_allclose(shifted['c'],np.roll(c0,int(a)),rtol=0,atol=2e-16)
    invalid=0
    for kw in [{'D':-1},{'a':float('nan')},{'dt':1.},{'L':0},{'end':-1}]:
        try:solve(c0,**kw)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid configuration accepted')
    result={'cases':[{'label':label,**{k:v for k,v in r.items() if k not in ('c','x')}} for label,r in zip(['advection','diffusion','both'],cases)],'open_boundary_budget_residual':float(.5*sum(after-before)-.2*(f[0]-f[-1])),'checks':{'constant_preserved':True,'zero_transport_identity':True,'both_signs_exact_Courant_one_shift':True,'invalid_cases_rejected':invalid},'runtime_seconds':time.perf_counter()-start}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
