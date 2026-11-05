/* Open Swiss-roll strip: an extruded Archimedean spiral, not a periodic cylinder.
 * Exact intrinsic coordinates (s,z) flatten the induced metric to ds²+dz².
 * Graph edge weights are ambient chords; graph distances only estimate surface distances.
 */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.RollGeometry = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  const a = 0.25, thetaMin = 1.5 * Math.PI, thetaMax = 4.5 * Math.PI;
  const zMin = -2, zMax = 2;
  const primitive = theta => a / 2 * (theta * Math.hypot(1, theta) + Math.asinh(theta));
  const origin = primitive(thetaMin);
  const arc = theta => primitive(theta) - origin;
  const sMin = 0, sMax = arc(thetaMax), arcLength = sMax;
  function inverse(s) {
    if (!Number.isFinite(s)) throw new TypeError('Arc coordinate must be finite.');
    const target = Math.max(sMin, Math.min(sMax, s));
    if (target === 0) return thetaMin;
    if (target === sMax) return thetaMax;
    let lo = thetaMin, hi = thetaMax;
    for (let i = 0; i < 55; i++) {
      const mid = (lo + hi) / 2;
      if (arc(mid) < target) lo = mid; else hi = mid;
    }
    return (lo + hi) / 2;
  }
  function point(theta, z) {
    if (!Number.isFinite(theta) || !Number.isFinite(z)) throw new TypeError('Coordinates must be finite.');
    return { theta, z, x: a * theta * Math.cos(theta), y: a * theta * Math.sin(theta), s: arc(theta) };
  }
  function distance(A, B) { return Math.hypot(arc(B.theta) - arc(A.theta), B.z - A.z); }
  function geodesic(A, B, t) {
    const s = arc(A.theta) + t * (arc(B.theta) - arc(A.theta));
    return point(inverse(s), A.z + t * (B.z - A.z));
  }
  function randomSource(seed) {
    let state = seed >>> 0;
    return function() {
      state += 0x6D2B79F5;
      let t = state;
      t = Math.imul(t ^ t >>> 15, t | 1);
      t ^= t + Math.imul(t ^ t >>> 7, t | 61);
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  const defaultA = Object.freeze({ theta: 1.8 * Math.PI, z: 0 });
  const defaultB = Object.freeze({ theta: 3.8 * Math.PI, z: 0 });
  const chord = (A, B) => {
    const p = point(A.theta, A.z), q = point(B.theta, B.z);
    return Math.hypot(p.x - q.x, p.y - q.y, p.z - q.z);
  };
  function buildGraph({ count = 200, neighbors = 6, seed = 42, A = defaultA, B = defaultB } = {}) {
    if (!Number.isInteger(count) || count < 2 || count > 2000) throw new RangeError('count must be 2–2000, including endpoints.');
    if (!Number.isInteger(neighbors) || neighbors < 0) throw new RangeError('neighbors must be a nonnegative integer.');
    const rng = randomSource(seed), k = Math.min(neighbors, count - 1);
    const samples = [point(A.theta, A.z), point(B.theta, B.z)];
    while (samples.length < count) samples.push(point(inverse(sMax * rng()), zMin + (zMax - zMin) * rng()));
    const edgeMap = new Map();
    for (let i = 0; i < count; i++) {
      const candidates = [];
      for (let j = 0; j < count; j++) if (i !== j) {
        const p = samples[i], q = samples[j];
        candidates.push([j, Math.hypot(p.x - q.x, p.y - q.y, p.z - q.z)]);
      }
      candidates.sort((p, q) => p[1] - q[1] || p[0] - q[0]);
      for (const [j, w] of candidates.slice(0, k)) {
        const lo = Math.min(i, j), hi = Math.max(i, j);
        edgeMap.set(lo + ':' + hi, [lo, hi, w]);
      }
    }
    const edges = [...edgeMap.values()], adj = Array.from({ length: count }, () => []);
    for (const [i, j, w] of edges) { adj[i].push([j, w]); adj[j].push([i, w]); }
    const d = Array(count).fill(Infinity), prev = Array(count).fill(-1), visited = Array(count).fill(false);
    d[0] = 0;
    for (let iteration = 0; iteration < count; iteration++) {
      let u = -1;
      for (let i = 0; i < count; i++) if (!visited[i] && (u < 0 || d[i] < d[u])) u = i;
      if (u < 0 || !Number.isFinite(d[u])) break;
      visited[u] = true;
      if (u === 1) break;
      for (const [v, w] of adj[u]) if (!visited[v] && d[u] + w < d[v]) { d[v] = d[u] + w; prev[v] = u; }
    }
    const path = [];
    if (Number.isFinite(d[1])) { for (let at = 1; at !== -1; at = prev[at]) path.push(at); path.reverse(); }
    return { samples, edges, path, distance: d[1], connected: Number.isFinite(d[1]), count, neighbors: k, seed: seed >>> 0 };
  }
  return { a, thetaMin, thetaMax, zMin, zMax, sMin, sMax, arcLength, defaultA, defaultB,
    point, arc, inverse, geodesic, distance, chord, buildGraph };
});
