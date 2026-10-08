---
title: "Comparing anatomical shapes"
description: "Elastic geometry gives us a way to compare surfaces without requiring matching mesh vertices."
layout: single
math: true
papers: ["ESA", "abstract-shape-stroke"]
---

How different are two anatomical shapes? Comparing vertex coordinates only works if we already know which points correspond. Elastic shape analysis takes a different route: measure the deformation needed to move from one surface to another.

## Distance as deformation

Let {{< inline-math >}}q(t){{< /inline-math >}} be a path of surfaces joining {{< inline-math >}}q_0{{< /inline-math >}} to {{< inline-math >}}q_1{{< /inline-math >}}, and let {{< inline-math >}}G_q{{< /inline-math >}} measure the cost of a deformation at the surface {{< inline-math >}}q{{< /inline-math >}}. On a unit time interval, the squared geodesic distance is the minimum path energy:

{{< equation >}}
d_G(q_0,q_1)^2
=\inf_{\substack{q(0)=q_0\\q(1)=q_1}}
\int_0^1G_{q(t)}\!\left(\dot q(t),\dot q(t)\right)\,dt.
{{< /equation >}}

The tangent vector {{< inline-math >}}\dot q(t){{< /inline-math >}} describes how the surface moves. An elastic Sobolev metric assigns costs to different kinds of deformation rather than treating every coordinate change alike. The metric is part of the model: it determines what we mean by “similar.”

If we care about shapes rather than their parametrizations, we also optimize over reparametrizations of the target surface. Writing {{< inline-math >}}[q]{{< /inline-math >}} for the shape represented by {{< inline-math >}}q{{< /inline-math >}},

{{< equation >}}
d_{\mathrm{shape}}([q_0],[q_1])
=\inf_{\varphi\in\operatorname{Diff}(M)}
d_G(q_0,q_1\circ\varphi).
{{< /equation >}}

Here {{< inline-math >}}M{{< /inline-math >}} is the common parameter surface and {{< inline-math >}}\operatorname{Diff}(M){{< /inline-math >}} is the set of smooth invertible reparametrizations. This separates a change in surface shape from a change in how its points are labeled.

{{< research-figure src="/images/shape.png" width="1402" height="308" alt="Intermediate surfaces along a computed deformation between two left atrial appendage shapes" caption="A computed deformation path between left atrial appendage surfaces." >}}

## Left atrial appendage morphology

Our computational pipeline uses elastic shape analysis to compare and cluster left atrial appendage surfaces. The appendage has substantial anatomical variation, which makes it a useful setting for studying shape representations beyond a small set of hand-chosen measurements.

The resulting distances and clusters provide a way to describe variation in a collection of shapes. They are not, by themselves, a validated patient-level stroke predictor or a rule for choosing a device. The 2025 *Computers in Biology and Medicine* article describes the pipeline and its evaluation; the earlier preprint remains available from the publication list.

This project sits close to my work on [cardiac flow and electrical models](/research/cardiovascular-modeling/): geometry is both something to compare and the domain on which dynamics unfold.
