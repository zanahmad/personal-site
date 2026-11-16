"""Original reduced two-storage implicit valve step. This closed reduction is not
Ahmad/Peskin's public two-storage model with external reservoirs.
"""
from pathlib import Path
import json,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def implicit_step(old_pressure,old_compliance,new_compliance,h_min,resistance,initial_open=False):
    p0=np.asarray(old_pressure,float);c0=np.asarray(old_compliance,float);c1=np.asarray(new_compliance,float)
    if any(a.shape!=(2,) for a in (p0,c0,c1)):raise ValueError('Use two entries per state.')
    if not all(np.isfinite(a).all() for a in (p0,c0,c1)) or not np.isfinite([h_min,resistance]).all():raise ValueError('Inputs must be finite.')
    if np.min(p0)<0 or min(np.min(c0),np.min(c1),h_min,resistance)<=0:raise ValueError('Use nonnegative pressure and positive compliance, step and resistance.')
    old_amount=c0*p0;state=bool(initial_open);trace=[]
    for _ in range(3):
        try:
            with np.errstate(over='raise',invalid='raise',divide='raise'):
                z=h_min/resistance if state else 0.;matrix=np.diag(c1)+z*np.array([[1.,-1.],[-1.,1.]])
                pressure=np.linalg.solve(matrix,old_amount)
        except (FloatingPointError,np.linalg.LinAlgError) as e:raise RuntimeError('Implicit pressure solve failed.') from e
        if not np.isfinite(pressure).all():raise RuntimeError('Nonfinite pressure solution.')
        difference=pressure[0]-pressure[1];consistent=(difference>=-1e-12) if state else (difference<=1e-12)
        trace.append({'assumed_open':state,'pressure_mmHg':pressure.tolist(),'consistent':bool(consistent)})
        if consistent:
            q=max(difference,0.)/resistance;new_amount=c1*pressure;residual=(new_amount-old_amount)/h_min-np.array([-q,q])
            if np.max(abs(residual))>1e-9*(1+abs(q)):raise RuntimeError('Valve and compartment balances disagree.')
            return {'pressure_mmHg':pressure,'flow_L_min':q,'volume_L':new_amount,'trace':trace,'residual_L_min':residual,'open':state}
        state=not state
    raise RuntimeError('No consistent valve state; step rejected.')


def reduction(h_min=.02):
    return implicit_step([12.,4.],[.02,.03],[.01,.04],h_min,2.,False)


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).parent);out.mkdir(exist_ok=True,parents=True);b=reduction()
    plt.rcParams.update({'font.size':18,'axes.titlesize':18,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(10.5,5),constrained_layout=True)
    labels=['Old state','Closed guess','Consistent open'];states=np.array([[12.,4.],* [row['pressure_mmHg'] for row in b['trace']]])
    for j,name in enumerate(['Upstream','Downstream']):axs[0].plot(np.arange(3),states[:,j],'o-',label=name)
    axs[0].set(xticks=np.arange(3),xticklabels=labels,ylabel='Pressure (mmHg)',title='A guessed valve state\nmust be checked');axs[0].tick_params(axis='x',labelrotation=18);axs[0].legend(loc='center',bbox_to_anchor=(.5,.30))
    volumes=np.array([[.24,.12],[.24,.12],b['volume_L']]);axs[1].bar(labels,volumes[:,0],label='Upstream',color='#087e8b');axs[1].bar(labels,volumes[:,1],bottom=volumes[:,0],label='Downstream',color='#b16a20');axs[1].set(ylabel='Stored stressed volume\n(L)',title='Conservation alone\ncannot choose the valve');axs[1].tick_params(axis='x',labelrotation=18);axs[1].set_ylim(0,.53);axs[1].legend(loc='upper center',ncol=1,fontsize=18)
    save(fig,out,'valve-trace','A complete pressure and valve consistency trace','Old pressures12 and4mmHg become a rejected closed candidate24 and3 after compliance changes. The consistent open candidate gives14.6667 and5.3333. Both candidates conserve0.36L, so conservation alone cannot select the valve state.')
    # Constant-compliance open-valve relaxation has an independent exact difference equation.
    c=np.array([.01,.04]);initial=np.array([20.,5.]);resistance=2.;end=.08;exact_eq=np.dot(c,initial)/sum(c);decay=(1/c[0]+1/c[1])/resistance
    fig,ax=plt.subplots(figsize=(7.8,4.8));fine=np.linspace(0,end,301);exact=exact_eq+(initial[0]-exact_eq)*np.exp(-decay*fine);ax.plot(fine*60,exact,color='#18384a',lw=2.3,label='Exact upstream pressure')
    errors=[]
    for h in [.02,.01,.005]:
        n=int(round(end/h));p=initial.copy();trajectory=[p[0]]
        for _ in range(n):p=implicit_step(p,c,c,h,resistance,True)['pressure_mmHg'];trajectory.append(p[0])
        errors.append(float(abs(p[0]-exact[-1])));ax.plot(np.arange(n+1)*h*60,trajectory,'o--',ms=3,label=f'Backward Euler h={h*60:g} s')
    ax.set(xlabel='Time (s)',ylabel='Upstream pressure (mmHg)',title='An implicit conservative update\nstill has time error');ax.legend(fontsize=18);ax.grid(alpha=.15)
    save(fig,out,'implicit-refinement','Refinement toward an independently derived relaxation solution','The two compartments have constant compliances0.01 and0.04L/mmHg, an open valve resistance2 and initial pressures20 and5. Their pressure difference decays exponentially. Three backward-Euler steps approach the exact upstream pressure.')
    np.testing.assert_allclose(b['pressure_mmHg'],[44/3,16/3],atol=1e-12,rtol=0);assert abs(b['flow_L_min']-14/3)<1e-12
    assert abs(b['volume_L'].sum()-.36)<1e-12 and len(b['trace'])==2
    # Wrong initial guesses converge to the same physical answer.
    other=implicit_step([12,4],[.02,.03],[.01,.04],.02,2,True);np.testing.assert_allclose(other['pressure_mmHg'],b['pressure_mmHg'],atol=1e-12,rtol=0)
    blocked=implicit_step([3,10],c,c,.01,2,True);assert blocked['flow_L_min']==0;np.testing.assert_array_equal(blocked['pressure_mmHg'],[3,10])
    equal=implicit_step([7,7],c,c,.01,2,False);np.testing.assert_allclose(equal['pressure_mmHg'],[7,7],atol=1e-12)
    assert errors[0]>errors[1]>errors[2]>0
    invalid=0
    for h in [0,-1,float('nan')]:
        try:implicit_step(initial,c,c,h,2)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid time accepted')
    result={'trace':b['trace'],'final_pressure_mmHg':b['pressure_mmHg'].tolist(),'flow_L_min':b['flow_L_min'],'total_volume_L':float(b['volume_L'].sum()),'max_balance_residual_L_min':float(np.max(abs(b['residual_L_min']))),'exact_relaxation_rate_per_min':decay,'upstream_final_errors_mmHg':errors,'checks':{'wrong_initial_guess_same_solution':True,'reverse_pressure_closes_valve':True,'equal_pressure_zero_flow':True,'refinement_errors_decrease':True,'invalid_cases_rejected':invalid}}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
