---
title: "High-Dimensional Learning"
description: "Studying low-dimensional coordinates, geometric constraints in autoencoders, and reusable random features for image classification."
layout: single
draft: false
math: true
papers: ["thinner-latent-spaces"]
---

An image or a simulation snapshot can contain thousands of numbers without having thousands of independent degrees of freedom. I’m interested in finding useful representations of that data, and in understanding what the geometry tells us about the coordinates we learn.

## Finding the dimension while learning coordinates

In **Thinner Latent Spaces**, we study conformal autoencoders: networks that reconstruct their input while encouraging different latent coordinates to have orthogonal gradients.

An encoder {{< inline-math >}}e_\theta{{< /inline-math >}} maps an observation {{< inline-math >}}x\in\mathbb{R}^D{{< /inline-math >}} to a latent vector {{< inline-math >}}z\in\mathbb{R}^m{{< /inline-math >}}. A decoder {{< inline-math >}}d_\psi{{< /inline-math >}} maps it back:

{{< equation >}}
z=e_\theta(x),
\qquad \widehat{x}=d_\psi(e_\theta(x)).
{{< /equation >}}

The parameters {{< inline-math >}}\theta{{< /inline-math >}} and {{< inline-math >}}\psi{{< /inline-math >}} are learned. The latent width {{< inline-math >}}m{{< /inline-math >}} is chosen before training; the question is how many of those coordinates the representation actually needs.

The training objective combines reconstruction with a geometric penalty:

{{< equation >}}
\begin{aligned}
\mathcal{L}_{\mathrm{rec}}
&=\frac{1}{N}\sum_{i=1}^{N}\|x_i-\widehat{x}_i\|^2,\\
\mathcal{L}_{\mathrm{orth}}
&=\frac{1}{N}\sum_{i=1}^{N}\sum_{j<k}
\langle\nabla e_j(x_i),\nabla e_k(x_i)\rangle^2,\\
\mathcal{L}&=\mathcal{L}_{\mathrm{rec}}+\lambda\mathcal{L}_{\mathrm{orth}}.
\end{aligned}
{{< /equation >}}

Here {{< inline-math >}}N{{< /inline-math >}} is the number of observations, {{< inline-math >}}e_j{{< /inline-math >}} is the encoder’s {{< inline-math >}}j{{< /inline-math >}}th coordinate, and each gradient is taken with respect to the input. The weight {{< inline-math >}}\lambda{{< /inline-math >}} balances reconstruction and orthogonality.

The geometric idea is that a {{< inline-math >}}d{{< /inline-math >}}-dimensional tangent space can contain at most {{< inline-math >}}d{{< /inline-math >}} independent, mutually orthogonal directions. The paper connects this observation to dimension inference and to coordinates invariant under local group actions. It also distinguishes the ideal tangent-space conditions from the ambient-gradient penalty used in practice: the latter is a useful regularizer, but does not guarantee the correct dimension for every dataset.

## Random features for image classification

With **James Schmidt**, I also explored a simpler representation: sample image patches, keep them fixed as convolutional filters, and learn only the downstream weights. The same feature vector can then be reused for different classification tasks.

A compact way to write the construction is

{{< equation >}}
\phi_k(I)=\operatorname{AvgPool}\!\left(\operatorname{ReLU}(I*P_k)\right),
\qquad f_s(I)=\sum_{k=1}^{K}\beta_{s,k}\phi_k(I).
{{< /equation >}}

{{< inline-math >}}I{{< /inline-math >}} is an image, {{< inline-math >}}P_k{{< /inline-math >}} is a sampled patch, and {{< inline-math >}}*{{< /inline-math >}} denotes convolution. The feature {{< inline-math >}}\phi_k{{< /inline-math >}} pools the activated response to that patch. Each task {{< inline-math >}}s{{< /inline-math >}} has its own fitted weights {{< inline-math >}}\beta_{s,k}{{< /inline-math >}}, while the patches remain fixed. Our experiments compared this approach with a shallow CNN on MNIST and CIFAR-10.

[Read the original poster: Random Convolutional Features and Patch-Based Learning for Multitask Image Classification (PDF)](/files/RandomProjPoster.pdf).
