---
title: "Graph Fourier Neural Kernels (G-FuNK): Learning Solutions of Nonlinear Diffusive Parametric PDEs on Multiple Domains"
subtitle: "Shane E. Loeffler, Zan Ahmad*, ..., Natalia Trayanova, Mauro Maggioni"
excerpt: ""
date: 2024-10-09
time: ""
author: ""
location: ""
featured: false
draft: false
# layout options: single, single-sidebar
layout: single
links:
- icon: door-open
  icon_pack: fas
  name: paper
  url: https://arxiv.org/pdf/2410.04655
---
Predicting time-dependent dynamics of complex systems governed by non-linear partial differential equations (PDEs) with varying parameters and domains is a challenging task motivated by applications across various fields. We introduce a novel family of neural operators based on our Graph Fourier Neural Kernels, designed to learn solution generators for nonlinear PDEs in which the highest-order term is diffusive, across multiple domains and parameters. G-FuNK combines components that are parameter- and domain-adapted with others that are not. The domain-adapted components are constructed using a weighted graph on the discretized domain, where the graph Laplacian approximates the highest-order diffusive term, ensuring boundary condition compliance and capturing the parameter and domain-specific behavior. Meanwhile, the learned components transfer across domains and parameters using our variant Fourier Neural Operators. This approach naturally embeds geometric and directional information, improving generalization to new test domains without need for retraining the network. To handle temporal dynamics, our method incorporates an integrated ODE solver to predict the evolution of the system. Experiments show G-FuNK's capability to accurately approximate heat, reaction diffusion, and cardiac electrophysiology equations across various geometries and anisotropic diffusivity fields. G-FuNK achieves low relative errors on unseen domains and fiber fields, significantly accelerating predictions compared to traditional finite-element solvers.