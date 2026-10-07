---
title: "From mathematical problems to SciPy solvers"
type: curated
layout: sample
url: /teaching/samples/python-scipy/
description: "Root finding, initial-value problems, and interpolation, with small reproducible examples and diagnostic checks."
---

<p class="sample-context">EN.553.285 Introduction to Scientific Programming in Python | Winter 2026<br>Zan Ahmad · Johns Hopkins University</p>

Edited lecture sample from January 15, 2026 (Lecture 4). Edited October 2026.

[Download PDF (3 pages)](/files/teaching-samples/python-scipy.pdf) · [Download Python code](/files/teaching-samples/python-scipy.py)

<p>NumPy gives us numerical arrays; SciPy provides algorithms for mathematical tasks. Start by identifying the problem, then choose the solver and inspect its diagnostics. The examples use synthetic data, Python 3, NumPy, and SciPy.</p>

<h2>1. Find a root</h2>

<p>Suppose f(x) = x³ - x - 2. The function is continuous and has opposite signs at x = 1 and x = 2, so there is at least one root between them. A sign-changing bracket is a guarantee of existence under continuity, not a guarantee of uniqueness.</p>

```python
from scipy import optimize

def f(x):
    return x**3 - x - 2

result = optimize.root_scalar(
    f, bracket=[1.0, 2.0], method="brentq"
)
if not result.converged:
    raise RuntimeError("Root finder did not converge")
print(result.root)
print(abs(f(result.root)))
```

<p>The root is approximately 1.52138. Inspect both the convergence flag and the residual. A small residual is useful evidence, although for a poorly conditioned problem it does not by itself establish a small error in the root.</p>

<h2>Why Brent’s method is useful</h2>

<p>Brent’s method maintains a bracket and combines bisection with secant and inverse-quadratic interpolation steps. Faster proposals are accepted when appropriate; bracket-based steps provide a safeguard. The method still depends on the mathematical assumptions and sensible tolerances.</p>

<h2>Try it</h2>

<p>Evaluate f at both endpoints before calling the solver. What happens if you supply a bracket with no sign change? Explain why a discontinuity can invalidate the existence argument even when endpoint signs differ.</p>

<h2>2. Solve an initial-value problem</h2>

<p>An ODE specifies how a state changes; an initial condition selects a particular solution. Consider dx/dt = 0.5x with x(0) = 1 on 0 ≤ t ≤ 10. This example has a known solution, exp(0.5t), which is useful for checking a numerical solver.</p>

```python
import numpy as np
from scipy.integrate import solve_ivp

def growth(t, state):
    return 0.5 * state

solution = solve_ivp(
    growth, (0.0, 10.0), [1.0], method="RK45",
    rtol=1e-7, atol=1e-9, dense_output=True
)
if not solution.success:
    raise RuntimeError(solution.message)
t = np.linspace(0.0, 10.0, 101)
approx = solution.sol(t)[0]
exact = np.exp(0.5*t)
print(np.max(np.abs(approx - exact)))
```

<p>The requested evaluation points do not force the solver’s internal steps. RK45 adapts those steps using an embedded pair of approximations to estimate local error. It advances with a fifth-order formula and estimates error using a fourth-order formula.</p>

<h2>Choose and check tolerances</h2>

<p>Relative and absolute tolerances control the local error estimate in relation to the state’s scale. They are not a blanket guarantee about the final global error. Repeat with tighter tolerances, compare the trajectory with the exact solution, and report the change in both error and computational effort.</p>

<p>This smooth example is suitable for RK45. Stiff systems may need other methods. A solver’s success flag does not prove that the model, units, initial state, or interpretation are correct.</p>

<h2>Try it</h2>

<p>Change the growth rate to a negative value and compare with the corresponding decaying exponential. Explain why absolute tolerance becomes important when the solution approaches zero.</p>

<h2>3. Interpolate sampled data</h2>

<p>Interpolation constructs a function that passes through supplied data points. A cubic spline is piecewise cubic with continuous first and second derivatives. It differs from fitting a model that may intentionally tolerate residual error.</p>

```python
from scipy.interpolate import CubicSpline

x = np.array([0.0, 1.0, 2.0, 3.0])
y = np.array([0.0, 1.0, 0.0, 1.0])
spline = CubicSpline(x, y, bc_type="natural",
                     extrapolate=False)
assert np.allclose(spline(x), y)
print(spline(1.5))  # approximately 0.5
```

<p>Natural boundary conditions specify zero second derivative at the two endpoints. They are a modeling choice. Smoothness does not guarantee that the curve stays within the range of the samples or preserves monotonicity. Here extrapolation is disabled explicitly; evaluating outside the sampled interval returns NaN.</p>

<h2>Try it</h2>

<p>Plot the spline on a fine grid, mark the original samples, and compare it with straight-line interpolation. Change the boundary condition and inspect the endpoints. If the data are noisy, explain why exact interpolation may be less useful than an appropriate fitted model.</p>

<h2>A reusable workflow</h2>

<p>Define the mathematical problem and assumptions. Choose a numerical representation and solver. Set units and tolerances. Inspect the return status and diagnostics. Compare with a known case, a refined calculation, or an independent formulation before interpreting the result.</p>

<h2>Source and revision</h2>

<p>Zan Ahmad, Johns Hopkins University, Lecture 4 (January 15, 2026). Edited October 2026: classroom transitions removed; convergence checks, explicit tolerances, an exact ODE comparison, and interpolation limits added. Brent’s interpolation step is described more precisely. Course reference: Robert Johansson’s <a href="https://github.com/jrjohansson/scientific-python-lectures">Lectures on scientific computing with Python</a> (CC BY 3.0).</p>

<p>Further reading: the official SciPy documentation for <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root_scalar.html">root_scalar</a>, <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html">solve_ivp</a>, and <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html">CubicSpline</a>.</p>

<p>Download the runnable companion at <a href="https://zanahmad.com/files/teaching-samples/python-scipy.py">zanahmad.com/files/teaching-samples/python-scipy.py</a>.</p>
