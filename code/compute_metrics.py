"""Validate deposited CSV data and recompute metrics, without running a controller.

Python 3.9+; standard library only. Run from any working directory:
    python path/to/code/compute_metrics.py
"""
from pathlib import Path
import csv
import json
import math

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def numbers(rows, name):
    result = [float(row[name]) for row in rows]
    if not all(math.isfinite(value) for value in result):
        raise ValueError(f"Non-finite values in {name}")
    return result


def is_true(value):
    return str(value).strip().lower() in {"1", "true"}


def error_metrics(error, sample_interval=None):
    if not error:
        raise ValueError("Empty evaluation window")
    count = len(error)
    absolute_sum = math.fsum(abs(e) for e in error)
    squared_sum = math.fsum(e * e for e in error)
    output = {"count": count, "MAE": absolute_sum / count,
              "RMSE": math.sqrt(squared_sum / count),
              "MAXE": max(abs(e) for e in error)}
    if sample_interval is not None:
        output.update(IAE=absolute_sum * sample_interval,
                      ISE=squared_sum * sample_interval)
    return output


def assert_close(actual, expected, label, atol=1e-10, rtol=1e-9):
    if not math.isclose(actual, expected, rel_tol=rtol, abs_tol=atol):
        raise AssertionError(f"{label}: {actual} differs from {expected}")


def main():
    dual_summary = json.loads((DATA / "dual_summary.json").read_text())
    grid_summary = json.loads((DATA / "microgrid_summary.json").read_text())
    dual_fit = read_csv("dual_fit.csv")
    dual_raw = read_csv("dual_identification.csv")
    dual_control = read_csv("dual_control.csv")
    grid_control = read_csv("microgrid_control.csv")
    validation = read_csv("microgrid_validation.csv")
    train_fit = read_csv("microgrid_training_diagnostics.csv")
    keep = [is_true(row["retained"]) for row in dual_fit]
    injected = {int(row["sample_index"]) for row in dual_raw if is_true(row["injected_outlier"])}
    pruned = {int(row["sample_index"]) for row in dual_fit if not is_true(row["retained"])}
    dual = {"fit_samples": len(dual_fit), "retained": sum(keep),
            "pruned": len(keep) - sum(keep), "retention_ratio": sum(keep) / len(keep),
            "injected_outliers": len(injected), "injected_outliers_pruned": len(injected & pruned)}
    assert len(dual_raw) == dual_summary["raw_samples"]
    assert dual["fit_samples"] == dual_summary["fit_samples"]
    assert dual["retained"] == dual_summary["retained"]
    assert dual["pruned"] == dual_summary["pruned"]
    assert injected & pruned == set(dual_summary["pruned_outlier_indices"])
    for row in dual_fit:
        for mode in (1, 2):
            assert_close(float(row[f"residual_{mode}_after"]),
                         float(row["target"]) - float(row[f"prediction_{mode}_after"]), "dual residual")
    dual_errors = [float(row["output"]) - float(row["reference"]) for row in dual_control]
    assert [int(row["step"]) for row in dual_control] == list(range(3, 2000))
    for row, err in zip(dual_control, dual_errors):
        assert_close(float(row["error"]), err, "dual error")
    dual["control"] = error_metrics(dual_errors)
    assert_close(dual["control"]["RMSE"], dual_summary["control_RMSE"], "dual RMSE")
    dt = grid_summary["sample_interval_s"]
    times = numbers(grid_control, "time_s")
    assert len(grid_control) == grid_summary["control_samples"]
    for previous, current in zip(times, times[1:]):
        assert_close(current - previous, dt, "sample interval")
    grid = {}
    for controller in ("gmvc", "mv"):
        err = [float(row[f"{controller}_voltage_V"]) - float(row["reference_V"]) for row in grid_control]
        for row, value in zip(grid_control, err):
            assert_close(float(row[f"{controller}_error_V"]), value, controller + " stored error")
        grid[controller] = error_metrics(err, dt)
        for key in ("IAE", "ISE", "RMSE", "MAXE"):
            assert_close(grid[controller][key], grid_summary[controller][key], controller + " " + key)
    grid["reduction_vs_mv"] = {}
    for key in ("IAE", "ISE", "RMSE", "MAXE"):
        baseline = grid["mv"][key]
        grid["reduction_vs_mv"][key] = None if baseline == 0 else (baseline - grid["gmvc"][key]) / baseline
    grid["validation"] = []
    for mode in (1, 2, 3):
        subset = [row for row in validation if int(row["target_mode"]) == mode]
        if len(subset) < 10:
            subset = validation
        err = [float(row["actual_voltage_V"]) - float(row[f"prediction_{mode}_V"]) for row in subset]
        result = error_metrics(err)
        assert_close(result["RMSE"], grid_summary["validation_rmse_by_mode"][mode - 1], "validation RMSE")
        grid["validation"].append({"mode": mode, **result})
    grid["training"] = {"fit_samples": len(train_fit), "retained": sum(is_true(row["retained"]) for row in train_fit)}
    assert grid["training"]["retained"] == grid_summary["retained"]
    for row in validation:
        for prefix in ("residual_belief", "scheduled_belief", "display_belief"):
            weights = [float(row[f"{prefix}_{mode}"]) for mode in (1, 2, 3)]
            assert all(0 <= weight <= 1 for weight in weights)
            assert_close(math.fsum(weights), 1, prefix + " normalization")
        for mode in (1, 2, 3):
            expected = 0.94 * float(row[f"scheduled_belief_{mode}"]) + 0.06 * float(row[f"residual_belief_{mode}"])
            assert_close(float(row[f"display_belief_{mode}"]), expected, "display mixture")
            assert_close(float(row[f"residual_{mode}_V"]), float(row["actual_voltage_V"]) - float(row[f"prediction_{mode}_V"]), "grid residual")
    output = {"dual_model": dual, "microgrid": grid,
              "scope": "Metrics recomputed from deposited outputs; this script does not rerun model training, optimization, or closed-loop simulation."}
    destination = ROOT / "analysis_results"
    destination.mkdir(exist_ok=True)
    (destination / "recomputed_metrics.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print("CSV checks and independent metric comparisons passed.")
    print(json.dumps({"dual_RMSE": dual["control"]["RMSE"], "microgrid": grid}, indent=2))


if __name__ == "__main__":
    main()
