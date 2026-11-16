"""Synthetic two-channel mixture measurements.

Run: python demo.py
Dependencies: numpy, matplotlib. All data synthetic. No internet required.
Response coefficients use arbitrary signal units per millimolar (AU/mM).
This is a linear calibration example, not a validated chemical assay.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RESPONSE = np.array([[1.00, 0.25], [0.20, 1.20]], dtype=float)
CONCENTRATIONS = np.array([[2.0, 1.0], [0.5, 3.0], [1.5, 1.5]], dtype=float)


def finite_array(value, name, ndim=None):
    arr = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f'{name} must contain only finite numbers')
    if ndim is not None and arr.ndim != ndim:
        raise ValueError(f'{name} must have {ndim} dimensions, got {arr.shape}')
    return arr


def measure(concentrations, response=RESPONSE):
    """Rows are specimens, columns are components. Return specimen x channel."""
    c = finite_array(concentrations, 'concentrations', 2)
    a = finite_array(response, 'response', 2)
    if c.shape[1] != a.shape[1] or a.shape[0] == 0:
        raise ValueError('component dimension must match response columns')
    return c @ a.T


def recover(signals, response=RESPONSE):
    """Recover rows of concentrations from square nonsingular response matrix.

    Negative inferred concentrations are returned, not silently clipped. They can
    indicate noise, calibration mismatch, or limitations of this linear model.
    """
    y = finite_array(signals, 'signals', 2)
    a = finite_array(response, 'response', 2)
    if a.shape[0] != a.shape[1] or a.shape[0] == 0:
        raise ValueError('response must be a nonempty square matrix')
    if y.shape[1] != a.shape[0]:
        raise ValueError('signal columns must match detector channels')
    try:
        return np.linalg.solve(a, y.T).T
    except np.linalg.LinAlgError as exc:
        raise ValueError('response cannot uniquely separate these components') from exc


def describe_svg(path, title, description):
    tree = ET.parse(path)
    node = tree.getroot()
    ns = '{http://www.w3.org/2000/svg}'
    node.set('role', 'img')
    node.set('aria-labelledby', 'figure-title figure-description')
    t = ET.Element(ns+'title', id='figure-title'); t.text = title
    d = ET.Element(ns+'desc', id='figure-description'); d.text = description
    node.insert(0, d); node.insert(0, t)
    tree.write(path, encoding='utf-8', xml_declaration=True)


def save_figure(fig, out, stem, title, description):
    fig.savefig(out/(stem+'.svg'), bbox_inches='tight')
    fig.savefig(out/(stem+'.pdf'), bbox_inches='tight')
    describe_svg(out/(stem+'.svg'), title, description)
    plt.close(fig)


def run(output_dir=None):
    out = Path(output_dir) if output_dir else Path(__file__).resolve().parent
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'font.family': 'DejaVu Sans',
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none'})
    y = measure(CONCENTRATIONS)
    recovered = recover(y)
    baseline = np.array([2.0, 1.0])
    weak = np.array([[1.0, 1.0], [1.0, 1.01]])
    perturbation = np.array([0.001, -0.001])
    comparisons = []
    for name, a in [('Distinct channels', RESPONSE), ('Nearly redundant channels', weak)]:
        clean = measure(baseline[None, :], a)
        noisy = clean + perturbation[None, :]
        estimate = recover(noisy, a)
        comparisons.append({'label': name, 'condition_number_2': float(np.linalg.cond(a)),
                            'signal': clean[0].tolist(), 'perturbed_signal': noisy[0].tolist(),
                            'estimated_concentrations': estimate[0].tolist(),
                            'concentration_error': (estimate[0]-baseline).tolist(),
                            'residual_norm': float(np.linalg.norm(measure(estimate, a)-noisy))})
    # Checks compare independent model descriptions, not merely plotting output.
    loop_result = np.array([[sum(RESPONSE[j,k]*row[k] for k in range(2))
                            for j in range(2)] for row in CONCENTRATIONS])
    assert np.allclose(y, loop_result, rtol=0, atol=1e-14)
    assert np.allclose(recovered, CONCENTRATIONS, rtol=0, atol=1e-12)
    assert np.allclose(measure(np.zeros((1,2))), 0)
    assert np.allclose(measure(CONCENTRATIONS*2), y*2)
    assert np.linalg.norm(comparisons[1]['concentration_error']) > 100*np.linalg.norm(comparisons[0]['concentration_error'])
    rejected = 0
    for call in [lambda: measure(np.ones((3,3))), lambda: recover(np.ones((2,3))),
                 lambda: measure([[np.nan,1]]), lambda: recover([[1,1]], [[1,1],[1,1]])]:
        try: call()
        except ValueError: rejected += 1
        else: raise AssertionError('invalid input was not rejected')
    fig, axs = plt.subplots(1,3, figsize=(10.2,3.1), gridspec_kw={'width_ratios':[3,2,3]})
    matrices = [(CONCENTRATIONS, 'C: specimens × components\n(3, 2), mM', ['A','B']),
                (RESPONSE.T, 'Aᵀ: components × channels\n(2, 2), AU/mM', ['1','2']),
                (y, 'Y: specimens × channels\n(3, 2), AU', ['1','2'])]
    for ax,(arr,title,xlabels) in zip(axs,matrices):
        ax.imshow(arr, cmap='Blues', vmin=0, vmax=max(float(arr.max())*1.6,1), aspect='auto')
        for (i,j),v in np.ndenumerate(arr): ax.text(j,i,f'{v:.3g}',ha='center',va='center',color='#10253d')
        ax.set_title(title, fontsize=11); ax.set_xticks(range(arr.shape[1]),xlabels)
        ax.set_yticks(range(arr.shape[0]),range(1,arr.shape[0]+1))
        ax.set_xlabel('component' if ax is axs[0] else 'channel')
        ax.set_ylabel('component' if ax is axs[1] else 'specimen')
        ax.tick_params(length=0)
    fig.suptitle('Batch measurements: Y = C @ A.T', y=1.03, fontsize=13)
    fig.tight_layout()
    save_figure(fig,out,'mixture-shapes','Three matrices in a batched sensor calculation',
                'Three specimens with two component concentrations multiply a two by two response transpose to produce three rows of two signals. Every matrix entry and axis role is labeled.')
    fig,axs=plt.subplots(1,2,figsize=(9.2,3.8),sharey=True)
    for ax,item in zip(axs,comparisons):
        x=np.arange(2); ax.bar(x-.18,baseline,.36,label='Known synthetic amount',color='#8096a7')
        ax.bar(x+.18,item['estimated_concentrations'],.36,label='Recovered after perturbation',color='#294e70')
        ax.set_xticks(x,['Component A','Component B']); ax.set_ylim(0,2.6)
        ax.set_title(item['label']+'\ncondition number = '+f"{item['condition_number_2']:.2f}",fontsize=11)
        ax.set_xlabel('Same signal perturbation: (+0.001, −0.001) AU')
    axs[0].set_ylabel('Concentration (mM)')
    handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,1.03),ncol=2,frameon=False)
    fig.tight_layout(rect=(0,0,1,.92))
    save_figure(fig,out,'sensitivity','Sensitivity to nearly redundant detector channels',
                'Identical small signal perturbations barely change the inferred concentrations for distinct channels but noticeably change both estimates for nearly redundant channels. Both solve residuals remain near machine precision.')
    report={'model':'synthetic linear mixture; not an experimental assay','response_AU_per_mM':RESPONSE.tolist(),
            'concentrations_mM':CONCENTRATIONS.tolist(),'signals_AU':y.tolist(),
            'maximum_recovery_error_mM':float(np.max(np.abs(recovered-CONCENTRATIONS))),
            'comparisons':comparisons,'checks':{'loop_and_matrix_agree':True,'zero_and_scaling_limits':True,
                                             'exact_synthetic_recovery':True,'invalid_inputs_rejected':rejected}}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
