---
title: "Independence, Bernoulli Trials, and the Binomial Distribution"
layout: "single"
draft: false
url: "/tutorials/independence-bernoulli-binomial/"
description: "EN.553.211 review tutorial for September 28, 2026: independence, covariance, Bernoulli trials, binomial probabilities, and their mean and variance."
---

**EN.553.211 Probability and Statistics for Life Sciences**  
Lecture review · September 28, 2026 · Zan Ahmad

When can we add expectations, when can we add variances, and how do these rules help us count successes? These notes develop the ideas from individual trials, with worked derivations, examples, and binomial histograms.

[**Read or download the complete tutorial (PDF, 16 pages)**](/files/independence-bernoulli-binomial-2026-09-28.pdf)

## A guide to the notes

Read in order for the full argument, or use the page links to revisit a particular idea.

| Topic | Pages | What to focus on |
|---|---|---|
| [Independence, covariance, and variance of a sum](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=2) | 2–6 | Where independence is used, why covariance appears, and why zero covariance does not establish independence. |
| [A single Bernoulli trial](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=7) | 7–8 | Code an outcome as zero or one, then derive its expectation and variance. |
| [From trials to a binomial count](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=8) | 8–10 | Check the model assumptions, count success positions, and attach a probability to each sequence. |
| [Why the probabilities sum to one](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=11) | 11–12 | Connect the probability formula to Pascal's triangle and the binomial theorem. |
| [Histograms and the cereal decision rule](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=13) | 13–15 | Add the relevant bars and distinguish two errors calculated under different true prize rates. |
| [Binomial expectation and variance](/files/independence-bernoulli-binomial-2026-09-28.pdf#page=15) | 15–16 | Write the count as a sum of indicators and identify which calculation uses independence. |

## Ideas to carry forward

**Expectation is linear without independence.** For variance, first account for the covariance terms. Independence makes those terms zero; zero covariance alone does not prove independence.

**A binomial count starts with a model.** We need a fixed number of trials, two outcomes per trial, a common success probability, and mutually independent trials. The coefficient counts possible success positions; the probability factors describe one specified sequence.

**A decision rule is evaluated under an assumed truth.** The cereal example compares false rejection at a 15% prize rate with a missed false claim at a 5% rate. These are different probabilities under different assumptions, not complementary events in one distribution.

## Check your understanding

Before consulting the worked derivations, try to explain:

- Why adding two independent copies of a random variable differs from doubling the same variable.
- Why exactly two successes in five trials has ten possible arrangements.
- Why the binomial mean calculation uses linearity, while the variance calculation uses zero cross covariances.

[Return to all course notes and lectures](/teaching/)
