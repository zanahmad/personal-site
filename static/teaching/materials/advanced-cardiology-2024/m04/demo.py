"""A six-compartment feedback model.

Methodological sources: Hoppensteadt & Peskin, ch.1; recovered original MATLAB
circulation source; Ahmad & Peskin public feedback paper. This is an illustrative
model, not a clinical model. The public
feedback paper has only TWO storage compartments; this code has SIX.

Run: python demo.py. Core requires NumPy; figures additionally need Matplotlib.
All times exposed to learners are seconds; hydraulic equations use minutes.
"""
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path
import json
import math
import numpy as np

NAMES = ('LV', 'systemic artery', 'systemic vein', 'RV', 'pulmonary artery', 'pulmonary vein')
# Four directed ideal valves, then two bidirectional tissue beds.
EDGES = ((5, 0), (0, 1), (2, 3), (3, 4), (1, 2), (4, 5))
VD = np.array([.027, .825, 0., .027, .0382, 0.])  # L, unstressed volumes
P_INITIAL = np.array([5., 80., 2., 2., 8., 5.])  # mmHg

@dataclass(frozen=True)
class Parameters:
    # The baseline uses Rs = 17.86; the reference in_circ.m uses Rs = 8.
    rs_rest: float = 17.86
    resistance_factor: float = .5
    rp: float = 1.79
    valve_resistance: float = .01
    f0: float = 80.0
    gain: float = 10.0  # nonnegative; opposite sign to historical c
    pressure_target: float = 90.0  # illustrative mmHg; not a fitted target
    target_factor: float = 1.0
    tau_filter_s: float = 3.0
    fmin: float = 30.0
    fmax: float = 240.0
    start_s: float = 30.0
    stop_s: float = 60.0
    duration_s: float = 90.0
    resistance_recovery_delay_s: float = 0.0
    target_recovery_delay_s: float = 0.0
    dt_s: float = .00046875  # 1600 steps per 80-bpm reference beat; coarse feedback is sensitive
    filter_method: str = 'euler'

    def validate(self):
        numeric = [v for v in self.__dict__.values() if not isinstance(v, str)]
        if not all(math.isfinite(v) for v in numeric):
            raise ValueError('Every numerical parameter must be finite.')
        positive = ('rs_rest','resistance_factor','rp','valve_resistance','f0','pressure_target',
                    'target_factor','tau_filter_s','fmin','fmax','duration_s','dt_s')
        if any(getattr(self,k)<=0 for k in positive):
            raise ValueError('Resistances, targets, rates, time constants and steps must be positive.')
        if self.gain<0 or not self.fmin<=self.f0<=self.fmax:
            raise ValueError('Require gain >= 0 and fmin <= f0 <= fmax.')
        if not 0<=self.start_s<self.stop_s<self.duration_s:
            raise ValueError('Require 0 <= exercise start < stop < duration.')
        if min(self.resistance_recovery_delay_s,self.target_recovery_delay_s)<0:
            raise ValueError('Recovery delays must be nonnegative.')
        if self.stop_s+max(self.resistance_recovery_delay_s,self.target_recovery_delay_s)>=self.duration_s:
            raise ValueError('Recovery changes must occur before the run ends.')
        if self.dt_s>self.tau_filter_s:
            raise ValueError('Use dt <= tau_filter for a non-overshooting Euler filter.')
        if self.filter_method not in ('euler','held-input'):
            raise ValueError('Choose euler or held-input filter.')
        if math.ceil(self.duration_s/self.dt_s)>2_000_000:
            raise ValueError('Requested run exceeds the 2,000,000-step CPU teaching limit.')


def compliance(phase):
    """Both ventricles use one phase in cycles; all compliances are L/mmHg."""
    theta=float(phase)%1.0
    if theta<.4:
        e=-math.expm1(-theta/.2)/-math.expm1(-.4/.2)
        lv=.0146*(.00003/.0146)**e
        rv=.0365*(.0002/.0365)**e
    else:
        e=-math.expm1(-(theta-.4)/.6)/-math.expm1(-.6/.6)
        lv=.00003*(.0146/.00003)**e
        rv=.0002*(.0365/.0002)**e
    return np.array([lv,.00175,1.75,rv,.00412,.08])


def schedule(t_s,p):
    rs=p.rs_rest*(p.resistance_factor if p.start_s<=t_s<p.stop_s+p.resistance_recovery_delay_s else 1.)
    target=p.pressure_target*(p.target_factor if p.start_s<=t_s<p.stop_s+p.target_recovery_delay_s else 1.)
    return rs,target


