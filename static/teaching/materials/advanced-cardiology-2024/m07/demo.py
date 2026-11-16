"""Original steady planar channel BVP: mu*u''=-G with prescribed wall speeds.
SI units. This reduced benchmark is not a full Navier–Stokes flow solver.
"""
from pathlib import Path
import html,json,time,re
import numpy as np
from scipy.linalg import solve_banded
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator, NullFormatter, FuncFormatter


def channel(n=40,H=.002,G=100.,mu=.004,bottom=0.,top=0.):
    if isinstance(n,bool) or not isinstance(n,(int,np.integer)) or not 2<=n<=10000:raise ValueError('n is an integer interval count from2 to10000.')
    if not np.isfinite([H,G,mu,bottom,top]).all() or H<=0 or mu<=0:raise ValueError('Finite parameters and positive H and mu required.')
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            y=np.linspace(0,H,n+1);h=H/n;rhs=np.full(n-1,G*h*h/mu);rhs[0]+=bottom;rhs[-1]+=top
            band=np.zeros((3,n-1));band[0,1:]=-1;band[1]=2;band[2,:-1]=-1
            interior=solve_banded((1,1),band,rhs,check_finite=True);u=np.r_[bottom,interior,top]
            exact=G*y*(H-y)/(2*mu)+bottom+(top-bottom)*y/H
            flux=float(np.trapezoid(u,y));exact_flux=G*H**3/(12*mu)+H*(bottom+top)/2
            residual=(2*u[1:-1]-u[:-2]-u[2:])-G*h*h/mu
    except (FloatingPointError,ValueError,OverflowError,ZeroDivisionError,np.linalg.LinAlgError) as e:raise ValueError('Channel solve failed or overflowed.') from e
    if not np.isfinite(u).all() or not np.isfinite([flux,exact_flux]).all():raise ValueError('Nonfinite channel output.')
    return {'y':y,'u':u,'exact':exact,'flux_per_width':flux,'exact_flux_per_width':float(exact_flux),'max_profile_error':float(np.max(abs(u-exact))),'max_algebraic_residual':float(np.max(abs(residual)))}


def save(fig,out,stem,title,description):
    description=re.sub(r'(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])', ' ', description)
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+f'<title>{html.escape(title)}</title><desc>{html.escape(description)}</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':20,'axes.titlesize':20,'legend.fontsize':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    a=channel(n=12);b=channel(n=12,top=.02);fine=channel(n=200)
    fig,ax=plt.subplots(figsize=(10.2,5.6));ax.plot(fine['exact']*1000,fine['y']*1000,lw=2.5,label='Exact, fixed walls');ax.plot(a['u']*1000,a['y']*1000,'o',label='12 intervals');ax.plot(b['u']*1000,b['y']*1000,'s--',lw=2,label='Top: 20 mm/s');ax.set(xlabel='Axial speed (mm/s)',ylabel='Distance from lower wall (mm)',title='Boundary values determine the velocity profile');ax.legend(loc='center left');ax.grid(alpha=.15)
    save(fig,out,'channel-profiles','Planar Poiseuille and moving-wall profiles','Channel gap2mm,viscosity0.004Pa s,driving pressure gradient100Pa/m. Stationary-wall center speed12.5mm/s. A20mm/s upper-wall condition adds a linear Couette contribution. This is an exact reduced steady benchmark.')
    ns=[4,8,16,32,64];rows=[channel(n=n) for n in ns];errors=[abs(r['flux_per_width']-r['exact_flux_per_width']) for r in rows]
    fig,ax=plt.subplots(figsize=(10.2,5.6));ax.loglog(np.array(ns),np.array(errors)/a['exact_flux_per_width'],'o-',lw=2.5,label='Trapezoidal flow-rate error');ax.loglog(ns,1/np.array(ns,dtype=float)**2,'--',lw=2,label='Exact relative error 1/N²');ax.set(xlabel='Number of gap intervals N',ylabel='Relative flow-rate error',title='An exact nodal profile can have an inexact integral');ax.set_xticks(ns,[str(n) for n in ns]);ax.xaxis.set_minor_locator(NullLocator());ax.legend();ax.grid(which='both',alpha=.15)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:g}'));ax.yaxis.set_minor_formatter(NullFormatter())
    save(fig,out,'channel-flux-error','Separate the profile solve from flow integration','The centered second difference is exact for a quadratic at grid nodes. Trapezoidal integration underestimates its flow by1/N² for N equal intervals. The convergence plot measures quadrature error, not a claimed profile discretization order.')
    assert a['max_profile_error']<2e-15
    assert abs(a['exact_flux_per_width']-1/60000)<1e-18
    np.testing.assert_allclose(np.array(errors)/a['exact_flux_per_width'],1/np.array(ns,dtype=float)**2,rtol=1e-9,atol=1e-12)
    zero=channel(G=0);assert np.max(abs(zero['u']))==0
    reverse=channel(G=-100);np.testing.assert_allclose(reverse['u'],-channel()['u'],rtol=1e-13,atol=1e-15)
    couette=channel(G=0,bottom=-.01,top=.02);np.testing.assert_allclose(couette['u'],couette['exact'],atol=1e-14,rtol=0)
    double=channel(G=200);np.testing.assert_allclose(double['u'],2*channel()['u'],rtol=0,atol=1e-15)
    invalid=0
    for kw in [{'mu':0},{'H':-1},{'G':float('nan')},{'n':3.5},{'H':1e200}]:
        try:channel(**kw)
        except (ValueError,OverflowError):invalid+=1
        else:raise AssertionError('Invalid case accepted')
    result={'stationary':{k:v for k,v in a.items() if k not in ('y','u','exact')},'center_speed_m_s':.0125,'gap_m':.002,'viscosity_Pa_s':.004,'gradient_Pa_m':100.,'width_m':.01,'total_flow_mL_s':a['exact_flux_per_width']*.01*1e6,'reynolds_based_on_gap':1060*(a['exact_flux_per_width']/.002)*.002/.004,'n_values':ns,'flux_absolute_errors_m2_s':errors,'observed_flux_orders':np.log2(np.array(errors[:-1])/errors[1:]).tolist(),'checks':{'zero_gradient_rest':True,'reverse_gradient_reverses_flow':True,'Couette_linear_solution':True,'double_gradient_doubles_velocity':True,'invalid_cases_rejected':invalid},'runtime_seconds':time.perf_counter()-start}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
