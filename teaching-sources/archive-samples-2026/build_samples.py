from pathlib import Path
import json, re, html, hashlib, shutil, sys
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

SITE=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]
SRC=SITE/'teaching-sources/archive-samples-2026'
OUT=SITE/'static/files/teaching-samples'
for p in (SRC,OUT):p.mkdir(parents=True,exist_ok=True)

docs=[]
def doc(slug,title,course,origin,description,blocks):
    docs.append(dict(slug=slug,title=title,course=course,origin=origin,description=description,blocks=blocks))
def P(s):return ('p',s)
def H(s):return ('h',s)
def C(s):return ('code',s)
def E(s):return ('eq',s)
def B():return ('break','')

doc('heroic-circulation-control','Feedback control in a circulation model',
    'HEROIC: Advanced Topics in Computational Cardiology | Fall 2024',
    'Edited from Project 1, Enhancing the Zero-Dimensional Pulsatile Circulation Model.',
    'A modeling project on pressure feedback, heart-rate control, and time-varying ventricular compliance.',[
P('This project explores how a simplified pulsatile circulation model responds to a change in systemic vascular resistance. The aim is to move from a fixed heart rate to a pressure-sensitive feedback law, then explain what the model can and cannot capture about exercise.'),
H('Before you begin'),
P('Background: ordinary differential equations, the Forward Euler method, and a programming language such as MATLAB or Python. This is a project brief for use with an existing zero-dimensional pulsatile circulation model; the original third-party model implementation is not included. No patient data are needed.'),
P('The original course used the circulation model in the course reference by Peskin and collaborators (section 1.12). Consult the model documentation for state variables, units, valve laws, and ventricular compliance. Keep those conventions consistent throughout the project.'),
H('1. Establish a baseline'),
P('Run the fixed-heart-rate model until its cycles have settled. Record systemic arterial pressure P<sub>sa</sub>, systemic flow Q, and the reference heart rate F<sub>0</sub>. Plot several complete cycles and report cycle-averaged quantities, as well as pulsatile traces. State how you decided that the initial transient had ended.'),
H('2. Perturb systemic resistance'),
P('Represent the start of exercise by lowering systemic resistance R<sub>s</sub>, for example to half its resting value. Later restore R<sub>s</sub>. Keep the heart rate fixed for this comparison. Describe the resulting changes in pressure and flow rather than assuming their direction in advance; the response depends on the complete model and its parameters.'),
P('Use the same initial state, resistance schedule, plotting intervals, and averaging windows in the controlled and uncontrolled simulations. This makes the contribution of feedback interpretable.'),
H('Questions to carry forward'),
P('Which parts of the response follow immediately from the resistance change? Which require physiological regulation that a fixed-heart-rate model omits? What information is lost when you summarize a pulsatile signal only by its mean?'),
B(),
H('3. Filter the pressure signal'),
P('Heart rate should respond to a smoothed pressure signal rather than to every within-beat fluctuation. Let P<sub>f</sub> be filtered pressure and choose a positive filter time constant τ<sub>P</sub>:'),
E('dP<sub>f</sub>/dt = (P<sub>sa</sub> - P<sub>f</sub>) / τ<sub>P</sub>'),
P('Implement this ODE using Forward Euler. Initialize P<sub>f</sub> consistently with the resting state. Explain how τ<sub>P</sub> affects smoothing and lag. Reduce the time step to check numerical sensitivity; the isolated filter is stable for 0 &lt; Δt/τ<sub>P</sub> &lt; 2, but the full coupled model may need a smaller step.'),
H('4. Introduce pressure feedback'),
P('For target mean pressure P* &gt; 0 and dimensionless gain c &lt; 0, use the original project’s feedback law:'),
E('F(t) = F<sub>0</sub> [1 + c (P<sub>f</sub>(t) - P*) / P*]'),
P('Check the sign: a pressure below P* should increase the heart rate. Use compatible time units. Document a physiologically reasonable positive range for F and any bounds imposed; an unrestricted linear controller can request an impossible heart rate. Compare several gains and look for overshoot or oscillation.'),
H('5. Update the cardiac clock'),
P('The baseline compliance waveform C<sub>0</sub>(s) has period T<sub>0</sub> = 1/F<sub>0</sub>. To change heart rate continuously without restarting the waveform at each step, evolve an internal clock s(t):'),
E('ds/dt = F(t)/F<sub>0</sub>,     C(t) = C<sub>0</sub>(s(t))'),
P('Advance s using Forward Euler and evaluate the periodic waveform at its corresponding phase. Apply the clock consistently to both ventricular compliance functions. With F = F<sub>0</sub>, the clock must advance at the original rate; with F = 2F<sub>0</sub>, the waveform must cycle twice as fast.'),
B(),
H('6. Compare complete exercise responses'),
P('Allow the circulation to settle at rest, apply the exercise resistance change, allow a new response to develop, and restore resting resistance. Compare the fixed-rate and feedback-controlled cases. Report heart rate, mean arterial pressure, mean flow, and the corresponding time traces. Explain any remaining mismatch with the physiological behavior you intend to represent.'),
H('Extension: a time-dependent target pressure'),
P('Replace the constant target P* with a prescribed schedule that increases at exercise onset and returns to baseline. Compare an immediate reset at exercise cessation with a delayed reset. Treat this as a modeling experiment about anticipatory control, not a universal physiological law. If you choose target values from the literature, cite the population and conditions.'),
H('Suggested report'),
P('<b>Model and methods.</b> Give the governing changes, parameter values and units, numerical step, initial conditions, and resistance/target schedules.'),
P('<b>Results.</b> Show comparable plots for the fixed-rate, feedback-controlled, and dynamic-target cases. Separate cycle-averaged values from instantaneous values.'),
P('<b>Verification.</b> Demonstrate the baseline-clock and controller-sign checks. Repeat with a smaller time step and explain whether your conclusions change.'),
P('<b>Discussion.</b> Identify what the model captures, what remains absent, and which conclusions depend on your parameter choices. Include your own implementation in an appendix.'),
H('About this public sample'),
P('Course material by Zan Ahmad, Johns Hopkins University. Edited October 2026 for standalone reading: the expired deadline and submission instructions were removed; notation, verification prompts, and numerical/physiological qualifications were clarified. This is a project brief, not a solution key.'),
P('Course context: <a href="https://zanahmad.com/teaching/heroic/">zanahmad.com/teaching/heroic/</a>. This educational model is not a clinical decision tool.')])