def edge_flows(pressure,rs,p):
    """Recompute from CURRENT resistance; never reuse cached output conductance."""
    pressure=np.asarray(pressure,dtype=float)
    diff=np.array([pressure[a]-pressure[b] for a,b in EDGES])
    q=diff/np.array([p.valve_resistance]*4+[rs,p.rp])
    q[:4]=np.maximum(q[:4],0.)
    return q


def pressure_step(old_p,old_c,new_c,h_min,rs,p,initial_valves=None):
    """Backward Euler with bounded valve iteration and exhaustive fallback.

    Returns pressures, consistent four-valve states, flows and residuals.
    The four ideal valves yield only 16 states. Tissue-bed flows may reverse.
    """
    old_p=np.asarray(old_p,dtype=float);old_c=np.asarray(old_c,dtype=float);new_c=np.asarray(new_c,dtype=float)
    if any(x.shape!=(6,) for x in (old_p,old_c,new_c)):
        raise ValueError('Pressure and compliance vectors must have six entries.')
    if not all(np.all(np.isfinite(x)) for x in (old_p,old_c,new_c)):
        raise ValueError('State values must be finite.')
    if min(old_c.min(),new_c.min(),h_min,rs,p.rp,p.valve_resistance)<=0 or old_p.min()<0:
        raise ValueError('Require nonnegative pressure and positive compliance, step and resistance.')
    conductance=1./np.array([p.valve_resistance]*4+[rs,p.rp])
    rhs=old_c*old_p
    def candidate(valves):
        active=np.r_[np.array(valves,dtype=float),[1.,1.]]*conductance
        A=np.diag(new_c.copy())
        for g,(i,j) in zip(active,EDGES):
            z=h_min*g
            A[i,i]+=z;A[j,j]+=z;A[i,j]-=z;A[j,i]-=z
        pressure=np.linalg.solve(A,rhs)
        diffs=np.array([pressure[i]-pressure[j] for i,j in EDGES[:4]])
        consistent=all(d>=-1e-10 if s else d<=1e-10 for d,s in zip(diffs,valves))
        return pressure,diffs,consistent
    valves=tuple(bool(x) for x in (initial_valves if initial_valves is not None else [False]*4))
    seen=set();answer=None;solves=0
    for _ in range(16):
        if valves in seen:break
        seen.add(valves);solves+=1
        pressure,diffs,ok=candidate(valves)
        if ok:answer=(pressure,valves);break
        valves=tuple(diffs>0)
    if answer is None:
        for valves in product((False,True),repeat=4):
            solves+=1;pressure,_,ok=candidate(valves)
            if ok:answer=(pressure,valves);break
    if answer is None:
        raise RuntimeError('No consistent valve state found; the time step was NOT accepted.')
    pressure,valves=answer
    if not np.all(np.isfinite(pressure)) or pressure.min()<-1e-10:
        raise RuntimeError('Invalid pressure after implicit solve.')
    q=edge_flows(pressure,rs,p)
    rate=np.zeros(6)
    for flow,(i,j) in zip(q,EDGES):rate[i]-=flow;rate[j]+=flow
    residual=(new_c*pressure-old_c*old_p)/h_min-rate
    scale=1+max(np.max(abs(rate)),np.max(abs((new_c*pressure-old_c*old_p)/h_min)))
    if np.max(abs(residual))>1e-8*scale:
        raise RuntimeError(f'Compartment balance failed: h_min={h_min:.17g}, residual={np.max(abs(residual)):.17g}, scale={scale:.17g}; the time step was NOT accepted.')
    return pressure,np.array(valves),q,residual,solves


