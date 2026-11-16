# Reused original 2026 teaching implementation from advanced m04 demo.py.
# This local copy supplies only compliance, ideal-valve hydraulics and parameters.
# The baseline driver does not execute a pressure filter or a feedback controller.
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

