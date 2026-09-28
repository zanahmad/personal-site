#!/usr/bin/env python3
"""Reproducible hypergeometric-to-binomial teaching figures, Python stdlib only.

Run: python3 simulate-hypergeometric.py
Outputs only lightweight JSON and a LaTeX fragment beside this script.
There are no plots, PDFs, caches, external data files, or NumPy dependencies.
The parent document needs amsmath, xcolor, and PGFPlots (compat=1.18).

Each Monte Carlo repetition resets the population and draws ten times without
replacement. Exactly 100,000 repetitions are performed for each population.
Exact probabilities and exact moments use rational arithmetic; Monte Carlo
results illustrate sampling, and are never used as evidence of the limit.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from math import comb, sqrt
from pathlib import Path
import random


SAMPLE_SIZE = 10
POPULATIONS = (12, 40, 400)
SUCCESS_PROBABILITY = Fraction(1, 2)
REPETITIONS = 100_000
BASE_SEED = 20260930


def hypergeometric_pmf(population: int, successes: int, draws: int) -> list[Fraction]:
    denominator = comb(population, draws)
    lower, upper = max(0, draws - (population - successes)), min(draws, successes)
    return [
        Fraction(comb(successes, k) * comb(population - successes, draws - k), denominator)
        if lower <= k <= upper else Fraction(0)
        for k in range(draws + 1)
    ]


def binomial_pmf(draws: int, probability: Fraction) -> list[Fraction]:
    return [Fraction(comb(draws, k)) * probability**k * (1 - probability)**(draws - k)
            for k in range(draws + 1)]


def moments(pmf: list[Fraction]) -> tuple[Fraction, Fraction]:
    mean = sum((k * mass for k, mass in enumerate(pmf)), Fraction(0))
    variance = sum(((k - mean)**2 * mass for k, mass in enumerate(pmf)), Fraction(0))
    return mean, variance


def simulate(population: int, successes: int, draws: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    counts = [0] * (draws + 1)
    for _ in range(REPETITIONS):
        remaining_successes = successes
        observed = 0
        for draw in range(draws):
            # Reset above for every repetition; deplete inside each sample.
            if rng.random() < remaining_successes / (population - draw):
                remaining_successes -= 1
                observed += 1
        counts[observed] += 1
    return counts


def build_results() -> dict:
    binomial = binomial_pmf(SAMPLE_SIZE, SUCCESS_PROBABILITY)
    binomial_mean, binomial_variance = moments(binomial)
    assert sum(binomial) == 1
    assert binomial_mean == 5 and binomial_variance == Fraction(5, 2)
    result = {
        "sample_size": SAMPLE_SIZE,
        "success_probability": float(SUCCESS_PROBABILITY),
        "repetitions_per_population": REPETITIONS,
        "base_seed": BASE_SEED,
        "seed_rule": "base_seed + population_size",
        "algorithm": "Python random.Random(seed).random(); sequential sampling without replacement; population reset for every repetition",
        "monte_carlo_role": "Illustration only, not a proof; all convergence distances use exact PMFs",
        "binomial": {"pmf": [float(v) for v in binomial],
                     "pmf_fractions": [str(v) for v in binomial],
                     "mean": float(binomial_mean), "variance": float(binomial_variance)},
        "populations": [],
    }
    for population in POPULATIONS:
        successes = population // 2
        pmf = hypergeometric_pmf(population, successes, SAMPLE_SIZE)
        mean, variance = moments(pmf)
        expected_variance = (SAMPLE_SIZE * SUCCESS_PROBABILITY * (1 - SUCCESS_PROBABILITY)
                             * Fraction(population - SAMPLE_SIZE, population - 1))
        assert sum(pmf) == 1 and all(v >= 0 for v in pmf)
        assert mean == SAMPLE_SIZE * SUCCESS_PROBABILITY
        assert variance == expected_variance
        distance = sum((abs(x - y) for x, y in zip(pmf, binomial)), Fraction(0)) / 2
        seed = BASE_SEED + population
        counts = simulate(population, successes, SAMPLE_SIZE, seed)
        empirical = [Fraction(count, REPETITIONS) for count in counts]
        mc_mean, mc_variance = moments(empirical)
        assert sum(counts) == REPETITIONS
        assert all(count == 0 for count, mass in zip(counts, pmf) if mass == 0)
        mean_se = sqrt(float(variance) / REPETITIONS)
        fourth_moment = sum(((k - mean)**4 * mass for k, mass in enumerate(pmf)), Fraction(0))
        variance_se = sqrt(float(fourth_moment - variance**2) / REPETITIONS)
        assert abs(float(mc_mean - mean)) <= 6 * mean_se
        assert abs(float(mc_variance - variance)) <= 6 * variance_se + float(variance) / REPETITIONS
        for mass, observed in zip(pmf, empirical):
            # A broad six-SE check catches simulation defects without demanding
            # that noisy empirical distances decrease monotonically with N.
            se = sqrt(float(mass * (1 - mass)) / REPETITIONS)
            assert abs(float(observed - mass)) <= 6 * se + 1 / REPETITIONS
        result["populations"].append({
            "N": population, "K": successes, "n": SAMPLE_SIZE,
            "sampling_fraction": SAMPLE_SIZE / population,
            "support": [k for k, mass in enumerate(pmf) if mass > 0],
            "seed": seed,
            "exact_pmf": [float(v) for v in pmf],
            "exact_pmf_fractions": [str(v) for v in pmf],
            "exact_mean": float(mean), "exact_variance": float(variance),
            "variance_fraction": str(variance),
            "total_variation_to_binomial": float(distance),
            "total_variation_fraction": str(distance),
            "simulation_counts": counts,
            "simulation_pmf": [float(v) for v in empirical],
            "simulation_mean": float(mc_mean),
            "simulation_variance_ddof0": float(mc_variance),
            "simulation_max_absolute_pmf_error": max(float(abs(x - y)) for x, y in zip(empirical, pmf)),
        })
    populations = result["populations"]
    variances = [p["exact_variance"] for p in populations]
    distances = [p["total_variation_to_binomial"] for p in populations]
    assert 0 < variances[0] < variances[1] < variances[2] < 2.5
    assert distances[0] > distances[1] > distances[2] > 0
    assert 0.34 < distances[0] < 0.35
    assert 0.070 < distances[1] < 0.071
    assert 0.006 < distances[2] < 0.0065
    result["checks"] = {
        "exact_normalization_mean_variance": "passed using Fraction arithmetic",
        "sampling_support_and_count": "passed",
        "simulation_six_standard_error_checks": "passed",
        "variance_and_exact_total_variation_convergence": "passed for the three specified populations",
    }
    return result


def coordinates(values: list[float]) -> str:
    return "\n".join(f"  ({k},{value:.14g})" for k, value in enumerate(values))


def make_fragment(data: dict) -> str:
    parts = [r"""% Generated by simulate-hypergeometric.py. Do not edit numerical data by hand.