def run_experiment(p=Parameters()):
    p.validate()
    # Construct each event interval from integer step indices. Repeated t += dt
    # can leave a roundoff-sized residual step that amplifies balance roundoff.
    events=sorted(set([0.,p.start_s,p.stop_s,p.stop_s+p.resistance_recovery_delay_s,
                       p.stop_s+p.target_recovery_delay_s,p.duration_s]))
    time_grid=[0.]
    time_tolerance=64*np.finfo(float).eps*max(1.,p.duration_s)
    for left,right in zip(events[:-1],events[1:]):
        count=int(math.floor((right-left)/p.dt_s))
        points=left+p.dt_s*np.arange(1,count+1,dtype=float)
        time_grid.extend(points[points<right-time_tolerance])
        time_grid.append(right)  # preserve the exact requested forcing time
    phase=0.;pressure=P_INITIAL.copy();c=compliance(phase);pf=p.pressure_target
    total_volume=float(np.sum(VD+c*pressure));valves=np.zeros(4,dtype=bool)
    rows=[];t=0.;max_residual=0.;max_drift=0.;max_solves=0
    def save(rate,rs,target,q,command):
        rows.append(np.r_[t,phase,pf,rate,rs,target,command,pressure,q])
    rs,target=schedule(t,p);save(p.f0,rs,target,edge_flows(pressure,rs,p),p.f0)
    for t_new in time_grid[1:]:
        h_s=t_new-t;h=h_s/60.
        rs,target=schedule(t,p)
        weight=h_s/p.tau_filter_s if p.filter_method=='euler' else -math.expm1(-h_s/p.tau_filter_s)
        pf_new=pf+weight*(pressure[1]-pf)
        command=p.f0*(1+p.gain*(target-pf_new)/target)
        rate=float(np.clip(command,p.fmin,p.fmax))
        phase_new=phase+h*rate
        c_new=compliance(phase_new)
        pressure,valves,q,residual,solves=pressure_step(pressure,c,c_new,h,rs,p,valves)
        phase=phase_new;c=c_new;pf=pf_new;t=float(t_new)
        max_residual=max(max_residual,float(abs(residual).max()))
        max_drift=max(max_drift,abs(float(np.sum(VD+c*pressure))-total_volume))
        max_solves=max(max_solves,solves)
        save(rate,rs,target,q,command)
    z=np.array(rows)
    return {'time_s':z[:,0],'phase':z[:,1],'filtered_pressure':z[:,2],'rate_bpm':z[:,3],
            'resistance':z[:,4],'target':z[:,5],'unbounded_command':z[:,6],
            'pressure':z[:,7:13],'flows':z[:,13:19],
            'diagnostics':{'initial_total_volume_L':total_volume,'max_volume_drift_L':max_drift,
               'max_balance_residual_L_min':max_residual,'max_linear_solves_per_step':max_solves,
               'filter':p.filter_method,'hemodynamic_method':'backward Euler with consistent ideal valves',
               'clock_method':'Euler using bounded rate from updated filtered pressure'}}


def summarize(result,start_s,stop_s):
    """Time-weighted trapezoidal means with interpolated window endpoints."""
    t=result['time_s'];inner=(t>start_s)&(t<stop_s)
    if not t[0]<=start_s<stop_s<=t[-1]:raise ValueError('Average window must be inside the run.')
    tx=np.r_[start_s,t[inner],stop_s]
    out={}
    for key,series in [('Psa_mmHg',result['pressure'][:,1]),('Qsystemic_L_min',result['flows'][:,4]),('heart_rate_bpm',result['rate_bpm'])]:
        y=np.r_[np.interp(start_s,t,series),series[inner],np.interp(stop_s,t,series)]
        out[key]=float(np.trapezoid(y,tx)/(stop_s-start_s))
    return out


def accessible_svg(path,title,description):
    import xml.etree.ElementTree as ET
    ET.register_namespace('','http://www.w3.org/2000/svg')
    tree=ET.parse(path);root=tree.getroot();root.set('role','img');root.set('aria-labelledby','figure-title figure-description')
    a=ET.Element('{http://www.w3.org/2000/svg}title',{'id':'figure-title'});a.text=title
    b=ET.Element('{http://www.w3.org/2000/svg}desc',{'id':'figure-description'});b.text=description
    root.insert(0,b);root.insert(0,a);tree.write(path,encoding='utf-8',xml_declaration=True)


