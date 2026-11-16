"""A three-mode linear spectral baseline, explicitly NOT G-FuNK.

This finite-band fixed-kappa/fixed-time fit is intentionally exactly representable.
It illustrates what grid reuse does and does not establish; it does not learn an
anisotropic graph neural generator, nonlinear closure, geometry family or patient.
"""
from pathlib import Path
import json,time
import numpy as np
from operator_bench import grid,field,dataset,fit,predict,metrics
from plot_helpers import configure,save,plt

def run(output_dir=None):
 start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);configure()
 train=dataset(seed=1801);test=dataset(count=16,seed=1802);model=fit(train['initial'],train['final'])
 gains=np.exp(-.1*(np.pi*np.arange(1,4))**2*.1);np.testing.assert_allclose(model['gains'],gains,rtol=0,atol=8e-16)
 id_errors=[metrics(p,y)['relative_l2'] for p,y in zip(predict(model,test['initial']),test['final'])];assert max(id_errors)<1e-14
 coeff=np.array([1.,.3,-.15,.1]);grid_errors=[]
 for n in [32,64,128,256]:grid_errors.append(metrics(predict(model,field(coeff,n,T=0)),field(coeff,n))['relative_l2'])
 assert max(grid_errors)<1e-14
 n=128;x=grid(n);initial=field(coeff,n,T=0);same_prediction=predict(model,initial);changed_truth=field(coeff,n,kappa=.02)
 missed=np.array([1.,.1,0.,0.,.5]);missing_initial=field(missed,n,T=0);missing_prediction=predict(model,missing_initial);missing_truth=field(missed,n)
 changed_error=metrics(same_prediction,changed_truth);missing_error=metrics(missing_prediction,missing_truth)
 assert changed_error['relative_l2']>.02 and missing_error['relative_l2']>.05
 fig,axs=plt.subplots(1,2,figsize=(11.5,5.8),constrained_layout=True)
 axs[0].plot([1,2,3],gains,'o-',lw=2.5,label='Analytic');axs[0].plot([1,2,3],model['gains'],'x',ms=12,mew=2.5,label='Fitted');axs[0].set(xlabel='Retained mode index',ylabel='Attenuation gain',title='An exactly representable fit');axs[0].set_xticks([1,2,3]);axs[0].legend();axs[0].grid(alpha=.15)
 axs[1].plot(x,field(coeff,n),'--',lw=3,label='Exact target');axs[1].plot(x,same_prediction,':',lw=3,label='3-mode fit');axs[1].set(xlabel='Position x (128 cells)',ylabel='Field at t=0.1',title='Reuse on a finer sampling grid');axs[1].legend();axs[1].grid(alpha=.15)
 save(fig,out,'spectral-baseline','An exactly representable three-mode spectral baseline','Original least-squares fit of three independent heat attenuation gains at fixed diffusivity0.1 and time0.1. The shown128-cell prediction reuses a fit from64-cell samples. Roundoff-level error is expected for this deliberately matched linear finite-mode family; this is not G-FuNK.')
 fig,axs=plt.subplots(1,2,figsize=(11.5,7.2),constrained_layout=True)
 for ax,target,pred,title in [(axs[0],changed_truth,same_prediction,'Changed diffusivity'),(axs[1],missing_truth,missing_prediction,'An omitted input mode')]:
  ax.plot(x,target,'-',lw=2.8,label='Exact target');ax.plot(x,pred,'--',lw=2.8,label='Unchanged fit');ax.set(xlabel='Position x',ylabel='Output field',title=title);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.23));ax.grid(alpha=.15)
 save(fig,out,'transfer-failures','Two deliberately unsupported transfers','Left: the fitted fixed-kappa map is compared with a target at diffusivity0.02. Right: the input contains a fourth cosine mode absent from the three-mode representation. Both failures occur despite successful same-family grid reuse. All quantities are nondimensional.')
 # A sign flip of a modal basis cancels in projection/reconstruction; raw mode
 # amplitudes cannot be compared across arbitrary bases without conventions.
 B=np.cos(np.pi*x[:,None]*np.arange(1,4));sign=np.array([-1,1,-1]);flipped=initial.mean()+(2/n*(initial@(B*sign))*model['gains'])@(B*sign).T
 np.testing.assert_allclose(flipped,same_prediction,atol=5e-16,rtol=0)
 assert abs(missing_prediction.mean()-missing_initial.mean())<1e-14
 bad=np.ones((8,64))
 try:fit(bad,bad)
 except ValueError:pass
 else:raise AssertionError('Unexcited modes accepted as identifiable')
 W=np.array([[0.,1,0],[1,0,2],[0,2,0]]);degree=W.sum(axis=1);Lsym=np.eye(3)-W/np.sqrt(degree[:,None]*degree[None,:])
 np.testing.assert_allclose(Lsym@np.sqrt(degree),0,rtol=0,atol=5e-16)
 assert np.linalg.norm(Lsym@np.ones(3))>.1
 result={'model':'original three-mode diagonal linear spectral regression; not G-FuNK','training_cases':48,'test_cases':16,'training_grid':64,'fixed_kappa':.1,'fixed_output_time':.1,'fitted_gains':model['gains'].tolist(),'analytic_gains':gains.tolist(),'max_id_relative_l2':max(id_errors),'transfer_grids':[32,64,128,256],'same_family_grid_errors':grid_errors,'changed_kappa':.02,'changed_parameter_error':changed_error,'omitted_fourth_mode_error':missing_error,'checks':{'complete_case_split_disjoint':not bool(set(train['ids'])&set(test['ids'])),'basis_sign_invariance':True,'normalized_graph_degree_null_mode':True,'mean_preserved_by_construction':True,'unidentifiable_modes_rejected':True},'runtime_seconds':time.perf_counter()-start}
 (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
