"""Original optional pump-cycle and muscle cartoons. No clinical estimates.
The rectangular PV loop and normalized force-speed curve are prescribed
teaching models, not fitted cardiac mechanics or simulated ion channels.
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


def cycle(edv=120.,esv=50.,low_pressure=10.,high_pressure=100.,heart_rate=75.):
    vals=np.array([edv,esv,low_pressure,high_pressure,heart_rate],dtype=float)
    if not np.all(np.isfinite(vals)) or not (0<=esv<=edv and edv>0 and 0<=low_pressure<=high_pressure and heart_rate>=0):
        raise ValueError("finite nonnegative values, EDV positive, ESV<=EDV and low<=high required")
    v=np.array([esv,edv,edv,esv,esv]);p=np.array([low_pressure,low_pressure,high_pressure,high_pressure,low_pressure])
    sv=edv-esv; work=(high_pressure-low_pressure)*sv
    return v,p,{"stroke_volume_mL":sv,"ejection_fraction":sv/edv,"cardiac_output_L_min":heart_rate*sv/1000,"net_work_mmHg_mL":work,"net_work_J":work*133.322e-6}


def shortening_speed(load_fraction):
    f=np.asarray(load_fraction,dtype=float)
    if not np.all(np.isfinite(f)) or np.any((f<0)|(f>1)):
        raise ValueError("load fraction must be finite and between 0 and 1")
    return (1-f)/(1+3*f)


def run(output_dir=None):
    out=setup(output_dir)
    fig,axs=plt.subplots(1,2,figsize=(10.5,5.7))
    ax=axs[0];ax.axis("off");ax.set_xlim(0,10);ax.set_ylim(0,7)
    for left,right,y,label in [(1,9,5.3,"Less overlap"),(2,8,2.3,"More overlap")]:
        ax.plot([left,left],[y-1,y+1],color="#18384a",lw=3);ax.plot([right,right],[y-1,y+1],color="#18384a",lw=3)
        ax.plot([left,left+2.5],[y+.6,y+.6],color="#087e8b",lw=4);ax.plot([right-2.5,right],[y+.6,y+.6],color="#087e8b",lw=4)
        ax.plot([3.5,6.5],[y,y],color="#a54e2c",lw=6)
        for xx in [3.8,4.5,5.5,6.2]:ax.plot([xx,xx+.2],[y,y+.5],color="#a54e2c",lw=2)
        ax.text(5,y-1.2,label,ha="center",fontsize=16)
    ax.text(5,6.8,"Actin slides past myosin",ha="center",fontsize=16)
    ax.annotate("",xy=(4,3.75),xytext=(2,3.75),arrowprops={"arrowstyle":"->","lw":2})
    ax.annotate("",xy=(6,3.75),xytext=(8,3.75),arrowprops={"arrowstyle":"->","lw":2})
    ax.set_title("Original sarcomere schematic")
    f=np.linspace(0,1,151);axs[1].plot(f,shortening_speed(f),color="#087e8b",lw=2.5)
    axs[1].scatter([0,.5,1],shortening_speed([0,.5,1]),color="#a54e2c",zorder=3)
    axs[1].set(xlabel="Load / isometric load\n(dimensionless)",ylabel="Speed / unloaded speed\n(dimensionless)",title="Fixed activation: illustration",xlim=(0,1),ylim=(0,1.05))
    fig.tight_layout()
    save(fig,out,"muscle-and-load","Sliding filaments and a normalized load-speed cartoon","Original schematic shows unchanged actin and myosin filament lengths with increased overlap. A separate prescribed curve u=(1-f)/(1+3f) decreases from one at zero load to zero at unit load; it illustrates a fixed-activation muscle trend and is not a fitted cardiac contraction model.")
    v,p,summary=cycle();fig,ax=plt.subplots(figsize=(9.4,6.3))
    ax.fill(v,p,color="#dcebf1",alpha=.8);ax.plot(v,p,color="#18384a",lw=2.5)
    colors=["#087e8b","#a54e2c","#087e8b","#a54e2c"]
    labels=["1 Filling\nInlet open","2 Pressure rises: both closed","3 Ejection: outlet open","4 Pressure falls: both closed"]
    for i in range(4):
        va,pa=v[i],p[i];vb,pb=v[i+1],p[i+1]
        ax.annotate("",xy=(va+.62*(vb-va),pa+.62*(pb-pa)),xytext=(va+.38*(vb-va),pa+.38*(pb-pa)),arrowprops={"arrowstyle":"->","lw":3,"color":colors[i]})
    ax.text(85,15,labels[0],ha="center",va="bottom",fontsize=18)
    ax.text(122,55,"2 Both\nclosed",ha="left",va="center",fontsize=18)
    ax.text(85,104,labels[2],ha="center",va="bottom",fontsize=18)
    ax.text(48,55,"4 Both\nclosed",ha="right",va="center",fontsize=18)
    ax.text(85,57,"Net loop area\n= 70 mL × 90 mmHg",ha="center",fontsize=18)
    ax.set(xlim=(26,149),ylim=(0,124),xlabel="Ventricular volume (mL)",ylabel="Ventricular pressure (mmHg)",title="Prescribed rectangular pump cycle")
    ax.tick_params(labelsize=18)
    for label in (ax.xaxis.label, ax.yaxis.label, ax.title):
        label.set_fontsize(18)
    fig.tight_layout();save(fig,out,"pump-cycle","Four phases of an idealized pressure-volume loop","Counterclockwise loop: fill from 50 to 120 mL at 10 mmHg; raise pressure at fixed volume to 100; eject to 50 mL at 100; relax at fixed volume to 10. The shaded net work area is 6300 mmHg mL, about 0.840 J. Valve labels are idealizations; real loops are curved.")
    assert np.allclose(v[0],v[-1]) and np.allclose(p[0],p[-1])
    # Independent polygon-area computation; the area has units pressure times volume.
    area=.5*abs(np.dot(v[:-1],np.roll(p[:-1],-1))-np.dot(p[:-1],np.roll(v[:-1],-1)))
    assert abs(area-summary["net_work_mmHg_mL"])<1e-12
    assert cycle(edv=50,esv=50)[2]["net_work_J"]==0
    assert cycle(low_pressure=10,high_pressure=10)[2]["net_work_J"]==0
    assert cycle(heart_rate=0)[2]["cardiac_output_L_min"]==0
    assert np.all(np.diff(shortening_speed(f))<=0)
    assert np.array_equal(shortening_speed([0,1]),[1,0])
    rejected=0
    for call in [lambda:cycle(esv=121),lambda:cycle(edv=np.nan),lambda:cycle(heart_rate=-1),lambda:shortening_speed(1.1)]:
        try:call()
        except ValueError:rejected+=1
        else:raise AssertionError("invalid input accepted")
    report={"model":"prescribed rectangular loop and separate illustrative muscle relation","summary":summary,"checks":{"polygon_area_matches_rectangle":True,"zero_width_zero_work":True,"zero_height_zero_work":True,"zero_rate_zero_output":True,"load_speed_limits":True,"invalid_inputs_rejected":rejected},"limitations":["not a measured ventricular loop","no coupled muscle-valve dynamics","loop work is not total metabolic energy","normalized muscle curve does not predict ventricular ejection"]}
    (out/"results.json").write_text(json.dumps(report,indent=2)+"\n");return report

if __name__=="__main__":print(json.dumps(run(),indent=2))
