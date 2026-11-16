"""Original conservative tree cable teaching solver, in cm, ms, mV and microamperes.

This gate-first, backward-Euler voltage method differs from the AP report's
staggered Crank-Nicolson method. Geometry has one shared node per junction.
"""
import numpy as np
from membrane import rates,gate_step,conductances,rest,timeline,EREV,C


def geometry(intervals=30,daughter_ratio=.7,branched=True):
    if isinstance(intervals,bool) or int(intervals)!=intervals or not 3<=intervals<=300:
        raise ValueError('Use integer trunk intervals from 3 to 300.')
    if not np.isfinite(daughter_ratio) or not .25<=daughter_ratio<=2:raise ValueError('Daughter radius ratio must be finite and between .25 and 2.')
    n=int(intervals);parent=[-1];xy=[[0.,0.]];edge_r=[0.];edge_l=[0.];trunk_radius=.0005
    def segment(start,end,count,r):
        origin=np.asarray(xy[start]);previous=start
        for k in range(1,count+1):
            position=origin+(np.asarray(end)-origin)*k/count
            parent.append(previous);xy.append(position.tolist());edge_r.append(r);edge_l.append(float(np.linalg.norm(np.asarray(end)-origin)/count));previous=len(parent)-1
        return previous
    joint=segment(0,[.3,0],n,trunk_radius)
    tips=[joint]
    if branched:
        nd=max(2,round(2*n/3));dx=.2*np.cos(np.pi/6);dy=.2*np.sin(np.pi/6)
        tips=[segment(joint,[.3+dx,dy],nd,trunk_radius),segment(joint,[.3+dx,-dy],nd,trunk_radius*daughter_ratio)]
    parent=np.array(parent,int);xy=np.array(xy);rad=np.array(edge_r);length=np.array(edge_l)
    area=np.zeros(len(parent));half=np.pi*rad[1:]*length[1:]
    np.add.at(area,parent[1:],half);area[1:]+=half
    K=np.zeros(len(parent));K[1:]=np.pi*rad[1:]**2/(.0354*length[1:])
    return {'parent':parent,'xy_cm':xy,'radius_cm':rad,'length_cm':length,'area_cm2':area,'axial_mS':K,'junction':joint,'tips':tips}


def laplacian(g):
    p=g['parent'];K=g['axial_mS'];L=np.zeros((len(p),len(p)))
    for i in range(1,len(p)):
        j=p[i];L[i,i]+=K[i];L[j,j]+=K[i];L[i,j]-=K[i];L[j,i]-=K[i]
    return L


def solve_tree(parent,K,diagonal,rhs):
    """Solve a symmetric tree matrix, with parent index lower than child index."""
    p=np.asarray(parent);k=np.asarray(K,float);d=np.asarray(diagonal,float).copy();b=np.asarray(rhs,float).copy();n=len(p)
    if p.ndim!=1 or n<1 or p[0]!=-1 or np.any(p[1:]<0) or np.any(p[1:]>=np.arange(1,n)) or not np.issubdtype(p.dtype,np.integer):raise ValueError('Use a rooted parent-before-child integer tree.')
    if any(x.shape!=(n,)for x in [k,d,b]) or not all(np.isfinite(x).all()for x in [k,d,b]) or np.any(k<0):raise ValueError('Tree arrays must have matching finite entries and nonnegative conductances.')
    for i in range(n-1,0,-1):
        if d[i]<=0:raise ValueError('Tree solve requires positive elimination pivots.')
        j=p[i];d[j]-=k[i]*k[i]/d[i];b[j]+=k[i]*b[i]/d[i]
    if d[0]<=0:raise ValueError('Tree solve requires positive elimination pivots.')
    x=np.empty(n);x[0]=b[0]/d[0]
    for i in range(1,n):x[i]=(b[i]+k[i]*x[p[i]])/d[i]
    return x


def simulate(intervals=30,daughter_ratio=.7,dt=.005,end=12.,amplitude=.006,on=1.,duration=1.,active=True,branched=True,initial_voltage=None):
    if not np.isfinite([amplitude,on,duration]).all() or not 0<=amplitude<=.02 or on<0 or duration<=0:raise ValueError('Use finite current from 0 to .02 µA, nonnegative onset and positive duration.')
    g=geometry(intervals,daughter_ratio,branched);n=len(g['parent']);area=g['area_cm2'];K=g['axial_mS'];p=g['parent'];M=C*area
    eq=rest();V=np.full(n,eq[0] if active else EREV[2]) if initial_voltage is None else np.broadcast_to(initial_voltage,(n,)).astype(float).copy()
    if not np.isfinite(V).all() or np.any((V< -150)|(V>100)):raise ValueError('Initial voltages must be finite and in [-150,100] mV.')
    gates=np.broadcast_to(eq[1:,None],(3,n)).copy();times=timeline(end,dt,[on,on+duration]);vs=[V.copy()];gate_min=float(gates.min());gate_max=float(gates.max());charge=0.;budget_error=0.
    axial_diag=K.copy();np.add.at(axial_diag,p[1:],K[1:])
    for t0,t1 in zip(times[:-1],times[1:]):
        h=t1-t0;I=np.zeros(n);I[0]=amplitude if on<=t0<on+duration else 0.
        if active:
            a,b=rates(V);gates=gate_step(gates,a,b,h);gs=conductances(gates)
            gate_min=min(gate_min,float(gates.min()));gate_max=max(gate_max,float(gates.max()))
        else:gs=np.vstack([np.zeros(n),np.zeros(n),np.full(n,.3)])
        total_g=gs.sum(axis=0);drive=EREV@gs
        diag=M/h+axial_diag+area*total_g;rhs=M/h*V+area*drive+I
        updated=solve_tree(p,K,diag,rhs)
        residual=np.dot(M,updated-V)+h*np.dot(area,total_g*updated-drive)-h*I.sum()
        budget_error=max(budget_error,abs(float(residual)));charge+=float(I.sum()*h)
        V=updated;vs.append(V.copy())
    vs=np.array(vs)
    if not np.isfinite(vs).all():raise RuntimeError('Nonfinite cable solution.')
    return {'geometry':g,'time_ms':times,'voltage_mV':vs,'charge_uA_ms':charge,'max_budget_error_uA_ms':budget_error,'gate_range':[gate_min,gate_max]}


def arrivals(t,V,threshold=0.):
    out=[]
    for x in V.T:
        k=np.flatnonzero((x[:-1]<threshold)&(x[1:]>=threshold))
        out.append(float(t[k[0]]+(threshold-x[k[0]])*(t[k[0]+1]-t[k[0]])/(x[k[0]+1]-x[k[0]])) if len(k) else None)
    return out
