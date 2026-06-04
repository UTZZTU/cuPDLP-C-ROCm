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

NUMERIC_KEYS = [
    "nIter",
    "dPrimalObj",
    "dDualObj",
    "dPrimalFeas",
    "dDualFeas",
    "dDualityGap",
    "dRelPrimalFeas",
    "dRelDualFeas",
    "dRelDualityGap",
]


TOLERANCES = {
    "nIter": 10,
    "dPrimalObj": 1e-1,
    "dDualObj": 1e-1,
    "dPrimalFeas": 1e-1,
    "dDualFeas": 1e-3,
    "dDualityGap": 1e-1,
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


def compare_numeric(cpu: dict, rocm: dict):
    rows = []
    ok = True

    for key in NUMERIC_KEYS:
        c_raw = cpu.get(key)
        r_raw = rocm.get(key)
        c = as_float(c_raw)
        r = as_float(r_raw)

        if c is None or r is None:
            rows.append((key, c_raw, r_raw, "missing", "FAIL"))
            ok = False
            continue

        diff = abs(r - c)
        tol = TOLERANCES[key]
        passed = diff <= tol or math.isclose(c, r, abs_tol=tol, rel_tol=0.0)
        ok = ok and passed
        rows.append((key, c_raw, r_raw, f"{diff:.6g} <= {tol:g}", "PASS" if passed else "FAIL"))

    return ok, rows


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
    numeric_ok, numeric_rows = compare_numeric(cpu, rocm)
    overall_ok = status_ok and numeric_ok

    lines = []
    lines.append(f"# Validation report: {args.case}")
    lines.append("")
    lines.append(f"Overall result: **{'PASS' if overall_ok else 'FAIL'}**")
    lines.append("")
    lines.append("## Status comparison")
    lines.append("")
    lines.append("| Metric | CPU | ROCm | Result |")
    lines.append("|---|---:|---:|---|")
    for key, c, r, result in status_rows:
        lines.append(f"| `{key}` | `{c}` | `{r}` | {result} |")

    lines.append("")
    lines.append("## Numeric comparison")
    lines.append("")
    lines.append("| Metric | CPU | ROCm | Difference / tolerance | Result |")
    lines.append("|---|---:|---:|---:|---|")
    for key, c, r, detail, result in numeric_rows:
        lines.append(f"| `{key}` | `{c}` | `{r}` | `{detail}` | {result} |")

    report = "\n".join(lines) + "\n"
    print(report)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")

    raise SystemExit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
