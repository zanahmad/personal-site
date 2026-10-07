---
title: "Thinking in Python"
type: curated
layout: sample
url: /teaching/samples/python-thinking/
description: "Object references, data structures, recurring algorithmic patterns, and the cost of working at scientific scale."
---

<p class="sample-context">EN.553.285 Introduction to Scientific Programming in Python | Winter 2026<br>Zan Ahmad · Johns Hopkins University</p>

Edited lecture sample from January 8, 2026 (Lecture 1). Edited October 2026.

[Download PDF (2 pages)](/files/teaching-samples/python-thinking.pdf)

<p>Scientific programming requires more than syntax. We need to explain what code does, choose representations that fit the problem, and anticipate how the work grows with the size of the input. These notes condense the conceptual core of the original lecture.</p>

<h2>1. Names refer to objects</h2>

<p>Assignment binds a name to an object. It does not automatically copy that object. In the example below, both names refer to the same mutable list:</p>

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)  # [1, 2, 3, 4]
```

<p>A function can likewise modify a mutable object passed to it. When mutation is intended, document it; when it is not, return a new result. A shallow copy of a list copies its outer container, but nested objects can still be shared.</p>

```python
def with_extra_value(values, extra):
    return values + [extra]

original = [1, 2]
updated = with_extra_value(original, 10)
assert original == [1, 2]
```

<h2>2. Choose the representation</h2>

<p><b>List:</b> use when order and indexing matter, such as a time series or simulation output. Lists may contain repeated values.</p>

<p><b>Dictionary:</b> use for a mapping from keys to values, such as counts, labeled observations, or configuration settings. Keys must be hashable.</p>

<p><b>Set:</b> use for uniqueness and membership, such as the labels encountered so far. Do not rely on a meaningful iteration order.</p>

<h2>3. Recognize the pattern</h2>

<p>Many tasks combine accumulation (a running total), transformation (unit conversion), filtering (selecting valid observations), counting (frequencies), and two-pass logic (first compute a summary, then use it). Before writing the loop, name the pattern and the information you must keep.</p>

<h2>4. Reason about growth</h2>

<p>Big-O notation describes an asymptotic bound on resource use as input size n increases. It is not a prediction of exact seconds. State what n means, which operation you count, and whether your claim is worst-case, average-case, or amortized.</p>

<p>For ordinary Python lists, indexing and len(a) are O(1); scanning with sum(a), max(a), or a membership test is O(n), assuming constant-cost element operations. Appending is O(1) amortized. Inserting near the front can require O(n) movement.</p>

<p>Dictionary and set lookup are O(1) on average under ordinary hashing assumptions; pathological collisions can worsen that bound. A nested all-pairs comparison is O(n²), while comparison sorting is typically O(n log n). These are growth statements, not guarantees that one implementation wins on every small input.</p>

<h2>A short worked example: frequency counts</h2>

```python
def frequencies(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts

print(frequencies(["rest", "walk", "rest"]))
# {"rest": 2, "walk": 1}
```

<p>For n hashable values and k distinct keys, this uses O(n) expected time and O(k) additional storage under the usual hash-table assumptions. It remembers each count instead of rescanning the entire input for every key.</p>

<h2>Practice prompts</h2>

<p>Explain how aliasing differs from copying. Give an example where a shallow copy still shares an inner list. Choose a data structure for time-ordered readings, unique sensor names, and sensor-name-to-calibration mappings. Finally, compare a two-loop duplicate check with a set-based approach, stating the time and space assumptions.</p>

<h2>From Python to NumPy</h2>

<p>These same patterns appear in array programming. Vectorization can reduce interpreter overhead and use compiled numerical routines, but it does not automatically fix a poor algorithm or eliminate memory costs. Check correctness and array shape before focusing on speed.</p>

<p><b>Source and revision.</b> Zan Ahmad, Johns Hopkins University, Lecture 1 (January 8, 2026). Edited October 2026; classroom logistics removed, the original len(list) complexity error corrected, and average/amortized bounds and shallow-copy behavior clarified. The course reference was Robert Johansson’s <a href="https://github.com/jrjohansson/scientific-python-lectures">Lectures on scientific computing with Python</a> (CC BY 3.0).</p>
