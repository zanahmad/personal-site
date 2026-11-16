"""Meeting 1: adult circulation topology and an algebraic pressure-flow model.

Educational figures and synthetic calculations.
No patient data, clinical calibration, random draws, or numerical time solver.
Run `python demo.py`; a guided optional edit is `python demo.py --resistance 36`.
All files are written next to this script. No assigned exercise answers appear here.
"""
from pathlib import Path
import argparse
import csv
import json
import math
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

OUT = Path(__file__).resolve().parent
INK, TEAL, GOLD = '#18384A', '#087E8B', '#A66515'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'svg.fonttype': 'none', 'svg.hashsalt': 'cardiology-m01-v1',
                     'axes.spines.top': False, 'axes.spines.right': False})


def flow(p_in, p_out, resistance):
    """Signed L/min from pressures in mmHg and R in mmHg min/L.

    A passive, time-independent, linear resistance only. A negative result means
    flow opposite the chosen inlet-to-outlet orientation, not valve behavior.
    """
    values = [float(p_in), float(p_out), float(resistance)]
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Pressures and resistance must be finite numbers.')
    if values[2] <= 0:
        raise ValueError('Resistance must be positive.')
    return (values[0] - values[1]) / values[2]


def volume_change(q_in, q_out, minutes):
    """Net liters stored over an interval with constant flows in L/min."""
    values = [float(q_in), float(q_out), float(minutes)]
    if not all(math.isfinite(v) for v in values) or values[2] < 0:
        raise ValueError('Flows must be finite and duration finite and nonnegative.')
    return (values[0] - values[1]) * values[2]


def check_model():
    checks = {}
    checks['baseline_5_L_per_min'] = math.isclose(flow(95, 5, 18), 5)
    checks['equal_pressures_zero_flow'] = flow(20, 20, 18) == 0
    checks['pressure_reference_shift_invariant'] = math.isclose(flow(125, 35, 18), flow(95, 5, 18))
    checks['doubling_resistance_halves_flow_at_fixed_pressures'] = math.isclose(flow(95, 5, 36), 2.5)
    checks['reversing_difference_reverses_passive_flow'] = math.isclose(flow(5, 95, 18), -5)
    checks['no_net_storage_when_inflow_equals_outflow'] = volume_change(5, 5, 0.5) == 0
    checks['constant_flow_volume_balance'] = math.isclose(volume_change(5.2, 5, 0.5), 0.1)
    rejected = 0
    for args in [(95, 5, 0), (95, 5, -1), (float('nan'), 5, 18), (95, float('inf'), 18)]:
        try:
            flow(*args)
        except ValueError:
            rejected += 1
    checks['invalid_parameters_rejected'] = rejected == 4
    if not all(checks.values()):
        raise AssertionError(checks)
    return checks


def save_figure(fig, stem, title, description):
    """Write the same original vector figure as SVG and PDF; attach SVG text."""
    svg = OUT / (stem + '.svg')
    pdf = OUT / (stem + '.pdf')
    fig.savefig(svg, bbox_inches='tight', metadata={'Date': None, 'Title': title})
    fig.savefig(pdf, bbox_inches='tight', metadata={'Title': title, 'Author': 'Zan Ahmad',
                                                  'CreationDate': None, 'ModDate': None})
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    tree = ET.parse(svg)
    root = tree.getroot()
    root.set('role', 'img')
    root.set('aria-labelledby', stem + '-title ' + stem + '-desc')
    t = ET.Element('{' + ns + '}title', id=stem + '-title'); t.text = title
    d = ET.Element('{' + ns + '}desc', id=stem + '-desc'); d.text = description
    root.insert(0, t); root.insert(1, d)
    tree.write(svg, encoding='utf-8', xml_declaration=True)
    plt.close(fig)


