"""Original discrete rate controller and separate static fluid column.
Not a fitted baroreflex, exercise/standing simulator, or clinical controller.
"""
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def finite(value,name):
    try:value=float(value)
    except (TypeError,ValueError,OverflowError) as exc:raise ValueError(name+' must be a finite scalar') from exc
    if not math.isfinite(value):raise ValueError(name+' must be finite')
    return value


def simulate(resistance=10,gain=.5,stroke_volume=100,venous_pressure=5,target=95,initial_rate=60,min_rate=40,max_rate=160,steps=20,step_seconds=10):
    r=finite(resistance,'resistance');k=finite(gain,'gain');sv=finite(stroke_volume,'stroke volume')
    pv=finite(venous_pressure,'venous pressure');pt=finite(target,'target');h=finite(initial_rate,'initial rate')
    lo=finite(min_rate,'minimum rate');hi=finite(max_rate,'maximum rate');dt=finite(step_seconds,'update spacing')
    if r<=0 or sv<=0 or dt<=0 or k<0 or lo<=0 or hi<lo or not lo<=h<=hi or pv<0 or pt<pv:
        raise ValueError('positive resistance, stroke volume and spacing; nonnegative gain/reference; ordered valid bounds and target required')
    if isinstance(steps,bool) or not isinstance(steps,(int,np.integer)) or not 1<=steps<=10000:raise ValueError('steps must be an integer from 1 to 10000')
    factor=r*(sv/1000)
    if not math.isfinite(factor) or factor<=0 or k*factor>1:raise ValueError('basic demo requires finite 0 <= gain*R*Vs/1000 <= 1')
    if not math.isfinite(pv+factor*hi) or not math.isfinite(steps*dt):raise ValueError('requested outputs exceed finite range')
    target_rate=(pt-pv)/factor
    if not math.isfinite(target_rate) or not math.isfinite(hi*(sv/1000)):
        raise ValueError('required rate or output exceeds finite arithmetic range')
    rates=[];pressures=[]
    for n in range(steps+1):
        p=pv+factor*h;rates.append(h);pressures.append(p)
        error=pt-p;change=k*error
        if not math.isfinite(change):raise ValueError('rate update exceeds finite range')
        h=min(hi,max(lo,h+change))
    return {'time_seconds':np.arange(steps+1,dtype=float)*dt,'rate':np.array(rates),'pressure':np.array(pressures),'output':np.array(rates)*(sv/1000),'target_rate':target_rate}


def hydrostatic(height_m,density=1060,gravity=9.81):
    z=finite(height_m,'height');rho=finite(density,'density');g=finite(gravity,'gravity')
    if rho<=0 or g<0:raise ValueError('density positive and gravity nonnegative required')
    value=-rho*g*z/133.322
    if not math.isfinite(value):raise ValueError('hydrostatic pressure exceeds finite range')
    return value


def save(fig,out,name,title,desc):
    fig.savefig(out/(name+'.svg'),bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
    path=out/(name+'.svg');tree=ET.parse(path);root=tree.getroot();ns='{http://www.w3.org/2000/svg}'
    root.set('role','img');root.set('aria-labelledby','figure-title figure-description')
    for tag,ident,txt in [('title','figure-title',title),('desc','figure-description',desc)]:
        el=ET.Element(ns+tag,id=ident);el.text=txt;root.insert(0,el)
    tree.write(path,encoding='utf-8',xml_declaration=True)


def box(ax,x,y,text,w=3,h=.85):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.06',facecolor='#eef4f4',edgecolor='#244c59',lw=1.5))
    ax.text(x,y,text,ha='center',va='center',fontsize=20)


def arrow(ax,a,b,rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=20,linewidth=1.8,color='#244c59',connectionstyle=f'arc3,rad={rad}'))


