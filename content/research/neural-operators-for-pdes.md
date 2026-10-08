---
title: "Neural Operators for PDEs"
description: "Learning PDE dynamics across changing geometries using graph Fourier representations and maps to a common reference domain."
layout: single
draft: false
math: true
papers: ["Gfunk", "dimon", "ultrasound-deeponet"]
---

Solving a partial differential equation once is one problem; solving it for many shapes, parameters, and initial conditions is another. I’m interested in what helps a learned model carry useful information from one geometry to the next.

## Learning a family of solutions

A neural operator approximates a map between functions. For a domain {{< inline-math >}}\Omega_\alpha{{< /inline-math >}}, we can write

{{< equation >}}
\mathcal{N}_\theta:\mathcal{A}(\Omega_\alpha)\longrightarrow\mathcal{U}(\Omega_\alpha),
\qquad a\longmapsto u.
{{< /equation >}}

Here {{< inline-math >}}a{{< /inline-math >}} collects the input fields, {{< inline-math >}}u{{< /inline-math >}} is the solution field, {{< inline-math >}}\alpha{{< /inline-math >}} specifies the domain, and {{< inline-math >}}\theta{{< /inline-math >}} contains learned parameters. The spaces {{< inline-math >}}\mathcal{A}{{< /inline-math >}} and {{< inline-math >}}\mathcal{U}{{< /inline-math >}} describe admissible inputs and outputs. Training pairs come from numerical simulations. The challenge is choosing a representation that makes the relationships between those pairs easier to learn.

## Graph Fourier neural kernels

In **G-FuNK**, we study dynamics with a diffusive leading term:

{{< equation >}}
\partial_t u
=\nabla\cdot(\mathbf{K}\nabla u)
+S(u,\mathbf{x},\nabla u).
{{< /equation >}}

The field {{< inline-math >}}u{{< /inline-math >}} evolves over time, {{< inline-math >}}\mathbf{K}{{< /inline-math >}} describes diffusion—including preferred directions—and {{< inline-math >}}S{{< /inline-math >}} collects the remaining reaction or source terms. A weighted graph represents the spatial domain and its diffusion properties. Its Laplacian supplies a Fourier basis adapted to that particular problem:

{{< equation >}}
L=D_g-W=\Psi\Lambda\Psi^{\mathsf T},
\qquad \widehat a=\Psi^{\mathsf T}a.
{{< /equation >}}

{{< inline-math >}}W{{< /inline-math >}} is the matrix of graph weights, {{< inline-math >}}D_g{{< /inline-math >}} contains their row sums, and the columns of {{< inline-math >}}\Psi{{< /inline-math >}} are orthonormal eigenvectors. The diagonal matrix {{< inline-math >}}\Lambda{{< /inline-math >}} holds the eigenvalues. Multiplication by {{< inline-math >}}\Psi^{\mathsf T}{{< /inline-math >}} expresses a field in these graph Fourier coordinates.

The network learns an approximation to the time derivative, which an ODE solver then integrates. We tested this approach on heat flow, reaction–diffusion, and cardiac electrophysiology, including test geometries and fiber fields absent from training.

{{< research-figure src="/images/rf_heat_3_animated.gif" poster="/images/research-stills/rf_heat_3_animated.png" width="757" height="491" alt="Comparison of a numerical heat-equation solution and a neural-operator prediction over time" caption="Anisotropic heat flow: numerical solution and neural-operator prediction." >}}

{{< research-figure src="/images/random_rect_animation_3.gif" poster="/images/research-stills/random_rect_animation_3.png" width="942" height="489" alt="Reaction–diffusion dynamics on a rectangular domain, comparing a numerical solver with the learned model" caption="Reaction–diffusion on a rectangular domain with anisotropic diffusion." >}}

{{< research-figure src="/images/septal_single_atria_animation2.gif" poster="/images/research-stills/septal_single_atria_animation2.png" width="2067" height="993" alt="Electrical propagation across a left atrium, with the numerical solution on the left and prediction on the right" caption="Cardiac electrophysiology on a test atrial geometry and fiber field: numerical solution at left, prediction at right." >}}

## Learning on a reference domain

Another approach is to map different domains into a common coordinate system. Let {{< inline-math >}}\varphi_\alpha:\Omega_0\to\Omega_\alpha{{< /inline-math >}} be a smooth invertible map from a reference domain to a target domain. For a scalar input field, the construction is

{{< equation >}}
u^\alpha\approx
\mathcal{F}_\theta\!\left(\alpha,a^\alpha\circ\varphi_\alpha\right)
\circ\varphi_\alpha^{-1}.
{{< /equation >}}

The input {{< inline-math >}}a^\alpha{{< /inline-math >}} is first expressed on {{< inline-math >}}\Omega_0{{< /inline-math >}}. The latent operator {{< inline-math >}}\mathcal{F}_\theta{{< /inline-math >}} predicts a solution there, and the inverse map returns it to {{< inline-math >}}\Omega_\alpha{{< /inline-math >}}.

The choice of map matters: two maps can align the same shapes while producing very different solution fields in the reference coordinates. Our diffeomorphic-operator study explores this with a two-dimensional Laplace problem, comparing maps that preserve different amounts of the equation’s structure.

## A related application: focused ultrasound

In collaborative work on focused ultrasound, we used a convolutional DeepONet to approximate pressure fields in heterogeneous spinal-cord anatomy. This is another setting where evaluating many simulated configurations motivates a learned surrogate. The linked preprint describes the model and its numerical evaluation.
