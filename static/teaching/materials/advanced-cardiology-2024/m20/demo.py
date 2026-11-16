"""Original synthesis audit: field accuracy, mean and correlation differ.

All examples are synthetic outputs around the known sealed heat solution. They
are not trained-model results or patient measurements. A perfect correlation
under a bias, or a conserved mean under lost spatial detail, is insufficient
validation. Undefined correlations remain undefined in records and plots.
"""
from pathlib import Path
import json,time
import numpy as np
from operator_bench import grid,field,metrics
from plot_helpers import configure,save,plt

def correlation(a,b):
 """Pearson correlation of finite float64 vectors, or None for exact constants.

 Power-of-two rescaling prevents overflow without rounding away representable
 near-constant differences. Centering differences from an anchor also avoids
 cancellation in a large mean. Finite representable nonconstant inputs remain
 defined; this numerical convention does not assess measurement uncertainty.
 Empty vectors are invalid. Values already rounded to a constant on conversion
 to float64 have no recoverable variation and therefore return None.
 """
 a=np.asarray(a,float);b=np.asarray(b,float)
 if a.shape!=b.shape or a.ndim!=1 or not a.size or not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('Matched nonempty finite field vectors required.')
 def centered_unit(v):
  if np.all(v==v[0]):return None
  exponent=int(np.frexp(np.max(np.abs(v)))[1])
  scaled=np.ldexp(v,-exponent)
  delta=scaled-scaled[0];centered=delta-delta.mean()
  centered/=np.max(np.abs(centered))
  return centered/np.linalg.norm(centered)
 ac=centered_unit(a);bc=centered_unit(b)
 if ac is None or bc is None:return None
 return float(np.clip(np.dot(ac,bc),-1.,1.))

def run(output_dir=None):
 start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);configure()
 coeff=np.array([1.,.3,-.15,.1]);n=128;x=grid(n);times=np.linspace(0,.2,81);truth=np.array([field(coeff,n,T=t) for t in times]);biased=truth+.2;flat=np.broadcast_to(truth.mean(axis=1,keepdims=True),truth.shape).copy()
 candidates={'Exact':truth,'Biased':biased,'Mean only':flat};rows=[]
 for label,values in candidates.items():
  errors=metrics(values[-1],truth[-1]);rows.append({'candidate':label,'final_errors':errors,'final_spatial_correlation':correlation(values[-1],truth[-1]),'initial_rms_mismatch':metrics(values[0],truth[0])['rms'],'max_mean_error_vs_prescribed_initial':float(np.max(abs(values.mean(axis=1)-coeff[0]))),'max_own_mean_change':float(np.max(abs(values.mean(axis=1)-values[0].mean())))})
 assert abs(rows[1]['final_spatial_correlation']-1)<1e-14 and rows[1]['final_errors']['rms']>.19
 assert rows[2]['final_spatial_correlation'] is None and rows[2]['max_mean_error_vs_prescribed_initial']<1e-14 and rows[2]['final_errors']['rms']>.1
 assert all(r['max_own_mean_change']<1e-14 for r in rows)
 fig,axs=plt.subplots(1,2,figsize=(11.5,7.2),constrained_layout=True)
 for (label,values),style in zip(candidates.items(),['-','--',':']):
  axs[0].plot(x,values[-1],ls=style,lw=2.8,label=label);axs[1].plot(times,values.mean(axis=1),ls=style,lw=2.8,label=label)
 axs[0].set(xlabel='Position x',ylabel='Final field at t=0.2',title='Three different field claims');axs[1].set(xlabel='Time',ylabel='Spatial mean',title='Conserved does not mean correct')
 for ax in axs:ax.legend(loc='upper center',bbox_to_anchor=(.5,-.23));ax.grid(alpha=.15)
 save(fig,out,'field-and-moment','Three synthetic field candidates and their means','Original exact heat reference, a synthetic additive-bias candidate and a spatial-mean-only candidate. All preserve their own mean, but the biased candidate violates the prescribed initial mean and the mean-only candidate discards spatial structure. These are teaching counterexamples, not learned or patient outputs.')
 fig,axs=plt.subplots(1,2,figsize=(11.5,5.8),constrained_layout=True);labels=['Exact','Biased','Mean\nonly'];colors=['#2879a3','#d07c2c','#55945a']
 bars=axs[0].bar(labels,[r['final_errors']['relative_l2'] for r in rows],color=colors)
 for b,hatch in zip(bars,['/','x','.']):b.set_hatch(hatch)
 axs[0].set(ylabel='Final relative L2 error',title='A field metric sees both failures')
 bars=axs[1].bar(labels[:2],[rows[j]['final_spatial_correlation'] for j in range(2)],color=colors[:2])
 for b,hatch in zip(bars,['/','x']):b.set_hatch(hatch)
 axs[1].set_xticks([0,1,2],labels);axs[1].set_xlim(-.5,2.5);axs[1].set_ylim(0,1.2);axs[1].text(2,.45,'Undefined',ha='center',rotation=90,fontsize=22);axs[1].set(ylabel='Spatial Pearson correlation',title='Correlation can miss a bias')
 save(fig,out,'evidence-audit','Field error and correlation answer different questions','Final-time relative L2 error detects both synthetic failures. Spatial Pearson correlation remains one for an additive bias and is undefined for a constant field; the missing value is not replaced by zero. Pair these metrics with initial-condition and mean-budget checks.')
 # Independent affine identity and zero-reference relative-error convention.
 a=np.array([1.,4.,2.,8.]);assert abs(correlation(a,3*a+7)-1)<1e-14
 assert correlation(np.ones(4),a) is None
 assert metrics(np.ones(8),np.zeros(8))['relative_l2'] is None
 result={'model':'synthetic audit around an analytic nondimensional heat solution; no patient or trained-model outputs','final_time':.2,'grid_cells':128,'candidates':rows,'checks':{'affine_correlation_identity':True,'constant_correlation_undefined':True,'zero_reference_relative_error_undefined':True,'all_own_means_preserved':True,'counterexamples_detected_by_field_metric':True},'runtime_seconds':time.perf_counter()-start}
 (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
