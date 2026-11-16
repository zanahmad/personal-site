"""Original steady-flow network: synthetic pressures and linear resistances.
The five links are open resistors, not one-way valves. Signed flow follows the
stored reference arrows. Python/NumPy/Matplotlib only; no external data.
"""
from pathlib import Path
import json, html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

EDGES=(('source','A'),('A','sink'),('source','B'),('B','sink'),('A','B'))
DEFAULT_R=np.array([20.,10.,10.,20.,20.])


def solve_network(source=96.,sink=6.,resistances=None):
    r=np.asarray(DEFAULT_R if resistances is None else resistances,dtype=float)
    if r.shape!=(5,) or not np.isfinite(r).all() or np.any(r<=0):
        raise ValueError('Provide five finite positive resistances in mmHg min/L.')
    if not np.isfinite([source,sink]).all():raise ValueError('Boundary pressures must be finite.')
    try:
        with np.errstate(over='raise',divide='raise',invalid='raise'):
            boundary={'source':float(source),'sink':float(sink)};unknown={'A':0,'B':1}
            matrix=np.zeros((2,2));rhs=np.zeros(2)
            for (u,v),rr in zip(EDGES,r):
                g=1/rr
                for here,there in ((u,v),(v,u)):
                    if here in unknown:
                        i=unknown[here];matrix[i,i]+=g
                        if there in unknown:matrix[i,unknown[there]]-=g
                        else:rhs[i]+=g*boundary[there]
            internal=np.linalg.solve(matrix,rhs)
            pressures={**boundary,**{name:float(internal[i]) for name,i in unknown.items()}}
            q=np.array([(pressures[u]-pressures[v])/rr for (u,v),rr in zip(EDGES,r)])
            net_out={node:0. for node in pressures}
            for (u,v),flow in zip(EDGES,q):net_out[u]+=flow;net_out[v]-=flow
            if not np.isfinite(matrix).all() or not np.isfinite(rhs).all() or not np.isfinite(internal).all() or not np.isfinite(q).all():
                raise ValueError('The specified network exceeds finite numerical range.')
            return {'pressure_mmHg':pressures,'flow_L_min':q,'resistance_mmHg_min_L':r,'net_out_L_min':net_out,'matrix':matrix,'rhs':rhs}
    except (FloatingPointError,np.linalg.LinAlgError) as exc:
        raise ValueError('The specified network cannot be solved within finite numerical range.') from exc