doc('heroic-finite-differences','Transport and diffusion with finite differences',
    'HEROIC: Advanced Topics in Computational Cardiology | Fall 2024',
    'Selected and revised from the asynchronous Python tutorial for CFD.',
    'A runnable introduction to one-dimensional linear transport and diffusion, with explicit boundary and stability conditions.',[
P('Finite differences connect a differential equation to a numerical experiment. This selected tutorial studies two distinct processes: transport moves a profile; diffusion smooths it. The examples use Python 3, NumPy, and Matplotlib, and contain only synthetic data.'),
H('1. Linear transport'),
P('For a constant speed c &gt; 0, the equation u<sub>t</sub> + c u<sub>x</sub> = 0 translates an initial profile to the right. On an unbounded domain, the exact solution is u(x,t) = u<sub>0</sub>(x - ct). On our finite interval, we must also prescribe the value entering at the left boundary.'),
P('Let x<sub>i</sub> = i Δx and t<sub>n</sub> = n Δt. A forward difference in time and a backward (upwind) difference in space give:'),
E('u<sub>i</sub><super>n+1</super> = u<sub>i</sub><super>n</super> - λ (u<sub>i</sub><super>n</super> - u<sub>i-1</sub><super>n</super>),     λ = c Δt/Δx'),
P('For this scheme, use 0 ≤ λ ≤ 1. This restriction is part of the numerical method, not an optional plotting preference. If the wave speed is negative, the upwind direction must change.'),
C('import numpy as np\nimport matplotlib.pyplot as plt\n\nx = np.linspace(0.0, 2.0, 81)\ndx = x[1] - x[0]\nc = 1.0\ndt = 0.5 * dx / c\nsteps = 40\ninitial = np.where((x >= 0.5) & (x <= 1.0), 2.0, 1.0)\nu = initial.copy()\nlam = c * dt / dx\nassert 0.0 <= lam <= 1.0\n\nfor _ in range(steps):\n    old = u.copy()\n    u[1:] = old[1:] - lam * (old[1:] - old[:-1])\n    u[0] = 1.0  # prescribed inflow; right end is outflow'),
P('Keep the previous time level in a separate array. Updating in place from left to right would accidentally mix old and new values and change the method.'),
B(),
H('2. Inspect transport error'),
C('t = steps * dt\nexact = np.where((x-c*t >= 0.5) & (x-c*t <= 1.0),\n                 2.0, 1.0)\nplt.plot(x, initial, "--", label="initial")\nplt.plot(x, exact, label="translated profile")\nplt.plot(x, u, label="upwind approximation")\nplt.xlabel("x")\nplt.ylabel("u")\nplt.legend()\nplt.show()'),
P('At this final time the transported pulse has not reached the outflow boundary. Compare its predicted location and edge shape. First-order upwinding generally smears sharp edges through numerical diffusion; this should not be confused with physical diffusion in the model.'),
H('3. Physical diffusion'),
P('The diffusion equation is u<sub>t</sub> = ν u<sub>xx</sub>, where ν &gt; 0 is a diffusivity. A centered second difference gives:'),
E('v<sub>i</sub><super>n+1</super> = v<sub>i</sub><super>n</super> + r (v<sub>i+1</sub><super>n</super> - 2v<sub>i</sub><super>n</super> + v<sub>i-1</sub><super>n</super>)'),
E('r = ν Δt/Δx²,     0 ≤ r ≤ 1/2'),
P('Use the same spatial grid and initial hat profile, but hold both endpoint values at 1. The explicit scheme requires a time step proportional to Δx².'),
C('nu = 0.3\ndt_diff = 0.2 * dx**2 / nu\nr = nu * dt_diff / dx**2\nv = initial.copy()\nassert 0.0 <= r <= 0.5\n\nfor _ in range(100):\n    old = v.copy()\n    v[1:-1] = old[1:-1] + r * (\n        old[2:] - 2.0*old[1:-1] + old[:-2]\n    )\n    v[[0, -1]] = 1.0\n\nplt.plot(x, initial, "--", label="initial")\nplt.plot(x, v, label="diffusion")\nplt.xlabel("x")\nplt.ylabel("u")\nplt.legend()\nplt.show()'),
B(),
H('Experiments'),
P('<b>Translation.</b> Check that the pulse moves by ct. Vary λ while keeping the final physical time fixed. Describe how the edge smearing changes.'),
P('<b>Refinement.</b> Double the spatial resolution. Reduce Δt appropriately and compare at the same physical time. For diffusion, halving Δx requires roughly four times as many steps when r is held fixed.'),
P('<b>Constant solutions.</b> Replace the hat profile by u = 1 everywhere. Both numerical updates should preserve this constant, including the boundaries.'),
P('<b>Stability.</b> In a separate experiment, deliberately exceed the stated restriction. Record the first sign of nonphysical behavior. Restore stable parameters before making accuracy comparisons.'),
H('What this sample does and does not cover'),
P('The full archived tutorial also introduced nonlinear convection and Burgers’ equation. This public selection focuses on the two linear problems so that the stencil, boundary conditions, stability restriction, and physical-time comparison are explicit. Extending a method to shocks requires additional care; copying a linear stencil is not a general shock solver.'),
H('Attribution and revision'),
P('Course adaptation by Zan Ahmad. The sequence and hat-profile exercises follow Lorena A. Barba and Gilbert F. Forsyth, <i>CFD Python: the 12 steps to Navier-Stokes equations</i>, Journal of Open Source Education 1(9), 21 (2018), <a href="https://doi.org/10.21105/jose.00021">doi:10.21105/jose.00021</a>.'),
P('Copyright (c) Barba group. Upstream materials: <a href="https://github.com/barbagroup/CFDPython">github.com/barbagroup/CFDPython</a>. The project README specifies <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> for instructional content; the historical LICENSE also references <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. Code is BSD 3-Clause; the accompanying file retains the notice. This October 2026 selection rewrites the explanation, uses vectorized updates, adds explicit boundaries/stability checks, and corrects the discussion of numerical diffusion. No endorsement by the original authors is implied.'),
P('Download the runnable companion at <a href="https://zanahmad.com/files/teaching-samples/heroic-finite-differences.py">zanahmad.com/files/teaching-samples/heroic-finite-differences.py</a>.')])

