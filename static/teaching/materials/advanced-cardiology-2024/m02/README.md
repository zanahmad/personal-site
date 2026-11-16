# Fixed-rate six-compartment baseline

Computational cardiology, lecture 2. Run `python demo.py` with Python, NumPy and Matplotlib; keep `hydraulic_core.py` beside it. No internet access or recovered source archive is required.

The baseline uses 80 beats/min, systemic resistance 17.86 mmHg min/L, a 15-second duration and 0.001875-second step. The recovered historical initializer instead uses resistance 8; the notes preserve this distinction. Both ventricular compliances use phase = rate × seconds / 60. No pressure filter or feedback controller is run.

The local hydraulic component is shared with lecture 4. It implements backward Euler with consistent ideal-valve states, a bounded valve iteration and explicit failure on an unbalanced solve. Methodology is attributed to Hoppensteadt and Peskin, chapter 1. The baseline driver advances its fixed phase directly and reconstructs matched volumes.

Outputs are original SVG/PDF figures, baseline.npz and a numerical results summary. The initialized total is 5.13616 L. Useful checks include volume reconstruction, closed-volume balance, forward-valve nonnegativity, shared phase, step refinement and an Rs=8 conservation probe. The wrong fixed-compliance audit is a deliberate teaching counterexample. These are model calculations, not laboratory validation.

The notebook's required implementation cell asks learners to sum compartment volumes. An unfilled cell prints a clear prompt; fill it and run the known check.
