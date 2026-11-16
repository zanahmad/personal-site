"""Reusable original neuronal Hodgkin–Huxley membrane component.

Units: voltage mV, time ms, specific capacitance uF/cm², conductance mS/cm²,
current density uA/cm². Ionic current is positive outward; stimulus positive
inward. Rate convention and constants follow section2/Table1 of Zan Ahmad's
current8-page Action Potential Propagation in Branched Neuronal Cables report.
This is a neuronal model, not a cardiac-cell calibration.

rates(V) accepts scalar or node-array voltage and returns alpha,beta with gate
axis first, ordered m,h,n. gate_step supports broadcasting and never clips.
conductances(gates) returns Na,K,leak with channel axis first. ionic_current
accepts the matching voltage scalar/vector. rest() returns scalar[V,m,h,n].
simulate() is a single-cell original first-order split exponential integrator.
Spatial coupling must be separately derived, integrated and verified.
"""
import numpy as np
from scipy.optimize import brentq

C=1.;GMAX=np.array([120.,36.,.3]);EREV=np.array([45.,-82.,-59.])


def vtrap(z):
    """z/(1-exp(-z)), including its continuous value1 at zero."""
    z=np.asarray(z,float)
    if not np.isfinite(z).all() or np.any(abs(z)>100):raise ValueError('Finite rate arguments with |z|<=100 required.')
    out=np.empty_like(z);small=abs(z)<1e-5
    out[small]=1+z[small]/2+z[small]**2/12-z[small]**4/720
    out[~small]=z[~small]/(-np.expm1(-z[~small]))
    return out


def rates(V):
    V=np.asarray(V,float)
    if not np.isfinite(V).all() or np.any((V< -500)|(V>500)):raise ValueError('Voltage outside the finite teaching range [-500,500]mV.')
    a=np.array([vtrap((V+45)/10),.07*np.exp(-(V+70)/20),.1*vtrap((V+60)/10)])
    b=np.array([4*np.exp(-(V+70)/18),1/(1+np.exp(-(V+40)/10)),.125*np.exp(-(V+70)/80)])
    return a,b


def gate_step(s,alpha,beta,dt):
    s,alpha,beta=np.broadcast_arrays(np.asarray(s,float),np.asarray(alpha,float),np.asarray(beta,float))
    if not all(np.isfinite(z).all() for z in (s,alpha,beta)) or np.any((s<0)|(s>1)) or np.any(alpha<0) or np.any(beta<0) or not np.isfinite(dt) or dt<=0:raise ValueError('Finite gates in[0,1], nonnegative rates and a positive finite step required.')
    total=alpha+beta
    if not np.isfinite(total).all():raise ValueError('Gate rate sum overflows.')
    equilibrium=np.divide(alpha,total,out=s.copy(),where=total>0)
    # Convex combination, avoiding subtraction of nearly equal exponentials.
    weight=-np.expm1(-total*dt)
    new=(1-weight)*s+weight*equilibrium
    if not np.isfinite(new).all() or np.any((new<0)|(new>1)):raise RuntimeError('Gate admissibility failure; no clipping applied.')
    return new


def conductances(gates):
    """Return Na,K,leak conductances; gate axis is first, optional node axes follow."""
    gates=np.asarray(gates,float)
    if gates.ndim==0 or gates.shape[0]!=3 or not np.isfinite(gates).all() or np.any((gates<0)|(gates>1)):raise ValueError('Three finite gate fractions in[0,1] required.')
    m,h,n=gates
    return np.stack([120*m**3*h,36*n**4,np.full_like(m,.3)])


def ionic_current(V,gates):
    """Outward-positive current density; scalar or node vector V."""
    g=conductances(gates);reversal=EREV.reshape((3,)+(1,)*(g.ndim-1))
    current=np.sum(g*(np.asarray(V,float)-reversal),axis=0)
    return float(current) if current.ndim==0 else current


def rest():
    def equilibrium_current(V):
        a,b=rates(V);return ionic_current(V,a/(a+b))
    V=brentq(equilibrium_current,-80,-60,xtol=1e-13);a,b=rates(V)
    return np.r_[V,a/(a+b)]


def rhs(t,state,current=0.):
    V=state[0];s=state[1:];a,b=rates(V)
    return np.r_[(current-ionic_current(V,s))/C,a*(1-s)-b*s]


def timeline(end,dt,events=()):
    if not np.isfinite([end,dt]).all() or end<=0 or dt<=0 or end/dt>200000:raise ValueError('Positive finite time and step with at most200000 nominal intervals required.')
    cuts=sorted({0.,float(end),*[float(x) for x in events if 0<x<end]});pieces=[]
    for a,b in zip(cuts[:-1],cuts[1:]):pieces.extend(np.linspace(a,b,int(np.ceil((b-a)/dt))+1)[1:])
    return np.r_[0.,pieces]


def simulate(dt=.005,end=20.,amplitude=10.,on=1.,duration=1.,initial=None):
    if not np.isfinite([amplitude,on,duration]).all() or not 0<=amplitude<=50 or on<0 or duration<=0:raise ValueError('Use stimulus0–50uA/cm², nonnegative onset and positive duration.')
    state=rest() if initial is None else np.asarray(initial,float).copy()
    if state.shape!=(4,) or not np.isfinite(state).all() or np.any((state[1:]<0)|(state[1:]>1)):raise ValueError('Use finite[V,m,h,n] with gates in[0,1].')
    rates(state[0]);times=timeline(end,dt,[on,on+duration]);history=[state.copy()];charge=0.
    for a,b in zip(times[:-1],times[1:]):
        h=b-a;current=amplitude if on<=a<on+duration else 0.;alpha,beta=rates(state[0]);gates=gate_step(state[1:],alpha,beta,h)
        g=conductances(gates);total=g.sum();target=(np.dot(g,EREV)+current)/total
        V=(1-(-np.expm1(-total*h/C)))*state[0]+(-np.expm1(-total*h/C))*target
        state=np.r_[V,gates];history.append(state);charge+=current*h
    history=np.array(history)
    if not np.isfinite(history).all():raise RuntimeError('Nonfinite membrane trajectory.')
    return {'time':times,'state':history,'charge_uA_ms_cm2':charge,'peak_mV':float(history[:,0].max()),'gate_min':float(history[:,1:].min()),'gate_max':float(history[:,1:].max())}

