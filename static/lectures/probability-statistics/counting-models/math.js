/* Exact model probabilities and reproducible Monte Carlo counts.
 * Browser: window.CountMath. Node: require('./math.js'). No dependencies.
 * Parameters: {n,p}, {N,K,n}, {lambda}; Bernoulli uses {p}.
 * Arrays have indices k=0,...,maxK. Poisson defaults to maxK=18.
 * Omitted tails are reported explicitly, NEVER renormalized or folded into k=maxK.
 * Simulated frequencies are estimates, not exact model probabilities.
 * Empirical variance uses divisor reps, the variance of the empirical distribution.
 */
(function (root) {
  'use strict';
  const DEFAULT_SEED = 20260930;
  const DEFAULT_POISSON_MAX = 18;

  function integer(value, name, minimum = 0) {
    if (!Number.isSafeInteger(value) || value < minimum) {
      throw new RangeError(name + ' must be an integer >= ' + minimum);
    }
    return value;
  }
  function probability(p) {
    if (!Number.isFinite(p) || p < 0 || p > 1) throw new RangeError('p must lie in [0,1]');
  }
  function rate(lambda) {
    if (!Number.isFinite(lambda) || lambda < 0) throw new RangeError('lambda must be finite and >= 0');
  }
  function population(N, K, n) {
    integer(N, 'N', 1); integer(K, 'K'); integer(n, 'n');
    if (K > N || n > N) throw new RangeError('K and n must not exceed N');
  }
  function kindName(kind) {
    const name = String(kind).toLowerCase();
    if (name === 'hypergeometric') return 'hypergeom';
    if (!['bernoulli', 'binomial', 'hypergeom', 'poisson'].includes(name)) {
      throw new RangeError('Unknown model: ' + kind);
    }
    return name;
  }
  function logChoose(n, k) {
    if (!Number.isInteger(k) || k < 0 || k > n) return -Infinity;
    k = Math.min(k, n - k);
    let value = 0;
    for (let j = 1; j <= k; j++) value += Math.log(n - k + j) - Math.log(j);
    return value;
  }
  /** Number of k-subsets. Invalid support gives 0; overflow gives Infinity. */
  function choose(n, k) {
    integer(n, 'n');
    if (!Number.isInteger(k) || k < 0 || k > n) return 0;
    k = Math.min(k, n - k);
    let value = 1;
    for (let j = 1; j <= k; j++) value *= (n - k + j) / j;
    return value <= Number.MAX_SAFE_INTEGER ? Math.round(value) : value;
  }
  function binomialPMF(n, p, k) {
    integer(n, 'n'); probability(p);
    if (!Number.isInteger(k) || k < 0 || k > n) return 0;
    if (p === 0) return k === 0 ? 1 : 0;
    if (p === 1) return k === n ? 1 : 0;
    return Math.exp(logChoose(n, k) + k * Math.log(p) + (n - k) * Math.log1p(-p));
  }
  function hypergeomPMF(N, K, n, k) {
    population(N, K, n);
    if (!Number.isInteger(k) || k < Math.max(0, n - (N - K)) || k > Math.min(n, K)) return 0;
    return Math.exp(logChoose(K, k) + logChoose(N - K, n - k) - logChoose(N, n));
  }
  function poissonPMF(lambda, k) {
    rate(lambda);
    if (!Number.isInteger(k) || k < 0) return 0;
    if (lambda === 0) return k === 0 ? 1 : 0;
    let logFactorial = 0;
    for (let j = 2; j <= k; j++) logFactorial += Math.log(j);
    return Math.exp(-lambda + k * Math.log(lambda) - logFactorial);
  }
  /** Mulberry32 generator; uint32 coercion fixes the sequence across browsers. */
  function seededRng(seed = DEFAULT_SEED) {
    if (!Number.isSafeInteger(seed)) throw new RangeError('seed must be a safe integer');
    let state = seed >>> 0;
    return function () {
      state = (state + 0x6D2B79F5) >>> 0;
      let t = Math.imul(state ^ (state >>> 15), 1 | state);
      t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function sampleBinomial(n, p, rng = Math.random) {
    integer(n, 'n'); probability(p);
    let successes = 0;
    for (let i = 0; i < n; i++) successes += rng() < p ? 1 : 0;
    return successes;
  }
  function sampleHypergeom(N, K, n, rng = Math.random) {
    population(N, K, n);
    let remaining = N, successesRemaining = K, successes = 0;
    for (let i = 0; i < n; i++) {
      if (rng() < successesRemaining / remaining) { successes++; successesRemaining--; }
      remaining--;
    }
    return successes;
  }
  /** Exact Poisson sampling by the product method. Splitting rates above 20
   * avoids exp(-lambda) underflow; sums of independent Poissons add rates. */
  function samplePoisson(lambda, rng = Math.random) {
    rate(lambda);
    let remaining = lambda, total = 0;
    while (remaining > 0) {
      const part = Math.min(remaining, 20), threshold = Math.exp(-part);
      let product = 1, k = 0;
      do { k++; product *= rng(); } while (product > threshold);
      total += k - 1;
      remaining -= part;
    }
    return total;
  }
  function model(kind, params) {
    kind = kindName(kind);
    if (!params || typeof params !== 'object') throw new TypeError('params must be an object');
    if (kind === 'bernoulli' || kind === 'binomial') {
      const n = kind === 'bernoulli' ? 1 : params.n, p = params.p;
      integer(n, 'n'); probability(p);
      return {kind, upper: n, mean: n * p, variance: n * p * (1 - p),
        pmf: k => binomialPMF(n, p, k), sample: rng => sampleBinomial(n, p, rng)};
    }
    if (kind === 'hypergeom') {
      const {N, K, n} = params;
      population(N, K, n);
      const p = K / N;
      return {kind, upper: n, mean: n * p,
        variance: N === 1 ? 0 : n * p * (1 - p) * (N - n) / (N - 1),
        pmf: k => hypergeomPMF(N, K, n, k), sample: rng => sampleHypergeom(N, K, n, rng)};
    }
    const {lambda} = params;
    rate(lambda);
    return {kind, upper: Infinity, mean: lambda, variance: lambda,
      pmf: k => poissonPMF(lambda, k), sample: rng => samplePoisson(lambda, rng)};
  }
  /** Exact model pmf on a displayed range, plus its omitted right-tail mass.
   * mean/variance are the full theoretical moments, not truncated moments. */
  function distribution(kind, params, maxK) {
    const m = model(kind, params);
    maxK = maxK ?? params.maxK ?? (m.upper === Infinity ? DEFAULT_POISSON_MAX : m.upper);
    integer(maxK, 'maxK');
    const probabilities = Array.from({length: maxK + 1}, (_, k) => m.pmf(k));
    const sum = probabilities.reduce((a, p) => a + p, 0);
    // A complete finite support has no omitted mass; roundoff is not a tail.
    const overflowProbability = maxK >= m.upper ? 0 : Math.max(0, 1 - sum);
    return {kind: m.kind, params: {...params}, maxK, probabilities,
      values: probabilities.map((p, k) => ({k, probability: p})),
      overflowProbability, mean: m.mean, variance: m.variance};
  }
  /** Monte Carlo output: raw counts and relative frequencies, with tail counts
   * separately reported. Reusing a seed reproduces this run, not new evidence. */
  function simulate(kind, params, reps = 10000, seed = DEFAULT_SEED) {
    integer(reps, 'reps', 1);
    const m = model(kind, params), rng = seededRng(seed);
    const maxK = params.maxK ?? (m.upper === Infinity ? DEFAULT_POISSON_MAX : m.upper);
    integer(maxK, 'maxK');
    const counts = Array(maxK + 1).fill(0);
    let mean = 0, m2 = 0, overflowCount = 0;
    for (let i = 1; i <= reps; i++) {
      const value = m.sample(rng);
      if (value > maxK) overflowCount++; else counts[value]++;
      const delta = value - mean;
      mean += delta / i;
      m2 += delta * (value - mean);
    }
    return {counts, frequencies: counts.map(count => count / reps), mean,
      variance: m2 / reps, reps, seed, maxK, overflowCount,
      overflowFrequency: overflowCount / reps};
  }
  const api = {choose, binomialPMF, hypergeomPMF, poissonPMF, seededRng,
    sampleBinomial, sampleHypergeom, samplePoisson, distribution, simulate,
    DEFAULT_SEED, DEFAULT_POISSON_MAX};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.CountMath = api;
})(typeof window !== 'undefined' ? window : typeof globalThis !== 'undefined' ? globalThis : this);
