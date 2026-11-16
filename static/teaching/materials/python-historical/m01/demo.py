"""Original synthetic temperature record; no measured data or cooling-law fit.
Run python demo.py. Plotting helpers are supplied scaffolding for a first lesson.
"""
from pathlib import Path
import json, math
from numbers import Real
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TIME_SECONDS = [0., 60., 120., 180., 240.]
TEMPERATURE_C = [80., 62., 48., 38., 31.]

def validate_record(seconds, temperatures):
    if len(seconds) != len(temperatures) or len(seconds) < 2:
        raise ValueError('Use equal-length lists with at least two observations.')
    values = list(seconds) + list(temperatures)
    if not all(isinstance(v, Real) and not isinstance(v, bool) and math.isfinite(v) for v in values):
        raise ValueError('Every time and temperature must be a finite number, not text or a boolean.')
    if seconds[0] < 0 or any(b <= a for a,b in zip(seconds,seconds[1:])):
        raise ValueError('Times must be nonnegative and strictly increasing.')
    if any(v < -273.15 for v in temperatures):
        raise ValueError('Celsius values cannot be below absolute zero.')

def summarize(seconds, temperatures):
    validate_record(seconds,temperatures)
    elapsed_min=(seconds[-1]-seconds[0])/60
    change=temperatures[-1]-temperatures[0]
    return {'observations':len(seconds),'elapsed_minutes':elapsed_min,
            'first_temperature_C':temperatures[0],'last_temperature_C':temperatures[-1],
            'temperature_change_C':change,'average_change_C_per_min':change/elapsed_min,
            'arithmetic_mean_C':sum(temperatures)/len(temperatures)}

def save(fig, folder, name, title, desc):
    fig.savefig(folder/(name+'.svg'),bbox_inches='tight');fig.savefig(folder/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
    ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
    tree=ET.parse(folder/(name+'.svg'));r=tree.getroot();r.set('role','img');r.set('aria-labelledby',name+'-title '+name+'-desc')
    for tag,suffix,value in [('title','title',title),('desc','desc',desc)]:
        e=ET.Element('{'+ns+'}'+tag,id=name+'-'+suffix);e.text=value;r.insert(0,e)
    tree.write(folder/(name+'.svg'),encoding='utf-8',xml_declaration=True)

def run(output_dir=None):
    out=Path(output_dir) if output_dir else Path(__file__).resolve().parent;out.mkdir(parents=True,exist_ok=True)
    report=summarize(TIME_SECONDS,TEMPERATURE_C)
    minutes=np.asarray(TIME_SECONDS)/60;kelvin=np.asarray(TEMPERATURE_C)+273.15
    assert report['elapsed_minutes']==4 and report['temperature_change_C']==-49
    assert report['average_change_C_per_min']==-12.25
    assert np.allclose(np.diff(kelvin),np.diff(TEMPERATURE_C))
    assert np.allclose(np.asarray(TIME_SECONDS),minutes*60)
    rejected=0
    for a,b in [([0,1],[10]),([0,0],[10,9]),([0,1],[10,float('nan')]),([0,1],[10,-274]),([0,1],[10,'9']),([0,1],[10,True])]:
        try:validate_record(a,b)
        except ValueError:rejected+=1
    assert rejected==6
    plt.rcParams.update({'font.size':14,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(7.5,4.5));ax.plot(minutes,TEMPERATURE_C,'o',color='#176c7b',ms=8,label='Synthetic recorded values')
    ax.plot(minutes,TEMPERATURE_C,':',color='#7d9095',label='Visual connector; no fitted law')
    ax.set(xlabel='Elapsed time (min)',ylabel='Temperature (°C)',title='Five observations, with their units');ax.set_xticks(minutes);ax.legend(frameon=False);ax.grid(alpha=.2)
    save(fig,out,'temperature-record','Five synthetic temperature observations','Temperatures at 0, 1, 2, 3 and 4 minutes are 80, 62, 48, 38 and 31 degrees Celsius. Dotted segments connect samples for reading only; no differential equation or fitted cooling law is asserted.')
    plt.rcParams.update({'font.size':16})
    fig,axs=plt.subplots(1,2,figsize=(9.0,4.1))
    for ax,values,label in [(axs[0],TEMPERATURE_C,'Temperature (°C)'),(axs[1],kelvin,'Temperature (K)')]:
        ax.plot(minutes,values,'o-',color='#176c7b');ax.set_xlabel('Time (min)');ax.set_ylabel(label);ax.grid(alpha=.2)
    axs[0].set_title('Celsius');axs[1].set_title('Kelvin: add 273.15');fig.tight_layout()
    save(fig,out,'temperature-scales','One record in Celsius and Kelvin','Both panels show the same synthetic observations. Adding 273.15 changes absolute numerical temperatures but leaves a 49-degree decrease equal to a 49-kelvin decrease. Values and axis labels reflect the conversion; this is not a second experiment.')
    report['checks']={'same_changes_in_C_and_K':True,'seconds_minutes_roundtrip':True,'invalid_records_rejected':rejected}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(run(),indent=2))
