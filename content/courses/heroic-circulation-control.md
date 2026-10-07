---
title: "Feedback control in a circulation model"
type: curated
layout: sample
url: /teaching/samples/heroic-circulation-control/
description: "A modeling project on pressure feedback, heart-rate control, and time-varying ventricular compliance."
---

<p class="sample-context">HEROIC: Advanced Topics in Computational Cardiology | Fall 2024<br>Zan Ahmad · Johns Hopkins University</p>

Edited from Project 1, Enhancing the Zero-Dimensional Pulsatile Circulation Model. Edited October 2026.

[Download PDF (3 pages)](/files/teaching-samples/heroic-circulation-control.pdf)

<p>This project explores how a simplified pulsatile circulation model responds to a change in systemic vascular resistance. The aim is to move from a fixed heart rate to a pressure-sensitive feedback law, then explain what the model can and cannot capture about exercise.</p>

<h2>Before you begin</h2>

<p>Background: ordinary differential equations, the Forward Euler method, and a programming language such as MATLAB or Python. This is a project brief for use with an existing zero-dimensional pulsatile circulation model; the original third-party model implementation is not included. No patient data are needed.</p>

<p>The original course used the circulation model in the course reference by Peskin and collaborators (section 1.12). Consult the model documentation for state variables, units, valve laws, and ventricular compliance. Keep those conventions consistent throughout the project.</p>

<h2>1. Establish a baseline</h2>

<p>Run the fixed-heart-rate model until its cycles have settled. Record systemic arterial pressure P<sub>sa</sub>, systemic flow Q, and the reference heart rate F<sub>0</sub>. Plot several complete cycles and report cycle-averaged quantities, as well as pulsatile traces. State how you decided that the initial transient had ended.</p>

<h2>2. Perturb systemic resistance</h2>

<p>Represent the start of exercise by lowering systemic resistance R<sub>s</sub>, for example to half its resting value. Later restore R<sub>s</sub>. Keep the heart rate fixed for this comparison. Describe the resulting changes in pressure and flow rather than assuming their direction in advance; the response depends on the complete model and its parameters.</p>

<p>Use the same initial state, resistance schedule, plotting intervals, and averaging windows in the controlled and uncontrolled simulations. This makes the contribution of feedback interpretable.</p>

<h2>Questions to carry forward</h2>

<p>Which parts of the response follow immediately from the resistance change? Which require physiological regulation that a fixed-heart-rate model omits? What information is lost when you summarize a pulsatile signal only by its mean?</p>

<h2>3. Filter the pressure signal</h2>

<p>Heart rate should respond to a smoothed pressure signal rather than to every within-beat fluctuation. Let P<sub>f</sub> be filtered pressure and choose a positive filter time constant τ<sub>P</sub>:</p>

<p class="sample-equation">dP<sub>f</sub>/dt = (P<sub>sa</sub> - P<sub>f</sub>) / τ<sub>P</sub></p>

<p>Implement this ODE using Forward Euler. Initialize P<sub>f</sub> consistently with the resting state. Explain how τ<sub>P</sub> affects smoothing and lag. Reduce the time step to check numerical sensitivity; the isolated filter is stable for 0 &lt; Δt/τ<sub>P</sub> &lt; 2, but the full coupled model may need a smaller step.</p>

<h2>4. Introduce pressure feedback</h2>

<p>For target mean pressure P* &gt; 0 and dimensionless gain c &lt; 0, use the original project’s feedback law:</p>

<p class="sample-equation">F(t) = F<sub>0</sub> [1 + c (P<sub>f</sub>(t) - P*) / P*]</p>

<p>Check the sign: a pressure below P* should increase the heart rate. Use compatible time units. Document a physiologically reasonable positive range for F and any bounds imposed; an unrestricted linear controller can request an impossible heart rate. Compare several gains and look for overshoot or oscillation.</p>

<h2>5. Update the cardiac clock</h2>

<p>The baseline compliance waveform C<sub>0</sub>(s) has period T<sub>0</sub> = 1/F<sub>0</sub>. To change heart rate continuously without restarting the waveform at each step, evolve an internal clock s(t):</p>

<p class="sample-equation">ds/dt = F(t)/F<sub>0</sub>,     C(t) = C<sub>0</sub>(s(t))</p>

<p>Advance s using Forward Euler and evaluate the periodic waveform at its corresponding phase. Apply the clock consistently to both ventricular compliance functions. With F = F<sub>0</sub>, the clock must advance at the original rate; with F = 2F<sub>0</sub>, the waveform must cycle twice as fast.</p>

<h2>6. Compare complete exercise responses</h2>

<p>Allow the circulation to settle at rest, apply the exercise resistance change, allow a new response to develop, and restore resting resistance. Compare the fixed-rate and feedback-controlled cases. Report heart rate, mean arterial pressure, mean flow, and the corresponding time traces. Explain any remaining mismatch with the physiological behavior you intend to represent.</p>

<h2>Extension: a time-dependent target pressure</h2>

<p>Replace the constant target P* with a prescribed schedule that increases at exercise onset and returns to baseline. Compare an immediate reset at exercise cessation with a delayed reset. Treat this as a modeling experiment about anticipatory control, not a universal physiological law. If you choose target values from the literature, cite the population and conditions.</p>

<h2>Suggested report</h2>

<p><b>Model and methods.</b> Give the governing changes, parameter values and units, numerical step, initial conditions, and resistance/target schedules.</p>

<p><b>Results.</b> Show comparable plots for the fixed-rate, feedback-controlled, and dynamic-target cases. Separate cycle-averaged values from instantaneous values.</p>

<p><b>Verification.</b> Demonstrate the baseline-clock and controller-sign checks. Repeat with a smaller time step and explain whether your conclusions change.</p>

<p><b>Discussion.</b> Identify what the model captures, what remains absent, and which conclusions depend on your parameter choices. Include your own implementation in an appendix.</p>

<h2>About this public sample</h2>

<p>Course material by Zan Ahmad, Johns Hopkins University. Edited October 2026 for standalone reading: the expired deadline and submission instructions were removed; notation, verification prompts, and numerical/physiological qualifications were clarified. This is a project brief, not a solution key.</p>

<p>Course context: <a href="https://zanahmad.com/teaching/heroic/">zanahmad.com/teaching/heroic/</a>. This educational model is not a clinical decision tool.</p>
