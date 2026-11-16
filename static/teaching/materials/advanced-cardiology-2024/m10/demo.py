"""Original 1D reduced cardiac wave teaching implementation.
Reaction: Mitchell–Schaeffer2003 equations1–5; dimensionless v and h, time ms.
Diffusion: newly added homogeneous scalar D in cm²/ms on a sealed strand.
Exact frozen-regime gate, semi-implicit reaction, backward-Euler diffusion:
a first-order splitting, not an ionic cardiac calibration or a bidomain solver.
"""
from pathlib import Path
import html,json,time
import numpy as np
from scipy.linalg import solve_banded
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

TAU_IN=.3;TAU_OUT=6.;TAU_OPEN=120.;TAU_CLOSE=150.;V_GATE=.13


def gate_step(v,h,dt):
    v,h=np.broadcast_arrays(np.asarray(v,float),np.asarray(h,float))
    if not np.isfinite(v).all() or not np.isfinite(h).all() or np.any((h<0)|(h>1)) or not np.isfinite(dt) or dt<=0:raise ValueError('Finite states, gate in[0,1], and positive finite dt required.')
    # Equality uses the closing branch, an explicit convention for the piecewise model.
    opening=v<V_GATE;target=opening.astype(float);tau=np.where(opening,TAU_OPEN,TAU_CLOSE)
    weight=-np.expm1(-dt/tau);return (1-weight)*h+weight*target



def reaction_step(v,h,dt,stim=0.):
    v,h,stim=np.broadcast_arrays(np.asarray(v,float),np.asarray(h,float),np.asarray(stim,float))
    if not all(np.isfinite(a).all() for a in (v,h,stim)) or np.any((v<0)|(v>1)) or np.any((h<0)|(h>1)) or np.any((stim<0)|(stim>1/TAU_OUT)):raise ValueError('Reaction states in[0,1] and stimulus in[0,1/tau_out] required.')
    hn=gate_step(v,h,dt);strength=hn*v*v/TAU_IN
    vn=(v+dt*(strength+stim))/(1+dt*(strength+1/TAU_OUT))
    if not np.isfinite(vn).all():raise ValueError('Nonfinite reaction step.')
    return vn,hn


def diffusion_matrix(n,dx,D,dt):
    if not isinstance(n,(int,np.integer)) or isinstance(n,bool) or not 3<=n<=2000 or not np.isfinite([dx,D,dt]).all() or dx<=0 or D<0 or dt<=0:raise ValueError('Valid interval count and finite positive spacing/step, nonnegative D required.')
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):r=np.float64(D)*dt/np.float64(dx)**2
    except FloatingPointError as e:raise ValueError('Diffusion coefficient exceeds numerical range.') from e
    if not np.isfinite(r):raise ValueError('Nonfinite diffusion number.')
    ab=np.zeros((3,n));ab[0,1:]=-r;ab[1]=1+2*r;ab[1,[0,-1]]=1+r;ab[2,:-1]=-r
    return ab


def diffuse(v,dx,D,dt):
    v=np.asarray(v,float)
    if v.ndim!=1 or not np.isfinite(v).all():raise ValueError('Finite 1D voltage vector required.')
    new=solve_banded((1,1),diffusion_matrix(len(v),dx,D,dt),v,check_finite=True)
    if not np.isfinite(new).all():raise RuntimeError('Nonfinite diffusion solve.')
    return new


def timeline(end,dt,events):
    if not np.isfinite([end,dt]).all() or end<=0 or dt<=0 or end/dt>200000:raise ValueError('Positive finite end/step within the teaching work limit required.')
    cuts=sorted({0.,float(end),*[float(t) for t in events if 0<t<end]});times=[0.]
    for a,b in zip(cuts[:-1],cuts[1:]):times.extend(np.linspace(a,b,int(np.ceil((b-a)/dt))+1)[1:])
    return np.array(times)


def crossing(t,signal,threshold=.5):
    t=np.asarray(t);signal=np.asarray(signal)
    idx=np.flatnonzero((signal[:-1]<threshold)&(signal[1:]>=threshold))
    if not len(idx):return None
    j=idx[0];return float(t[j]+(threshold-signal[j])/(signal[j+1]-signal[j])*(t[j+1]-t[j]))


