"""Original introductory branched neuronal cable experiment and verification."""
from pathlib import Path
import json,html,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.linalg import expm
from cable import geometry,laplacian,solve_tree,simulate,arrivals


def save(fig,out,name,title,desc):
    for ext in ('svg','pdf'):fig.savefig(out/f'{name}.{ext}',bbox_inches='tight')
    p=out/f'{name}.svg';s=p.read_text();k=s.index('>',s.index('<svg'))+1;p.write_text(s[:k]+f'<title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc>'+s[k:]);plt.close(fig)


def verify():
    rng=np.random.default_rng(20261114);worst=0.
    for n in [2,5,12,31]:
        for _ in range(5):
            p=np.r_[-1,[rng.integers(i)for i in range(1,n)]];k=np.r_[0.,rng.uniform(.1,2,n-1)];diag=rng.uniform(.2,2,n)+k;np.add.at(diag,p[1:],k[1:]);A=np.diag(diag)
            for i in range(1,n):A[i,p[i]]=A[p[i],i]=-k[i]
            rhs=rng.normal(size=n);worst=max(worst,float(np.max(abs(solve_tree(p,k,diag,rhs)-np.linalg.solve(A,rhs)))))
    assert worst<1e-12
    g=geometry();L=laplacian(g);assert np.max(abs(L.sum(axis=0)))<1e-15 and np.allclose(L,L.T)
    geometric_area=2*np.pi*np.dot(g['radius_cm'][1:],g['length_cm'][1:]);assert abs(g['area_cm2'].sum()-geometric_area)<10*np.finfo(float).eps*geometric_area  # independent summation order, relative roundoff bound
    # Isolate spatial error with exact time evolution of a passive sealed cable.
    errs=[]
    for n in [10,20,40,80]:
        g0=geometry(n,branched=False);x=g0['xy_cm'][:,0];L0=laplacian(g0);mass=g0['area_cm2'];T=.2
        initial=5*np.cos(np.pi*x/.3);A=-(L0/mass[:,None]+.3*np.eye(n+1));numerical=expm(T*A)@initial
        exact=initial*np.exp(-(.3+.0005/(2*.0354)*(np.pi/.3)**2)*T)
        errs.append(float(np.max(abs(numerical-exact))))
    orders=np.log2(np.array(errs[:-1])/errs[1:]);assert np.all(orders>1.98)
    # Isolate time error against the same discrete matrix exponential.
    g0=geometry(12,branched=False);x=g0['xy_cm'][:,0];initial=-59+5*np.cos(np.pi*x/.3);A=-(laplacian(g0)/g0['area_cm2'][:,None]+.3*np.eye(13));exact=-59+expm(.2*A)@(initial+59);time_errors=[]
    for h in [.02,.01,.005]:
        r=simulate(intervals=12,branched=False,active=False,amplitude=0,initial_voltage=initial,dt=h,end=.2)
        time_errors.append(float(np.max(abs(r['voltage_mV'][-1]-exact))))
    time_orders=np.log2(np.array(time_errors[:-1])/time_errors[1:]);assert np.all(time_orders>.98)
    quiet=simulate(end=.5,amplitude=0,intervals=12);assert np.max(abs(quiet['voltage_mV']-quiet['voltage_mV'][0]))<1e-9
    symmetric=simulate(intervals=12,daughter_ratio=1,dt=.01,end=7);g1=symmetric['geometry'];sym_error=float(np.max(abs(symmetric['voltage_mV'][:,g1['tips'][0]]-symmetric['voltage_mV'][:,g1['tips'][1]])));assert sym_error<1e-10
    invalid=0
    for call in [lambda:geometry(2),lambda:geometry(10,daughter_ratio=np.nan),lambda:simulate(dt=0),lambda:simulate(amplitude=-1),lambda:solve_tree([-1,1],[0,1],[2,2],[1,1])]:
        try:call()
        except ValueError:invalid+=1
        else:raise AssertionError('Invalid input accepted')
    return {'tree_dense_solve_max_error':worst,'passive_spatial_errors_mV':errs,'passive_spatial_orders':orders.tolist(),'passive_temporal_errors_mV':time_errors,'passive_temporal_orders':time_orders.tolist(),'symmetric_tip_gap_mV':sym_error,'invalid_cases_rejected':invalid}


