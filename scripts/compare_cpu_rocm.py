#!/usr/bin/env python3

import argparse
import json
import math
from pathlib import Path


STATUS_KEYS = [
    "terminationCode",
    "primalCode",
    "dualCode",
]

# These are hard validation metrics when both solvers report OPTIMAL.
HARD_RELATIVE_KEYS = [
    "dRelPrimalFeas",
    "dRelDualFeas",
    "dRelDualityGap",
]

# These are useful diagnostics, but should not fail validation by themselves.
INFO_KEYS = [
    "nIter",
    "dPrimalObj",
    "dDualObj",
    "dPrimalFeas",
    "dDualFeas",
    "dDualityGap",
]

HARD_TOLERANCES = {
    "dRelPrimalFeas": 1e-4,
    "dRelDualFeas": 1e-4,
    "dRelDualityGap": 1e-4,
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def as_float(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def compare_status(cpu: dict, rocm: dict):
    rows = []
    ok = True

    for key in STATUS_KEYS:
        c = cpu.get(key)
        r = rocm.get(key)
        passed = c == r
        ok = ok and passed
        rows.append((key, c, r, "PASS" if passed else "FAIL"))

    return ok, rows


def compare_hard_relative(cpu: dict, rocm: dict, require_hard_numeric: bool):
    rows = []
    ok = True

    for key in HARD_RELATIVE_KEYS:
        c_raw = cpu.get(key)
        r_raw = rocm.get(key)
        c = as_float(c_raw)
        r = as_float(r_raw)

        if c is None or r is None:
            result = "FAIL" if require_hard_numeric else "INFO"
            rows.append((key, c_raw, r_raw, "missing", result))
            ok = ok and not require_hard_numeric
            continue

        diff = abs(r - c)
        tol = HARD_TOLERANCES[key]
        passed = diff <= tol or math.isclose(c, r, abs_tol=tol, rel_tol=0.0)

        if require_hard_numeric:
            ok = ok and passed
            result = "PASS" if passed else "FAIL"
        else:
            result = "INFO"

        rows.append((key, c_raw, r_raw, f"{diff:.6g} <= {tol:g}", result))

    return ok, rows


def collect_info_rows(cpu: dict, rocm: dict):
    rows = []

    for key in INFO_KEYS:
        c_raw = cpu.get(key)
        r_raw = rocm.get(key)
        c = as_float(c_raw)
        r = as_float(r_raw)

        if c is None or r is None:
            rows.append((key, c_raw, r_raw, "missing", "INFO"))
            continue

        diff = abs(r - c)
        rows.append((key, c_raw, r_raw, f"{diff:.6g}", "INFO"))

    return rows


def main():
    parser = argparse.ArgumentParser(description="Compare cuPDLP-C CPU and ROCm JSON outputs.")
    parser.add_argument("--case", required=True, help="Case name, for example afiro")
    parser.add_argument("--cpu", required=True, type=Path, help="CPU JSON output path")
    parser.add_argument("--rocm", required=True, type=Path, help="ROCm JSON output path")
    parser.add_argument("--out", type=Path, help="Optional markdown report path")
    args = parser.parse_args()

    cpu = load_json(args.cpu)
    rocm = load_json(args.rocm)

    status_ok, status_rows = compare_status(cpu, rocm)

    cpu_term = cpu.get("terminationCode")
    rocm_term = rocm.get("terminationCode")

    both_optimal = (cpu_term == "OPTIMAL" and rocm_term == "OPTIMAL")
    both_iterlimit = (cpu_term == "TIMELIMIT_OR_ITERLIMIT" and rocm_term == "TIMELIMIT_OR_ITERLIMIT")

    hard_ok, hard_rows = compare_hard_relative(
        cpu,
        rocm,
        require_hard_numeric=both_optimal,
    )

    info_rows = collect_info_rows(cpu, rocm)

    if not status_ok:
        overall = "FAIL"
        exit_code = 1
        note = "CPU and ROCm status codes differ."
    elif both_iterlimit:
        overall = "INCOMPLETE"
        exit_code = 1
        note = "Both CPU and ROCm hit the iteration or time limit. This case needs a larger iteration limit or separate investigation."
    elif both_optimal and hard_ok:
        overall = "PASS"
        exit_code = 0
        note = "Both CPU and ROCm reported OPTIMAL, and relative validation metrics are within tolerance."
    elif both_optimal and not hard_ok:
        overall = "FAIL"
        exit_code = 1
        note = "Both CPU and ROCm reported OPTIMAL, but one or more relative validation metrics exceeded tolerance."
    else:
        overall = "FAIL"
        exit_code = 1
        note = "Unhandled termination status combination."

    lines = []
    lines.append(f"# Validation report: {args.case}")
    lines.append("")
    lines.append(f"Overall result: **{overall}**")
    lines.append("")
    lines.append(note)
    lines.append("")
    lines.append("## Status comparison")
    lines.append("")
    lines.append("| Metric | CPU | ROCm | Result |")
    lines.append("|---|---:|---:|---|")
    for key, c, r, result in status_rows:
        lines.append(f"| `{key}` | `{c}` | `{r}` | {result} |")

    lines.append("")
    lines.append("## Hard relative metric comparison")
    lines.append("")
    lines.append("| Metric | CPU | ROCm | Difference / tolerance | Result |")
    lines.append("|---|---:|---:|---:|---|")
    for key, c, r, detail, result in hard_rows:
        lines.append(f"| `{key}` | `{c}` | `{r}` | `{detail}` | {result} |")

    lines.append("")
    lines.append("## Informational diagnostics")
    lines.append("")
    lines.append("| Metric | CPU | ROCm | Difference | Result |")
    lines.append("|---|---:|---:|---:|---|")
    for key, c, r, detail, result in info_rows:
        lines.append(f"| `{key}` | `{c}` | `{r}` | `{detail}` | {result} |")

    report = "\n".join(lines) + "\n"
    print(report)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
