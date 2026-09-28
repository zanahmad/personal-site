export const questions = [
  {
    topic: 'Linearity of expectation', page: 2, pages: '2–6',
    prompt: 'Suppose E(X) = 3 and E(Y) = 4. We do not know whether X and Y are independent. What is E(2X + Y)?',
    choices: ['14', '10', '7', 'Cannot determine without independence'], answer: 1,
    hint: 'Which operation averages outcomes? Does repeating the same variable stop that operation from being linear?',
    explanation: 'Expectation is linear: E(2X + Y) = 2E(X) + E(Y) = 2(3) + 4 = 10. Independence is not needed.'
  },
  {
    topic: 'The covariance term', page: 2, pages: '2–6',
    prompt: 'Suppose Var(X) = 2, Var(Y) = 3, and Cov(X,Y) = 1. What is Var(X + Y)?',
    choices: ['5', '6', '7', '9'], answer: 2,
    hint: 'Expand the square of the sum of two centered deviations. How many cross terms appear?',
    explanation: 'Var(X + Y) = Var(X) + Var(Y) + 2Cov(X,Y) = 2 + 3 + 2(1) = 7. The covariance appears twice in the squared sum.'
  },
  {
    topic: 'Zero covariance and dependence', page: 2, pages: '2–6',
    prompt: 'X takes −1, 0, and 1 with equal probabilities, and Y = X². Which statement is correct?',
    choices: ['X and Y are independent because their covariance is zero.', 'X and Y are dependent, even though their covariance is zero.', 'X and Y are dependent and their covariance is 2/3.', 'There is not enough information to determine dependence.'], answer: 1,
    hint: 'Compare P(Y = 0) with P(Y = 0 | X = 0). Separately compute E(XY) − E(X)E(Y).',
    explanation: 'E(X) = 0, E(Y) = 2/3, and E(XY) = E(X³) = 0, so Cov(X,Y) = 0. But P(Y = 0 | X = 0) = 1, while P(Y = 0) = 1/3. Knowing X changes the distribution of Y, so they are dependent.'
  },
  {
    topic: 'Independent copies versus scaling', page: 2, pages: '2–6',
    prompt: 'X has variance 4. X₁ and X₂ are independent copies of X. What are Var(X₁ + X₂) and Var(2X), in that order?',
    choices: ['8 and 8', '16 and 16', '16 and 8', '8 and 16'], answer: 3,
    hint: 'For independent copies, the covariance is zero. For scaling, think about what happens to squared deviations.',
    explanation: 'Independent copies have zero covariance, so Var(X₁ + X₂) = 4 + 4 = 8. Doubling one variable doubles every deviation, so Var(2X) = 2²Var(X) = 16.'
  },
  {
    topic: 'One Bernoulli trial', page: 7, pages: '7–8',
    prompt: 'Let B = 1 if a seed sprouts and B = 0 otherwise. The probability of sprouting is 0.30. What are E(B) and Var(B)?',
    choices: ['0.30 and 0.21', '0.30 and 0.30', '0.70 and 0.21', '1 and 0.30'], answer: 0,
    hint: 'List the two possible values of B². How do they compare with B?',
    explanation: 'B is Bernoulli(0.30). E(B) = 0(0.70) + 1(0.30) = 0.30. Because B² = B, Var(B) = E(B²) − E(B)² = 0.30 − 0.09 = 0.21.'
  },
  {
    topic: 'Checking the binomial model', page: 8, pages: '8–10',
    prompt: 'Four mutually independent trials each have two outcomes. Their success probabilities are 0.10, 0.20, 0.30, and 0.40. Which usual binomial assumption is missing?',
    choices: ['A fixed number of trials', 'Two outcomes per trial', 'A common success probability', 'Independence of the trials'], answer: 2,
    hint: 'In Binomial(n,p), one p is used for all n trials.',
    explanation: 'The success probabilities differ. The usual Binomial(n,p) model requires the same p on every trial, along with a fixed number of trials, two outcomes per trial, and mutual independence.'
  },
  {
    topic: 'Counting success positions', page: 8, pages: '8–10',
    prompt: 'How many different success/failure sequences of length five contain exactly two successes?',
    choices: ['5', '20', '10', '32'], answer: 2,
    hint: 'Choose two of the five positions. Does labeling one success “first chosen” create a different sequence?',
    explanation: 'Choose the two success positions: C(5,2) = 5! / (2! 3!) = 10. The other three positions must be failures. Choosing the positions in order gives 5 × 4 = 20, but counts every pair twice.'
  },
  {
    topic: 'From one sequence to a probability', page: 8, pages: '8–10',
    prompt: 'Five mutually independent trials each have success probability 0.40. What is the probability of exactly two successes?',
    choices: ['0.03456', '0.3456', '0.1600', '0.4000'], answer: 1,
    hint: 'Find the probability of one specified sequence with two successes and three failures, then count all such sequences.',
    explanation: 'One specified sequence has probability 0.40² × 0.60³ = 0.03456. There are C(5,2) = 10 disjoint such sequences, so P(S = 2) = 10 × 0.03456 = 0.3456.'
  },
  {
    topic: 'Why the probabilities sum to one', page: 11, pages: '11–12',
    prompt: 'For S distributed as Binomial(n,p), which identity explains why adding P(S = k) over k = 0, 1, …, n gives 1?',
    choices: ['The binomial theorem gives (p + (1 − p))ⁿ = 1.', 'The expected number of successes np always equals 1.', 'Each possible success count has probability 1/(n + 1).', 'The probabilities of zero successes and n successes always add to 1.'], answer: 0,
    hint: 'Compare the binomial probability formula with the terms in the expansion of (a + b)ⁿ.',
    explanation: 'Summing C(n,k) pᵏ (1 − p)ⁿ⁻ᵏ from k = 0 through n gives (p + (1 − p))ⁿ = 1. The possible counts cover all outcomes without overlap; they need not be equally likely.'
  },
  {
    topic: 'Cereal: changing the decision rule', page: 13, pages: '13–15',
    prompt: 'In 50 independent cereal boxes, X counts prizes. The company claims p ≥ 0.15. Change the rejection rule from X ≤ 4 to X ≤ 3. What happens to false rejection at p = 0.15 and missing a false claim at p = 0.05?',
    choices: ['Both error probabilities increase.', 'Both error probabilities decrease.', 'False rejection increases; missing a false claim decreases.', 'False rejection decreases; missing a false claim increases.'], answer: 3,
    hint: 'The outcome X = 4 moves from “reject” to “do not reject.” What does that do when the claim is true? When it is false?',
    explanation: 'Fewer outcomes trigger rejection. At p = 0.15, false rejection drops from about 0.1121 to 0.0460. At p = 0.05, missing a false claim rises from about 0.1036 to 0.2396. Both changes come from moving X = 4 out of the rejection region.'
  },
  {
    topic: 'Cereal: false rejection', page: 13, pages: '13–15',
    prompt: 'A company claims that at least 15% of its cereal boxes contain prizes. We sample 50 boxes under the lecture’s independent binomial model and reject the claim when X ≤ 4. If the true prize rate is 15%, which probability measures false rejection?',
    choices: ['P(X ≤ 4) at p = 0.15, about 0.1121', 'P(X ≥ 5) at p = 0.15, about 0.8879', 'P(X ≤ 4) at p = 0.05, about 0.8964', 'P(X ≥ 5) at p = 0.05, about 0.1036'], answer: 0,
    hint: 'First choose the true prize rate. Then choose the outcomes on which the rule rejects.',
    explanation: 'At p = 0.15 the claim is true, and the rule rejects when X ≤ 4. Add the Binomial(50,0.15) probabilities for k = 0 through 4 to get 0.1121. This is the largest false-rejection probability over p ≥ 0.15. It is not the probability that the claim is false.'
  },
  {
    topic: 'Cereal: missing a false claim', page: 13, pages: '13–15',
    prompt: 'The company claims a prize rate of at least 15%. Under the independent binomial model for 50 boxes, reject when X ≤ 4. Now the true rate is 5%. Which statement describes the error of not rejecting?',
    choices: ['It is false rejection, with probability about 0.8964.', 'Its probability is 1 − 0.1121, the complement of the error at a 15% rate.', 'It is missing a false claim: P(X ≥ 5) at p = 0.05 is about 0.1036.', 'The probability that the company’s claim is false is 0.1036.'], answer: 2,
    hint: 'At a 5% prize rate, is the claim true? Which values of X make the rule leave the claim unrejected?',
    explanation: 'At p = 0.05 the claim p ≥ 0.15 is false. The rule misses it when X ≥ 5. This probability is 1 minus the sum of the Binomial(50,0.05) probabilities for k = 0 through 4, or about 0.1036. The 0.1121 false-rejection probability uses a different true rate, so these two errors are not complements.'
  }
];