doc('python-thinking','Thinking in Python',
    'EN.553.285 Introduction to Scientific Programming in Python | Winter 2026',
    'Edited lecture sample from January 8, 2026 (Lecture 1).',
    'Object references, data structures, recurring algorithmic patterns, and the cost of working at scientific scale.',[
P('Scientific programming requires more than syntax. We need to explain what code does, choose representations that fit the problem, and anticipate how the work grows with the size of the input. These notes condense the conceptual core of the original lecture.'),
H('1. Names refer to objects'),
P('Assignment binds a name to an object. It does not automatically copy that object. In the example below, both names refer to the same mutable list:'),
C('a = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)  # [1, 2, 3, 4]'),
P('A function can likewise modify a mutable object passed to it. When mutation is intended, document it; when it is not, return a new result. A shallow copy of a list copies its outer container, but nested objects can still be shared.'),
C('def with_extra_value(values, extra):\n    return values + [extra]\n\noriginal = [1, 2]\nupdated = with_extra_value(original, 10)\nassert original == [1, 2]'),
H('2. Choose the representation'),
P('<b>List:</b> use when order and indexing matter, such as a time series or simulation output. Lists may contain repeated values.'),
P('<b>Dictionary:</b> use for a mapping from keys to values, such as counts, labeled observations, or configuration settings. Keys must be hashable.'),
P('<b>Set:</b> use for uniqueness and membership, such as the labels encountered so far. Do not rely on a meaningful iteration order.'),
H('3. Recognize the pattern'),
P('Many tasks combine accumulation (a running total), transformation (unit conversion), filtering (selecting valid observations), counting (frequencies), and two-pass logic (first compute a summary, then use it). Before writing the loop, name the pattern and the information you must keep.'),
B(),
H('4. Reason about growth'),
P('Big-O notation describes an asymptotic bound on resource use as input size n increases. It is not a prediction of exact seconds. State what n means, which operation you count, and whether your claim is worst-case, average-case, or amortized.'),
P('For ordinary Python lists, indexing and len(a) are O(1); scanning with sum(a), max(a), or a membership test is O(n), assuming constant-cost element operations. Appending is O(1) amortized. Inserting near the front can require O(n) movement.'),
P('Dictionary and set lookup are O(1) on average under ordinary hashing assumptions; pathological collisions can worsen that bound. A nested all-pairs comparison is O(n²), while comparison sorting is typically O(n log n). These are growth statements, not guarantees that one implementation wins on every small input.'),
H('A short worked example: frequency counts'),
C('def frequencies(values):\n    counts = {}\n    for value in values:\n        counts[value] = counts.get(value, 0) + 1\n    return counts\n\nprint(frequencies(["rest", "walk", "rest"]))\n# {"rest": 2, "walk": 1}'),
P('For n hashable values and k distinct keys, this uses O(n) expected time and O(k) additional storage under the usual hash-table assumptions. It remembers each count instead of rescanning the entire input for every key.'),
H('Practice prompts'),
P('Explain how aliasing differs from copying. Give an example where a shallow copy still shares an inner list. Choose a data structure for time-ordered readings, unique sensor names, and sensor-name-to-calibration mappings. Finally, compare a two-loop duplicate check with a set-based approach, stating the time and space assumptions.'),
H('From Python to NumPy'),
P('These same patterns appear in array programming. Vectorization can reduce interpreter overhead and use compiled numerical routines, but it does not automatically fix a poor algorithm or eliminate memory costs. Check correctness and array shape before focusing on speed.'),
P('<b>Source and revision.</b> Zan Ahmad, Johns Hopkins University, Lecture 1 (January 8, 2026). Edited October 2026; classroom logistics removed, the original len(list) complexity error corrected, and average/amortized bounds and shallow-copy behavior clarified. The course reference was Robert Johansson’s <a href="https://github.com/jrjohansson/scientific-python-lectures">Lectures on scientific computing with Python</a> (CC BY 3.0).')])

