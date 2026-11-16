# Implicit pressure and valve consistency

Computational cardiology, lecture 3. Run `python demo.py` with Python, NumPy and Matplotlib. All inputs are synthetic and the script needs no external files.

The first calculation is a closed two-storage reduction with a single ideal valve, changing compliances and zero unstressed volumes. It is not the public two-storage feedback model with external reservoirs. Both candidate valve guesses conserve total volume, but only the open candidate has a consistent pressure inequality. Old pressures are 12 and 4 mmHg; the accepted new pressures are 44/3 and 16/3 mmHg, with flow 14/3 L/min and conserved stressed volume 0.36 L.

The second calculation holds compliance constant and compares backward-Euler relaxation with a separately derived exponential solution. It isolates time error while preserving the same model, state and final physical time. Units are L, mmHg and min internally; the plot uses seconds.

The notebook contains a required matrix-assembly scaffold with a known result. Its default unfilled cell prints a prompt, so the original notebook remains runnable; learners must replace the missing expression to complete the activity. The assigned exercises use different data, and their solutions are not embedded in the code.

Methodological attribution: Hoppensteadt and Peskin, chapter 1, for volume balances and implicit valve consistency. Test the numerical trace, reversed and equal pressures, invariance to the initial valve guess and decreasing refinement error. These checks do not establish clinical validity.
