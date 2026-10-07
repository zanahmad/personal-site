"""Transport and diffusion with finite differences
Zan Ahmad, selected course material; edited October 2026.
Selected and revised from the asynchronous Python tutorial for CFD.

Based on Barba and Forsyth, CFD Python: https://github.com/barbagroup/CFDPython
Copyright (c) Barba group. Vectorized updates and stability checks added.


Copyright (c) 2013 Lorena A. Barba, Gilbert F. Forsyth


Instructional Material
======================

All instructional material is made available under the Creative
Commons Attribution license. You are free:

* to Share---to copy, distribute and transmit the work
* to Remix---to adapt the work

Under the following conditions:

* Attribution---You must attribute the work using "Copyright (c)
  Barba group" (but not in any way that suggests that we
  endorse you or your use of the work).  Where practical, you must
  also include a hyperlink to https://github.com/barbagroup/CFDPython.

With the understanding that:

* Waiver---Any of the above conditions can be waived if you get
  permission from the copyright holder.
* Other Rights---In no way are any of the following rights
  affected by the license:
    * Your fair dealing or fair use rights;
    * The author's moral rights;
    * Rights other persons may have either in the work itself or in
      how the work is used, such as publicity or privacy rights.  *
* Notice---For any reuse or distribution, you must make clear to
  others the license terms of this work. The best way to do this is
  with a link to http://creativecommons.org/licenses/by/3.0/.

For the full legal text of this license, please see:
  http://creativecommons.org/licenses/by/3.0/legalcode



Software
=========

Except where otherwise noted, all software is made available under the
OSI-approved BSD-3-Clause license (https://opensource.org/licenses/BSD-3-Clause):

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or other
materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may
be used to endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.
"""

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
