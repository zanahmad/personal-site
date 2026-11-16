"""Function-to-field and trajectory data for an exactly solvable heat operator."""
from pathlib import Path
import json,time
import numpy as np
from scipy.linalg import expm
from operator_bench import grid,basis,field,project,dataset,reference_fd,metrics
from plot_helpers import configure,save,plt

def run(output_dir=None):
 start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);configure()
 train=dataset(seed=1701);test=dataset(count=16,seed=1702);assert not set(train['ids'])&set(test['ids'])
 coeff=np.array([1.,.3,-.15,.1]);x=grid(128);times=[0.,.05,.1,.2]
 fig,axs=plt.subplots(1,2,figsize=(11.5,7.2),constrained_layout=True)
 for t,style in zip(times,['-','--','-.',':']):axs[0].plot(x,field(coeff,128,T=t),ls=style,lw=2.8,label=f't={t:g}')
 axs[0].set(xlabel='Position x',ylabel='Field u(x,t)',title='One input → a trajectory');axs[0].legend(loc='upper center',bbox_to_anchor=(.5,-.23),ncol=2);axs[0].grid(alpha=.15)
 for kap,style in zip([.02,.1,.3],['-','--',':']):axs[1].plot(x,field(coeff,128,kappa=kap),ls=style,lw=2.8,label=f'κ={kap:g}')
 axs[1].set(xlabel='Position x',ylabel='Field at t=0.1',title='A parameter changes the map');axs[1].legend(loc='upper center',bbox_to_anchor=(.5,-.23));axs[1].grid(alpha=.15)
 save(fig,out,'operator-family','Initial fields, trajectories and a parameterized solution map','Original nondimensional sealed heat equation with cosine-mode exact solutions. One panel evolves the same initial field; the second changes diffusivity at a fixed output time. Neither is a cardiac simulation.')
 fig,axs=plt.subplots(1,2,figsize=(11.5,7.2),constrained_layout=True)
 for j,style in zip([0,1,2],['-','--',':']):axs[0].plot(grid(64),train['initial'][j],lw=2.5,ls=style,label=f'case {j+1}')
 axs[0].set(xlabel='Position x',ylabel='Training input field',title='Cases are complete functions');axs[0].legend(loc='upper center',bbox_to_anchor=(.5,-.23));axs[0].grid(alpha=.15)
 axs[1].scatter(train['coefficients'][:,1],train['coefficients'][:,2],marker='o',s=48,label='Train');axs[1].scatter(test['coefficients'][:,1],test['coefficients'][:,2],marker='x',s=70,label='Test')
 axs[1].set(xlabel='Input mode 1 amplitude',ylabel='Input mode 2 amplitude',title='Split by case, not mesh node');axs[1].legend(loc='upper center',bbox_to_anchor=(.5,-.23));axs[1].grid(alpha=.15)
 save(fig,out,'dataset-regimes','Complete-case train and test regimes','Deterministic disjoint case identifiers assign whole initial conditions and their output fields to train or test. The projection shown includes only the first two of three input modes; neighboring space/time samples are not independent cases.')
 # Analytic semigroup, discrete quadrature and an independent dense matrix exponential.
 u=field(coeff,64,T=.07);c=project(u,3);np.testing.assert_allclose(field(c,64,T=.13),field(coeff,64,T=.2),atol=2e-15,rtol=0)
 assert abs(u.mean()-coeff[0])<1e-14
 n=16;L=np.diag(np.r_[1.,np.full(n-2,2.),1.])+np.diag(-np.ones(n-1),1)+np.diag(-np.ones(n-1),-1);initial=field(coeff,n,T=0)
 lam=4*.1*np.sin(np.pi*np.arange(1,4)/(2*n))**2*n*n;sem=coeff[0]+(coeff[1:]*np.exp(-lam*.1))@basis(n,3).T
 np.testing.assert_allclose(expm(-.1*L*n*n*.1)@initial,sem,atol=3e-15,rtol=0)
 errors=[]
 for n in [20,40,80,160]:
  lam=4*.1*np.sin(np.pi*np.arange(1,4)/(2*n))**2*n*n;sem=coeff[0]+(coeff[1:]*np.exp(-lam*.1))@basis(n,3).T;errors.append(metrics(sem,field(coeff,n))['rms'])
 orders=np.log2(np.array(errors[:-1])/errors[1:]);assert np.all((orders>1.98)&(orders<2.02))
 assert np.max(abs(reference_fd(np.ones(32)) -1))<1e-13
 for n in [32,64,128]:np.testing.assert_allclose(project(field(coeff,n,T=0),3),coeff,rtol=0,atol=3e-16)
 invalid=0
 for kw in [{'kappa':-1},{'T':-1},{'n':8}]:
  try:field([1,0,0,0,0],**kw)
  except ValueError:invalid+=1
  else:raise AssertionError('Invalid operator input accepted')
 result={'model':'nondimensional sealed heat equation; analytic cosine benchmark, not cardiac','train_cases':len(train['ids']),'test_cases':len(test['ids']),'train_seed':1701,'test_seed':1702,'train_test_case_overlap':0,'input_modes':3,'kappa':.1,'output_time':.1,'spatial_errors':errors,'spatial_orders':orders.tolist(),'checks':{'analytic_semigroup':True,'mean_conservation':True,'dense_semidiscrete_reference':True,'coefficient_recovery_across_grids':True,'constant_fd_state':True,'invalid_cases_rejected':invalid},'runtime_seconds':time.perf_counter()-start}
 (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
