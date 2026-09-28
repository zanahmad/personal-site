# Chapter 5 cumulative lecture notes

September 28 review and September 30, 2026 read-ahead for EN.553.211.

`notes.tex` is a standalone source; all chart data are inline. Compile with pdfLaTeX (or `latexmk -pdf`) until references settle. The published PDF is `static/files/independence-bernoulli-binomial-2026-09-28.pdf`. Keep that URL stable for the tutorial and quiz. Wednesday starts at cereal part (b), currently page 16.

Run `python3 simulate-hypergeometric.py` to reproduce `Convergence-Data.json` and `Convergence-Figures.tex`. It uses the Python standard library, exact rational probabilities, and 100,000 seeded samples for each population size. The figure fragment is already embedded in `notes.tex`; regenerate and re-inline it if the experiment changes.

Model: fixed sample n=10, K/N=1/2, population N=12,40,400. Exact hypergeometric PMFs and simulated frequencies are compared with Binomial(10,1/2). The mathematical convergence proof and assumptions are in the notes.

After edits, compile and visually review the PDF, then update the tutorial and quiz PDF page links if pagination changes. Build Hugo to a separate output directory to preserve unrelated generated `public/` changes.

## Notes release and Canvas handoff — September 28

The revised student PDF has 35 pages. It includes Bernoulli reminders, an intuitive explanation of equal draw probabilities before the optional marginal-probability terminology, a law-of-total-probability example, the role of dependence in variance, and the Poisson rain example. Instructor pacing stays in the separate private Wednesday guide.

Zan will push this commit. After deployment, verify the PDF hash against the committed file, then post the [Canvas lecture page](Canvas-Lecture-Page.md) and [announcement with the two weeks of office hours](Canvas-Announcement-Draft.md) to Sections 5 and 6. Prepared copy is not a Canvas post; Chrome automation was unavailable in the preparation session.

## Animation links remain hidden

This release includes no new animation assets or links. The public quiz continues to link only to the notes. The private animation-to-question map is retained in the teaching-media source project while the animation is revised.

Before enabling animation links in a later release, reconcile each quiz question and notes section with the finished animation's semantic slide ID, confirm classroom versus detailed destinations, and test every target. Update the animation assets and corresponding links together in that later commit; do not enable links from a preview build.
