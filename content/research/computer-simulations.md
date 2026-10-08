---
title: "A trampoline, some springs, and a ball"
description: "A three-dimensional mechanics project built from spring networks, damping, and frictionless contact."
layout: single
math: true
draft: false
---

A small mechanics project with Chongkun Zhao: build a trampoline from springs and dampers, drop a ball onto it, and follow the motion in three dimensions. Once the basic bounce works, the same model can handle tilted trampolines and sequences of bounces.

{{< research-figure src="/images/tramp1.gif" poster="/images/research-stills/tramp1.png" width="190" height="164" alt="Numerical simulation of a ball bouncing on a deformable trampoline" caption="A spring-network trampoline deforming under a bouncing ball. Simulation from our October 2020 project." >}}

## From a grid to a trampoline

The surface is a square grid of point masses. Neighboring nodes are joined by springs and dampers, and the boundary nodes are fixed. Making the springs' rest lengths shorter than their initial spacing puts the surface under tension before the ball arrives.

For a movable node {{< inline-math >}}i{{< /inline-math >}}, Newton's law gives the force balance:

{{< equation >}}
m_i\ddot{\mathbf x}_i
=\mathbf F_i^{\mathrm{spring}}
+\mathbf F_i^{\mathrm{damping}}
+\mathbf F_i^{\mathrm{contact}}
+m_i\mathbf g.
{{< /equation >}}

Here {{< inline-math >}}\mathbf x_i{{< /inline-math >}} is the node's position, {{< inline-math >}}m_i{{< /inline-math >}} its mass, and {{< inline-math >}}\mathbf g{{< /inline-math >}} gravitational acceleration. Each link pulls or pushes along the line joining its two nodes. If that link has length {{< inline-math >}}\ell_{ij}{{< /inline-math >}}, its tension is

{{< equation >}}
T_{ij}=k_{ij}\left(\ell_{ij}-\ell_{ij}^0\right)
+d_{ij}\frac{d\ell_{ij}}{dt}.
{{< /equation >}}

The stiffness {{< inline-math >}}k_{ij}{{< /inline-math >}} sets the elastic response, {{< inline-math >}}\ell_{ij}^0{{< /inline-math >}} is the rest length, and {{< inline-math >}}d_{ij}{{< /inline-math >}} sets the damping. The damping term removes energy as the link stretches and contracts.

## Adding the ball

The ball is a point mass with a specified radius. Contact is modeled by a repulsive spring force whenever a surface node enters that radius; equal and opposite forces act on the ball and the node. Away from the trampoline, the ball is in free fall. Contact is frictionless, so this model leaves out spin.

The MATLAB simulation updates velocities and then positions at each time step. Changing the grid, spring parameters, drop position, or trampoline orientation gives a useful way to explore the mechanics—and makes for some good animations.

[Simulation of a bouncing ball on a trampoline in 3D — report and MATLAB code, October 2020](/files/Trampoline.pdf) · [More simulation videos](https://www.youtube.com/watch?v=yUCRSj4tcbQ&list=PLQ_KsQ99ZUQOOsvtNYw3o9EywuQ9gaHj3)
