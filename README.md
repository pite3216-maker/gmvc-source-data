# GMVC simulation data and selected analysis code

This deposit contains simulation output data for a two-mode identification and control experiment and a three-mode DC microgrid control experiment. It includes an English Excel workbook, machine-readable CSV files, a variable dictionary, run provenance, and selected scripts for metric verification and plotting.

The data were regenerated on 31 October 2026 using the existing fixed-seed MATLAB scripts. The dual-model output matches the previously saved numerical log at its displayed precision. The regenerated microgrid control trajectories also agree with the previously saved vector control figure within its coordinate precision; see `PROVENANCE.json` for the comparison and tolerance. These are simulation data, not physical measurements.

## Start here

- `GMVC_Source_Data.xlsx`: summary metrics, dual-model coefficients, selected source-data tables, variable definitions, and run metadata. Numerical summaries are linked to the source-data sheets with Excel formulas.
- `data/`: authoritative numeric exports from MATLAB. CSV files use a header row, decimal points, and no thousands separators. No values were digitized from a plot to fill a missing metric.
- `DATA_DICTIONARY.csv`: definitions, units, and flags for all deposited CSV variables.
- `PROVENANCE.json`: software version, seeds, source-script hashes, generation method, and historical-result checks.
- `code/compute_metrics.py`: independent metric recomputation and consistency checks using only the Python standard library.
- `code/plot_results.m`: plots the deposited data using MATLAB, without running an identification or control algorithm.
- `analysis_results/`: verification results and English plots produced by the two scripts.
- `MANIFEST.csv`: relative file paths, sizes, record counts where applicable, and SHA-256 checksums. The manifest does not hash itself.

## Data files

| File | Records | Content |
| --- | ---: | --- |
| `dual_identification.csv` | 2,000 | Identification input/output sequence, prescribed reliability, injected-outlier flags, and known modes. |
| `dual_fit.csv` | 1,998 | Local predictions before/after pruning, residuals, beliefs, contributions, and final retention flags. |
| `dual_control.csv` | 1,997 | Evaluated dual-model closed-loop steps, references, outputs, control inputs, local predictions, and weights. |
| `dual_summary.json` | one record | Scalar dual-model results and full-precision fitted coefficients. |
| `microgrid_train_raw.csv` | 2,200 | Raw simulated training sequence and known operating modes. |
| `microgrid_validation_raw.csv` | 1,000 | Raw simulated validation sequence and known operating modes. |
| `microgrid_training_diagnostics.csv` | 2,196 | Regressor-aligned sample weights, uncertainty/LOF diagnostics, retention flags, and training beliefs. |
| `microgrid_validation.csv` | 996 | Two-step-ahead local predictions, raw physical residuals, and three distinct weight sequences. |
| `microgrid_residual_display.csv` | 996 | Transformed, dimensionless coordinates used for the residual-space display. |
| `microgrid_control.csv` | 900 | Reference voltage, GMVC/MV voltage and input trajectories, errors, known modes, and load state. |
| `microgrid_optimization_trace.csv` | 65 | Best objective at the end of each PSO iteration. |
| `microgrid_summary.json` | one record | Scalar microgrid performance metrics and run settings. |

## Metric verification

Use Python 3.9 or later. No third-party packages are required:

```bash
python code/compute_metrics.py
```

The script checks recorded errors, pruning counts, target-mode validation RMSE, time spacing, weight normalization, and the displayed-weight mixture. It writes `analysis_results/recomputed_metrics.json` and raises an error if a numerical comparison fails.

For microgrid tracking error `e = voltage - reference`, the original sample-sum definitions are retained:

- `IAE = sum(abs(e)) * Ts`
- `ISE = sum(e**2) * Ts`
- `RMSE = sqrt(mean(e**2))`
- `MAXE = max(abs(e))`

All 900 microgrid control samples, including the initial sample, are included, with `Ts = 0.01 s`. The timestamps run from 0 to 8.99 s. The IAE/ISE definitions are sample sums multiplied by Ts, rather than trapezoidal integration. Local validation RMSE is evaluated using each predictor on samples belonging to its corresponding known target mode.

The dual-model signal units are unspecified in the original synthetic experiment. Its added tracking RMSE is evaluated only over steps 3 through 1999, where the source loop actually computes an output. Initialization steps 1-2 and the uncomputed terminal step 2000 are excluded. No seconds-based IAE or ISE is assigned to that experiment.

## Plotting

In MATLAB, run:

```matlab
run('code/plot_results.m')
```

The script resolves file locations from its own location and writes English PNG figures to `analysis_results`. It was tested with MATLAB R2025a and does not require specialist toolboxes. Its plots use the deposited arrays; they are not an end-to-end simulation rerun.

## Index alignment and display transformations

All sample indices are one-based. Dual-model fitting starts at original index 3 because two lagged samples are needed. Microgrid predictors use values available at index `k`, with target index `k+2`; therefore, 1,000 raw validation samples yield 996 prediction records. `predictor_index` and `target_index` are both provided to prevent shifting predictions against measurements.

The microgrid validation file separates:

1. `residual_belief_*`: smoothed residual-derived weights;
2. `scheduled_belief_*`: weights constructed from prescribed segment positions;
3. `display_belief_*`: the normalized mixture `0.94 * scheduled_belief + 0.06 * residual_belief`.

The displayed weights should not be interpreted as independent evidence of operating-mode recognition. The raw residuals are in volts in `microgrid_validation.csv`. The separate residual-display coordinates are standardized, projected using known target-mode labels, and rescaled for visualization. Display spheres in the original graphic are fitted to those transformed points using their known mode labels, and are distinct from the predictor-training boundaries. The point marked as an outlier in that display is selected by maximum displayed norm; it is not a ground-truth outlier-detection test.

The dual-model script enlarges residual boundaries by a factor of 3 for plotting. `dual_summary.json` supplies the unscaled boundary values and that display factor separately. Convergence iteration numbers are the zero-based iteration labels printed by the source, not a conversion to loop-execution counts.

## Scope of the provided code

The distributed code covers reading deposited data, checking derived quantities, recomputing performance metrics, and plotting. The complete identification/training implementation, PSO search implementation and tuned controller settings, closed-loop controller implementation, Simulink models, private MATLAB workspace files, and original source-code collection are not distributed in this package.

Accordingly, this deposit enables independent inspection of the simulation outputs and recomputation of their reported numerical metrics. It does not provide a complete implementation for regenerating the simulations from scratch. Source-script hashes identify the private versions used to generate the exports.

## Version and repository information

Dataset version: `1.0.0`. Repository: [pite3216-maker/gmvc-source-data](https://github.com/pite3216-maker/gmvc-source-data). The target journal is *International Journal of Systems Science*. No DOI has been assigned. No open-source or open-data license has been selected for this deposit. The complete research implementation is not distributed.
