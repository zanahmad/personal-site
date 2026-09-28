---
title: "Counting Models"
layout: "single"
draft: false
url: "/tutorials/independence-bernoulli-binomial/"
description: "EN.553.211 September 28 and 30 lecture notes: independence, Bernoulli sums, binomial and hypergeometric counting, simulation, and Poisson distributions."
---

**EN.553.211 Probability and Statistics for Life Sciences**  
Monday review and Wednesday read-ahead · September 28 and 30, 2026 · Zan Ahmad

When can we add expectations, when can we add variances, and how do the sampling assumptions change a count's distribution? These cumulative notes connect independence and Bernoulli trials to binomial, hypergeometric, and Poisson models, with worked derivations and simulation figures.

[**Read or download the complete notes (PDF, 35 pages)**](/files/independence-bernoulli-binomial-2026-09-28.pdf)

[**Try the interactive practice quiz — 12 questions with hints and explanations**](/practice/independence-bernoulli-binomial/)

**Wednesday starts at [cereal example, part (b), page 16](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=16).** We will use the binomial theorem to check that binomial probabilities sum to one, set the success probability to one-half to connect the formula to counting, compare sampling with and without replacement, and introduce Poisson counts with a rain example. The combined notes include additional derivations and examples for review beyond what we will cover in class. The quiz reviews the earlier material through cereal.

## A guide to the notes

| Topic | Pages | What to focus on |
|---|---|---|
| [Independence, covariance, and variance of a sum](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=3) | 3–8 | Where independence is used, why covariance appears, and why zero covariance does not establish independence. |
| [A single Bernoulli trial](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=8) | 8–9 | Code an outcome as zero or one, then derive its expectation and variance. |
| [Binomial trials, counting, and normalization](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=9) | 9–14 | Count success positions, assign probabilities to sequences, and sum the pmf to one. |
| [The cereal decision rule](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=14) | 14–17 | Keep the rule fixed while changing the true prize rate. Wednesday resumes at part (b), page 16. |
| [A binomial count as a Bernoulli sum](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=17) | 17–18 | Linearity gives the expectation; independence removes covariance terms from the variance. |
| [Fair-coin counting and sampling with replacement](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=18) | 18–20 | Set p = 1/2 to get C(n,k)/2^n, then compare the counting assumptions. |
| [Hypergeometric probabilities and moments](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=20) | 20–25 | Distinguish population N, sample n, population successes K, and sample successes k. See why each draw has success probability K/N and where dependence enters the variance. |
| [Hypergeometric convergence and simulation](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=25) | 25–28 | Hold n fixed while the population grows. Compare exact probabilities and 100,000 simulated samples for each population. |
| [Poisson: example, pmf, and normalization](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=28) | 28–29 | Start with many rare opportunities; identify the expected count and check that the probabilities sum to one. |
| [Poisson derivation, exposure, and moments](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=29) | 29–34 | Keep np finite in the binomial limit, scale the observation window, and derive mean and variance. |
| [Final insurance example and model comparison](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=34) | 34–35 | Infer the Poisson parameter from a probability ratio and select models from their assumptions. |

## Ideas to carry forward

**Expectation is linear without independence.** Variance includes covariance terms. Independent Bernoulli trials make those terms zero; sampling without replacement introduces a finite-population correction. Each draw is still a Bernoulli success/failure variable with probability K/N before earlier outcomes are revealed. The notes explain this with a shuffled row and the law of total probability before introducing the term “marginal probability.”

**Choose the experiment before the formula.** Independent binary trials with a common success probability give a binomial count. A uniform sample without replacement from a fixed population gives a hypergeometric count. Many rare independent opportunities motivate Poisson.

**Keep track of what stays fixed.** For the hypergeometric-to-binomial limit, the sample size stays fixed while the population grows. For the binomial-to-Poisson limit, the number of opportunities grows, the success probability shrinks, and their product approaches the desired expected count.

**Simulation illustrates the result.** The figures distinguish exact pmfs from simulated frequencies; the notes also give the mathematical convergence argument.

[Return to all course notes and lectures](/teaching/probability-statistics/)
