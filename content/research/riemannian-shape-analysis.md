---
title: "Riemannian Shape Analysis"
description: ""
layout: single
draft: false
buttons:
- icon: book
  icon_pack: fas
  name: arXiv
  url: https://arxiv.org/abs/2403.08685
---

<!-- Main content with larger font -->
<div style="text-align: justify; font-size: 1.2rem;">

Riemannian shape analysis studies the geometric properties of shapes by embedding them into Riemannian manifolds, where each shape corresponds to a point on a shape space manifold. A shape space manifold, $\mathcal{M}$, is equipped with a Riemannian metric $g$, which defines distances and enables geodesics—curves representing optimal shape transformations—between shapes. Mathematically, given two shapes $S_1$ and $S_2$ on the manifold, their geodesic distance $d(S_1, S_2)$ reflects the least deformation required to morph one shape into another:

$$
d(S_1, S_2) = \inf_{\gamma \in \Gamma} \int_0^1 \sqrt{g(\dot{\gamma}(t), \dot{\gamma}(t))} \, dt,
$$

where $\Gamma$ is the set of all smooth paths connecting $S_1$ and $S_2$, and $\gamma(t)$ is a geodesic path parameterized by $t \in [0, 1]$.
<!-- Second Image/GIF with caption -->
<div style="text-align: center; margin-top: 50px;">
  <img src="/images/shape.png" alt="geodesic" 
       style="width: 500px; height: auto;">
  <p style="font-size: 0.9rem; color: gray; margin-top: 5px;">
    Figure 1: Geodesic between source shape and target shape shown in both directions (symmetric).
  </p>
</div>

In medical image analysis, Riemannian shape spaces are used to study anatomical variability. For example, clustering **left atrial appendages (LAAs)** based on their geometric properties can aid in stratifying patients by anatomical risk factors for stroke. By representing LAAs as points on a shape manifold, one can use geodesic distances to cluster similar shapes and detect outliers:

$$
\{ S_1, S_2, \ldots, S_n \} \mapsto \mathcal{C}_1, \mathcal{C}_2, \ldots, \mathcal{C}_k,
$$

where each $\mathcal{C}_i$ is a cluster of shapes. This approach enables automated classification, patient-specific risk assessment, and treatment planning, such as determining the optimal occlusion device for stroke prevention.




<!-- Back Button at the Bottom with Hover Effect -->
<div style="text-align: left; margin-top: 30px;">
  <a href="javascript:history.back()" 
     class="link dim ba br2 ph3 pv2 mb2 dib gray"
     style="transition: background-color 0.3s ease, color 0.3s ease;">
    ← Back
  </a>
</div>