def save(fig,out,stem,title,description):
    fig.savefig(out/(stem+'.svg'),bbox_inches='tight');fig.savefig(out/(stem+'.pdf'),bbox_inches='tight')
    p=out/(stem+'.svg');s=p.read_text();i=s.index('>',s.index('<svg'))+1
    p.write_text(s[:i]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'+s[i:]);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).resolve().parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':12,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    b=solve_network();p=b['pressure_mmHg'];q=b['flow_L_min']
    fig,ax=plt.subplots(figsize=(8.5,4.6));ax.set(xlim=(-1.5,7.5),ylim=(-1.1,4.8));ax.axis('off')
    pos={'source':(0,2),'A':(3,4),'B':(3,0),'sink':(6,2)}
    for (u,v),r in zip(EDGES,DEFAULT_R):
        a=np.array(pos[u]);z=np.array(pos[v]);delta=z-a;direction=delta/np.linalg.norm(delta)
        ax.annotate('',z-.42*direction,a+.42*direction,arrowprops={'arrowstyle':'->','lw':2,'color':'#4d7180'})
        midpoint=(a+z)/2
        offset=np.array([.65,0]) if (u,v)==('A','B') else np.array([0,.35 if midpoint[1]>2 else -.35])
        ax.text(*(midpoint+offset),f'R = {r:g}',ha='center',va='center',bbox={'fc':'white','ec':'none','pad':2})
    for node,(x,y) in pos.items():
        ax.scatter([x],[y],s=1000,color='#d9eeee',edgecolor='#18384a',zorder=3)
        ax.text(x,y,node,ha='center',va='center',zorder=4,fontsize=11)
        if node in ('source','sink'):ax.text(x,y-1.0,f'{p[node]:g} mmHg',ha='center')
    ax.text(3,-.9,'Reference arrows; all R in mmHg min/L',ha='center',fontsize=11)
    save(fig,out,'network','Five resistors and two unknown pressures','The source pressure is96mmHg and sink pressure6mmHg. Unknown nodes A and B are connected by a bridge resistor. Arrows define positive-flow references; they do not impose one-way flow. Five positive resistance values are shown.')
    fig,axs=plt.subplots(1,2,figsize=(9.4,4.7),gridspec_kw={'width_ratios':[1,1.35]},constrained_layout=True)
    order=['source','A','B','sink'];axs[0].bar(order,[p[n] for n in order],color=['#839eae','#087e8b','#087e8b','#839eae'])
    axs[0].set(ylabel='Pressure (mmHg)',ylim=(0,110),title='Solved pressures')
    for i,n in enumerate(order):axs[0].text(i,p[n]+3,f'{p[n]:g}',ha='center',fontsize=11)
    labels=[u+' → '+v for u,v in EDGES];colors=['#087e8b' if f>=0 else '#b16a20' for f in q]
    axs[1].barh(labels,q,color=colors);axs[1].invert_yaxis();axs[1].axvline(0,color='#555',lw=1)
    axs[1].set(xlabel='Signed flow (L/min)',xlim=(-1.9,4.7),title='Bridge flow opposes its arrow')
    for i,v in enumerate(q):axs[1].text(v+(.12 if v>=0 else -.12),i,f'{v:g}',ha='left' if v>=0 else 'right',va='center',fontsize=11)
    save(fig,out,'pressures-and-flows','Conserved flow can oppose a reference arrow','Solved pressures are96,42,60,6mmHg at source,A,B,sink. The A-to-B reference flow is minus0.9L/min, meaning0.9L/min actually moves from B to A. Total source flow and sink flow are both6.3L/min.')
    assert np.allclose([p['A'],p['B']],[42,60],atol=1e-12)
    assert np.allclose(q,[2.7,3.6,3.6,2.7,-.9],atol=1e-12)
    residual=max(abs(b['net_out_L_min'][k]) for k in ('A','B'));assert residual<1e-12
    assert abs(sum(b['net_out_L_min'].values()))<1e-12
    equal=solve_network(source=6,sink=6);assert np.allclose(equal['flow_L_min'],0,atol=1e-12)
    shifted=solve_network(source=108,sink=18);assert np.allclose(shifted['flow_L_min'],q,atol=1e-12)
    doubled=solve_network(resistances=DEFAULT_R*2);assert np.allclose(doubled['flow_L_min'],q/2,atol=1e-12)
    assert all(np.isclose(doubled['pressure_mmHg'][k],p[k]) for k in p)
    dissipation=float(np.sum(q*q*DEFAULT_R));boundary_work=(p['source']-p['sink'])*b['net_out_L_min']['source']
    assert np.isclose(dissipation,boundary_work,rtol=0,atol=1e-10)
    rejected=0
    for kwargs in [{'source':float('nan')},{'resistances':[20,10,10,20,0]},{'resistances':[20,10,10,20,-1]},{'resistances':[20,10]},{'resistances':[20,10,10,20,float('inf')]},{'resistances':[1e-320]*5}]:
        try:solve_network(**kwargs)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid input accepted')
    result={'model':'original synthetic steady linear-resistance network, not a specific patient or anatomical circuit','pressure_mmHg':p,'reference_edges':EDGES,'flow_L_min':q.tolist(),'total_source_flow_L_min':b['net_out_L_min']['source'],'checks':{'maximum_internal_balance_residual_L_min':residual,'equal_boundary_zero_flow':True,'pressure_reference_shift_invariant':True,'uniform_resistance_scaling':True,'pressure_work_equals_dissipation':True,'dissipation_mmHg_L_min':dissipation,'invalid_cases_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