doc('python-scipy','From mathematical problems to SciPy solvers',
    'EN.553.285 Introduction to Scientific Programming in Python | Winter 2026',
    'Edited lecture sample from January 15, 2026 (Lecture 4).',
    'Root finding, initial-value problems, and interpolation, with small reproducible examples and diagnostic checks.',[
P('NumPy gives us numerical arrays; SciPy provides algorithms for mathematical tasks. Start by identifying the problem, then choose the solver and inspect its diagnostics. The examples use synthetic data, Python 3, NumPy, and SciPy.'),
H('1. Find a root'),
P('Suppose f(x) = x³ - x - 2. The function is continuous and has opposite signs at x = 1 and x = 2, so there is at least one root between them. A sign-changing bracket is a guarantee of existence under continuity, not a guarantee of uniqueness.'),
C('from scipy import optimize\n\ndef f(x):\n    return x**3 - x - 2\n\nresult = optimize.root_scalar(\n    f, bracket=[1.0, 2.0], method="brentq"\n)\nif not result.converged:\n    raise RuntimeError("Root finder did not converge")\nprint(result.root)\nprint(abs(f(result.root)))'),
P('The root is approximately 1.52138. Inspect both the convergence flag and the residual. A small residual is useful evidence, although for a poorly conditioned problem it does not by itself establish a small error in the root.'),
H('Why Brent’s method is useful'),
P('Brent’s method maintains a bracket and combines bisection with secant and inverse-quadratic interpolation steps. Faster proposals are accepted when appropriate; bracket-based steps provide a safeguard. The method still depends on the mathematical assumptions and sensible tolerances.'),
H('Try it'),
P('Evaluate f at both endpoints before calling the solver. What happens if you supply a bracket with no sign change? Explain why a discontinuity can invalidate the existence argument even when endpoint signs differ.'),
B(),
H('2. Solve an initial-value problem'),
P('An ODE specifies how a state changes; an initial condition selects a particular solution. Consider dx/dt = 0.5x with x(0) = 1 on 0 ≤ t ≤ 10. This example has a known solution, exp(0.5t), which is useful for checking a numerical solver.'),
C('import numpy as np\nfrom scipy.integrate import solve_ivp\n\ndef growth(t, state):\n    return 0.5 * state\n\nsolution = solve_ivp(\n    growth, (0.0, 10.0), [1.0], method="RK45",\n    rtol=1e-7, atol=1e-9, dense_output=True\n)\nif not solution.success:\n    raise RuntimeError(solution.message)\nt = np.linspace(0.0, 10.0, 101)\napprox = solution.sol(t)[0]\nexact = np.exp(0.5*t)\nprint(np.max(np.abs(approx - exact)))'),
P('The requested evaluation points do not force the solver’s internal steps. RK45 adapts those steps using an embedded pair of approximations to estimate local error. It advances with a fifth-order formula and estimates error using a fourth-order formula.'),
H('Choose and check tolerances'),
P('Relative and absolute tolerances control the local error estimate in relation to the state’s scale. They are not a blanket guarantee about the final global error. Repeat with tighter tolerances, compare the trajectory with the exact solution, and report the change in both error and computational effort.'),
P('This smooth example is suitable for RK45. Stiff systems may need other methods. A solver’s success flag does not prove that the model, units, initial state, or interpretation are correct.'),
H('Try it'),
P('Change the growth rate to a negative value and compare with the corresponding decaying exponential. Explain why absolute tolerance becomes important when the solution approaches zero.'),
B(),
H('3. Interpolate sampled data'),
P('Interpolation constructs a function that passes through supplied data points. A cubic spline is piecewise cubic with continuous first and second derivatives. It differs from fitting a model that may intentionally tolerate residual error.'),
C('from scipy.interpolate import CubicSpline\n\nx = np.array([0.0, 1.0, 2.0, 3.0])\ny = np.array([0.0, 1.0, 0.0, 1.0])\nspline = CubicSpline(x, y, bc_type="natural",\n                     extrapolate=False)\nassert np.allclose(spline(x), y)\nprint(spline(1.5))  # approximately 0.5'),
P('Natural boundary conditions specify zero second derivative at the two endpoints. They are a modeling choice. Smoothness does not guarantee that the curve stays within the range of the samples or preserves monotonicity. Here extrapolation is disabled explicitly; evaluating outside the sampled interval returns NaN.'),
H('Try it'),
P('Plot the spline on a fine grid, mark the original samples, and compare it with straight-line interpolation. Change the boundary condition and inspect the endpoints. If the data are noisy, explain why exact interpolation may be less useful than an appropriate fitted model.'),
H('A reusable workflow'),
P('Define the mathematical problem and assumptions. Choose a numerical representation and solver. Set units and tolerances. Inspect the return status and diagnostics. Compare with a known case, a refined calculation, or an independent formulation before interpreting the result.'),
H('Source and revision'),
P('Zan Ahmad, Johns Hopkins University, Lecture 4 (January 15, 2026). Edited October 2026: classroom transitions removed; convergence checks, explicit tolerances, an exact ODE comparison, and interpolation limits added. Brent’s interpolation step is described more precisely. Course reference: Robert Johansson’s <a href="https://github.com/jrjohansson/scientific-python-lectures">Lectures on scientific computing with Python</a> (CC BY 3.0).'),
P('Further reading: the official SciPy documentation for <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root_scalar.html">root_scalar</a>, <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html">solve_ivp</a>, and <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html">CubicSpline</a>.'),
P('Download the runnable companion at <a href="https://zanahmad.com/files/teaching-samples/python-scipy.py">zanahmad.com/files/teaching-samples/python-scipy.py</a>.')])

