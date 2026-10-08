---
title: "High Dimensional Statistics"
description: ""
layout: single
draft: false
buttons:
- icon: image
  icon_pack: fas
  name: IDIES '23
  url: /files/RandomProjPoster.pdf
---

<!-- Main content with larger font -->
<div style="text-align: justify; font-size: 1.2rem;">
  High-dimensional statistical learning refers to analyzing data where the number of features or dimensions is very large, often exceeding the number of observations. This approach leverages the fact that despite their high dimensionality, many real-world datasets exhibit low intrinsic dimensionality. High-dimensional learning methods aim to uncover underlying geometric structures—such as manifolds—embedded in the high-dimensional space, allowing data to be meaningfully represented in lower dimensions.

  Mathematically, manifold learning assumes that high-dimensional data points lie on or near a lower-dimensional manifold $\mathcal{M}$ embedded in a high-dimensional space $\mathbb{R}^D$. If the intrinsic dimension of the manifold is $d \ll D$, the data can be mapped from $\mathbb{R}^D$ to a lower-dimensional space $\mathbb{R}^d$ without losing significant structure or meaning. The mapping can be expressed as:

  $$
  f: \mathbb{R}^D \rightarrow \mathbb{R}^d, \quad \text{where } d = \text{dim}(\mathcal{M}).
  $$

  One of the key goals of manifold learning techniques is to preserve local geometric properties, such as distances or angles, during this mapping. Given two data points $x_i, x_j \in \mathbb{R}^D$, the geodesic distance between them on the manifold, $d_{\mathcal{M}}(x_i, x_j)$, captures the shortest path along the manifold. A common approximation in manifold learning is to preserve these geodesic distances in the low-dimensional representation:

  $$
  d_{\mathcal{M}}(x_i, x_j) \approx \lVert f(x_i) - f(x_j) \rVert.
  $$

  Techniques such as **Principal Component Analysis (PCA)**, **Isomap**, **Locally Linear Embedding (LLE)**, and **t-SNE** seek to discover these lower-dimensional structures by projecting the data onto meaningful manifolds. These methods are crucial in tasks like clustering, classification, and visualization, where meaningful patterns can only be observed after reducing the data to its intrinsic dimensions.

  The reduction to intrinsic dimensions also helps overcome the **curse of dimensionality**, which refers to the challenges posed by sparse data distributions in high-dimensional spaces. By learning the low-dimensional manifold $\mathcal{M}$ that underlies the data, high-dimensional statistical learning techniques enable models to generalize better and extract meaningful insights.

  In summary, high-dimensional statistical learning leverages the geometry of data manifolds to perform dimensionality reduction, revealing latent structures and facilitating tasks like clustering, pattern recognition, and visualization:

  $$
  \{ x_1, x_2, \ldots, x_n \} \subset \mathbb{R}^D \quad \xrightarrow{f} \quad \{ y_1, y_2, \ldots, y_n \} \subset \mathbb{R}^d,
  $$

  where $d \ll D$, and the goal is to preserve the manifold's structure as much as possible in the low-dimensional space.
</div>

<!-- Embed PDF Poster -->
<figure style="margin-top: 30px; text-align: center;">
  <iframe 
    src="/files/RandomProjPoster.pdf" 
    width="100%" 
    height="555px" 
    style="border: none;" 
    loading="lazy">
  </iframe>
  <figcaption style="font-size: 1rem; color: gray; margin-top: 10px;">
    My work on random features in machine learning earned first place in the Institute for Data Intensive Engineering and Science (IDIES) Poster Contest in 2023.
  </figcaption>
</figure>

<!-- Back Button at the Bottom with Hover Effect -->
<div style="text-align: left; margin-top: 30px;">
  <a href="javascript:history.back()" 
     class="link dim ba br2 ph3 pv2 mb2 dib gray"
     style="transition: background-color 0.3s ease, color 0.3s ease;">
    ← Back
  </a>
</div>
