"""Original volume-accounting example; synthetic bench reservoir, not a patient.
Run with Python, NumPy and Matplotlib. Piecewise constant flows are integrated
exactly at the stated change times; no differential-equation solver is required.
"""
from pathlib import Path
import json, html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def volume_budget(initial_ml=500., durations_min=(3.,3.), inflows_ml_min=(100.,100.), outflows_ml_min=(80.,120.)):
    duration=np.asarray(durations_min,float);qin=np.asarray(inflows_ml_min,float);qout=np.asarray(outflows_ml_min,float)
    if duration.ndim!=1 or not len(duration) or duration.shape!=qin.shape or duration.shape!=qout.shape:
        raise ValueError('Provide one duration, inflow and outflow per interval.')
    if not np.isfinite(initial_ml) or initial_ml<0 or not all(np.all(np.isfinite(v)) for v in (duration,qin,qout)):
        raise ValueError('Use finite values and a nonnegative initial volume.')
    if np.any(duration<=0) or np.any(qin<0) or np.any(qout<0):
        raise ValueError('Durations must be positive; arrow flow magnitudes nonnegative.')
    try:
        with np.errstate(over='raise', invalid='raise'):
            t=np.r_[0.,np.cumsum(duration)]
            entered=np.r_[0.,np.cumsum(duration*qin)]
            left=np.r_[0.,np.cumsum(duration*qout)]
            volume=initial_ml+entered-left
    except FloatingPointError as exc:
        raise ValueError('The specified budget exceeds finite numerical range.') from exc
    if not all(np.all(np.isfinite(v)) for v in (t,entered,left,volume)):
        raise ValueError('The specified budget exceeds finite numerical range.')
    # Permit only a few floating-point rounding units at exact emptying.
    # This does not rescue a physically negative continuation.
    tolerance=8*np.finfo(float).eps*np.maximum.reduce([np.full_like(volume,initial_ml),entered,left])
    if np.any(volume < -tolerance):
        raise ValueError('The prescribed outflow would empty the reservoir: change the model or stop earlier.')
    volume=np.where((volume<0)&(volume>=-tolerance),0.,volume)
    return {'time_min':t,'volume_ml':volume,'cumulative_in_ml':entered,'cumulative_out_ml':left}


def save(fig,out,stem,title,description):
    fig.savefig(out/(stem+'.svg'),bbox_inches='tight');fig.savefig(out/(stem+'.pdf'),bbox_inches='tight')
    p=out/(stem+'.svg');s=p.read_text();i=s.index('>',s.index('<svg'))+1
    s=s[:i]+'<title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc>'+s[i:]
    p.write_text(s);plt.close(fig)


def run(output_dir=None):
    out=Path(output_dir or Path(__file__).resolve().parent);out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':12,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    b=volume_budget()
    fig,ax=plt.subplots(figsize=(8.4,3.8));ax.set(xlim=(0,10),ylim=(0,4));ax.axis('off')
    ax.add_patch(FancyBboxPatch((3.3,.8),3.4,2.4,boxstyle='round,pad=.08',fc='#e6f4f4',ec='#18384a',lw=2))
    ax.text(5,2.3,'Stored volume V',ha='center',weight='bold');ax.text(5,1.7,'Initial: 500 mL',ha='center')
    ax.annotate('',(3.25,2),(1,2),arrowprops={'arrowstyle':'->','lw':2.5,'color':'#087e8b'})
    ax.annotate('',(9,2),(6.75,2),arrowprops={'arrowstyle':'->','lw':2.5,'color':'#b16a20'})
    ax.text(1.9,2.6,'Inflow\n100 mL/min',ha='center');ax.text(8.15,2.6,'Outflow\n80 then 120 mL/min',ha='center')
    ax.text(5,.25,'Boundary: one bench reservoir; fluid is treated as incompressible',ha='center',fontsize=11)
    save(fig,out,'reservoir','Define storage and boundary flows','An original bench-reservoir diagram distinguishes stored volume in milliliters from incoming and outgoing flow in milliliters per minute. Outflow changes after three minutes.')
    fig,axs=plt.subplots(2,1,figsize=(7.6,5.8),sharex=True,constrained_layout=True)
    axs[0].stairs([100,100],[0,3,6],label='Inflow',color='#087e8b',lw=2.5,baseline=None)
    axs[0].stairs([80,120],[0,3,6],label='Outflow',color='#b16a20',lw=2.5,baseline=None)
    axs[0].set(ylabel='Flow (mL/min)',ylim=(60,140));axs[0].legend(loc='upper left',ncol=2,fontsize=11)
    axs[1].plot(b['time_min'],b['volume_ml'],'o-',color='#18384a',lw=2.5)
    axs[1].set(xlabel='Time (min)',ylabel='Stored volume (mL)',ylim=(480,580))
    axs[1].annotate('560 mL',(3,560),xytext=(3.7,558),fontsize=11)
    for ax in axs:ax.axvline(3,color='#777',ls=':',lw=1);ax.grid(alpha=.15)
    save(fig,out,'flow-and-storage','A change of flow reverses accumulation','Inflow stays at100 milliliters per minute. Outflow is80 for the first three minutes and120 for the next three. Volume rises linearly from500 to560 milliliters, then falls to500. The volume is continuous at the flow change.')
    balance=float(np.max(np.abs(b['volume_ml']+b['cumulative_out_ml']-500-b['cumulative_in_ml'])))
    assert balance<1e-10
    assert np.array_equal(b['volume_ml'],[500,560,500])
    eq=volume_budget(outflows_ml_min=(100,100));assert np.array_equal(eq['volume_ml'],[500]*3)
    closed=volume_budget(inflows_ml_min=(0,0),outflows_ml_min=(0,0));assert np.array_equal(closed['volume_ml'],[500]*3)
    # Same trajectory expressed in liters must agree after conversion.
    liters=volume_budget(.5,(3,3),(.1,.1),(.08,.12));assert np.allclose(liters['volume_ml']*1000,b['volume_ml'])
    empty=volume_budget(.3,(3.,),(0.,),(.1,))
    assert empty['volume_ml'][-1]==0.
    rejected=0
    for kwargs in [{'durations_min':(0,3)},{'initial_ml':float('nan')},{'outflows_ml_min':(-1,120)},{'outflows_ml_min':(1000,1000)},{'inflows_ml_min':(100,)},{'initial_ml':1e308,'durations_min':(10.,),'inflows_ml_min':(1e308,),'outflows_ml_min':(1e308,)}]:
        try:volume_budget(**kwargs)
        except ValueError:rejected+=1
        else:raise AssertionError('Invalid budget accepted')
    result={'units':{'time':'min','volume':'mL'},'trajectory':{k:v.tolist() for k,v in b.items()},'checks':{'budget_residual_ml':balance,'equal_flow_constant_volume':True,'closed_reservoir_constant_volume':True,'unit_conversion_agrees':True,'invalid_cases_rejected':rejected}}
    np.savetxt(out/'trajectory.csv',np.column_stack(list(b.values())),delimiter=',',header=','.join(b),comments='')
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
