---
title: "Small models of living systems"
description: "Circulation, branching neurons, and muscle mechanics through compartment models, differential equations, and stochastic simulation."
layout: single
math: true
draft: false
papers: [fontan, gravity-hemodynamics]
---

Some physiological questions become easier to explore with a deliberately small model. A few connected compartments can describe circulation; a tree of cables can carry an action potential; a population of randomly attaching crossbridges can generate muscle force. These projects look at what those models explain, and where their assumptions matter.

## A shortcut through the Fontan circulation

A fenestration gives blood in a Fontan circulation another route back to the heart. It can lower venous pressure and increase flow, while some blood bypasses the lungs and arterial oxygen saturation falls. With Charles Puelz, Charles Peskin, and collaborators, I worked on models of circulation and oxygen transport to study that tradeoff as the opening changes.

{{< research-figure src="/images/fen-fontan.png" width="322" height="284" alt="Diagram of the Fontan circulation with a fenestration connecting the systemic and pulmonary veins" caption="The fenestration creates a shortcut around the lungs, coupling a change in blood flow to a change in oxygen content." >}}

The circulation is represented by compliant compartments joined by resistive connections. Each compartment obeys a pressure–volume relation and conservation of blood volume:

{{< equation >}}
\begin{aligned}
V_i &= V_i^0+C_i(t)P_i,\\
\frac{dV_i}{dt} &= \sum_j\left(Q_{ji}-Q_{ij}\right).
\end{aligned}
{{< /equation >}}

Here {{< inline-math >}}V_i{{< /inline-math >}} is volume, {{< inline-math >}}V_i^0{{< /inline-math >}} is unstressed volume, {{< inline-math >}}C_i{{< /inline-math >}} is compliance, and {{< inline-math >}}P_i{{< /inline-math >}} is transmural pressure. The flow {{< inline-math >}}Q_{ij}{{< /inline-math >}} runs from compartment {{< inline-math >}}i{{< /inline-math >}} to {{< inline-math >}}j{{< /inline-math >}}. Time-varying ventricular compliance supplies the heartbeat; separate flow laws describe valves and the fenestration. Tracking oxygen alongside blood makes it possible to distinguish greater flow from greater oxygen delivery.

[Optimal Fenestration of the Fontan Circulation — published paper, 2022](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2022.867995/full) · [Original project report — November 2021](/reports/Optimal_Fontan_Paper.pdf)

## Letting the model change its heart rate

What changes when heart rate becomes part of the model? In this earlier project with Charles Peskin, I added pressure feedback to a pulsatile circulation model. Filtered arterial pressure is compared with a set point, and the error changes heart rate. A change of clock then lets the ventricular compliance cycle speed up or slow down without restarting the heartbeat.

{{< equation >}}
C(t)=C_0(\tau(t)),\qquad
\frac{d\tau}{dt}=\frac{F(t)}{F_0}.
{{< /equation >}}

The reference compliance function {{< inline-math >}}C_0{{< /inline-math >}} repeats at heart rate {{< inline-math >}}F_0{{< /inline-math >}}. The warped clock {{< inline-math >}}\tau{{< /inline-math >}} advances faster when the controlled rate {{< inline-math >}}F(t){{< /inline-math >}} rises. Exercise is represented by a fall in systemic resistance together with a change in the pressure set point, allowing the model to explore the resulting pressure and flow transients.

{{< research-figure src="/images/propercontrol.png" width="577" height="433" alt="Plots of simulated cardiac output and arterial pressure rising during exercise and returning toward baseline afterward" caption="Pulsatile and filtered cardiac output (top) and arterial pressure (bottom) in the controlled circulation model." >}}

[Variable Heart Rate Method for Modeling Exercise in a Pulsatile Circulation Model — report, December 2020](/files/feedback-control.pdf)

## Circulation under gravity

Gravity changes where blood collects and the pressure needed to return it to the heart. This work splits the circulation into upper and lower compartments, includes partial venous collapse, and models feedback through heart rate and reserve volume. A steady-state reduction lets us examine how body geometry, vascular compliance, and gravitational acceleration affect the circulation.

{{< research-figure src="/images/gravity-schematic.png" width="583" height="428" alt="Compartment model separating upper and lower systemic circulation from the heart and pulmonary circulation" caption="Upper and lower vascular compartments bring height and gravitational pressure differences into the circulation model." >}}

One piece of the model is the hydrostatic pressure difference:

{{< equation >}}
P_{\mathrm{sa}}^{\mathrm{lower}}-P_{\mathrm{sa}}^{\mathrm{upper}}
=\rho g\left(H_{\mathrm{upper}}-H_{\mathrm{lower}}\right).
{{< /equation >}}

