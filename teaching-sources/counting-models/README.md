# Counting models: animation release

Zan approved adding the reviewed animations and their reconciled resource links on September 28, 2026. This package is prepared locally for Zan to push. A local commit does not establish public deployment.

## Student resources

- `/lectures/probability-statistics/counting-models/`: introduction and section index.
- `classroom.html`: 47 teaching points, 130 underlying frames. Coin and die examples lead into binomial counts, cereal, Skittles and Poisson; Wednesday resumes at `#cereal-rule`.
- `detailed.html`: 83 teaching points, 240 underlying frames, including proofs, Pascal’s triangle and simulations.
- Existing PDF, tutorial and quiz URLs are preserved. The chronological course card links both versions. The reading guide links 11 detailed sections, and all 12 quiz questions have corresponding detailed links.

The decks share colors and pictures. Next plays one connected explanation and then holds; version links retain the current semantic frame or closest related explanation. Cereal illustrations compare expected counts 7.5 and 2.5 with the fixed cutoff 4. All scripts, mathematical typesetting and fonts are local assets; the linked notes require internet.

## Source and rebuilding

The website’s `static/lectures/probability-statistics/counting-models/` folder contains the complete deployable HTML, JavaScript, CSS, notes map and vendored KaTeX 0.16.11 (license included). Hugo copies this folder without a JavaScript build step.

Authoring source: `Math/Teaching-Media-Lab/FA26-Discrete-Counting-Models-2026-09-30/` in Zan’s Vault. The authoring `build.cjs` writes its preview to the verified external teaching workspace and derives note pages from the auxiliary labels belonging to the reviewed 35-page PDF. The canonical quiz owns its animation mappings in `static/practice/independence-bernoulli-binomial/animation-links.mjs`; preview builds reuse them.

To refresh after an approved revision: run the authoring build; verify its math, playback and links; copy the completed preview assets to this static route, excluding its `quiz/` preview copy. In the landing page, replace `quiz/index.html` with `/practice/independence-bernoulli-binomial/` and add the course-resource return link. Preserve semantic anchors, reconcile tutorial and quiz mappings, and regenerate `release-manifest.json` with asset SHA-256 hashes. Build Hugo to an external preview directory and check the nested website routes before committing.

The manifest records the packaged bytes, unchanged question data and the matching student PDF. The full student LaTeX and separate Wednesday instructor timing guide were not changed or combined for this release. Private teaching cues, reminder drafts, screenshots, reports, caches and runtime dependencies are not published in the animation folder.

## Validation

The four core animation assets match the final reviewed source hashes. Existing review covered all version mappings, representative live switches, cereal mean/cutoff motion, exact box counts and final laptop/phone layouts. Exact-model checks cover enumeration, normalization, moments, deterministic simulation seeds and limiting comparisons. This release also passed the Hugo build, 71 HTTP asset/hash comparisons, all twelve quiz answer/link checks, and 137 full-site navigation/layout assertions at laptop and phone sizes. The existing reading-guide theme loads MathJax multiple times and emits a pre-existing console error; its resource links work, and the new animation pages use their own local KaTeX without that error. The unrelated theme was preserved. Deployment is left to Zan.
