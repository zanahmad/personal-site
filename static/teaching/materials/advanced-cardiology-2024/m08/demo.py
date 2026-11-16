"""Original synthetic atrial-inspired kinematic verification fixture.
Prescribed streamfunction in a widening 2D chamber: no momentum equation,
patient anatomy, wall motion, physiological calibration or clinical prediction.
SI units. q is flow per out-of-plane width (m^2/s); alpha alters internal flow
without altering port flow. Mesh derivatives and flux budgets are verified.
"""
from pathlib import Path
import html,json,time,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator, NullFormatter, FuncFormatter


def field(n=32,q=2e-4,alpha=12.,L=.06,H0=.01,bulge=1.5,width=.02):
    if isinstance(n,bool) or not isinstance(n,(int,np.integer)) or not 8<=n<=512:raise ValueError('n must be an integer from8 to512.')
    if not np.isfinite([q,alpha,L,H0,bulge,width]).all() or min(q,L,H0,width)<=0 or not 0<=bulge<=5 or not abs(alpha)<=40:raise ValueError('Finite positive dimensions/flow, bulge0–5 and |alpha|<=40 required.')
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            x=np.linspace(0,L,n+1);eta=np.linspace(0,1,n+1);X,E=np.meshgrid(x,eta,indexing='ij')
            H=H0*(1+bulge*np.sin(np.pi*X/L)**2);Hp=H0*bulge*np.pi/L*np.sin(2*np.pi*X/L);Y=E*H
            f=3*E**2-2*E**3;fp=6*E*(1-E);g=E**2*(1-E)**2;gp=2*E*(1-E)*(1-2*E)
            s=np.sin(np.pi*X/L)**2;sp=np.pi/L*np.sin(2*np.pi*X/L)
            psi=q*(f+alpha*s*g);pe=q*(fp+alpha*s*gp);px=q*alpha*sp*g
            u=pe/H;v=-px+E*Hp*pe/H
            dx=L/n;de=1/n
            dpx,dpe=np.gradient(psi,dx,de,edge_order=2)
            un=dpe/H;vn=-dpx+E*Hp*dpe/H
            if not all(np.isfinite(z).all() for z in [H,Hp,psi,u,v,un,vn]):raise ValueError('Field exceeded finite numerical range.')
            # Each edge flux is a difference of the same corner streamfunction.
            right=psi[1:,1:]-psi[1:,:-1];left=psi[:-1,1:]-psi[:-1,:-1]
            top=-(psi[1:,1:]-psi[:-1,1:]);bottom=-(psi[1:,:-1]-psi[:-1,:-1])
            cell_net=right-left+top-bottom
            # Integrate analytic velocity samples; derivative reconstruction is tested separately.
            section_flux=np.trapezoid(u,Y,axis=1)
            analytic_volume=width*H0*L*(1+bulge/2)
            if not np.isfinite(analytic_volume) or analytic_volume<=0 or not np.isfinite(q*width) or q*width<=0:raise ValueError('Volume or flow is outside numerical range.')
            interior=(slice(1,-1),slice(1,-1));error=np.sqrt(np.mean((un[interior]-u[interior])**2+(vn[interior]-v[interior])**2))
            if not np.isfinite(error) or not np.isfinite(analytic_volume/(q*width)):raise ValueError('Derived metrics are outside numerical range.')
            return {'X':X,'Y':Y,'psi':psi,'u':u,'v':v,'un':un,'vn':vn,'rms_velocity_error':float(error),'max_cell_flux_residual_m2_s':float(np.max(abs(cell_net))),'section_flux':section_flux,'exact_port_flux_mL_s':q*width*1e6,'volume_mL':analytic_volume*1e6,'volume_over_flow_s':analytic_volume/(q*width),'max_speed_m_s':float(np.max(np.hypot(u,v))),'quadrature_port_flux_mL_s':float(section_flux[0]*width*1e6)}
    except (FloatingPointError,OverflowError,ZeroDivisionError) as e:raise ValueError('Chamber inputs exceed numerical range.') from e


