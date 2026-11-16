"""Original cost/error bookkeeping and a fitted one-mode generator example.

Measured timings are local CPU observations, not portable speedup promises.
Known analytic heat truth makes learning unnecessary here; it is deliberately
included as a baseline. The training-step example is scalar mathematics, not a
reproduction of G-FuNK's neural architecture, cardiac results or performance.
"""
from pathlib import Path
import json,time
import numpy as np
from operator_bench import grid,field,project,dataset,fit,predict,reference_fd,metrics
from plot_helpers import configure,save,plt

def timed(fn,repeats=7,batch=10):
 fn();samples=[]
 for _ in range(repeats):
  t=time.perf_counter()
  for __ in range(batch):fn()
  samples.append((time.perf_counter()-t)/batch)
 return float(np.median(samples)),samples

def learned_decay(step,training_step=.1,rate=2.,T=.5):
 if not np.isfinite([step,training_step,rate,T]).all() or min(step,training_step,rate,T)<=0:raise ValueError('Positive finite decay controls required.')
 ratio=T/step
 if not np.isfinite(ratio) or ratio<1 or ratio>100000:raise ValueError('Use1–100000 inference intervals.')
 n=round(ratio)
 if abs(n*step-T)>16*np.finfo(float).eps*max(T,step):raise ValueError('Step must divide the tested horizon within roundoff tolerance.')
 gain=np.exp(-rate*training_step);generator=np.expm1(-rate*training_step)/training_step
 factor=1+step*generator
 if factor<0:raise ValueError('This Euler step would reverse the sign of the decaying state.')
 return float(factor**n),float(generator)

def run(output_dir=None):
 start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);configure()
 setup=time.perf_counter();train=dataset(seed=1901,n=128);generation_seconds=time.perf_counter()-setup
 setup=time.perf_counter();model=fit(train['initial'],train['final']);fit_seconds=time.perf_counter()-setup
 coeff=np.array([1.,.3,-.15,.1]);initial=field(coeff,128,T=0);truth=field(coeff,128)
 functions={'BE reference':lambda:reference_fd(initial,dt=.0005),'Analytic spectral':lambda:field(project(initial,3),128),'3-mode fit':lambda:predict(model,initial)}
 rows=[]
 for label,fn in functions.items():
  duration,samples=timed(fn);rows.append({'method':label,'median_seconds_per_query':duration,'timing_samples_seconds':samples,'error':metrics(fn(),truth)})
 setup_seconds=generation_seconds+fit_seconds;saving=rows[0]['median_seconds_per_query']-rows[2]['median_seconds_per_query'];break_even=None if saving<=0 else setup_seconds/saving
 assert rows[0]['error']['rms']<.001 and rows[1]['error']['rms']<1e-14 and rows[2]['error']['rms']<1e-14
 assert all(r['median_seconds_per_query']>0 for r in rows)
 fig,axs=plt.subplots(1,2,figsize=(11.5,5.8),constrained_layout=True);labels=['BE','Analytic','Fit'];colors=['#2879a3','#d07c2c','#55945a']
 bars=axs[0].bar(labels,[r['median_seconds_per_query']*1e6 for r in rows],color=colors)
 for b,hatch in zip(bars,['/','x','.']):b.set_hatch(hatch)
 axs[0].set_yscale('log');axs[0].set_yticks([10,100,1000,10000],['10','100','1000','10000']);axs[0].minorticks_off();axs[0].set(ylabel='Local time per query (µs)',title='Measured CPU cost')
 bars=axs[1].bar(labels,[r['error']['rms']*1e6 for r in rows],color=colors)
 for b,hatch in zip(bars,['/','x','.']):b.set_hatch(hatch)
 axs[1].set(ylabel='RMS field error × 1e6',title='Error against analytic truth');axs[1].text(.72,.65,'Near roundoff\nfor both\nspectral maps.',transform=axs[1].transAxes,ha='center',fontsize=22)
 save(fig,out,'cost-error','Measured cost and error with an analytic baseline','Local warm-query CPU medians from seven batches of ten calls, including per-query projection or matrix assembly. Setup and analytic-label generation are recorded separately. The known analytic solution is itself inexpensive, so this benchmark is an accounting exercise rather than an argument for machine learning. No paper timing is reproduced.')
 steps=[.1,.05,.025,.0125];values=[learned_decay(h)[0] for h in steps];generator=learned_decay(.1)[1];exact=np.exp(-1);continuous=np.exp(generator*.5);errors=np.abs(np.array(values)-exact)
 assert errors[0]<1e-15 and np.all(np.diff(errors)>0)
 np.testing.assert_allclose(learned_decay(.1)[0],np.exp(-2*.5),rtol=0,atol=1e-15)
 fig,axs=plt.subplots(1,2,figsize=(11.5,7.2),constrained_layout=True)
 axs[0].plot(steps,values,'o-',lw=2.5,label='Learned + Euler');axs[0].axhline(exact,color='#a75620',ls='--',lw=2.5,label='True decay');axs[0].axhline(continuous,color='#477c48',ls=':',lw=2.5,label='Exact learned flow');axs[0].set(xlabel='Inference step',ylabel='State at T=0.5',title='A step-coupled fitted generator');axs[0].legend(loc='upper center',bbox_to_anchor=(.5,-.23));axs[0].set_xticks([.0125,.05,.1],['0.0125','0.05','0.1']);axs[0].grid(alpha=.15)
 axs[1].plot(steps,errors,'s-',lw=2.5,color='#a75620');axs[1].set(xlabel='Inference step',ylabel='Absolute state error',title='Smaller steps need not help');axs[1].set_xticks([.0125,.05,.1],['0.0125','0.05','0.1']);axs[1].grid(alpha=.15)
 save(fig,out,'learned-step','A generator fitted through one discretization','Original scalar example: exact decay rate2 is sampled with training step0.1, then a generator is fitted through a forward-Euler update. The training-step rollout matches sampled truth, while smaller Euler steps approach the biased learned continuous flow. This illustrates a mechanism, not a reproduction of G-FuNK sensitivity results.')
 result={'model':'nondimensional heat cost audit plus independent scalar fitted-generator example','timing_protocol':{'repeats':7,'queries_per_batch':10,'warmup_calls':1,'clock':'perf_counter','hardware':'current local CPU; no portability claim'},'analytic_training_label_generation_seconds':generation_seconds,'fit_seconds':fit_seconds,'setup_seconds':setup_seconds,'query_methods':rows,'measured_setup_break_even_queries_vs_BE':break_even,'training_step':.1,'true_rate':2.,'learned_generator':generator,'inference_steps':steps,'inference_values':values,'true_state_at_half':float(exact),'exact_learned_flow_at_half':float(continuous),'absolute_errors':errors.tolist(),'checks':{'training_step_matches_sampled_truth':True,'smaller_step_bias_exposed':True,'analytic_baseline_included':True},'runtime_seconds':time.perf_counter()-start}
 (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
