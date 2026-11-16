PLANAR CURVE LABORATORY — Zan Ahmad

Open index.html locally. The HTML contains its own dataset, styles, and JavaScript;
no network, installation, or account is required. Nothing is uploaded or stored.

Select source/target curves and a landmark count. Drag the active curve landmarks,
use Tab and arrow keys (Shift for a larger step), or enter coordinates numerically.
Compare centering, proper rotation, scale normalization, and target correspondence.
Play or scrub the two maps; reset restores the starting experiment.

The exact smooth ambient flow preserves orientation. The RK4 implementation reports
finite-sample checks, not a global numerical injectivity certificate. Its endpoint
is not optimized to meet the target. Read notes.pdf for definitions and limitations.

REPRODUCE
Python 3 with NumPy:
  python companion.py --out results.json
Use Download experiment in the laboratory, then:
  python companion.py --experiment shape-experiment.json --out replay.json
The reported default results use 16 landmarks, centering and rotation on, no scale
normalization, zero cyclic shift, forward ordering, and support ratio 1.2.
JavaScript and Python implement the same equations with independently written
linear solves and integrators. Different platforms may differ in roundoff.

FILES
notes.pdf / notes.tex — derivations, assumptions, guided practice, scholarly sources
curves.json — original analytic curves with explicit generation formulas
companion.py — NumPy reproduction and input guards
shape-core.js / app.js — original numerical core and accessible interaction
curated-curves.pdf / flow-comparison.pdf / landmark-collapse.pdf — vector figures

ATTRIBUTION
Kernel: H. Wendland (1995), doi:10.1007/BF02123482.
Smooth-flow framework: M. F. Beg et al. (2005), doi:10.1023/B:VISI.0000043755.93987.aa.
Research context: Z. Ahmad et al. (2025), doi:10.1016/j.compbiomed.2025.110905.
All dataset curves, code, diagrams, and exposition here are original teaching work.
This finite landmark lab does not implement elastic shape matching or geodesic
optimization, and its synthetic contours are not patient measurements.
