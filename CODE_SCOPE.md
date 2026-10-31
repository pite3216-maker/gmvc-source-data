# Scope of the public code

## Included

- A Python script that reads exported CSV files, verifies pruning and error definitions, and recomputes scalar metrics.
- A MATLAB script that plots those exported CSV files.
- Simulation output tables sufficient to inspect the deposited comparisons and verify their numerical summaries.

## Retained by the authors

- The complete local-model training and uncertainty-weighted pruning implementation.
- The full PSO implementation, objective implementation, and optimized controller parameter set.
- The complete online controller, simulation plant implementation, Simulink model, and original MATLAB source collection.
- Private workspace MAT files, execution wrappers, machine-specific logs, and internal preparation scripts.

The public scripts do not call an undistributed function and can be run directly on the deposited files. They do not retrain a model or rerun the controller. The repository description and any code-availability statement should preserve this distinction.