% Fragment only: requires amsmath, xcolor, and PGFPlots compat=1.18.
% No groupplots library, external images, data files, or shell escape required.
% Each panel is unbreakable; page breaks are allowed between panels.
\begingroup
\noindent\textbf{A fixed sample from a growing population.}
Keep the sample size $n=10$ and success fraction $p=K/N=1/2$ fixed.
Increase the population through $N=12,40,400$, with $K=N/2$ successes.
Sampling is without replacement within each sample; the population is reset
before the next Monte Carlo repetition.

\smallskip
\noindent Blue bars are the \textbf{exact hypergeometric probabilities}.
Orange open diamonds are the \textbf{exact $\operatorname{Bin}(10,1/2)$ probabilities}.
Black crosses are \textbf{Monte Carlo relative frequencies} from $100{,}000$
repetitions per panel. Marks refer only to integer counts, not a density.
All panels have the same axes, show every count $k=0,\ldots,10$, and omit no mass.
"""]
    for panel in data["populations"]:
        population, successes = panel["N"], panel["K"]
        support = r"\{4,5,6\}" if population == 12 else r"\{0,1,\ldots,10\}"
        parts.append(r"""
\par\medskip
\noindent\begin{minipage}{\linewidth}
\centering
""")
        parts.append(f"{{\\small\\bfseries Population $N={population}$, with $K={successes}$ successes; sample $n=10$}}\\par\n")
        parts.append(f"{{\\small Sample fraction $n/N={100 * panel['sampling_fraction']:.2f}\\%$; exact support ${support}$; exact variance ${panel['exact_variance']:.6f}$}}\\par\n")
        parts.append(r"""\begin{tikzpicture}
