"""Original optional prescribed electrical-wave visualization.
A piecewise-linear ventricular-shaped voltage trace is delayed by x/speed.
No ionic currents, reaction-diffusion PDE, ECG, patient anatomy or diagnosis.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save(fig, out, name, title, description):
    fig.savefig(out/(name+".svg"), bbox_inches="tight")
    fig.savefig(out/(name+".pdf"), bbox_inches="tight")
    plt.close(fig)
    path=out/(name+".svg"); tree=ET.parse(path); node=tree.getroot()
    ns="{http://www.w3.org/2000/svg}"
    node.set("role","img");node.set("aria-labelledby","figure-title figure-description")
    for tag,ident,text in [("title","figure-title",title),("desc","figure-description",description)]:
        el=ET.Element(ns+tag,id=ident);el.text=text;node.insert(0,el)
    tree.write(path,encoding="utf-8",xml_declaration=True)


def setup(output_dir):
    out=Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent
    out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({"font.size":16,"axes.titlesize":16,"font.family":"DejaVu Sans","svg.fonttype":"none",
                         "axes.spines.top":False,"axes.spines.right":False})
    return out


def voltage(age):
    age=np.asarray(age,dtype=float)
    if not np.all(np.isfinite(age)):raise ValueError("time must be finite")
    return np.interp(age,[0.,2.,12.,160.,220.],[-85.,30.,15.,0.,-85.],left=-85.,right=-85.)


def arrival(position,speed=.4):
    x=np.asarray(position,dtype=float)
    if not np.all(np.isfinite(x)) or np.any(x<0) or not np.isfinite(speed) or speed<=0:
        raise ValueError("positions finite nonnegative; speed finite positive in mm/ms")
    return x/speed


def wave(position,time,speed=.4):
    return voltage(np.asarray(time,dtype=float)-arrival(position,speed))


def run(output_dir=None):
    out=setup(output_dir)
    time=np.linspace(-20,350,741);position=np.linspace(0,40,161)
    fig,axs=plt.subplots(1,2,figsize=(10.5,5.7))
    for x,style in [(0,"-"),(20,"--"),(40,":")]:axs[0].plot(time,wave(x,time),style,label=f"x = {x:g} mm",lw=2.2)
    axs[0].set(xlabel="Time (ms)",ylabel="Membrane voltage (mV)",title="Same shape, later arrival",ylim=(-95,40))
    field=wave(position[:,None],time[None,:])
    im=axs[1].pcolormesh(time,position,field,cmap="viridis",vmin=-85,vmax=30,shading="auto",rasterized=True)
    axs[1].plot(arrival(position),position,color="white",lw=2,label="Onset x/c")
    axs[1].set(xlabel="Time (ms)",ylabel="Distance along tissue (mm)",title="Space-time: c = 0.4 mm/ms")
    axs[1].legend(loc="lower right",fontsize=16)
    fig.colorbar(im,ax=axs[1],label="Membrane voltage (mV)")
    fig.legend(*axs[0].get_legend_handles_labels(),loc="lower center",bbox_to_anchor=(.5,.01),ncol=3,fontsize=16)
    fig.tight_layout(rect=(0,.12,1,1))
    save(fig,out,"trace-and-travel","Voltage traces and space-time propagation","A supplied ventricular-shaped piecewise-linear pulse is delayed by x divided by 0.4 mm/ms. Positions zero, twenty and forty mm begin at zero, fifty and one hundred ms. This demonstrates time delay, not ion-channel kinetics; the color field is membrane voltage, not an ECG or blood oxygenation.")
    from matplotlib.colors import Normalize
    fig=plt.figure(figsize=(10.5,6.1));cmap=plt.get_cmap("viridis");norm=Normalize(-85,30)
    xx=np.linspace(0,40,81);yy=np.linspace(0,30,31);zz=np.linspace(0,8,13)
    for i,speed in enumerate([.4,.2],1):
        ax=fig.add_subplot(1,2,i,projection="3d")
        X,Y=np.meshgrid(xx,yy);Z=np.full_like(X,8.)
        ax.plot_surface(X,Y,Z,facecolors=cmap(norm(wave(X,80,speed))),shade=False,rstride=1,cstride=1,linewidth=0)
        X,Z=np.meshgrid(xx,zz);Y=np.zeros_like(X)
        ax.plot_surface(X,Y,Z,facecolors=cmap(norm(wave(X,80,speed))),shade=False,rstride=1,cstride=1,linewidth=0)
        Y,Z=np.meshgrid(yy,zz);X=np.zeros_like(Y)
        ax.plot_surface(X,Y,Z,facecolors=cmap(norm(wave(X,80,speed))),shade=False,linewidth=0)
        # Color the visible far end: its voltage follows the same prescribed field.
        X=np.full_like(Y,40.)
        ax.plot_surface(X,Y,Z,facecolors=cmap(norm(wave(X,80,speed))),shade=False,linewidth=0)
        ax.set(xlabel="x (mm)",ylabel="y (mm)",zlabel="z (mm)",xlim=(0,40),ylim=(0,30),zlim=(0,8),title=f"c = {speed:g} mm/ms\nOnset ≈ {speed*80:g} mm")
        ax.set_title(ax.get_title(), fontsize=20, pad=0)
        ax.tick_params(labelsize=20)
        for label in (ax.xaxis.label, ax.yaxis.label, ax.zaxis.label, ax.title):
            label.set_fontsize(20)
        ax.set_box_aspect((40,30,12));ax.view_init(24,-62);ax.set_xticks([]);ax.set_yticks([]);ax.set_zticks([])
    fig.suptitle("40 × 30 × 8 mm slab at 80 ms",fontsize=20,y=1.04)
    cax=fig.add_axes([.25,.05,.5,.03]);colorbar=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation="horizontal",label="Membrane voltage (mV)")
    colorbar.ax.tick_params(labelsize=20)
    colorbar.ax.xaxis.label.set_fontsize(20)
    fig.subplots_adjust(top=.84,bottom=.28,left=.01,right=.99,wspace=.12)
    save(fig,out,"activation-slab","Three-dimensional slab views at two conduction speeds","Original 40 by 30 by 8 mm slab, not heart anatomy. A plane starts at x zero and moves uniformly in the positive x direction. At 80 ms its onset reaches 32 mm for speed 0.4 mm/ms and 16 mm for speed 0.2. Voltage is uniform across y and z by assumption. These geometric views do not solve a three-dimensional electrophysiology model.")
    assert np.array_equal(arrival([0,20,40]),[0,50,100])
    assert np.allclose(arrival(position,.2),2*arrival(position,.4))
    assert np.allclose(wave(20,time+50),wave(0,time))
    assert np.all(voltage([-100,300,1000])==-85)
    assert field.min()>=-85 and field.max()<=30
    assert np.allclose(wave(np.array([0,20,40]),arrival([0,20,40])+2),30)
    rejected=0
    for call in [lambda:arrival(2,0),lambda:arrival(-1),lambda:voltage(np.nan),lambda:arrival(2,np.inf)]:
        try:call()
        except ValueError:rejected+=1
        else:raise AssertionError("invalid input accepted")
    report={"model":"prescribed shape delayed by distance/speed; no ionic or tissue dynamics","units":{"distance":"mm","time":"ms","speed":"mm/ms","voltage":"mV"},"arrival_times_at_0_20_40_mm":[0,50,100],"front_at_80_ms_mm":{"speed_0.4":32,"speed_0.2":16},"checks":{"delay_matches_distance_over_speed":True,"half_speed_doubles_delay":True,"trace_translation":True,"rest_before_after":True,"voltage_bounds":True,"invalid_inputs_rejected":rejected},"limitations":["no spontaneous pacemaker","no refractoriness or reentry dynamics","no ion currents or calcium coupling","planar homogeneous propagation prescribed rather than solved","not ECG or anatomical ventricular model"]}
    (out/"results.json").write_text(json.dumps(report,indent=2)+"\n");return report

if __name__=="__main__":print(json.dumps(run(),indent=2))