def simulate(n=200,dt=.02,D=.001,L=2.,end=80.,amplitude=.1,on=1.,duration=2.,stim_width=.1):
    if not isinstance(n,(int,np.integer)) or isinstance(n,bool) or not 20<=n<=1000:raise ValueError('n must be20–1000 cells.')
    if not np.isfinite([D,L,amplitude,on,duration,stim_width]).all() or D<0 or not .1<=L<=10 or not 0<=amplitude<=1/TAU_OUT or on<0 or duration<=0 or not 0<stim_width<L:raise ValueError('Use finite coefficients and documented geometry/stimulus bounds.')
    dx=L/n;x=(np.arange(n)+.5)*dx;edges=np.arange(n+1)*dx
    fraction=np.maximum(0.,np.minimum(edges[1:],stim_width)-edges[:-1])/dx
    times=timeline(end,dt,[on,on+duration,10,20,30,40]);u=np.zeros(n);gate=np.ones(n);sensors=np.array([.3,.6])*L
    traces=[np.interp(sensors,x,u)];snapshots={};charge=0.;diff_drift=0.;umin=0.;umax=0.;gmin=1.;gmax=1.
    cache={}
    for a,b in zip(times[:-1],times[1:]):
        h=b-a;stim=amplitude*fraction if on<=a<on+duration else np.zeros(n)
        after_reaction,gate=reaction_step(u,gate,h,stim)
        key=round(h,14)
        if key not in cache:cache[key]=diffusion_matrix(n,dx,D,h)
        u=solve_banded((1,1),cache[key],after_reaction,check_finite=True)
        diff_drift=max(diff_drift,abs(dx*np.sum(u-after_reaction)))
        if not np.isfinite(u).all() or np.min(u)<-1e-12 or np.max(u)>1+1e-12 or np.min(gate)<0 or np.max(gate)>1:raise RuntimeError('Inadmissible wave state; no clipping applied.')
        traces.append(np.interp(sensors,x,u));charge+=h*dx*np.sum(stim);umin=min(umin,float(u.min()));umax=max(umax,float(u.max()));gmin=min(gmin,float(gate.min()));gmax=max(gmax,float(gate.max()))
        if b in (10.,20.,30.,40.):snapshots[str(int(b))]=u.copy()
    traces=np.array(traces);arrival=[crossing(times,traces[:,j]) for j in range(2)]
    # Simultaneous or reversed arrivals do not define forward conduction speed.
    speed=None if any(a is None for a in arrival) or arrival[1]<=arrival[0] else float((sensors[1]-sensors[0])/(arrival[1]-arrival[0])*10)
    return {'x':x,'time':times,'sensor_positions_cm':sensors,'sensor_traces':traces,'snapshots':snapshots,'arrival_ms':arrival,'speed_m_s':speed,'gate_min':gmin,'gate_max':gmax,'voltage_min':umin,'voltage_max':umax,'injected_integral_cm':charge,'max_diffusion_sum_drift_cm':diff_drift,'final_voltage':u,'final_gate':gate}


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+f'<title>{html.escape(title)}</title><desc>{html.escape(description)}</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'legend.fontsize':22,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    baseline=simulate();print('baseline',baseline['arrival_ms'],baseline['speed_m_s'],flush=True)
    if baseline['speed_m_s'] is None:raise RuntimeError('Specified wave did not reach both sensors.')
    ns=[100,200,400];space=[simulate(n=n,dt=.01)['speed_m_s'] for n in ns];hs=[.08,.04,.02,.01];temporal=[simulate(n=400,dt=h)['speed_m_s'] for h in hs]
    print('space',space,'time',temporal,flush=True)
    fig,axs=plt.subplots(1,2,figsize=(11.5,7.2),constrained_layout=True)
    for (label,u),style in zip(baseline['snapshots'].items(),['-','--','-.',':']):axs[0].plot(baseline['x']*10,u,lw=2.8,ls=style,label=f'{label} ms')
    axs[0].set(xlabel='Position along strand (mm)',ylabel='Scaled cardiac voltage v',title='Reduced cardiac front');axs[0].legend(loc='upper center',bbox_to_anchor=(.5,-.23),ncol=2);axs[0].grid(alpha=.15)
    for j,(pos,style) in enumerate(zip(baseline['sensor_positions_cm'],['-','--'])):axs[1].plot(baseline['time'],baseline['sensor_traces'][:,j],lw=2.8,ls=style,label=f'x={pos*10:g} mm')
    axs[1].axhline(.5,color='#6e7680',ls='--',lw=1.5);axs[1].set(xlabel='Time (ms)',ylabel='Scaled cardiac voltage v',title='Two physical sensors');axs[1].legend(loc='upper center',bbox_to_anchor=(.5,-.23),ncol=2);axs[1].grid(alpha=.15)
    save(fig,out,'cardiac-wave','A labeled reduced cardiac wave and its sensor arrivals','New homogeneous one-dimensional Mitchell–Schaeffer reaction–diffusion calculation on a20mm sealed strand. Voltage is dimensionless. A fixed-width2ms stimulus starts at1ms. The dashed levelv=0.5defines interpolated arrival; this window shows the propagating front, not the complete repolarization cycle.')
    fig,axs=plt.subplots(1,2,figsize=(11.5,5.8),constrained_layout=True)
    axs[0].plot(ns,space,'o-',lw=2.5);axs[0].set(xlabel='Cell count (dt = 0.01 ms)',ylabel='Measured speed (m/s)',title='Refine space');axs[0].set_xticks(ns);axs[0].grid(alpha=.15)
    axs[1].plot(hs,temporal,'s-',lw=2.5,color='#a55216');axs[1].set(xlabel='Time step (ms; 400 cells)',ylabel='Measured speed (m/s)',title='Refine time');axs[1].set_xticks([.01,.04,.08]);axs[1].grid(alpha=.15)
    save(fig,out,'wave-refinement','Separate spatial and temporal sensitivity of measured speed','Three meshes at a fixed0.01ms step and four steps at400cells produce a convergence comparison of the same two physical sensor locations. No universal error order or physiological conduction-speed accuracy is asserted from this table.')
    # Analytic passive cosine: exact semi-discrete evolution removes time error.
    passive_errors=[]
    for n in [20,40,80,160]:
        dx=2/n;x=(np.arange(n)+.5)*dx;k=np.pi/2;amplitude=np.sinc(1/(2*n));T=20.;lam=-4*.001*np.sin(k*dx/2)**2/dx**2
        sem=amplitude*np.cos(k*x)*np.exp(lam*T);exact=amplitude*np.cos(k*x)*np.exp(-.001*k*k*T);passive_errors.append(float(np.max(abs(sem-exact))))
    passive_orders=np.log2(np.array(passive_errors[:-1])/passive_errors[1:]);assert np.all((passive_orders>1.98)&(passive_orders<2.02))
    # Independently check implemented diffusion against a known discrete cosine amplification.
    n=40;dx=2/n;x=(np.arange(n)+.5)*dx;u=np.cos(np.pi*x/2);h=.2;lam=-4*.001*np.sin(np.pi*dx/4)**2/dx**2
    np.testing.assert_allclose(diffuse(u,dx,.001,h),u/(1-h*lam),rtol=0,atol=5e-15)
    np.testing.assert_allclose(diffuse(np.full(40,.3),dx,.001,h),.3,rtol=0,atol=2e-15)
    quiet=simulate(n=40,end=5,amplitude=0);assert np.max(abs(quiet['final_voltage']))==0 and np.min(quiet['final_gate'])==1
    uncoupled=simulate(n=100,end=20,D=0);assert uncoupled['arrival_ms']==[None,None]
    assert baseline['gate_min']>=0 and baseline['gate_max']<=1 and baseline['voltage_min']>=-1e-12 and baseline['voltage_max']<=1+1e-12
    assert baseline['max_diffusion_sum_drift_cm']<1e-12 and abs(baseline['injected_integral_cm']-.02)<1e-12
    assert abs(space[-1]-space[-2])<abs(space[-2]-space[-3])
    assert abs(temporal[-1]-temporal[-2])<abs(temporal[-2]-temporal[-3])
    # Independent smooth uniform-cell time reference, staying above the gate switch.
    def cell_rhs(t,z):
        v,g=z
        return [g*v*v*(1-v)/TAU_IN-v/TAU_OUT,-g/TAU_CLOSE]
    ref=solve_ivp(cell_rhs,[0,1],[.5,.8],method='DOP853',rtol=2e-12,atol=2e-13)
    if not ref.success or np.min(ref.y[0])<=V_GATE:raise RuntimeError('Uniform-cell reference failed or left the tested branch.')
    cell_hs=[.04,.02,.01,.005];cell_errors=[]
    for step in cell_hs:
        v,g=.5,.8
        for _ in range(round(1/step)):v,g=reaction_step(v,g,step)
        cell_errors.append(float(abs(v-ref.y[0,-1])))
    cell_orders=np.log2(np.array(cell_errors[:-1])/cell_errors[1:]);assert np.all((cell_orders>.9)&(cell_orders<1.1))
    invalid=0
    for kwargs in [{'dt':0},{'D':-1},{'amplitude':.3},{'stim_width':3},{'n':12.5}]:
        try:simulate(**kwargs)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid tissue input accepted')
    result={'model':'reduced cardiac Mitchell–Schaeffer reaction plus original scalar tissue coupling','baseline_arrival_ms':baseline['arrival_ms'],'baseline_speed_m_s':baseline['speed_m_s'],'gate_range':[baseline['gate_min'],baseline['gate_max']],'voltage_range':[baseline['voltage_min'],baseline['voltage_max']],'n_values':ns,'spatial_speeds_m_s':space,'dt_values_ms':hs,'temporal_speeds_m_s':temporal,'uniform_cell_dt_ms':cell_hs,'uniform_cell_reference_v':float(ref.y[0,-1]),'uniform_cell_errors':cell_errors,'uniform_cell_orders':cell_orders.tolist(),'passive_spatial_errors':passive_errors,'passive_spatial_orders':passive_orders.tolist(),'max_diffusion_sum_drift_cm':baseline['max_diffusion_sum_drift_cm'],'stimulus_integral_cm':baseline['injected_integral_cm'],'checks':{'exact_discrete_diffusion_mode':True,'constant_diffusion_state':True,'rest_preserved':True,'no_coupling_no_remote_excitation':True,'gate_admissibility_without_clipping':True,'invalid_cases_rejected':invalid},'runtime_seconds':time.perf_counter()-start}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
