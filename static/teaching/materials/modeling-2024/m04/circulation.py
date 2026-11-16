"""Fixed-rate six-compartment driver.
No controller or pressure filter runs in this baseline.
"""
import math
import numpy as np
from hydraulic_core import Parameters, compliance, pressure_step, edge_flows, VD, P_INITIAL

def baseline(duration_s=15.,dt_s=.001875,rate_bpm=80.,rs=17.86):
    values=np.array([duration_s,dt_s,rate_bpm,rs],float)
    if not np.isfinite(values).all() or np.any(values<=0):raise ValueError('Use finite positive duration, step, rate and resistance.')
    if duration_s/dt_s>250000:raise ValueError('Baseline workshop limit:250000 steps.')
    p=Parameters(f0=rate_bpm,rs_rest=rs);p.validate()
    n=math.ceil(duration_s/dt_s);times=np.minimum(np.arange(n+1)*dt_s,duration_s)
    c=compliance(0);pressure=P_INITIAL.copy();valves=np.zeros(4,bool);pressures=[pressure.copy()];volumes=[VD+c*pressure];flows=[edge_flows(pressure,rs,p)];max_residual=0.;max_solves=0
    for old,new in zip(times[:-1],times[1:]):
        cn=compliance(rate_bpm*new/60.)
        pressure,valves,q,residual,solves=pressure_step(pressure,c,cn,(new-old)/60.,rs,p,valves)
        c=cn;pressures.append(pressure.copy());volumes.append(VD+c*pressure);flows.append(q)
        max_residual=max(max_residual,float(np.max(abs(residual))));max_solves=max(max_solves,solves)
    pressures=np.array(pressures);volumes=np.array(volumes);flows=np.array(flows);total=volumes.sum(axis=1)
    return {'time_s':times,'phase':rate_bpm*times/60.,'pressure_mmHg':pressures,'volume_L':volumes,'flow_L_min':flows,'total_volume_L':total,'diagnostics':{'max_total_drift_L':float(np.max(abs(total-total[0]))),'max_balance_residual_L_min':max_residual,'max_solves':max_solves,'initial_total_L':float(total[0]),'rate_bpm':rate_bpm,'rs_mmHg_min_L':rs,'dt_s':dt_s}}

