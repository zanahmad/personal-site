"""Proposed 2027 day 2: trajectory tensors, functions, branches and rotations."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def trajectories():
    times=np.array([0.,1.,2.,3.,4.]);positions=np.array([[[0,0],[1,0],[2,0],[3,0],[4,0]],[[0,0],[0,2],[0,4],[0,6],[0,8]],[[1,1],[2,2],[3,3],[6,3],[7,4]]],dtype=float)
    return times,positions


def velocities(times,positions):
    t=np.asarray(times,dtype=float);p=np.asarray(positions,dtype=float)
    if t.ndim!=1 or len(t)<2 or not np.all(np.isfinite(t)) or np.any(t[1:]<=t[:-1]):raise ValueError('Use strictly increasing finite times.')
    if p.ndim!=3 or p.shape[1]!=len(t) or p.shape[2]!=2 or p.shape[0]<1 or not np.all(np.isfinite(p)):
        raise ValueError('Positions must have shape (trials, times, 2) with finite values.')
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        displacement=np.diff(p,axis=1);dt=np.diff(t)
        result=displacement/dt[None,:,None]
    if not all(np.all(np.isfinite(a)) for a in (displacement,dt,result)):
        raise ValueError('Time differences, displacements or velocities exceed finite arithmetic range.')
    return result


def screen_speeds(speed,limit=2.):
    s=np.asarray(speed,dtype=float)
    if s.ndim!=2 or not s.size or not np.all(np.isfinite(s)) or np.any(s<0):raise ValueError('Use a finite nonnegative trial-by-interval speed array.')
    if not np.isfinite(limit) or limit<0:raise ValueError('Limit must be finite and nonnegative.')
    # This is a declared display rule, not a physical validity or safety criterion.
    return s>limit


def rotation(angle_degrees):
    if not np.isfinite(angle_degrees):raise ValueError('Angle must be finite.')
    theta=np.deg2rad(angle_degrees);c=np.cos(theta);s=np.sin(theta)
    return np.array([[c,-s],[s,c]])


def save(fig,out,stem,title,description):
    for ext in ('svg','pdf'):fig.savefig(out/(stem+'.'+ext),bbox_inches='tight')
    plt.close(fig);ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(out/(stem+'.svg'));r=tree.getroot();r.set('role','img');r.set('aria-labelledby',stem+'-title '+stem+'-desc')
    for tag,text in [('title',title),('desc',description)]:
        node=ET.Element('{'+ns+'}'+tag,id=stem+'-'+tag);node.text=text;r.insert(0,node)
    tree.write(out/(stem+'.svg'),encoding='utf-8',xml_declaration=True)


def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    times,p=trajectories();v=velocities(times,p);speed=np.linalg.norm(v,axis=2);flags=screen_speeds(speed)
    R=rotation(30);rotated=p@R.T;rotated_speed=np.linalg.norm(velocities(times,rotated),axis=2)
    assert p.shape==(3,5,2) and v.shape==(3,4,2) and speed.shape==(3,4)
    assert np.allclose(R.T@R,np.eye(2)) and np.allclose(rotated_speed,speed)
    assert flags.sum()==1 and not flags[1].any() # equality at two is NOT above two
    loop_speed=np.empty((3,4))
    for trial in range(3):
        for interval in range(4):
            difference=p[trial,interval+1]-p[trial,interval]
            loop_speed[trial,interval]=np.sqrt(np.sum(difference**2))/(times[interval+1]-times[interval])
    assert np.allclose(loop_speed,speed)
    assert np.allclose(np.linalg.norm(velocities(times,p+np.array([100.,-50.])),axis=2),speed)
    rejected=0
    for fn in [lambda:velocities([0,1,1,3,4],p),lambda:velocities(times,p[:,:,0]),lambda:screen_speeds(speed,-1),lambda:rotation(float('nan'))]:
        try:fn()
        except ValueError:rejected+=1
    assert rejected==4
    plt.rcParams.update({'font.size':18, 'axes.titlesize':18, 'legend.fontsize':18,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    colors=['#176c7b','#b46d27','#6d5892'];fig,axs=plt.subplots(1,2,figsize=(9,5.2),sharex=True,sharey=True)
    for ax,data,title in zip(axs,[p,rotated],['Original coordinates','Rotated 30 degrees']):
        for i,color in enumerate(colors):ax.plot(data[i,:,0],data[i,:,1],['o-','s--','^:'][i],color=color,label=f'Trial {i+1}')
        ax.set(xlabel='x position (mm)',ylabel='y position (mm)',title=title,aspect='equal');ax.grid(alpha=.2)
    fig.legend(*axs[0].get_legend_handles_labels(),loc='lower center',ncol=3,frameon=False,bbox_to_anchor=(.5,0))
    fig.tight_layout(rect=[0,.1,1,1]);save(fig,out,'trajectory-rotation','Trajectories before and after rotation','Three synthetic trials contain five positions each. A thirty-degree coordinate rotation changes components while preserving interval displacement lengths and magnitudes of average velocity. Equal axis scales preserve the geometric comparison; connecting lines do not establish between-sample motion.')
    fig,ax=plt.subplots(figsize=(8,4.4));im=ax.imshow(speed,cmap='viridis',vmin=0,vmax=3,aspect='auto')
    for i in range(3):
        for j in range(4):ax.text(j,i,f'{speed[i,j]:.2f}'+(' *' if flags[i,j] else ''),ha='center',va='center',color='white' if speed[i,j]<2 else '#111',fontsize=18)
    ax.set(xticks=range(4),xticklabels=['0–1','1–2','2–3','3–4'],yticks=range(3),yticklabels=['Trial 1','Trial 2','Trial 3'],xlabel='Observation interval (s)',title='Average velocity magnitude\n* means above 2 mm/s');fig.colorbar(im,ax=ax,label='Velocity magnitude (mm/s)');fig.tight_layout()
    save(fig,out,'speed-shape-map','A trial-by-interval speed array','The position tensor has shape three by five by two. Differencing time leaves three by four by two velocity components; taking the last-axis norm gives three by four magnitudes of average velocity. These are not average path speeds when unobserved motion curves or reverses. Only trial three, interval two to three seconds, exceeds two millimeters per second; equality does not flag trial two.')
    report={'shapes':{'positions':list(p.shape),'velocity':list(v.shape),'speed':list(speed.shape)},'average_velocity_magnitude_mm_s':speed.tolist(),'strictly_above_2_mm_s':flags.tolist(),'rotation_max_speed_difference':float(np.max(abs(speed-rotated_speed))),'checks':{'loop_vectorized_agreement':True,'rotation_preserves_speed':True,'translation_preserves_speed':True,'equality_not_flagged':True,'invalid_inputs_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
