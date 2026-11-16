"""One original cooling model, four distinct numerical questions.
Core: initial-value solve, crossing-time root, sampled interpolation.
Optional new syllabus fill-in: one-parameter bounded least-squares optimization.
All values are synthetic; no physical calibration or safety threshold is implied.
"""
from pathlib import Path
import json,math
import xml.etree.ElementTree as ET
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq,minimize_scalar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AMBIENT_C=20.;INITIAL_C=80.;RATE_PER_MIN=.4

def parameters(k,initial=INITIAL_C,ambient=AMBIENT_C):
    if not all(np.isfinite(v) for v in (k,initial,ambient)) or k<0:
        raise ValueError('Rate must be nonnegative; parameters must be finite.')
    if initial<ambient or ambient<-273.15:
        raise ValueError('This cooling-only lesson requires initial >= ambient >= absolute zero.')

def exact_temperature(t,k=RATE_PER_MIN,initial=INITIAL_C,ambient=AMBIENT_C):
    parameters(k,initial,ambient);t=np.asarray(t,dtype=float)
    if not np.all(np.isfinite(t)) or np.any(t<0):raise ValueError('Times must be finite and nonnegative.')
    return ambient+(initial-ambient)*np.exp(-k*t)

def integrate(times,k=RATE_PER_MIN,rtol=1e-8,atol=1e-8):
    parameters(k);times=np.asarray(times,dtype=float)
    if times.ndim!=1 or len(times)<2 or times[0]!=0 or np.any(np.diff(times)<=0) or not np.all(np.isfinite(times)):
        raise ValueError('Use strictly increasing finite times beginning at zero.')
    if not np.isfinite(rtol) or not np.isfinite(atol) or min(rtol,atol)<=0:
        raise ValueError('Both tolerances must be finite and positive.')
    def rate(t,state):return [-k*(state[0]-AMBIENT_C)]
    solution=solve_ivp(rate,(0,float(times[-1])),[INITIAL_C],t_eval=times,method='RK45',rtol=rtol,atol=atol)
    if not solution.success:raise RuntimeError(solution.message)
    return solution.y[0],solution.nfev

def crossing(target=35.,bracket=(0.,8.),k=RATE_PER_MIN):
    parameters(k)
    if not np.isfinite(target) or not AMBIENT_C<target<INITIAL_C or k==0:
        raise ValueError('A finite future crossing requires ambient < target < initial and k > 0.')
    a,b=bracket
    if not all(np.isfinite(v) for v in (a,b)) or not 0<=a<b:raise ValueError('Use finite 0 <= left < right.')
    residual=lambda time:float(exact_temperature(time,k)-target)
    left_residual,right_residual=residual(a),residual(b)
    if left_residual==0:return {'time_min':float(a),'temperature_residual_C':0.,'iterations':0}
    if right_residual==0:return {'time_min':float(b),'temperature_residual_C':0.,'iterations':0}
    if left_residual*right_residual>0:raise ValueError('Bracket endpoints must straddle the target.')
    time,info=brentq(residual,a,b,xtol=1e-10,full_output=True)
    if not info.converged:raise RuntimeError('Root solve did not converge.')
    return {'time_min':time,'temperature_residual_C':residual(time),'iterations':info.iterations}

def interpolate_inside(query,times,values):
    times=np.asarray(times,dtype=float);values=np.asarray(values,dtype=float);query=np.asarray(query,dtype=float)
    if times.ndim!=1 or values.shape!=times.shape or len(times)<2 or np.any(np.diff(times)<=0):raise ValueError('Use matching samples at strictly increasing times.')
    if not all(np.all(np.isfinite(v)) for v in (times,values,query)):raise ValueError('Interpolation inputs must be finite.')
    if np.any(query<times[0]) or np.any(query>times[-1]):raise ValueError('Query is outside the observed interval; no extrapolation is supplied.')
    return np.interp(query,times,values)

def fit_rate(times,observed):
    times=np.asarray(times,dtype=float);observed=np.asarray(observed,dtype=float)
    if times.ndim!=1 or len(times)<2 or observed.shape!=times.shape or np.any(times<0) or not np.all(np.isfinite(times)) or not np.all(np.isfinite(observed)):
        raise ValueError('Use finite nonnegative sample times and matching observed temperatures.')
    if not np.any(times>0):raise ValueError('At least one positive sample time is needed to identify the cooling rate.')
    objective=lambda k:float(np.mean((exact_temperature(times,k)-observed)**2))
    result=minimize_scalar(objective,bounds=(.05,1.),method='bounded',options={'xatol':1e-10})
    if not result.success:raise RuntimeError(result.message)
    return {'rate_per_min':float(result.x),'mean_square_residual_C2':float(result.fun)}

def save(fig,out,stem,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/(stem+'.'+ext),bbox_inches='tight')
    plt.close(fig);ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(out/(stem+'.svg'));r=tree.getroot();r.set('role','img');r.set('aria-labelledby',stem+'-title '+stem+'-desc')
    for tag,value in [('title',title),('desc',desc)]:
        e=ET.Element('{'+ns+'}'+tag,id=stem+'-'+tag);e.text=value;r.insert(0,e)
    tree.write(out/(stem+'.svg'),encoding='utf-8',xml_declaration=True)

