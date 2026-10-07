"""From mathematical problems to SciPy solvers
Zan Ahmad, selected course material; edited October 2026.
Edited lecture sample from January 15, 2026 (Lecture 4).
"""

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

from scipy.interpolate import CubicSpline

x = np.array([0.0, 1.0, 2.0, 3.0])
y = np.array([0.0, 1.0, 0.0, 1.0])
spline = CubicSpline(x, y, bc_type="natural",
                     extrapolate=False)
assert np.allclose(spline(x), y)
print(spline(1.5))  # approximately 0.5