def run(output_dir=None):
    start=time.perf_counter();out=Path(output_dir or Path(__file__).parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'legend.fontsize':22,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    r=simulate();g=r['geometry'];V=r['voltage_mV'];t=r['time_ms'];probes=[0,g['junction'],*g['tips']];labels=['Start','Junction','Upper tip','Lower tip'];styles=['-', '--',':','-.'];colors=['#264653','#d16628','#087e8b','#7660a9']
    fig,axs=plt.subplots(1,2,figsize=(13,5.8),gridspec_kw={'width_ratios':[1,1.35]})
    xy=g['xy_cm']*10
    for i in range(1,len(g['parent'])):
        j=g['parent'][i];axs[0].plot(xy[[j,i],0],xy[[j,i],1],color='#647789',lw=7*g['radius_cm'][i]/.0005,solid_capstyle='round')
    for p,label,c in zip(probes,labels,colors):
        axs[0].plot(*xy[p],'o',color=c,ms=9);offset=(0,20)if label!='Lower tip'else(0,-30);axs[0].annotate(label,xy[p],xytext=offset,textcoords='offset points',ha='center',color=c)
    axs[0].set(xlabel='Position (mm)',ylabel='Position (mm)',title='One shared junction',xlim=(-.65,5.8),ylim=(-2,2));axs[0].set_aspect('equal',adjustable='box');axs[0].set_xticks([0,2,4]);axs[0].set_yticks([-1,0,1])
    for p,label,ls,c in zip(probes,labels,styles,colors):axs[1].plot(t,V[:,p],label=label,ls=ls,color=c,lw=2.5)
    axs[1].axvspan(1,2,color='gray',alpha=.15);axs[1].set(xlabel='Time (ms)',ylabel='Voltage (mV)',title='Signals arrive at different times',xlim=(0,10),ylim=(-85,55));fig.legend(*axs[1].get_legend_handles_labels(),loc='lower center',ncol=4,frameon=False)
    fig.tight_layout(rect=(0,.14,1,1));save(fig,out,'branched-probes','A branched cable and four voltage probes','Synthetic neuronal cable: 3 mm trunk and two 2 mm daughters. Trunk and upper daughter radius 5 µm; lower daughter radius 3.5 µm. A total inward current of 0.006 µA acts at the start from 1 to 2 ms. Junction and distal probes cross zero later than the stimulated start; the thinner lower daughter arrives later in this experiment. Diagram coordinates do not affect physical path length.')
    fig,axs=plt.subplots(1,2,figsize=(12.5,5.8));snapshots=[2.5,3.5,4.5];lines=['-','--',':'];nj=g['junction'];nd=(len(g['parent'])-nj-1)//2
    for j,ax in enumerate(axs):
        path=np.r_[np.arange(nj+1),np.arange(nj+1+j*nd,nj+1+(j+1)*nd)];dist=np.r_[0,np.cumsum(g['length_cm'][path[1:]])]*10
        for when,ls in zip(snapshots,lines):
            ix=int(np.argmin(abs(t-when)));ax.plot(dist,V[ix,path],ls=ls,lw=2.5,label=f'{t[ix]:g} ms')
        ax.axvline(3,color='gray',lw=1);ax.set(xlabel='Distance from start (mm)',ylabel='Voltage (mV)',title=('Upper path: radius 5 µm'if j==0 else'Lower daughter: radius 3.5 µm'),ylim=(-85,45));ax.set_xticks([0,1,2,3,4,5])
    fig.legend(*axs[0].get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False);fig.tight_layout(rect=(0,.13,1,1));save(fig,out,'traveling-profiles','Spatial profiles along both paths','At 2.5, 3.5 and 4.5 ms, the high-voltage region has moved farther from the stimulated start. Distance is measured along the cable, with the shared junction at 3 mm. The lower daughter is narrower after the junction; the common trunk is identical in both panels. These are snapshots of one coupled calculation, not independent shifted copies.')
    checks=verify();fine=simulate(dt=.0025);finer=simulate(dt=.00125)
    tip_times=[arrivals(x['time_ms'],x['voltage_mV'][:,x['geometry']['tips']])for x in [r,fine,finer]];gaps=[max(abs(np.array(tip_times[i])-tip_times[i+1]))for i in range(2)];assert gaps[1]<gaps[0]
    assert abs(r['charge_uA_ms']-.006)<1e-13 and r['max_budget_error_uA_ms']<1e-14 and 0<=r['gate_range'][0]<=r['gate_range'][1]<=1
    result={'probe_labels':labels,'arrival_definition':'first upward crossing of 0 mV, linearly interpolated','probe_arrival_ms':arrivals(t,V[:,probes]),'probe_peak_mV':V[:,probes].max(axis=0).tolist(),'nodes':len(g['parent']),'membrane_area_cm2':float(g['area_cm2'].sum()),'delivered_charge_uA_ms':r['charge_uA_ms'],'max_step_budget_error_uA_ms':r['max_budget_error_uA_ms'],'gate_range':r['gate_range'],'tip_refinement_arrivals_ms':tip_times,'tip_refinement_gaps_ms':[float(x)for x in gaps],**checks,'runtime_seconds':time.perf_counter()-start}
    np.savez(out/'cable-trajectories.npz',time_ms=t,voltage_mV=V,parent=g['parent'],xy_cm=g['xy_cm'],area_cm2=g['area_cm2'])
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