def make_figures(results,destination):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch,Ellipse
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(8.3,4.3));ax.set(xlim=(-1.,7.),ylim=(-.8,3.4));ax.axis('off')
    xy=[(0,2.3),(3,2.3),(6,2.3),(6,0),(3,0),(0,0)]
    labels=['Left ventricle\nC varies with phase','Systemic arteries\nconstant C','Systemic veins\nconstant C',
            'Right ventricle\nC varies with phase','Pulmonary arteries\nconstant C','Pulmonary veins\nconstant C']
    for k,(pos,label) in enumerate(zip(xy,labels)):
        ax.add_patch(Ellipse(pos,1.55,.85,facecolor='#eef2f3',edgecolor='#293e4c',lw=1.3))
        ax.text(*pos,label,ha='center',va='center',fontsize=9)
    linklabels=['aortic valve','systemic resistance','tricuspid valve','pulmonic valve','pulmonary resistance','mitral valve']
    for k,label in enumerate(linklabels):
        a=np.array(xy[k]);b=np.array(xy[(k+1)%6]);d=b-a;d=d/np.linalg.norm(d)
        ax.add_patch(FancyArrowPatch(a+d*.8,b-d*.8,arrowstyle='-|>',mutation_scale=13,color='#293e4c',lw=1.4))
        mid=(a+b)/2
        ax.text(mid[0]+(.32 if k==2 else -.35 if k==5 else 0),mid[1]+(.26 if k<2 else -.3 if k in (3,4) else 0),label,ha='center',va='center',fontsize=8.5,rotation=90 if k in (2,5) else 0)
    ax.text(3,1.15,'One accumulated phase drives both ventricles.\nNo external reservoir: total blood volume stays fixed.',ha='center',va='center',fontsize=10)
    fig.tight_layout()
    for ext in ('svg','pdf'):fig.savefig(destination/f'circuit.{ext}',bbox_inches='tight')
    plt.close(fig)
    accessible_svg(destination/'circuit.svg','Six-compartment closed circulation','Six chambers form a directed loop with four ideal valves and systemic and pulmonary resistance beds. One cardiac phase drives both ventricular compliances.')
    fig,axes=plt.subplots(3,1,figsize=(8.3,7),sharex=True)
    styles={'fixed rate':('#273f52','-'),'pressure feedback':('#ad5a2b','--')}
    for label,result in results.items():
        color,ls=styles[label];t=result['time_s']
        axes[0].plot(t,result['filtered_pressure'],color=color,ls=ls,label=label,lw=1.4)
        # Display a centered 0.75-s boxcar average, only where the full window exists.
        uniform=np.arange(0,t[-1]+1e-9,.0075)
        q=np.interp(uniform,t,result['flows'][:,4]);n=101
        axes[1].plot(uniform[n//2:-(n//2)],np.convolve(q,np.ones(n)/n,mode='valid'),color=color,ls=ls,lw=1.4)
        axes[2].plot(t,result['rate_bpm'],color=color,ls=ls,lw=1.4)
    for ax in axes:
        ax.axvspan(30,60,color='#dae2e6',alpha=.5);ax.grid(alpha=.2)
    axes[0].set_ylabel('Filtered pressure\n(mmHg)');axes[1].set_ylabel('Systemic flow, 0.75-s mean\n(L/min)');axes[2].set_ylabel('Heart rate\n(beats/min)');axes[2].set_xlabel('Time (s)')
    axes[0].legend(frameon=False,ncol=2);axes[0].set_title('Illustrative six-compartment calculation; resistance halved from 30–60 s',fontsize=11)
    fig.tight_layout()
    for ext in ('svg','pdf'):fig.savefig(destination/f'feedback-response.{ext}',bbox_inches='tight')
    plt.close(fig)
    accessible_svg(destination/'feedback-response.svg','Fixed rate versus pressure feedback','Three panels show filtered arterial pressure in mmHg, centered 0.75second mean systemic flow in litres per minute, and bounded heart rate in beats per minute. Shading marks resistance reduction from 30 to 60 seconds. These are model calculations, not clinical data.')


def main():
    out=Path(__file__).parent
    fixed=run_experiment(Parameters(gain=0.))
    controlled=run_experiment(Parameters())
    results={'fixed rate':fixed,'pressure feedback':controlled}
    report={label:{'parameters':replace(Parameters(),gain=0. if label=='fixed rate' else 10.).__dict__,
             'late_exercise_51_to_60_s':summarize(r,51,60),'diagnostics':r['diagnostics']} for label,r in results.items()}
    (out/'demo-results.json').write_text(json.dumps(report,indent=2)+'\n')
    for label,r in results.items():
        np.savez_compressed(out/('fixed-rate.npz' if label=='fixed rate' else 'feedback.npz'),**{k:v for k,v in r.items() if k!='diagnostics'})
    for label,r in results.items():
        times=np.arange(0.,90.00001,.075)
        series=np.column_stack([r['phase'],r['filtered_pressure'],r['rate_bpm'],r['pressure'],r['flows']])
        sampled=np.column_stack([times]+[np.interp(times,r['time_s'],series[:,k]) for k in range(series.shape[1])])
        name='cross-language-fixed.csv' if label=='fixed rate' else 'cross-language-feedback.csv'
        np.savetxt(out/name,sampled,delimiter=',',header='time_s,phase,filtered_pressure,rate_bpm,P_LV,P_sa,P_sv,P_RV,P_pa,P_pv,Q_mi,Q_ao,Q_tr,Q_pu,Q_s,Q_p',comments='')
    make_figures(results,out)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