def velocity_diagnostics(X,Y,u,v,width=.02):
    """Reusable audit for imported sampled velocity on y=eta*H(x), x increasing.
    Arrays share shape(nx,ny), with walls at eta=0 and1 and SI units.
    Reports velocity-derived divergence and oriented boundary flux, not a
    momentum residual. No pressure, viscosity or body force is inferred.
    """
    X,Y,u,v=[np.asarray(z,dtype=float) for z in (X,Y,u,v)]
    if X.ndim!=2 or min(X.shape)<5 or any(z.shape!=X.shape or not np.isfinite(z).all() for z in (X,Y,u,v)):raise ValueError('Matching finite 2D arrays with at least5 nodes per axis required.')
    if not np.isfinite(width) or width<=0:raise ValueError('Positive finite width required.')
    x=X[:,0];H=Y[:,-1];eta=np.linspace(0,1,X.shape[1])
    if np.min(np.diff(x))<=0 or np.min(H)<=0 or not np.allclose(X,x[:,None],rtol=1e-12,atol=1e-14) or not np.allclose(Y,H[:,None]*eta,rtol=1e-12,atol=1e-14):raise ValueError('Expected increasing x and a uniform eta grid mapped by y=eta*H(x).')
    try:
        with np.errstate(over='raise',invalid='raise',divide='raise'):
            Hp=np.gradient(H,x,edge_order=2)
            ux,ue=np.gradient(u,x,eta,edge_order=2);_,ve=np.gradient(v,x,eta,edge_order=2)
            divergence=ux-eta[None,:]*Hp[:,None]/H[:,None]*ue+ve/H[:,None]
            inlet=float(np.trapezoid(u[0],Y[0]));outlet=float(np.trapezoid(u[-1],Y[-1]));top=float(np.trapezoid(v[:,-1]-u[:,-1]*Hp,x));bottom=float(-np.trapezoid(v[:,0],x))
            net=(outlet-inlet+top+bottom)*width*1e6
            rms_div=float(np.sqrt(np.mean(divergence[1:-1,1:-1]**2)))
            if not np.isfinite([rms_div,net,inlet*width*1e6,outlet*width*1e6,(top+bottom)*width*1e6]).all():raise ValueError('Nonfinite imported-field diagnostic.')
            return {'divergence_rms_per_s':float(np.sqrt(np.mean(divergence[1:-1,1:-1]**2))),'net_outward_boundary_flow_mL_s':net,'inlet_flow_mL_s':inlet*width*1e6,'outlet_flow_mL_s':outlet*width*1e6,'wall_outward_flow_mL_s':(top+bottom)*width*1e6,'momentum_residual':'not assessed; pressure, viscous stress, time derivative and forcing are not supplied'}
    except (FloatingPointError,OverflowError,ZeroDivisionError) as e:raise ValueError('Imported-field diagnostic exceeds numerical range.') from e


def save(fig,out,stem,title,description):
    description=re.sub(r'(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])', ' ', description)
    for ext in ('svg','pdf'):fig.savefig(out/f'{stem}.{ext}',bbox_inches='tight')
    p=out/f'{stem}.svg';s=p.read_text();j=s.index('>',s.index('<svg'))+1;p.write_text(s[:j]+f'<title>{html.escape(title)}</title><desc>{html.escape(description)}</desc>'+s[j:]);plt.close(fig)


