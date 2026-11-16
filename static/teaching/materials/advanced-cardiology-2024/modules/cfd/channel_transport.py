"""Planar pressure-driven flow and conservative passive-tracer transport.
SI units throughout. Original instructional benchmark, not a patient model.
Run: python channel_transport.py --output results
"""
from pathlib import Path
import argparse,json
import numpy as np
from scipy.linalg import solve_banded

def velocity(n=40,H=.002,G=100.,mu=.004):
    if not isinstance(n,int) or n<4 or n>1000 or not np.isfinite([H,G,mu]).all() or H<=0 or mu<=0 or G<0:
        raise ValueError('Use 4–1000 intervals, H>0, mu>0, and G>=0, all finite.')
    y=np.linspace(0,H,n+1);h=H/n
    ab=np.zeros((3,n-1));ab[0,1:]=-1;ab[1]=2;ab[2,:-1]=-1
    u=np.r_[0.,solve_banded((1,1),ab,np.full(n-1,G*h*h/mu)),0.]
    exact=G*y*(H-y)/(2*mu)
    return y,u,exact

def transport(nx=80,ny=20,L=.02,H=.002,G=100.,mu=.004,D=2e-6,end=4.,pulse=.3,initial=0.,steady_inlet=False,store=True):
    if not all(isinstance(n,int) and 4<=n<=500 for n in (nx,ny)):raise ValueError('Use integer mesh counts 4–500.')
    if not np.isfinite([L,H,G,mu,D,end,pulse,initial]).all() or min(L,H,mu,end)<=0 or min(G,D,pulse)<0 or not 0<=initial<=1:
        raise ValueError('Finite positive geometry/time/viscosity, nonnegative forcing/diffusivity, and initial in [0,1] required.')
    dx=L/nx;dy=H/ny;x=(np.arange(nx)+.5)*dx;y=(np.arange(ny)+.5)*dy
    # The analytic channel velocity isolates the transport discretization error.
    u=G*y*(H-y)/(2*mu)
    rate=u.max()/dx+3*D/dx**2+2*D/dy**2
    step=min(.02,.9/rate) if rate>0 else .02
    if end/step>200000:raise ValueError('Requested run exceeds the teaching work limit.')
    cuts=sorted(set([0.,end]+([pulse] if 0<pulse<end else [])))
    times=[0.]
    for a,b in zip(cuts[:-1],cuts[1:]):times.extend(np.linspace(a,b,int(np.ceil((b-a)/step))+1)[1:])
    c=np.full((ny,nx),float(initial));vol=dx*dy
    initial_mass=float(c.sum()*vol);boundary_integral=0.;max_defect=0.;cmin=initial;cmax=initial
    saved=[c.copy()];saved_t=[0.];budgets=[[0.,initial_mass,0.,0.]]
    stride=max(1,int((len(times)-1)/100))
    for k,(a,b) in enumerate(zip(times[:-1],times[1:]),1):
        dt=b-a;cin=1. if steady_inlet or a<pulse else 0.
        fx=np.zeros((ny,nx+1));fy=np.zeros((ny+1,nx))
        fx[:,0]=u*cin-2*D*(c[:,0]-cin)/dx
        fx[:,1:-1]=u[:,None]*c[:,:-1]-D*(c[:,1:]-c[:,:-1])/dx
        fx[:,-1]=u*c[:,-1] # zero diffusive outlet flux
        fy[1:-1,:]=-D*(c[1:,:]-c[:-1,:])/dy # impermeable walls
        budget=dy*np.sum(fx[:,0]-fx[:,-1]);boundary_integral+=dt*budget
        c=c-dt*((fx[:,1:]-fx[:,:-1])/dx+(fy[1:,:]-fy[:-1,:])/dy)
        mass=float(c.sum()*vol);defect=mass-initial_mass-boundary_integral
        max_defect=max(max_defect,abs(defect));cmin=min(cmin,float(c.min()));cmax=max(cmax,float(c.max()))
        if not np.isfinite(c).all() or c.min()<-1e-11 or c.max()>1+1e-11:raise RuntimeError('Concentration left admissible range; no clipping is applied.')
        if k%stride==0 or k==len(times)-1:
            if store:saved.append(c.copy());saved_t.append(b)
            budgets.append([b,mass,boundary_integral,defect])
    return {'x':x,'y':y,'velocity':u,'concentration':c,'snapshots':np.array(saved),'snapshot_times':np.array(saved_t),'budgets':np.array(budgets),'dt_max':float(np.max(np.diff(times))),'max_mass_defect_m2':max_defect,'range':[cmin,cmax],'cell_area_m2':vol,'cfl_sum_bound':step*rate,'parameters':dict(nx=nx,ny=ny,L=L,H=H,G=G,mu=mu,D=D,end=end,pulse=pulse)}

