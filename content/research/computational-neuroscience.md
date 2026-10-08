---
title: "Computational Neuroscience"
description: "Analyzing intracranial EEG signals and behavioral responsiveness to study impaired consciousness during temporal lobe seizures."
layout: single
draft: false
math: true
papers: ["seizure-consciousness", "start-trial"]
---

At Yale, I worked with intracranial EEG recordings to study how seizure dynamics relate to impaired consciousness. The question was how changes in recorded brain activity line up with changes in a person’s responsiveness during a seizure.

## From recordings to frequency bands

Our original poster analyzed 76 medial temporal lobe seizures from eight patients. Behavioral responsiveness was scored independently from video. After removing signal artifacts, we compared EEG power in different frequency bands with a 30-second baseline before seizure onset.

The basic frequency-domain calculation can be summarized as

{{< equation >}}
X_k=\sum_{n=0}^{N-1}x_n\exp\!\left(-\frac{2\pi\mathrm{i}kn}{N}\right),
\qquad P_B\propto\sum_{f_k\in B}|X_k|^2.
{{< /equation >}}

Here {{< inline-math >}}x_n{{< /inline-math >}} are samples from an EEG time window, {{< inline-math >}}N{{< /inline-math >}} is the number of samples, {{< inline-math >}}X_k{{< /inline-math >}} is a discrete Fourier coefficient, and {{< inline-math >}}B{{< /inline-math >}} is a frequency band. The coefficient corresponds to frequency {{< inline-math >}}f_k=kf_s/N{{< /inline-math >}}, where {{< inline-math >}}f_s{{< /inline-math >}} is the sampling rate. The proportionality leaves out the normalization used for a particular power estimate; the point is to track how activity in each band changes around a seizure.

{{< research-figure src="/images/tlebrain.png" width="884" height="304" alt="Two views of brain surfaces with colored maps of EEG activity" caption="Spatial visualization of EEG activity from the temporal-lobe seizure work. The original poster provides the scale and comparison context." >}}

## Seizures and responsiveness

The poster reports differences in signal power and seizure duration between seizures with impaired and spared responsiveness. The aim was to identify signal features associated with impaired consciousness and understand how local seizure activity relates to wider disruption of brain function.

[Read the original AES 2021 poster: Increased Intracranial EEG Power and Duration in Medial Temporal Lobe Seizures with Impaired Consciousness (PDF)](/files/AES-TLE-Poster.pdf).

The related 2025 preprints below extend this line of collaborative work to low- and high-frequency signatures of impaired consciousness and to thalamic stimulation in the START clinical trial. Both are preprints and have not been peer reviewed.