def run(output_dir=None):
    start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':24,'axes.titlesize':24,'legend.fontsize':24,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    cases=[field(n=64,alpha=0),field(n=64,alpha=24)];maxspeed=max(r['max_speed_m_s'] for r in cases)
    fig,axs=plt.subplots(1,2,figsize=(13.5,5.4),constrained_layout=True)
    for ax,r,label in zip(axs,cases,['A: through-flow\nα = 0','B: circulation\nα = 24']):
        pc=ax.pcolormesh(r['X']*1000,r['Y']*1000,np.hypot(r['u'],r['v'])*1000,cmap='viridis',vmin=0,vmax=maxspeed*1000,shading='gouraud',rasterized=True)
        ax.contour(r['X']*1000,r['Y']*1000,r['psi'],levels=12,colors='white',linewidths=.8,alpha=.65)
        ix=(slice(2,-1,6),slice(2,-1,6));ax.quiver(r['X'][ix]*1000,r['Y'][ix]*1000,r['u'][ix],r['v'][ix],angles='xy',scale_units='xy',scale=.003,color='#e9e9e9',width=.003)
        ax.plot(r['X'][:,0]*1000,r['Y'][:,0]*1000,color='#182e3c',lw=2);ax.plot(r['X'][:,-1]*1000,r['Y'][:,-1]*1000,color='#182e3c',lw=2)
        ax.set(xlabel='Axial position (mm)',ylabel='Height (mm)',title=label,aspect='equal',xlim=(0,60),ylim=(-1,27))
    fig.colorbar(pc,ax=axs,label='Prescribed speed (mm/s)',shrink=.8)
    save(fig,out,'synthetic-chamber','Two synthetic fields with identical port flow','A fixed widening chamber is60mm long,10–25mm high and20mm deep. Both prescribed fields have4mL/s port flow and21mL volume. Alpha changes internal circulation while preserving no-slip side walls and port profiles. Contours are streamfunction levels, arrows indicate velocity. These are kinematic fixtures, not solutions of atrial momentum equations.')
    ns=[16,32,64,128];rows=[field(n=n) for n in ns];errors=[r['rms_velocity_error'] for r in rows];orders=np.log2(np.array(errors[:-1])/errors[1:])
    flow_factors=np.array([.8,1.,1.2]);boundary=[field(q=2e-4*f) for f in flow_factors]
    fig,axs=plt.subplots(1,2,figsize=(11.5,5.8),constrained_layout=True)
    axs[0].loglog(ns,errors,'o-',lw=2.5,color='#007e83');axs[0].set(xlabel='Intervals per coordinate',ylabel='RMS velocity error (m/s)',title='Derivative refinement');axs[0].set_xticks(ns,[str(n) for n in ns]);axs[0].xaxis.set_minor_locator(NullLocator());axs[0].grid(which='both',alpha=.15)
    axs[1].plot(flow_factors,[r['volume_over_flow_s'] for r in boundary],'o-',lw=2.5,color='#a55216');axs[1].set(xlabel='Inlet-flow multiplier',ylabel='Volume / flow (s)',title='Input sensitivity');axs[1].grid(alpha=.15)
    axs[0].yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:.0e}'.replace('e-0','e-')));axs[0].yaxis.set_minor_formatter(NullFormatter())
    axs[1].set_xticks([.8,1.,1.2])
    save(fig,out,'chamber-verification','Numerical refinement and prescribed-input sensitivity','Left: second-order finite differences reconstruct the known velocity from the analytic streamfunction on16–128interval grids. Right: changing imposed flow by±20percent changes volume/flow inversely. Volume/flow is a bulk turnover scale, not a particle residence-time distribution or a clinical risk measure.')
    assert np.all((orders>1.8)&(orders<2.2))
    assert max(r['max_cell_flux_residual_m2_s'] for r in rows)<1e-18
    for r in cases:
        assert abs(r['exact_port_flux_mL_s']-4)<1e-12 and abs(r['volume_mL']-21)<1e-12
        assert np.max(abs(r['u'][:,[0,-1]]))<1e-14 and np.max(abs(r['v'][:,[0,-1]]))<1e-14
    assert np.min(cases[1]['u'])<0 # explicit recirculation/reverse-flow diagnostic
    np.testing.assert_allclose([r['volume_over_flow_s'] for r in boundary],5.25/flow_factors,rtol=1e-14)
    np.testing.assert_allclose(field(q=4e-4)['u'],2*field()['u'],atol=1e-14,rtol=0)
    # Independent analytic quadrature error for parabolic port profile.
    for n,r in zip(ns,rows):assert abs(r['quadrature_port_flux_mL_s']/4-(1-1/n**2))<1e-13
    diagnostic=velocity_diagnostics(rows[2]['X'],rows[2]['Y'],rows[2]['u'],rows[2]['v'])
    assert abs(diagnostic['net_outward_boundary_flow_mL_s'])<1e-12
    bad=rows[2];corrupt=velocity_diagnostics(bad['X'],bad['Y'],bad['u'],bad['v']+.001*bad['Y']/bad['Y'][:,-1,None])
    assert abs(corrupt['net_outward_boundary_flow_mL_s']-1.2)<1e-12
    invalid=0
    for kw in [{'n':3},{'q':0},{'alpha':float('nan')},{'bulge':-1},{'width':-1},{'H0':1e308}]:
        try:field(**kw)
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid case accepted')
    result={'model':'prescribed kinematic verification fixture; no momentum solve','n_values':ns,'velocity_rms_errors_m_s':errors,'observed_orders':orders.tolist(),'max_cell_flux_residual_m2_s':max(r['max_cell_flux_residual_m2_s'] for r in rows),'exact_port_flow_mL_s':4.,'volume_mL':21.,'volume_over_flow_s':5.25,'boundary_factors':flow_factors.tolist(),'boundary_turnover_scales_s':[r['volume_over_flow_s'] for r in boundary],'importable_velocity_diagnostics':diagnostic,'deliberate_leak_detected_mL_s':corrupt['net_outward_boundary_flow_mL_s'],'two_fields_max_speeds_m_s':[r['max_speed_m_s'] for r in cases],'checks':{'same_port_flow_different_interior':True,'no_slip_side_walls':True,'prescribed_input_linear_velocity_response':True,'parabolic_port_quadrature_error':True,'invalid_cases_rejected':invalid},'runtime_seconds':time.perf_counter()-start}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