def make_network():
    # Six functional nodes keep labels readable when printed at a 6.6-inch width.
    fig, ax = plt.subplots(figsize=(6.8, 4.95))
    ax.set_xlim(0, 12); ax.set_ylim(-0.2, 7.0); ax.axis('off')
    ax.set_title('Adult circulation: a directed network', loc='left', fontsize=14, color=INK, pad=15)
    lower, higher, neutral = '#6B233A', '#B43C31', '#087E8B'
    nodes = [
        ((1.8, 5.2), 'Right atrium', 'Lower oxygen', lower),
        ((6.0, 5.2), 'Right ventricle', 'Lower oxygen', lower),
        ((10.2, 5.2), 'Lungs', 'Add oxygen', neutral),
        ((10.2, 1.55), 'Left atrium', 'Higher oxygen', higher),
        ((6.0, 1.55), 'Left ventricle', 'Higher oxygen', higher),
        ((1.8, 1.55), 'Body tissues', 'Use oxygen', neutral),
    ]
    w, h = 3.12, 1.27
    for (x, y), title, detail, color in nodes:
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle='round,pad=0.04,rounding_size=0.08',
                                    facecolor='white', edgecolor=color, linewidth=1.7))
        ax.text(x, y+0.17, title, ha='center', va='center', fontsize=11.3, weight='bold', color=INK)
        ax.text(x, y-0.27, detail, ha='center', va='center', fontsize=10.3, color=color)
    def arrow(start, end):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=15, linewidth=1.7, color=INK))
    for x1, x2 in [(1.8,6.0),(6.0,10.2)]: arrow((x1+w/2+.05,5.2),(x2-w/2-.05,5.2))
    for x1,x2 in [(10.2,6.0),(6.0,1.8)]: arrow((x1-w/2-.05,1.55),(x2+w/2+.05,1.55))
    arrow((10.2,5.2-h/2-.08),(10.2,1.55+h/2+.08))
    arrow((1.8,1.55+h/2+.08),(1.8,5.2-h/2-.08))
    for x,label in [(3.9,'Tricuspid\nvalve'),(8.1,'Pulmonary valve\nand arteries')]:
        ax.text(x,6.5,label,ha='center',va='center',fontsize=10.3,color=INK)
    for x,label in [(3.9,'Aortic valve;\naorta and arteries'),(8.1,'Mitral\nvalve')]:
        ax.text(x,.23,label,ha='center',va='center',fontsize=10.3,color=INK)
    ax.text(9.8,3.35,'Pulmonary\nveins',ha='right',va='center',fontsize=10.3,color=INK)
    ax.text(2.2,3.35,'Systemic veins /\nvenae cavae',ha='left',va='center',fontsize=10.3,color=INK)
    fig.text(.07,.01,'Functional connections, not anatomical positions or sizes.\nBlood is red at both oxygen levels.',
             ha='left',fontsize=10,color=INK,linespacing=1.35)
    fig.subplots_adjust(bottom=.15,top=.84,left=.04,right=.98)
    save_figure(fig,'network','Adult circulation as a directed network',
      'Follow the closed route: body tissues, systemic veins and venae cavae, right atrium, tricuspid valve, right ventricle, pulmonary valve and arteries, lungs, pulmonary veins, left atrium, mitral valve, left ventricle, aortic valve, aorta and systemic arteries, body tissue capillaries. Four heart chambers are named. Labels indicate lower or higher oxygen; colors are a diagram key, not literal blood colors. Arterioles and venules are included in the connecting vessels rather than shown as separate nodes. The drawing does not specify anatomic placement, geometry, pressure, or timing.')


def make_flow_plot():
    delta = np.linspace(0,108,109)
    fig,ax=plt.subplots(figsize=(7.4,5.0))
    for resistance,color,style in [(18,TEAL,'-'),(36,GOLD,'--')]:
        q=np.array([flow(p,0,resistance) for p in delta])
        ax.plot(delta,q,color=color,linestyle=style,linewidth=2.5,label=f'R = {resistance} mmHg min/L')
        ax.plot(90,flow(90,0,resistance),'o',color=color,markersize=7)
    ax.axvline(90,color='#5C6B73',linestyle=':',linewidth=1.5)
    ax.annotate('5 L/min',xy=(90,5),xytext=(67,5.35),fontsize=12,color=TEAL)
    ax.annotate('2.5 L/min',xy=(90,2.5),xytext=(65,2.9),fontsize=12,color=GOLD)
    ax.set(xlim=(0,108),ylim=(0,6.3),xlabel='Pressure difference, ΔP (mmHg)',ylabel='Flow, Q (L/min)')
    ax.set_title('Same pressure difference, different flow',loc='left',fontsize=15,color=INK,pad=16)
    ax.set_xticks([0,18,36,54,72,90,108]);ax.grid(alpha=.18);ax.legend(loc='upper left',frameon=False)
    fig.text(.14,.02,'Synthetic model: Q = ΔP / R. At ΔP = 90 mmHg, doubling R halves Q.',fontsize=10.5,color=INK)
    fig.tight_layout(rect=(0,.05,1,1))
    save_figure(fig,'pressure-flow','Pressure-flow curves for two fixed resistances',
      'Horizontal axis: pressure difference from 0 to 108 mmHg. Vertical axis: flow in liters per minute. The solid teal line uses resistance 18 mmHg minute per liter; the dashed brown line uses 36. Both pass through zero. At the marked pressure difference of 90 mmHg, the flows are 5 and 2.5 liters per minute. These are synthetic algebraic model values, not measurements or a whole-circulation prediction.')
    with (OUT/'flow-curves.csv').open('w',newline='')as f:
        writer=csv.writer(f);writer.writerow(['pressure_difference_mmHg','Q_R18_L_per_min','Q_R36_L_per_min'])
        for p in delta:writer.writerow([f'{p:.0f}',f'{flow(p,0,18):.8g}',f'{flow(p,0,36):.8g}'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--p-in',type=float,default=95,help='Inlet pressure, mmHg; classroom range 0..180.')
    parser.add_argument('--p-out',type=float,default=5,help='Outlet pressure, mmHg; classroom range 0..40.')
    parser.add_argument('--resistance',type=float,default=18,help='Resistance, mmHg min/L; classroom range 5..60.')
    args=parser.parse_args()
    for label,value,low,high in [('p-in',args.p_in,0,180),('p-out',args.p_out,0,40),('resistance',args.resistance,5,60)]:
        if not math.isfinite(value) or not low<=value<=high:
            parser.error(f'{label} must be finite and in [{low}, {high}]. These are teaching bounds, not clinical normal ranges.')
    checks=check_model()
    make_network();make_flow_plot()
    result={'description':'Synthetic fixed-pressure passive resistance; algebraic calculation, no time solver.',
            'p_in_mmHg':args.p_in,'p_out_mmHg':args.p_out,'resistance_mmHg_min_per_L':args.resistance,
            'flow_L_per_min':flow(args.p_in,args.p_out,args.resistance),'checks':checks,
            'figure_parameters':'Figures always show the documented baseline and doubled-resistance comparison; CLI edits affect the reported experiment only.'}
    (OUT/'model-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