FONT=Path('/Users/zanahmad/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype')
for family,file in [('Serif','DejaVuSerif.ttf'),('SerifBold','DejaVuSerif-Bold.ttf'),('SerifItalic','DejaVuSerif-Italic.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(family,str(FONT/file)))
pdfmetrics.registerFontFamily('Serif',normal='Serif',bold='SerifBold',italic='SerifItalic',boldItalic='SerifBold')
style=ParagraphStyle('body',fontName='Serif',fontSize=10.2,leading=15,spaceAfter=9,textColor=colors.HexColor('#1f2833'))
heading=ParagraphStyle('heading',parent=style,fontName='SerifBold',fontSize=12,leading=16,spaceBefore=11,spaceAfter=7,keepWithNext=True)
title=ParagraphStyle('title',parent=style,fontName='SerifBold',fontSize=22,leading=27,spaceAfter=12)
small=ParagraphStyle('small',parent=style,fontSize=8.2,leading=12,textColor=colors.HexColor('#536171'))
code=ParagraphStyle('code',fontName='Mono',fontSize=8,leading=11,backColor=colors.HexColor('#f2f4f6'),borderPadding=10,spaceBefore=8,spaceAfter=12)
eq=ParagraphStyle('eq',parent=style,fontSize=10.3,leading=17,leftIndent=14,spaceBefore=4,spaceAfter=10)

def footer(canvas,document):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#cad1d7'));canvas.line(48,44,564,44)
    canvas.setFont('Serif',8);canvas.setFillColor(colors.HexColor('#536171'))
    canvas.drawString(48,30,'Zan Ahmad | Selected teaching material | Edited October 2026')
    canvas.drawRightString(564,30,str(document.page));canvas.restoreState()

manifest=[]
for d in docs:
    story=[Paragraph(d['title'],title),Paragraph(d['course'],small),Paragraph('Zan Ahmad · Johns Hopkins University',small),Spacer(1,10),Paragraph(d['origin'],small),Spacer(1,8)]
    for typ,text in d['blocks']:
        if typ=='break':story.append(PageBreak())
        elif typ=='code':story.append(Preformatted(text,code))
        else:story.append(Paragraph(text,{'p':style,'h':heading,'eq':eq}[typ]))
    path=OUT/(d['slug']+'.pdf')
    SimpleDocTemplate(str(path),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=59,title=d['title'],author='Zan Ahmad',subject=d['course']).build(story,onFirstPage=footer,onLaterPages=footer)
    r=PdfReader(path)
    manifest.append(dict(slug=d['slug'],pages=len(r.pages),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
    md='---\n'+f'title: {json.dumps(d["title"])}\ntype: curated\nlayout: sample\nurl: /teaching/samples/{d["slug"]}/\ndescription: {json.dumps(d["description"])}\n'+'---\n\n'
    md+=f'<p class="sample-context">{d["course"]}<br>Zan Ahmad · Johns Hopkins University</p>\n\n{d["origin"]} Edited October 2026.\n\n'
    md+=f'[Download PDF ({len(r.pages)} pages)](/files/teaching-samples/{d["slug"]}.pdf)'
    if d['slug'] in ['heroic-finite-differences','python-scipy']:md+=f' · [Download Python code](/files/teaching-samples/{d["slug"]}.py)'
    md+='\n\n'
    for typ,text in d['blocks']:
        if typ=='break':continue
        if typ=='h':md+='<h2>'+text+'</h2>\n\n'
        elif typ=='code':md+='```python\n'+text+'\n```\n\n'
        else:md+=f'<p{chr(32)+"class=\"sample-equation\"" if typ=="eq" else ""}>'+text.replace('<super>','<sup>').replace('</super>','</sup>')+'</p>\n\n'
    (SITE/'content/courses').mkdir(exist_ok=True)
    (SITE/'content/courses'/(d['slug']+'.md')).write_text(md.rstrip()+'\n')
(SRC/'samples.json').write_text(json.dumps(docs,indent=2,ensure_ascii=False)+'\n')
(SRC/'pdf-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if Path(__file__).resolve() != (SRC/'build_samples.py').resolve():
    shutil.copy2(__file__,SRC/'build_samples.py')
print(json.dumps(manifest,indent=2))
