---
title: "Flow and electricity in the heart"
description: "Connecting cardiac anatomy and motion with blood flow, electrical propagation, and clinical observations."
layout: single
math: true
papers: ["scirep", "predicting-the-when", "abstract-stroke-flow"]
---

The heart is a moving domain, an electrical system, and a pump. I work on models that connect these pieces, using anatomical and functional measurements to build simulations for individual hearts.

## Blood flow in a moving atrium

In our 2024 study, we combined cardiac MRI measurements with moving-wall simulations of left atrial blood flow. We compared flow and functional measurements in eight patients: four with a history of stroke and four controls. The aim was to explore candidate markers and how they relate to one another; this small study does not establish a clinical prediction rule.

{{< research-figure src="/images/velocity-volume-rendering.gif" poster="/images/research-stills/velocity-volume-rendering.png" width="1159" height="257" alt="Simulated blood velocity over a cardiac cycle in patient-specific left atrial geometries" caption="Blood flow in moving left atrial geometries reconstructed from imaging." >}}

A useful mathematical starting point is incompressible flow on a moving domain. In an arbitrary Lagrangian–Eulerian description,

{{< equation >}}
\begin{aligned}
\rho\left(\left.\partial_t\mathbf u\right|_\xi
 +((\mathbf u-\mathbf w)\cdot\nabla)\mathbf u\right)
 &= -\nabla p+\mu\Delta\mathbf u,\\
\nabla\cdot\mathbf u&=0.
\end{aligned}
{{< /equation >}}

Here {{< inline-math >}}\mathbf u{{< /inline-math >}} is blood velocity, {{< inline-math >}}\mathbf w{{< /inline-math >}} is mesh velocity, {{< inline-math >}}p{{< /inline-math >}} is pressure, {{< inline-math >}}\rho{{< /inline-math >}} is density, and {{< inline-math >}}\mu{{< /inline-math >}} is dynamic viscosity. The time derivative holds the reference coordinate {{< inline-math >}}\xi{{< /inline-math >}} fixed. The relative velocity {{< inline-math >}}\mathbf u-\mathbf w{{< /inline-math >}} accounts for the moving computational mesh; wall motion enters through the domain and boundary conditions.

The simulations let us examine quantities such as low-velocity regions and blood residence alongside measured atrial function. Their interpretation depends on the imaging, boundary conditions, and assumptions in the flow model.

## Electrical propagation

Cardiac electrical activity brings another set of dynamics to the same complicated anatomy. A schematic monodomain model couples spatial propagation to local cellular states:

{{< equation >}}
\begin{aligned}
C_m\partial_t V&=\nabla\cdot(\mathbf D\nabla V)
-I_{\mathrm{ion}}(V,\mathbf z)+I_{\mathrm{stim}},\\
\partial_t\mathbf z&=F(V,\mathbf z).
\end{aligned}
{{< /equation >}}

{{< inline-math >}}V{{< /inline-math >}} is transmembrane voltage, {{< inline-math >}}\mathbf z{{< /inline-math >}} contains gating and other cellular variables, and {{< inline-math >}}C_m{{< /inline-math >}} is membrane capacitance. The effective conductivity tensor {{< inline-math >}}\mathbf D{{< /inline-math >}} accounts for preferred propagation directions, with geometric factors absorbed into its definition here. Outward ionic current {{< inline-math >}}I_{\mathrm{ion}}{{< /inline-math >}} is positive in this convention; {{< inline-math >}}I_{\mathrm{stim}}{{< /inline-math >}} supplies an applied stimulus.

{{< research-figure src="/images/ep-mult.gif" poster="/images/research-stills/ep-mult.png" width="600" height="300" alt="Electrical wave propagation in several biatrial simulation geometries" caption="Examples of simulated electrical propagation in biatrial geometries." >}}

I have also explored lattice Boltzmann methods for these propagation problems. The animation below shows a biatrial simulation. This numerical work connects naturally to the [neural-operator projects](/research/neural-operators-for-pdes/), where we learn approximate dynamics from simulation data.

{{< research-figure src="/images/heartep2.gif" poster="/images/research-stills/heartep2.png" width="240" height="168" alt="A lattice Boltzmann simulation of electrical propagation across both atria" caption="Biatrial electrical propagation using a lattice Boltzmann method." >}}

## From imaging to time-to-recurrence

A related collaborative project asks when atrial fibrillation recurs after ablation. *Predicting the When* combines biatrial imaging, clinical covariates, and procedural characteristics in a multimodal survival-analysis model. The linked May 2026 manuscript is a medRxiv preprint and has not been peer reviewed.

For a different way of using the anatomy itself, see [elastic shape analysis](/research/riemannian-shape-analysis/).
