---
title: "Cardiovascular Modeling"
description: ""
layout: single
draft: false
buttons:
- icon: book
  icon_pack: fas
  name: Nature Scientific Reports
  url: https://www.nature.com/articles/s41598-024-59997-2
- icon: image
  icon_pack: fas
  name: HRS '23
  url: /files/HRS23.pdf
  image: /path/to/poster_image.png
---

<!-- Main content with larger font -->

   

<div style="text-align: justify; font-size: 1.2rem;">
   Cardiovascular modeling is the use of mathematical models and computer simulations to replicate the complex interactions of blood flow, heart function, and electrical signaling in the cardiovascular system. My work focuses on developing computer models of the heart’s electrical activity and computational fluid dynamics (CFD) models of the heart to study blood flow patterns. 

   <div style="text-align: center; margin-top: 40px;">
  <img src="/images/velocity-volume-rendering.gif" alt="CFD" 
       style="width: 600; height: auto;">
  <p style="font-size: 0.9rem; color: gray; margin-top: 5px;">
    Figure 1: Cardiac fluid dynamics models of blood flow on patient-specific moving left atrial geometries.
  </p>
</div>
   By integrating these models with patient-specific medical images, we can analyze the unique physiological conditions of individuals, predict disease risks, and optimize treatments. This personalized approach helps improve diagnosis and management of conditions such as arrhythmias, heart failure, and stroke, guiding interventions like stent placement or ablation therapy more effectively.
<!-- Second Image/GIF with caption -->
<div style="text-align: center; margin-top: 50px;">
  <img src="/images/ep-mult.gif" alt="Cardiac Electrophysiology Example" 
       style="width: 650px; height: auto;">
  <p style="font-size: 0.9rem; color: gray; margin-top: 5px;">
    Figure 2: Cardiac electrophysiology (EP) simulations on patient specific biatrial geometries.
  </p>
</div>

CFD simulations involve solving the **Navier-Stokes equations** using finite element methods, such as the **Arbitrary Lagrangian-Eulerian (ALE) method** to handle moving boundaries (Figure 1). The Navier-Stokes equations, governing the fluid dynamics, are given by:

$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{f}$$ $$\nabla \cdot \mathbf{u} = 0$$

where $\mathbf{u}$ is the velocity field, $p$ is the pressure, $\nu$ is the kinematic viscosity, and $\mathbf{f}$ represents body forces (e.g., gravity). 

The **ALE formulation** introduces a mapping from a reference domain $\Omega_0$ to a time-dependent domain $\Omega(t)$. This mapping can be described by:

$$\mathbf{x} = \mathbf{x}(\boldsymbol{\xi}, t)$$

where $ \boldsymbol{\xi} $ are the coordinates in the reference domain $\Omega_0$ and $\mathbf{x}$ are the corresponding coordinates in the physical domain $\Omega(t)$. The mesh velocity $\mathbf{w}$ is defined as:

$$\mathbf{w} = \frac{\partial \mathbf{x}}{\partial t}$$

and the velocity field in the ALE formulation becomes:

$$\frac{d \mathbf{u}}{dt} = \frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} - \mathbf{w}) \cdot \nabla \mathbf{u}$$

This formulation ensures that the mesh deforms smoothly with the boundary motion, maintaining numerical stability in the simulation.

---

For cardiac electrophysiology (EP) simulations, the **monodomain anisotropic reaction-diffusion equation** is solved either using finite-element method (Figure 2) or the **Lattice Boltzmann Method (LBM)** (Figure 3). The monodomain equation is:

$$\frac{\partial V}{\partial t} = \nabla \cdot (\mathbf{D} \nabla V) + I_{\text{ion}}(V, w)$$

$$\frac{dw}{dt} = f(V, w)$$

where $ V $ is the transmembrane potential, $\mathbf{D}$ is the anisotropic diffusion tensor, $I_{\text{ion}}$ represents the ionic currents, and $w$ denotes the state variables for ion channels.

The **LBM** discretizes these equations by evolving particle distribution functions $f_i(\mathbf{x}, t)$ along characteristic directions:

$$f_i(\mathbf{x} + \mathbf{c}_i \Delta t, t + \Delta t) - f_i(\mathbf{x}, t) = -\frac{1}{\tau} \left( f_i(\mathbf{x}, t) - f_i^{\text{eq}}(\mathbf{x}, t) \right)$$

where $f_i^{\text{eq}}$ is the equilibrium distribution, $\mathbf{c}_i$ are discrete velocities, and $\tau$ is the relaxation time controlling diffusion. This method captures the anisotropic nature of cardiac tissue efficiently and facilitates large-scale simulations of cardiac dynamics through its compatibility with high performance parallel computing.
<div style="text-align: center; margin-top: 50px;">
  <img src="/images/heartep2.gif" alt="Cardiac Electrophysiology Example" 
       style="width: 300px; height: auto;">
  <p style="font-size: 0.9rem; color: gray; margin-top: 5px;">
    Figure 3: Cardiac electrophysiology (EP) simulations on patient-specific biatrial geometry using the Lattice Boltzmann method.
  </p>
</div>
<!-- Back Button at the Bottom with Hover Effect -->
<div style="text-align: left; margin-top: 30px;">
  <a href="javascript:history.back()" 
     class="link dim ba br2 ph3 pv2 mb2 dib gray"
     style="transition: background-color 0.3s ease, color 0.3s ease;">
    ← Back
  </a>
</div>