\begin{axis}[
  width=0.96\linewidth,height=5.1cm,
  xmin=-0.6,xmax=10.6,ymin=0,ymax=0.60,
  xtick={0,1,...,10},ytick={0,0.1,...,0.6},
  xlabel={Success count $k$ among $10$ draws},ylabel={Probability / frequency},
  tick label style={font=\small},label style={font=\small},
  scaled y ticks=false,grid=major,grid style={gray!15},
  axis line style={gray!60}]
\addplot[ybar,bar shift=0pt,bar width=13pt,
  fill=blue!35,draw=blue!65!black] coordinates {
""")
        parts.append(coordinates(panel["exact_pmf"]) + "\n};\n")
        parts.append(r"""\addplot[only marks,mark=diamond*,mark size=3.8pt,
  color=orange!80!black,mark options={fill=white,line width=1pt}] coordinates {
""")
        parts.append(coordinates(data["binomial"]["pmf"]) + "\n};\n")
        parts.append(r"""\addplot[only marks,mark=x,mark size=2.8pt,
  color=black,mark options={line width=0.8pt}] coordinates {
""")
        parts.append(coordinates(panel["simulation_pmf"]) + "\n};\n")
        parts.append(r"""\end{axis}
\end{tikzpicture}
\end{minipage}
""")
    parts.append(r"""
\par\medskip
\noindent\textbf{Measure the difference using exact probabilities.}
The common mean is $np=5$. Sampling without replacement reduces the variance:
\[
 \operatorname{Var}(X_N)=np(1-p)\frac{N-n}{N-1}
 =2.5\frac{N-10}{N-1}\longrightarrow 2.5.
\]
The total variation distance compares the two complete probability tables:
\[
 d_{\mathrm{TV}}(X_N,B)=\frac12\sum_{k=0}^{10}
 \left|\Pr(X_N=k)-\Pr(B=k)\right|,
 \qquad B\sim\operatorname{Bin}(10,1/2).
\]
It is the largest difference in probability the two models assign to the
same event. Here it is calculated from exact formulas, not simulated counts.

\begin{center}
\small
\begin{tabular}{rrrrr}
\hline
$N$ & $K$ & Sample fraction $n/N$ & Exact variance & Exact $d_{\mathrm{TV}}$\\
\hline
""")
    for panel in data["populations"]:
        parts.append(f"{panel['N']} & {panel['K']} & {100 * panel['sampling_fraction']:.2f}\\% & {panel['exact_variance']:.6f} & {panel['total_variation_to_binomial']:.6f}\\\\\n")
    parts.append(r"""\hline
\multicolumn{3}{l}{Binomial limit, $n=10$, $p=1/2$} & $2.500000$ & $0$\\
\hline
\end{tabular}
\end{center}

\noindent\small\textbf{How to read the comparison.}
For $N=12$, drawing $10$ of the $12$ objects forces the count into $4,5,6$.
The binomial model still assigns mass to $0,\ldots,10$, so it is a poor
approximation. As $N$ grows with $n$ fixed, the sample fraction becomes small,
the variance approaches $2.5$, and the exact bars approach the orange marks.
We are keeping $n$ fixed: this is a binomial limit, not a normal approximation.

\noindent\small\textbf{Simulation illustrates; it does not prove convergence.}
The three populations use seeds $20260942$, $20260970$, and $20261330$
(base seed $20260930$ plus $N$), with $100{,}000$ repetitions each.
The black crosses fluctuate around the exact blue bars. In the last panel,
sampling noise can obscure the small remaining difference from the binomial
model. The limit requires the mathematical PMF argument; neither a simulation
nor three finite comparisons prove it.
\endgroup
""")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent,
                        help="Destination for JSON and LaTeX source only")
    args = parser.parse_args()
    data = build_results()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "Convergence-Data.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
    (args.output_dir / "Convergence-Figures.tex").write_text(make_fragment(data), encoding="utf-8")
    print("All checks passed. Exact comparisons and Monte Carlo diagnostics:")
    for panel in data["populations"]:
        print(f"N={panel['N']:3d} K={panel['K']:3d} support={panel['support'][0]}..{panel['support'][-1]} "
              f"mean={panel['exact_mean']:.6f} variance={panel['exact_variance']:.6f} "
              f"TV={panel['total_variation_to_binomial']:.6f} "
              f"MC_mean={panel['simulation_mean']:.6f} MC_var={panel['simulation_variance_ddof0']:.6f} "
              f"max_PMF_error={panel['simulation_max_absolute_pmf_error']:.6f}")
    print("Wrote Convergence-Data.json and Convergence-Figures.tex; no media generated.")


if __name__ == "__main__":
    main()