Here {{< inline-math >}}P_{\mathrm{sa}}{{< /inline-math >}} is systemic arterial pressure, {{< inline-math >}}\rho{{< /inline-math >}} is blood density, {{< inline-math >}}g{{< /inline-math >}} is vertical gravitational acceleration, and {{< inline-math >}}H{{< /inline-math >}} is height. This relation sits alongside flow conservation and pressure–volume laws. The later collaborative preprint develops the steady-state analysis and includes a single-subject centrifuge calibration case.

[Steady-State Analysis of Gravitational Effects on Hemodynamics — preprint, 2025](https://doi.org/10.21203/rs.3.rs-6603346/v1) · [Mathematical model of the circulation under hypergravity — notes, December 2022](/files/gravity.pdf) · [SIAM News overview](https://www.siam.org/publications/siam-news/articles/circulation-models-assess-the-impacts-of-congenital-heart-defects-and-hypergravity)

## Signals at a branch point

A branching neuron raises a simple question: will an action potential enter both daughter branches, one, or neither? I explored this using Hodgkin–Huxley cable equations on a tree, with a Crank–Nicolson discretization that couples the branches at their junctions. Changing branch diameters and electrotonic lengths produces different propagation patterns.

{{< research-figure src="/images/neuron4.gif" poster="/images/research-stills/neuron4.png" width="275" height="281" alt="Simulation of an action potential traveling through a branching cable model of a neuron" caption="Action-potential propagation on a branching cable tree. The geometry is three-dimensional; voltage evolves along each cable." >}}

Along a cable, voltage and channel gates satisfy

{{< equation >}}
\begin{aligned}
C_m\frac{\partial V}{\partial t}
&=\frac{r}{2\rho_i}\frac{\partial^2V}{\partial x^2}-I_{\mathrm{ion}},\\
\frac{ds}{dt}&=\alpha_s(V)(1-s)-\beta_s(V)s.
\end{aligned}
{{< /equation >}}

Here {{< inline-math >}}V{{< /inline-math >}} is transmembrane voltage, {{< inline-math >}}C_m{{< /inline-math >}} is membrane capacitance per unit area, {{< inline-math >}}r{{< /inline-math >}} is cable radius, and {{< inline-math >}}\rho_i{{< /inline-math >}} is intracellular resistivity. The outward ionic current {{< inline-math >}}I_{\mathrm{ion}}{{< /inline-math >}} depends on voltage and the Hodgkin–Huxley gates {{< inline-math >}}s\in\{m,n,h\}{{< /inline-math >}}; {{< inline-math >}}\alpha_s{{< /inline-math >}} and {{< inline-math >}}\beta_s{{< /inline-math >}} are their opening and closing rates. At a branch point, voltage is shared and current is conserved. Those junction conditions connect local channel dynamics to the geometry of the tree.

[Computer Simulations of 3D Action Potential Propagation in a Branched Cable Network — report, December 2020](/files/AP_Propagation.pdf) · [Simulation videos](https://www.youtube.com/watch?v=3RDD7zvEwiA&list=PLQ_KsQ99ZUQMcyG-MsnAIeghDuepldWs7)

## Muscle force from many small attachments

Muscle force emerges from many small, random attachment-and-detachment events. With Charles Peskin, I compared Monte Carlo simulations of crossbridges in half a sarcomere with a steady-state population model. The comparison connects attachment rates and displacement-dependent forces to the force–velocity curve of a shortening muscle.

{{< research-figure src="/images/Sarcomere.png" width="621" height="402" alt="Sarcomere diagram showing crossbridges between thick and thin filaments and their displacement during sliding" caption="Sarcomere and crossbridge schematic, reproduced in the report from Hoppensteadt and Peskin's Modeling and Simulation in Medicine and the Life Sciences." >}}

The total force is the sum of the contributions from attached crossbridges, expressed as a population integral:

{{< equation >}}
P=n_0\int_{-\infty}^{\infty}p(x)u(x)\,dx,
\qquad
U=\int_{-\infty}^{\infty}u(x)\,dx.
{{< /equation >}}

Here {{< inline-math >}}n_0{{< /inline-math >}} is the available crossbridge population, {{< inline-math >}}p(x){{< /inline-math >}} is the force from a bridge displaced by {{< inline-math >}}x{{< /inline-math >}}, and {{< inline-math >}}u(x){{< /inline-math >}} is the density of attached bridges over displacement. Its integral {{< inline-math >}}U{{< /inline-math >}} is the attached fraction. The report uses constant attachment and detachment rates to compare an explicit steady-state force–velocity relation with the fluctuations in a finite simulated population.

[Mechanical Aspects of Crossbridge Muscle Dynamics — report, May 2020](/files/Crossbridge_Dynamics_Part_1.pdf)
