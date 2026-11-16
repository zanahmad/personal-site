"""Original optional reservoir model. Synthetic parameters; no patient data.
Run python demo.py. Dependencies: NumPy and Matplotlib. No calculus required
for the core worksheet; this script evaluates a supplied exact response.
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


def reservoir(t, inflow=2., resistance=10., compliance=2., outlet=5., initial=5.):
    t=np.asarray(t,dtype=float)
    values=np.array([inflow,resistance,compliance,outlet,initial],dtype=float)
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(t)):
        raise ValueError("all inputs must be finite")
    if np.any(t<0) or inflow<0 or resistance<=0 or compliance<=0 or initial<outlet:
        raise ValueError("t and inflow nonnegative, R/C positive, initial at least outlet")
    steady=outlet+resistance*inflow
    pressure=steady+(initial-steady)*np.exp(-t/(resistance*compliance))
    flow=(pressure-outlet)/resistance
    stored_change=compliance*(pressure-initial)
    cumulative_out=inflow*t-stored_change
    return pressure,flow,stored_change,cumulative_out


def run(output_dir=None):
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse
    out=setup(output_dir)
    fig,axs=plt.subplots(1,3,figsize=(10.8,5.4))
    for ax in axs:ax.set_xlim(0,10);ax.set_ylim(0,8);ax.axis("off")
    axs[0].add_patch(FancyBboxPatch((3,2.3),4,3,boxstyle="round,pad=.2",facecolor="#dcebf1",edgecolor="#18384a",lw=2))
    axs[0].text(5,4.6,"One stored\nvolume",ha="center",fontsize=16)
    axs[0].text(5,3.1,"P(t), V(t)",ha="center",fontsize=16)
    for a,b,txt in [((.5,3.7),(2.8,3.7),"in"),((7.2,3.7),(9.5,3.7),"out")]:
        axs[0].add_patch(FancyArrowPatch(a,b,arrowstyle="->",mutation_scale=18,lw=2));axs[0].text((a[0]+b[0])/2,4.3,txt,ha="center")
    axs[0].set_title("0D: compartment\naverages")
    axs[0].text(5,1,"Storage and\nmean pressure",ha="center",fontsize=16)
    x=np.linspace(.5,9.5,180)
    axs[1].plot(x,4+.35*np.sin(x*.8),color="#087e8b",lw=3)
    axs[1].plot(x,3-.35*np.sin(x*.8),color="#087e8b",lw=3)
    for xi in [1.5,3.8,6.1,8.4]:axs[1].plot([xi,xi],[3-.35*np.sin(xi*.8),4+.35*np.sin(xi*.8)],color="#9ba8b0",lw=1)
    axs[1].annotate("",xy=(8,5.1),xytext=(2,5.1),arrowprops={"arrowstyle":"->"})
    axs[1].text(5,5.5,"distance x",ha="center")
    axs[1].set_title("1D: along\na vessel")
    axs[1].text(5,1,"Travel and\nreflections",ha="center",fontsize=16)
    axs[2].add_patch(Ellipse((5,4),7,3,angle=20,facecolor="#edf2f5",edgecolor="#18384a",lw=2))
    for xx,yy,dx,dy in [(2,3.5,1.3,.5),(3.5,3,1.2,.7),(5,3.8,1.5,.3),(6,4.7,.8,-.2)]:
        axs[2].arrow(xx,yy,dx,dy,head_width=.23,length_includes_head=True,color="#087e8b")
    axs[2].set_title("3D: local geometry\nand flow")
    axs[2].text(5,1,"Jets and\nwall stresses",ha="center",fontsize=16)
    fig.suptitle("Choose the detail needed by the question",fontsize=16)
    fig.tight_layout()
    save(fig,out,"model-scales","Three levels of blood-flow description","Original schematic: a 0D storage compartment, a 1D vessel with cross-sections, and a perspective sketch of a 3D flow region. These are representations, not computed flow solutions or patient anatomy.")
    t=np.linspace(0,100,401)
    fig,axs=plt.subplots(1,2,figsize=(10.5,5.6))
    drop=np.linspace(0,40,100)
    for r,style in [(10.,"-"),(20.,"--")]:axs[0].plot(drop,drop/r,style,label=f"R = {r:g} mmHg s/mL",lw=2)
    axs[0].set(xlabel="Pressure drop (mmHg)",ylabel="Outflow (mL/s)",title="Resistance and flow")
    axs[0].legend(fontsize=16)
    for c,style in [(1.,"-"),(2.,"--"),(4.,":")]:
        p,_,_,_=reservoir(t,compliance=c);axs[1].plot(t,p,style,label=f"C = {c:g} mL/mmHg",lw=2.2)
    axs[1].axhline(25,color="#6b7780",lw=1)
    axs[1].set(xlabel="Time (s)",ylabel="Reservoir pressure (mmHg)",title="Compliance and filling")
    axs[1].legend(fontsize=16)
    fig.tight_layout()
    save(fig,out,"pressure-storage","Resistance and compliant storage","Left: positive pressure drops divided by resistances 10 and 20 mmHg seconds per mL. Right: constant inflow 2 mL/s, resistance 10, initial and outlet pressure 5 mmHg; compliance 1, 2 or 4 mL/mmHg changes approach speed but every curve approaches 25 mmHg.")
    p,q,dv,qo=reservoir(t)
    assert np.allclose(dv,2*t-qo)
    assert np.all(np.diff(p)>=0) and p.min()>=5 and p.max()<25
    assert np.allclose(reservoir(t,inflow=0)[0],5)
    assert np.allclose(reservoir(t,initial=25)[0],25)
    assert np.allclose(reservoir(2*t,compliance=4)[0],p)
    assert abs(float(reservoir(20)[0])-(25-20/np.e))<1e-12
    rejected=0
    for kwargs in [{"resistance":0},{"compliance":-1},{"inflow":np.nan},{"initial":4}]:
        try:reservoir([0,1],**kwargs)
        except ValueError:rejected+=1
        else:raise AssertionError("invalid inputs accepted")
    report={"model":"linear passive compliant reservoir; constant external/outlet pressure","units":{"pressure":"mmHg","flow":"mL/s","volume":"mL","time":"s"},"steady_pressure":25,"time_constant_seconds":20,"pressure_at_20_s":float(reservoir(20)[0]),"checks":{"volume_budget":True,"no_input_equilibrium":True,"initial_equilibrium":True,"compliance_time_scaling":True,"invalid_inputs_rejected":rejected},"limitations":["no pulsatile heart input","no spatial gradients within compartment","no valves or feedback","linear compliance over assumed range"]}
    (out/"results.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__=="__main__":print(json.dumps(run(),indent=2))
