#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path


DEFAULT_RESULT_GLOB = "/app/cupdlp_w7900/results/w7900_large_mps_initial17_safe_*"


def latest_result_dir() -> Path:
    candidates = [p for p in Path("/app/cupdlp_w7900/results").glob("w7900_large_mps_initial17_safe_*") if p.is_dir()]
    if not candidates:
        raise SystemExit(f"[error] no result directory found: {DEFAULT_RESULT_GLOB}")
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = find_key(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_key(value, key)
            if found is not None:
                return found
    return None


def read_runtime_summary(out_dir: Path):
    runtime_csv = out_dir / "runtime_summary.csv"
    rows = {}

    if not runtime_csv.exists():
        print(f"[warn] runtime_summary.csv not found: {runtime_csv}")
        return rows

    with runtime_csv.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_name = row.get("case", "")
            key = Path(case_name).stem
            rows[key] = row

    return rows


def to_float(value, default=-1.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def main():
    if len(sys.argv) >= 2:
        out_dir = Path(sys.argv[1]).resolve()
    else:
        out_dir = latest_result_dir().resolve()

    json_dir = out_dir / "json"
    if not out_dir.exists():
        raise SystemExit(f"[error] result dir not found: {out_dir}")
    if not json_dir.exists():
        raise SystemExit(f"[error] json dir not found: {json_dir}")

    runtime_rows = read_runtime_summary(out_dir)

    fields = [
        "case",
        "runtime_status",
        "exit_code",
        "wall_seconds",
        "terminationCode",
        "primalCode",
        "dualCode",
        "nIter",
        "dSolvingTime",
        "DeviceMatVecProdTime",
        "dRelPrimalFeas",
        "dRelDualFeas",
        "dRelDualityGap",
        "json",
        "log",
    ]

    solver_keys = [
        "terminationCode",
        "primalCode",
        "dualCode",
        "nIter",
        "dSolvingTime",
        "DeviceMatVecProdTime",
        "dRelPrimalFeas",
        "dRelDualFeas",
        "dRelDualityGap",
    ]

    rows = []
    for json_path in sorted(json_dir.glob("*.json")):
        case = json_path.stem
        try:
            data = json.loads(json_path.read_text())
        except Exception as exc:
            print(f"[warn] failed to read JSON: {json_path}: {exc}")
            continue

        runtime = runtime_rows.get(case, {})

        row = {
            "case": case,
            "runtime_status": runtime.get("status", ""),
            "exit_code": runtime.get("exit_code", ""),
            "wall_seconds": runtime.get("wall_seconds", ""),
            "json": str(json_path),
            "log": runtime.get("log", ""),
        }

        for key in solver_keys:
            row[key] = find_key(data, key)

        rows.append(row)

    csv_path = out_dir / "parsed_solver_summary.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[ok] result dir: {out_dir}")
    print(f"[ok] parsed json files: {len(rows)}")
    print(f"[ok] wrote: {csv_path}")

    abnormal = [
        r for r in rows
        if r.get("runtime_status") not in ("DONE", "")
        or r.get("terminationCode") not in ("OPTIMAL", "0", 0)
    ]

    if abnormal:
        print()
        print("[warn] abnormal or non-OPTIMAL rows:")
        for r in abnormal:
            print(
                r["case"],
                "runtime=", r.get("runtime_status"),
                "term=", r.get("terminationCode"),
                "iter=", r.get("nIter"),
                "solve=", r.get("dSolvingTime"),
                "gap=", r.get("dRelDualityGap"),
            )
    else:
        print("[ok] no abnormal runtime status detected in parsed rows")

    print()
    print("== Slowest cases by dSolvingTime ==")
    rows_sorted = sorted(rows, key=lambda r: to_float(r.get("dSolvingTime")), reverse=True)

    print("case,termination,nIter,wall_seconds,solve_time,matvec_time,rel_gap")
    for r in rows_sorted:
        print(
            r.get("case"),
            r.get("terminationCode"),
            r.get("nIter"),
            r.get("wall_seconds"),
            r.get("dSolvingTime"),
            r.get("DeviceMatVecProdTime"),
            r.get("dRelDualityGap"),
            sep=",",
        )


if __name__ == "__main__":
    main()
