---
title: "Transport and diffusion with finite differences"
type: curated
layout: sample
url: /teaching/samples/heroic-finite-differences/
description: "A runnable introduction to one-dimensional linear transport and diffusion, with explicit boundary and stability conditions."
---

<p class="sample-context">HEROIC: Advanced Topics in Computational Cardiology | Fall 2024<br>Zan Ahmad · Johns Hopkins University</p>

Selected and revised from the asynchronous Python tutorial for CFD. Edited October 2026.

[Download PDF (3 pages)](/files/teaching-samples/heroic-finite-differences.pdf) · [Download Python code](/files/teaching-samples/heroic-finite-differences.py)

<p>Finite differences connect a differential equation to a numerical experiment. This selected tutorial studies two distinct processes: transport moves a profile; diffusion smooths it. The examples use Python 3, NumPy, and Matplotlib, and contain only synthetic data.</p>

<h2>1. Linear transport</h2>

<p>For a constant speed c &gt; 0, the equation u<sub>t</sub> + c u<sub>x</sub> = 0 translates an initial profile to the right. On an unbounded domain, the exact solution is u(x,t) = u<sub>0</sub>(x - ct). On our finite interval, we must also prescribe the value entering at the left boundary.</p>

<p>Let x<sub>i</sub> = i Δx and t<sub>n</sub> = n Δt. A forward difference in time and a backward (upwind) difference in space give:</p>

<p class="sample-equation">u<sub>i</sub><sup>n+1</sup> = u<sub>i</sub><sup>n</sup> - λ (u<sub>i</sub><sup>n</sup> - u<sub>i-1</sub><sup>n</sup>),     λ = c Δt/Δx</p>

<p>For this scheme, use 0 ≤ λ ≤ 1. This restriction is part of the numerical method, not an optional plotting preference. If the wave speed is negative, the upwind direction must change.</p>

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0.0, 2.0, 81)
dx = x[1] - x[0]
c = 1.0
dt = 0.5 * dx / c
steps = 40
initial = np.where((x >= 0.5) & (x <= 1.0), 2.0, 1.0)
u = initial.copy()
lam = c * dt / dx
assert 0.0 <= lam <= 1.0

for _ in range(steps):
    old = u.copy()
    u[1:] = old[1:] - lam * (old[1:] - old[:-1])
    u[0] = 1.0  # prescribed inflow; right end is outflow
```

<p>Keep the previous time level in a separate array. Updating in place from left to right would accidentally mix old and new values and change the method.</p>

<h2>2. Inspect transport error</h2>

```python
t = steps * dt
exact = np.where((x-c*t >= 0.5) & (x-c*t <= 1.0),
                 2.0, 1.0)
plt.plot(x, initial, "--", label="initial")
plt.plot(x, exact, label="translated profile")
plt.plot(x, u, label="upwind approximation")
plt.xlabel("x")
plt.ylabel("u")
plt.legend()
plt.show()
```

<p>At this final time the transported pulse has not reached the outflow boundary. Compare its predicted location and edge shape. First-order upwinding generally smears sharp edges through numerical diffusion; this should not be confused with physical diffusion in the model.</p>

<h2>3. Physical diffusion</h2>

<p>The diffusion equation is u<sub>t</sub> = ν u<sub>xx</sub>, where ν &gt; 0 is a diffusivity. A centered second difference gives:</p>

<p class="sample-equation">v<sub>i</sub><sup>n+1</sup> = v<sub>i</sub><sup>n</sup> + r (v<sub>i+1</sub><sup>n</sup> - 2v<sub>i</sub><sup>n</sup> + v<sub>i-1</sub><sup>n</sup>)</p>

<p class="sample-equation">r = ν Δt/Δx²,     0 ≤ r ≤ 1/2</p>

<p>Use the same spatial grid and initial hat profile, but hold both endpoint values at 1. The explicit scheme requires a time step proportional to Δx².</p>

```python
nu = 0.3
dt_diff = 0.2 * dx**2 / nu
r = nu * dt_diff / dx**2
v = initial.copy()
assert 0.0 <= r <= 0.5

for _ in range(100):
    old = v.copy()
    v[1:-1] = old[1:-1] + r * (
        old[2:] - 2.0*old[1:-1] + old[:-2]
    )
    v[[0, -1]] = 1.0

plt.plot(x, initial, "--", label="initial")
plt.plot(x, v, label="diffusion")
plt.xlabel("x")
plt.ylabel("u")
plt.legend()
plt.show()
```

<h2>Experiments</h2>

<p><b>Translation.</b> Check that the pulse moves by ct. Vary λ while keeping the final physical time fixed. Describe how the edge smearing changes.</p>

<p><b>Refinement.</b> Double the spatial resolution. Reduce Δt appropriately and compare at the same physical time. For diffusion, halving Δx requires roughly four times as many steps when r is held fixed.</p>

<p><b>Constant solutions.</b> Replace the hat profile by u = 1 everywhere. Both numerical updates should preserve this constant, including the boundaries.</p>

<p><b>Stability.</b> In a separate experiment, deliberately exceed the stated restriction. Record the first sign of nonphysical behavior. Restore stable parameters before making accuracy comparisons.</p>

<h2>What this sample does and does not cover</h2>

<p>The full archived tutorial also introduced nonlinear convection and Burgers’ equation. This public selection focuses on the two linear problems so that the stencil, boundary conditions, stability restriction, and physical-time comparison are explicit. Extending a method to shocks requires additional care; copying a linear stencil is not a general shock solver.</p>

<h2>Attribution and revision</h2>

<p>Course adaptation by Zan Ahmad. The sequence and hat-profile exercises follow Lorena A. Barba and Gilbert F. Forsyth, <i>CFD Python: the 12 steps to Navier-Stokes equations</i>, Journal of Open Source Education 1(9), 21 (2018), <a href="https://doi.org/10.21105/jose.00021">doi:10.21105/jose.00021</a>.</p>

<p>Copyright (c) Barba group. Upstream materials: <a href="https://github.com/barbagroup/CFDPython">github.com/barbagroup/CFDPython</a>. The project README specifies <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> for instructional content; the historical LICENSE also references <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. Code is BSD 3-Clause; the accompanying file retains the notice. This October 2026 selection rewrites the explanation, uses vectorized updates, adds explicit boundaries/stability checks, and corrects the discussion of numerical diffusion. No endorsement by the original authors is implied.</p>

<p>Download the runnable companion at <a href="https://zanahmad.com/files/teaching-samples/heroic-finite-differences.py">zanahmad.com/files/teaching-samples/heroic-finite-differences.py</a>.</p>
