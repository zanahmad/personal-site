"""Proposed 2027 day 3: sensor linear solve and coupled tracer exchange.
Two fixed equal 1-L reservoirs exchange dissolved tracer with no sources/sinks.
States are tracer masses in mg; k is the exchange rate divided by volume (1/min).
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INITIAL=np.array([8.,2.]);SENSOR=np.array([[1.,.2],[.1,1.]])


def recover_initial(reading,sensor=SENSOR):
    y=np.asarray(reading,dtype=float);a=np.asarray(sensor,dtype=float)
    if y.shape!=(2,) or a.shape!=(2,2) or not np.all(np.isfinite(y)) or not np.all(np.isfinite(a)):raise ValueError('Use a finite 2-by-2 sensor map and two readings.')
    try:state=np.linalg.solve(a,y)
    except np.linalg.LinAlgError as error:raise ValueError('The sensor map does not uniquely identify two masses.') from error
    with np.errstate(over='ignore',invalid='ignore'):
        residual=float(np.linalg.norm(a@state-y))
    if not np.all(np.isfinite(state)) or not np.isfinite(residual):
        raise ValueError('The solved state or residual exceeds finite arithmetic range.')
    return state,residual


def rate_parameter(k):
    if not np.isfinite(k) or k<0:raise ValueError('Rate must be finite and nonnegative.')


def exact(times,k=.3):
    rate_parameter(k);t=np.asarray(times,dtype=float)
    if not np.all(np.isfinite(t)) or np.any(t<0):raise ValueError('Times must be finite and nonnegative.')
    excess=3*np.exp(-2*k*t)
    return np.stack([5+excess,5-excess],axis=-1)


def time_grid(times):
    t=np.asarray(times,dtype=float)
    if t.ndim!=1 or len(t)<2 or t[0]!=0 or not np.all(np.isfinite(t)) or np.any(np.diff(t)<=0):raise ValueError('Use increasing finite times starting at zero.')
    return t


def simulate(times,k=.3,rtol=1e-8,atol=1e-10):
    t=time_grid(times);rate_parameter(k)
    if not np.isfinite(rtol) or not np.isfinite(atol) or min(rtol,atol)<=0:raise ValueError('Tolerances must be finite and positive.')
    def rhs(time,state):
        transfer=k*(state[0]-state[1]);return [-transfer,transfer]
    solution=solve_ivp(rhs,(0,float(t[-1])),INITIAL,t_eval=t,rtol=rtol,atol=atol)
    if not solution.success:raise RuntimeError(solution.message)
    return solution.y.T


def euler(times,k=.3):
    t=time_grid(times);rate_parameter(k)
    if np.any(2*k*np.diff(t)>1):raise ValueError('This teaching Euler comparison requires 2*k*step <= 1 for monotone exchange.')
    state=np.empty((len(t),2));state[0]=INITIAL
    for i,h in enumerate(np.diff(t)):
        transfer=k*(state[i,0]-state[i,1]);state[i+1]=state[i]+h*np.array([-transfer,transfer])
    return state


def fit_rate(times,observed_A):
    t=np.asarray(times,dtype=float);y=np.asarray(observed_A,dtype=float)
    if t.ndim!=1 or len(t)<2 or y.shape!=t.shape or not np.all(np.isfinite(t)) or not np.all(np.isfinite(y)) or np.any(t<0):raise ValueError('Use matching finite observation vectors at nonnegative times.')
    if not np.any(t>0):raise ValueError('At least one positive observation time is needed to identify the exchange rate.')
    def objective(k):
        with np.errstate(over='ignore',invalid='ignore'):
            value=float(np.mean((exact(t,k)[:,0]-y)**2))
        if not np.isfinite(value):raise ValueError('Squared residuals exceed finite arithmetic range.')
        return value
    fit=minimize_scalar(objective,bounds=(.01,1.),method='bounded',options={'xatol':1e-10})
    if not fit.success:raise RuntimeError(fit.message)
    return {'rate_per_min':float(fit.x),'mean_squared_residual_mg2':float(fit.fun),'bounds_per_min':[.01,1.]}


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/(stem+'.'+ext),bbox_inches='tight')
    plt.close(fig);ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(out/(stem+'.svg'));r=tree.getroot();r.set('role','img');r.set('aria-labelledby',stem+'-title '+stem+'-desc')
    for tag,text in [('title',title),('desc',description)]:
        node=ET.Element('{'+ns+'}'+tag,id=stem+'-'+tag);node.text=text;r.insert(0,node)
    tree.write(out/(stem+'.svg'),encoding='utf-8',xml_declaration=True)


def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    recovered,residual=recover_initial(SENSOR@INITIAL);assert np.allclose(recovered,INITIAL)
    t=np.linspace(0,6,121);reference=exact(t);numerical=simulate(t);ode_error=float(np.max(abs(reference-numerical)))
    assert ode_error<1e-6 and np.max(abs(numerical.sum(axis=1)-10))<1e-10
    assert np.allclose(simulate([0,1,2],k=0),np.tile(INITIAL,(3,1)))
    coarse_t=np.linspace(0,6,13);fine_t=np.linspace(0,6,25)
    coarse=euler(coarse_t);fine=euler(fine_t);coarse_error=float(np.max(abs(coarse-exact(coarse_t))));fine_error=float(np.max(abs(fine-exact(fine_t))))
    assert fine_error<coarse_error and np.allclose(coarse.sum(axis=1),10)
    obs_t=np.arange(7.);offset=np.array([0,.04,-.03,.05,-.04,.02,-.01]);obs=exact(obs_t)[:,0]+offset;fit=fit_rate(obs_t,obs)
    recovery=fit_rate(obs_t,exact(obs_t)[:,0]);assert abs(recovery['rate_per_min']-.3)<1e-7
    rejected=0
    for fn in [lambda:recover_initial([1,1],[[1,1],[1,1]]),lambda:simulate([0,1,1]),lambda:euler([0,3],k=.3),lambda:fit_rate([0,0],[8,8]),lambda:exact([0,1],k=-1)]:
        try:fn()
        except ValueError:rejected+=1
    assert rejected==5
    plt.rcParams.update({'font.size':18, 'axes.titlesize':18, 'legend.fontsize':18,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(9.4,5.6))
    axs[0].plot(t,numerical[:,0],color='#176c7b',label='A');axs[0].plot(t,numerical[:,1],'--',color='#b46d27',label='B');axs[0].plot(t,numerical.sum(axis=1),':',color='#555',label='Total');axs[0].set(xlabel='Time (min)',ylabel='Tracer mass (mg)',title='Mass is conserved');axs[0].legend(frameon=False,fontsize=18,ncol=3,loc='upper center',bbox_to_anchor=(.5,-.23),columnspacing=.6,handlelength=1.2,handletextpad=.3)
    axs[1].plot(coarse_t,abs(coarse[:,0]-exact(coarse_t)[:,0]),'o-',label='h = 0.5 min',color='#b46d27');axs[1].plot(fine_t,abs(fine[:,0]-exact(fine_t)[:,0]),'s-',label='h = 0.25 min',color='#176c7b');axs[1].set(xlabel='Time (min)',ylabel='A-mass error (mg)',title='Accuracy still differs');axs[1].legend(frameon=False,fontsize=18,loc='upper center',bbox_to_anchor=(.5,-.23))
    for ax in axs:ax.grid(alpha=.2)
    fig.tight_layout();save(fig,out,'exchange-and-error','Tracer transfer and numerical error','Two equal-volume reservoirs begin with eight and two milligrams and exchange tracer at k equal to 0.3 per minute. Their total remains ten milligrams. Both forward-Euler runs conserve total mass, but their individual-state errors differ and shrink with the smaller step.')
    grid=np.linspace(.1,.7,150);objective=[np.mean((exact(obs_t,k)[:,0]-obs)**2) for k in grid]
    fig,axs=plt.subplots(1,2,figsize=(9.4,4.9));axs[0].plot(grid,objective,color='#176c7b');axs[0].axvline(fit['rate_per_min'],color='#b46d27',ls='--');axs[0].set(xlabel='Rate (1/min)',ylabel='Mean squared residual (mg²)',title='Fit one parameter')
    axs[1].scatter(obs_t,obs,color='#b46d27',label='Observations');axs[1].plot(t,exact(t,fit['rate_per_min'])[:,0],color='#176c7b',label='Fitted curve');axs[1].set(xlabel='Time (min)',ylabel='Mass in A (mg)',title='Fit needs validation');axs[1].legend(frameon=False,fontsize=18)
    for ax in axs:ax.grid(alpha=.2)
    fig.tight_layout();save(fig,out,'parameter-evidence','A bounded exchange-rate fit','A positive bounded rate is fitted against seven synthetic perturbed observations of reservoir A. The objective and fitted curve use the exact solution of the declared model, isolating parameter fitting from integration error. A small residual does not validate equal-volume exchange assumptions.')
    report={'sensor_reading_mg_equivalent':(SENSOR@INITIAL).tolist(),'recovered_initial_mg':recovered.tolist(),'linear_residual_mg_equivalent':residual,'maximum_ODE_error_mg':ode_error,'Euler_maximum_errors_mg':{'step_0.5_min':coarse_error,'step_0.25_min':fine_error},'fit':fit,'checks':{'total_mass_conserved':True,'zero_rate_constant':True,'Euler_refinement_improves_error':True,'noiseless_parameter_recovery':True,'zero_time_identifiability_rejected':True,'invalid_inputs_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
