# Pressure feedback in a closed six-compartment circulation

An illustrative six-compartment pressure-feedback model; it is not a clinical controller.

Run in this directory with Python 3.10+, NumPy 2.x and Matplotlib 3.8+:

```sh
python demo.py
```

The script creates the two original SVG/PDF figures, numerical traces (`fixed-rate.npz`, `feedback.npz`), a parameter/diagnostic summary (`demo-results.json`), and sampled references for a MATLAB/Octave comparison (`cross-language-fixed.csv`, `cross-language-feedback.csv`). These outputs are guided lecture calculations, not answers to the assigned problems. The notebook runs without internet access or private data after the dependencies are installed.

The hydraulic scheme is backward Euler with consistent ideal-valve states. A bounded iteration falls back to checking all sixteen valve configurations; an unsolved or unbalanced step raises an error. The pressure filter uses Euler by default; the common cardiac phase uses Euler with the bounded rate obtained from the updated filtered pressure. Both ventricular compliances use that phase. The optional `held-input` filter changes only the filter recurrence. Time supplied to the interface is seconds, while the hydraulic equations and rate clock convert it to minutes.

## Parameters and provenance

The model has six storage compartments and conserves total blood volume. It follows the compartment and implicit-valve methodology of Hoppensteadt and Peskin, *Modeling and Simulation in Medicine and the Life Sciences*, second edition, chapter 1. The continuously varying clock and pressure-feedback comparison are informed by Zan Ahmad and Charles S. Peskin, *Continuously Varying Heart Rate in a Pulsatile Circulation Model with Feedback Control*, current 21-page version. That paper has only two storage compartments and external reservoirs, so its numerical output is not an answer key for this model.

The default systemic resistance is 17.86 mmHg min/L; the recovered historical six-compartment initializer uses 8. The baseline is illustrative and not fitted to observations. Four valves enforce nonnegative forward flow; resistance beds permit signed flow. The reference rate is 80 beats/min, target 90 mmHg, filter time 3 s and gain 10. Resistance is halved from 30 to 60 seconds in a 90-second run. The 30–240 beats/min bounds are explicit modeling choices, not a universal physiological range. Initial total blood volume is determined by the specified initial pressures, compliances and unstressed volumes.

For an altered protocol, use the Python API or MATLAB structure overrides:

```python
from dataclasses import replace
from demo import Parameters, run_experiment
p = Parameters()
result = run_experiment(replace(p, gain=0.0))
```

```matlab
r = feedback_demo(struct('gain', 0));
```

`resistance_recovery_delay_s` and `target_recovery_delay_s` are separate inputs. Positive delays move their respective restoration events after `stop_s`. Inputs are validated; integer-indexed steps split at all exact forcing events. The default step is 0.00046875 s, or 1600 steps per 80-beats/min reference cycle. A coarser feedback calculation amplified tiny perturbations; the refined default was selected after an actual Python/Octave comparison passed the unchanged tolerance. The reported flow always uses the current resistance, avoiding stale conductance/output caches.

## Numerical checks

The numerical checks test compartment and total-volume balance, an independent nonlinear pressure root, ideal-valve flows, current-resistance updates, the zero-gain clock, bounded negative-command resets and invalid inputs. A separate volume-variable adaptive Radau integration supplies a one-cycle refinement reference. These checks do not establish a universal convergence order or physiological validity.

The companion `feedback_demo.m` and `run_matlab_checks.m` are supplied for actual cross-language verification. Generate Python references first, then run:

```matlab
run_matlab_checks
```

The checker writes `matlab-check-results.csv` only after executing and passing. It compares phase, filtered pressure, rate, all six pressures and all six flows at common sampled times, with absolute tolerance 1e-4 in each column's stated units. It separately checks volume drift, balance and clock bounds. Actual GNU Octave 10.3.0 runs of both 90-second refined cases passed these criteria. The largest sampled discrepancy was 4.47e-5 L/min in feedback aortic flow, below the unchanged 1e-4 threshold. The full Python demo took 50.96 seconds in the measured build environment.

The SVG figures include accessible titles and descriptions. Systemic flow in the response figure uses a centered 0.75 s display average; this is distinct from the causal controller pressure filter. The outputs are model calculations, not patient data.