def verify():
    y,u,e=velocity();assert np.max(abs(u-e))<1e-14
    _,u2,_=velocity(G=200.);np.testing.assert_allclose(u2,2*u,atol=1e-14)
    _,uz,_=velocity(G=0.);assert np.max(abs(uz))==0
    fine=transport(nx=40,ny=12,end=.8,store=False)
    assert fine['max_mass_defect_m2']<1e-16 and fine['range'][0]>=-1e-12 and fine['range'][1]<=1+1e-12
    constant=transport(nx=20,ny=8,end=.2,initial=1.,steady_inlet=True,store=False)
    np.testing.assert_allclose(constant['concentration'],1.,atol=1e-14)
    rest=transport(nx=20,ny=8,G=0.,D=0.,end=.2,store=False)
    assert np.max(abs(rest['concentration']))==0
    no_diff=transport(nx=40,ny=8,D=0.,end=.8,store=False);assert no_diff['max_mass_defect_m2']<1e-16
    # Refinement compares the same physical problem; this is sensitivity, not a claimed order.
    meshes=[(20,8),(40,16),(80,32)]
    refinement=[float(transport(nx=a,ny=b,end=1.,store=False)['concentration'].sum()*.02/a*.002/b) for a,b in meshes]
    return {'quadratic_velocity_exact_at_nodes':True,'forcing_linearity':True,'zero_forcing':True,'constant_transport_state':True,'zero_transport_state':True,'boundary_budget_conservation':True,'positivity_without_clipping':True,'advective_limit':True,'mass_defect_m2':fine['max_mass_defect_m2'],'refinement_meshes':meshes,'mass_at_1s_m2':refinement}

def main(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':16,'axes.spines.top':False,'axes.spines.right':False})
    r=transport();checks=verify();np.savez_compressed(out/'transport.npz',**{k:v for k,v in r.items() if isinstance(v,np.ndarray)})
    y,u,e=velocity();np.savetxt(out/'velocity.csv',np.c_[y,u,e],delimiter=',',header='y_m,u_fd_m_s,u_exact_m_s',comments='')
    np.savetxt(out/'mass-budget.csv',r['budgets'],delimiter=',',header='time_s,mass_per_width_m2,integrated_net_inflow_m2,budget_defect_m2',comments='')
    fig,ax=plt.subplots(figsize=(8,4.6));ax.plot(u*1000,y*1000,'o',ms=4,label='Difference equation');ax.plot(e*1000,y*1000,'-',label='Exact quadratic');ax.set(xlabel='Axial speed (mm/s)',ylabel='Distance from wall (mm)');ax.legend();fig.tight_layout();fig.savefig(out/'velocity.pdf');plt.close(fig)
    for t in [.2,1.,2.,4.]:
        i=int(np.argmin(abs(r['snapshot_times']-t)));fig,ax=plt.subplots(figsize=(10,3.8))
        im=ax.imshow(r['snapshots'][i],origin='lower',extent=[0,20,0,2],aspect=3,cmap='viridis',vmin=0,vmax=1)
        ax.set(xlabel='Axial position (mm)',ylabel='Gap position (mm)',title=f"Passive tracer, t={r['snapshot_times'][i]:.2f} s")
        fig.colorbar(im,ax=ax,label='Normalized concentration');fig.tight_layout();fig.savefig(out/f'tracer-{t:g}.pdf');plt.close(fig)
    b=r['budgets'];fig,ax=plt.subplots(figsize=(9,4.5));ax.plot(b[:,0],b[:,1]*1e6,label='Stored tracer per width');ax.plot(b[:,0],b[:,2]*1e6,'--',label='Integrated net boundary flux');ax.set(xlabel='Time (s)',ylabel='Normalized tracer area (mm²)');ax.legend();fig.tight_layout();fig.savefig(out/'budget.pdf');plt.close(fig)
    summary={'parameters':r['parameters'],'units':'SI; concentration normalized by the inlet pulse level','dt_max_s':r['dt_max'],'range':r['range'],'max_mass_defect_m2':r['max_mass_defect_m2'],'checks':checks}
    (out/'verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='results');a=p.parse_args();main(a.output)