def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    t=np.linspace(0,8,161);truth=exact_temperature(t);numeric,nfev=integrate(t);coarse,nfev_coarse=integrate(t,rtol=1e-3,atol=1e-4)
    error=float(np.max(abs(numeric-truth)));coarse_error=float(np.max(abs(coarse-truth)));root=crossing()
    analytic_time=math.log((INITIAL_C-AMBIENT_C)/(35-AMBIENT_C))/RATE_PER_MIN
    sample_times=np.arange(0,8.01,2.);sample_values=exact_temperature(sample_times);linear=interpolate_inside(t,sample_times,sample_values)
    interp_error=float(np.max(abs(linear-truth)))
    assert error<1e-5 and error<coarse_error
    assert abs(root['time_min']-analytic_time)<1e-9 and abs(root['temperature_residual_C'])<1e-8
    assert np.all(numeric>=AMBIENT_C-1e-7) and np.all(np.diff(numeric)<=1e-7)
    zero,_=integrate([0.,1.,2.],k=0);assert np.allclose(zero,INITIAL_C)
    assert np.allclose(interpolate_inside(sample_times,sample_times,sample_values),sample_values)
    fit_times=np.arange(9.);offsets=np.array([0,.3,-.2,.4,-.3,.2,0,-.2,.1]);observed=exact_temperature(fit_times)+offsets;fit=fit_rate(fit_times,observed)
    noiseless=fit_rate(fit_times,exact_temperature(fit_times));assert abs(noiseless['rate_per_min']-.4)<1e-7
    rejected=0
    for fn in [lambda:crossing(target=20),lambda:crossing(bracket=(0,1)),lambda:interpolate_inside(9,sample_times,sample_values),lambda:integrate([0,1,1]),lambda:exact_temperature([0],k=-1)]:
        try:fn()
        except ValueError:rejected+=1
    assert rejected==5
    plt.rcParams.update({'font.size':20,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(2,1,figsize=(9.2,6.1),sharex=True,gridspec_kw={'height_ratios':[2,1]})
    axs[0].plot(t,truth,label='Exact solution',color='#176c7b',lw=2);axs[0].plot(t,numeric,'--',label='ODE solution',color='#bd702d')
    axs[0].plot(sample_times,sample_values,'o',color='#39434b',label='2 min samples');axs[0].plot(t,linear,':',color='#737b83',label='Linear interpolation')
    axs[0].axhline(35,color='#555',ls='--',lw=.8);axs[0].axvline(root['time_min'],color='#555',ls=':',lw=.8)
    axs[0].annotate('35 °C crossing\n3.466 min',xy=(root['time_min'],35),xytext=(1.3,65),arrowprops={'arrowstyle':'->','color':'#555'},fontsize=20)
    axs[0].set(ylabel='Temperature (°C)',title='One model, three numerical questions',ylim=(18,95));axs[0].legend(frameon=False,fontsize=20,loc='upper right');axs[0].set_yticks([20,40,60,80])
    axs[1].plot(t,linear-truth,color='#737b83');axs[1].axhline(0,color='#555',lw=.7);axs[1].set(xlabel='Time (min)',ylabel='Error (°C)',title='Interpolation − exact');axs[1].set_yticks([0,1,2,3])
    for ax in axs:ax.grid(alpha=.2)
    fig.tight_layout();save(fig,out,'cooling-questions','ODE solution, crossing time and interpolation error','Cooling from 80 toward 20 degrees follows rate 0.4 per minute. The 35-degree crossing occurs at about 3.466 minutes. Linear interpolation from two-minute samples differs from the exact curve between samples; the lower panel displays that error explicitly.')
    grid=np.linspace(.1,.8,180);loss=[np.mean((exact_temperature(fit_times,k)-observed)**2) for k in grid]
    plt.rcParams.update({'font.size':16})
    fig,axs=plt.subplots(1,2,figsize=(9.2,4.2));axs[0].plot(grid,loss,color='#176c7b');axs[0].axvline(fit['rate_per_min'],color='#bd702d',ls='--');axs[0].set(xlabel='Cooling rate k (1/min)',ylabel='Mean squared\nresidual (°C²)',title='Optional: choose k')
    axs[1].bar(fit_times,observed-exact_temperature(fit_times,fit['rate_per_min']),color='#bd702d');axs[1].axhline(0,color='#555',lw=.7);axs[1].set(xlabel='Observation time (min)',ylabel='Observation − fitted\nmodel (°C)',title='Residuals after fitting')
    axs[0].set_xticks([.1,.2,.4,.6,.8]);axs[0].set_yticks([0,200,400]);axs[1].set_yticks([-.3,0,.3]);axs[1].set_xticks([0,2,4,6,8])
    fig.tight_layout();save(fig,out,'fit-and-residuals','Optional parameter fit and residuals','The left panel evaluates a one-parameter squared-error objective against nine synthetic perturbed observations; the minimum selects a rate near 0.4 per minute. The right panel shows remaining temperature residuals. An optimizer success flag does not validate the physical cooling assumptions or identify measurement uncertainty.')
    report={'model':{'initial_C':80,'ambient_C':20,'rate_per_min':.4},'max_ODE_error_C':error,'coarse_ODE_error_C':coarse_error,'function_evaluations':{'tight':nfev,'coarse':nfev_coarse},'crossing':root,'analytic_crossing_min':analytic_time,'max_two_minute_interpolation_error_C':interp_error,'optional_new_optimization':fit,'checks':{'zero_rate_constant':True,'interpolation_at_knots':True,'noiseless_parameter_recovery':True,'invalid_inputs_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