def run(output_dir=None):
    out=Path(output_dir) if output_dir is not None else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':22,'axes.titlesize':22,'legend.fontsize':20,'svg.fonttype':'none','font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(11,6.3),gridspec_kw={'width_ratios':[1.15,1]})
    ax=axs[0];ax.set(xlim=(-.5,7.5),ylim=(0,7));ax.axis('off');ax.set_title('Discrete feedback',pad=15)
    box(ax,4.7,6,'Target − P');box(ax,4.7,4.4,'Update rate');box(ax,4.7,2.8,'Pump + R');box(ax,4.7,1.2,'Measured P')
    for y in [6,4.4,2.8]:arrow(ax,(4.7,y-.5),(4.7,y-1.1))
    ax.plot([3.1,1.1,1.1,3.1],[1.2,1.2,6,6],color='#244c59',lw=1.8);arrow(ax,(2.6,6),(3.1,6))
    ax.text(.3,3.5,'Measurement\nreturns',ha='center',va='center',rotation=90,fontsize=20)
    ax.text(6.65,5.2,'error',ha='center',fontsize=20);ax.text(6.5,3.6,'H',ha='center',fontsize=20)
    ax=axs[1];ax.set(xlim=(-.5,5.8),ylim=(-.75,.75));ax.axis('off');ax.set_title('Separate static column',pad=15)
    ax.fill_betweenx([-.55,.55],.7,1.45,color='#dbe9eb');ax.plot([.7,.7,1.45,1.45],[-.55,.55,.55,-.55],color='#244c59',lw=2)
    for z,label in [(.5,'z = +0.5 m\nΔP ≈ −39 mmHg'),(0,'z = 0\nReference pressure'),(-.5,'z = −0.5 m\nΔP ≈ +39 mmHg')]:
        ax.plot([.7,1.7],[z,z],color='#244c59',lw=1.5);ax.text(1.9,z,label,va='center',fontsize=20)
    arrow(ax,(.15,-.3),(.15,.3));ax.text(-.35,0,'Upward z',rotation=90,va='center',fontsize=20)
    fig.subplots_adjust(left=.02,right=.98,bottom=.04,top=.87,wspace=.13)
    save(fig,out,'feedback-and-height','Discrete feedback and a separate hydrostatic column','The controller subtracts measured pressure from target, updates rate, and uses fixed stroke volume and resistance to produce next pressure. The distinct static column has lower pressure above and higher pressure below a reference; at half a meter the difference is about 39 mmHg. Height is not used in the controller.')
    ordinary=simulate();fixed=simulate(gain=0);limited=simulate(resistance=4)
    fig,axs=plt.subplots(2,1,figsize=(10,6.8),sharex=True)
    for row,label,color,style in [(ordinary,'Feedback, R = 10','#126782','-'),(fixed,'Fixed rate, R = 10','#777777',':'),(limited,'Limited, R = 4','#a34a28','--')]:
        axs[0].plot(row['time_seconds'],row['pressure'],label=label,color=color,ls=style,lw=2.5)
        axs[1].plot(row['time_seconds'],row['rate'],color=color,ls=style,lw=2.5)
    axs[0].axhline(95,color='#244c59',lw=1,alpha=.6);axs[0].set(ylabel='Pressure\n(mmHg)',ylim=(20,110),yticks=[30,60,95])
    axs[1].axhline(160,color='#244c59',lw=1,alpha=.6);axs[1].set(xlabel='Time after resistance step (s)',ylabel='Rate\n(beats/min)',ylim=(40,175),yticks=[60,90,160],xticks=[0,50,100,150,200])
    fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.58,1.01),ncol=1,fontsize=20,frameon=False)
    fig.tight_layout(rect=(0,0,1,.78))
    save(fig,out,'feedback-response','Fixed-rate and feedback pressure responses','At time zero resistance has dropped; no correction occurs before the initial measurement. With R 10 the fixed-rate pressure is 65, while the controller approaches 95 and rate 90. With R 4 the rate saturates at 160 and pressure at 69. Stroke volume is fixed at 100 mL/beat; these are synthetic recurrence outputs.')
    assert np.allclose(ordinary['rate'][:5],[60,75,82.5,86.25,88.125])
    assert abs(ordinary['pressure'][-1]-95)<3e-5 and ordinary['target_rate']==90
    assert np.all(fixed['rate']==60) and np.all(fixed['pressure']==65)
    assert limited['rate'][-1]==160 and limited['pressure'][-1]==69 and limited['target_rate']==225
    for row in [ordinary,fixed,limited]:assert np.all((row['rate']>=40)&(row['rate']<=160))
    assert hydrostatic(0)==0 and np.isclose(hydrostatic(-.5),-hydrostatic(.5)) and np.isclose(hydrostatic(-.5),5199.3/133.322)
    rejected=0
    cases=[lambda:simulate(resistance=0),lambda:simulate(gain=-1),lambda:simulate(gain=2),lambda:simulate(initial_rate=20),lambda:simulate(stroke_volume=float('nan')),lambda:simulate(steps=1.5),lambda:simulate(step_seconds=0),lambda:simulate(max_rate=20),lambda:hydrostatic(float('inf')),lambda:hydrostatic(1,density=-1),lambda:simulate(target=float('inf'))]
    for call in cases:
        try:call()
        except ValueError:rejected+=1
        else:raise AssertionError('invalid controls accepted')
    report={'model':'synthetic discrete rate controller; fixed stroke volume; static height illustration separate','first_rates':ordinary['rate'][:5].tolist(),'reachable_final_pressure_mmHg':float(ordinary['pressure'][-1]),'saturated_pressure_mmHg':69,'saturated_error_mmHg':26,'half_meter_below_delta_mmHg':hydrostatic(-.5),'checks':{'hand_updates':True,'target_convergence':True,'saturation':True,'zero_gain':True,'rate_bounds':True,'hydrostatic_sign_and_zero':True,'invalid_controls_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
