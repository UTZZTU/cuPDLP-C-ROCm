#!/usr/bin/env python3
"""
Summarize rocprofv3 tuning milestone traces.

Expected run layout:
  <run_root>/<milestone>/<case>/trace/

Outputs:
  trace_summary_by_run.csv
  trace_kernel_top.csv
  trace_hip_api_top.csv
  trace_memory_copy_top.csv
  trace_milestone_deltas.csv
  trace_milestone_summary.md
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Optional


ORDER = [
    "pre_tuning",
    "remove_sync",
    "cache_attrs",
    "fused_average",
    "reduce_scalar_copies",
    "current",
]


def read_csv_rows(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with path.open(newline="", errors="replace") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def pick(row: dict, names: Iterable[str]) -> Optional[str]:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    norm = {k.lower().replace(" ", "_").replace("-", "_"): k for k in row.keys()}
    for name in names:
        key = name.lower().replace(" ", "_").replace("-", "_")
        if key in norm:
            val = row.get(norm[key])
            if val not in (None, ""):
                return val
    return None


def to_float(x) -> Optional[float]:
    if x is None or x == "":
        return None
    try:
        return float(str(x).strip())
    except Exception:
        return None


def duration_ns(row: dict) -> Optional[float]:
    dur = pick(row, ["Duration", "Duration_ns", "Duration_Ns", "Duration (ns)", "Duration_ns"])
    if dur is not None:
        v = to_float(dur)
        if v is not None:
            return v

    start = pick(row, ["Start_Timestamp", "Begin_Timestamp", "Start", "Begin"])
    end = pick(row, ["End_Timestamp", "Stop_Timestamp", "End", "Finish"])
    s = to_float(start)
    e = to_float(end)
    if s is None or e is None:
        return None
    return max(0.0, e - s)


def duration_ms(row: dict) -> float:
    ns = duration_ns(row)
    return 0.0 if ns is None else ns / 1_000_000.0


def find_one(root: Path, suffix: str) -> Optional[Path]:
    matches = sorted(root.rglob(f"*{suffix}"))
    return matches[0] if matches else None


def load_solver_json(case_dir: Path, case: str) -> dict:
    candidates = [case_dir / f"{case}_rocm.json", *sorted(case_dir.glob("*.json"))]
    for p in candidates:
        if p.exists() and p.stat().st_size > 0:
            try:
                return json.loads(p.read_text(errors="replace"))
            except Exception:
                continue
    return {}


def summarize_group(rows, name_cols):
    total_ms = 0.0
    groups = defaultdict(lambda: {"calls": 0, "total_ms": 0.0, "max_ms": 0.0})
    for row in rows:
        d = duration_ms(row)
        total_ms += d
        name = pick(row, name_cols) or "UNKNOWN"
        groups[name]["calls"] += 1
        groups[name]["total_ms"] += d
        groups[name]["max_ms"] = max(groups[name]["max_ms"], d)

    top = []
    for name, val in groups.items():
        top.append({
            "name": name,
            "calls": val["calls"],
            "total_ms": val["total_ms"],
            "max_ms": val["max_ms"],
        })
    top.sort(key=lambda x: x["total_ms"], reverse=True)
    return len(rows), total_ms, top


def summarize_trace(label_dir: Path, label: str):
    summary_rows = []
    kernel_top_rows = []
    hip_top_rows = []
    memcopy_top_rows = []

    for case_dir in sorted(p for p in label_dir.iterdir() if p.is_dir()):
        case = case_dir.name
        trace_root = case_dir / "trace"
        solver = load_solver_json(case_dir, case)

        exitcode = ""
        exit_path = case_dir / f"{case}_rocm.exitcode"
        if exit_path.exists():
            exitcode = exit_path.read_text(errors="replace").strip()

        hip_csv = find_one(trace_root, "_hip_api_trace.csv")
        kernel_csv = find_one(trace_root, "_kernel_trace.csv")
        memcpy_csv = find_one(trace_root, "_memory_copy_trace.csv")
        memalloc_csv = find_one(trace_root, "_memory_allocation_trace.csv")
        scratch_csv = find_one(trace_root, "_scratch_memory_trace.csv")

        hip_rows = read_csv_rows(hip_csv) if hip_csv else []
        kernel_rows = read_csv_rows(kernel_csv) if kernel_csv else []
        memcpy_rows = read_csv_rows(memcpy_csv) if memcpy_csv else []
        memalloc_rows = read_csv_rows(memalloc_csv) if memalloc_csv else []
        scratch_rows = read_csv_rows(scratch_csv) if scratch_csv else []

        hip_count, hip_ms, hip_top = summarize_group(
            hip_rows, ["Function", "Name", "Operation"]
        )
        kernel_count, kernel_ms, kernel_top = summarize_group(
            kernel_rows, ["Kernel_Name", "KernelName", "Name", "Demangled_Kernel_Name", "Truncated_Kernel_Name"]
        )
        memcpy_count, memcpy_ms, memcpy_top = summarize_group(
            memcpy_rows, ["Direction", "Operation", "Name"]
        )
        memalloc_count, memalloc_ms, memalloc_top = summarize_group(
            memalloc_rows, ["Operation", "Name"]
        )
        scratch_count, scratch_ms, scratch_top = summarize_group(
            scratch_rows, ["Operation", "Name"]
        )

        total_alloc_bytes = 0.0
        for r in memalloc_rows:
            op = (pick(r, ["Operation"]) or "").upper()
            if "ALLOC" in op and "FREE" not in op:
                sz = to_float(pick(r, ["Allocation_Size", "Size", "Bytes"]))
                if sz:
                    total_alloc_bytes += sz

        summary_rows.append({
            "label": label,
            "case": case,
            "exitcode": exitcode,
            "status": solver.get("terminationCode", ""),
            "nIter": solver.get("nIter", ""),
            "solve_time_sec": solver.get("dSolvingTime", ""),
            "DeviceMatVecProdTime_sec": solver.get("DeviceMatVecProdTime", ""),
            "hip_api_calls": hip_count,
            "hip_api_total_ms": hip_ms,
            "kernel_dispatches": kernel_count,
            "kernel_total_ms": kernel_ms,
            "memory_copy_count": memcpy_count,
            "memory_copy_total_ms": memcpy_ms,
            "memory_allocation_count": memalloc_count,
            "memory_allocation_total_ms": memalloc_ms,
            "memory_allocation_bytes": total_alloc_bytes,
            "scratch_memory_count": scratch_count,
            "scratch_memory_total_ms": scratch_ms,
            "hip_trace_file": str(hip_csv or ""),
            "kernel_trace_file": str(kernel_csv or ""),
            "memory_copy_trace_file": str(memcpy_csv or ""),
            "memory_allocation_trace_file": str(memalloc_csv or ""),
            "scratch_memory_trace_file": str(scratch_csv or ""),
        })

        for rank, row in enumerate(kernel_top[:20], 1):
            kernel_top_rows.append({
                "label": label,
                "case": case,
                "rank": rank,
                "kernel": row["name"],
                "calls": row["calls"],
                "total_ms": row["total_ms"],
                "max_ms": row["max_ms"],
            })

        for rank, row in enumerate(hip_top[:20], 1):
            hip_top_rows.append({
                "label": label,
                "case": case,
                "rank": rank,
                "hip_api": row["name"],
                "calls": row["calls"],
                "total_ms": row["total_ms"],
                "max_ms": row["max_ms"],
            })

        for rank, row in enumerate(memcpy_top[:20], 1):
            memcopy_top_rows.append({
                "label": label,
                "case": case,
                "rank": rank,
                "direction_or_operation": row["name"],
                "calls": row["calls"],
                "total_ms": row["total_ms"],
                "max_ms": row["max_ms"],
            })

    return summary_rows, kernel_top_rows, hip_top_rows, memcopy_top_rows


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def fnum(row: dict, key: str) -> Optional[float]:
    return to_float(row.get(key))


def delta_pct(cur: Optional[float], prev: Optional[float]):
    if cur is None or prev in (None, 0):
        return ""
    return (cur / prev - 1.0) * 100.0


def fmt(x, digits=3):
    if x == "" or x is None:
        return ""
    try:
        return f"{float(x):.{digits}f}"
    except Exception:
        return str(x)


def milestone_sort(labels: set[str]) -> list[str]:
    known = [x for x in ORDER if x in labels]
    extra = sorted(labels - set(known))
    return known + extra


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: summarize_rocprofv3_milestones.py <run_root>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    if not root.exists():
        print(f"ERROR: run root does not exist: {root}", file=sys.stderr)
        return 1

    all_summary = []
    all_kernel_top = []
    all_hip_top = []
    all_memcopy_top = []

    for label_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        label = label_dir.name
        summary, kernels, hip, memcopy = summarize_trace(label_dir, label)
        all_summary.extend(summary)
        all_kernel_top.extend(kernels)
        all_hip_top.extend(hip)
        all_memcopy_top.extend(memcopy)

    summary_fields = [
        "label","case","exitcode","status","nIter","solve_time_sec","DeviceMatVecProdTime_sec",
        "hip_api_calls","hip_api_total_ms","kernel_dispatches","kernel_total_ms",
        "memory_copy_count","memory_copy_total_ms","memory_allocation_count",
        "memory_allocation_total_ms","memory_allocation_bytes",
        "scratch_memory_count","scratch_memory_total_ms",
        "hip_trace_file","kernel_trace_file","memory_copy_trace_file",
        "memory_allocation_trace_file","scratch_memory_trace_file"
    ]
    write_csv(root / "trace_summary_by_run.csv", all_summary, summary_fields)

    write_csv(root / "trace_kernel_top.csv", all_kernel_top, [
        "label","case","rank","kernel","calls","total_ms","max_ms"
    ])
    write_csv(root / "trace_hip_api_top.csv", all_hip_top, [
        "label","case","rank","hip_api","calls","total_ms","max_ms"
    ])
    write_csv(root / "trace_memory_copy_top.csv", all_memcopy_top, [
        "label","case","rank","direction_or_operation","calls","total_ms","max_ms"
    ])

    labels = milestone_sort({r["label"] for r in all_summary})
    cases = sorted({r["case"] for r in all_summary})
    by_key = {(r["label"], r["case"]): r for r in all_summary}

    metrics = [
        "solve_time_sec",
        "DeviceMatVecProdTime_sec",
        "hip_api_calls",
        "hip_api_total_ms",
        "kernel_dispatches",
        "kernel_total_ms",
        "memory_copy_count",
        "memory_copy_total_ms",
        "memory_allocation_count",
        "memory_allocation_total_ms",
        "memory_allocation_bytes",
        "scratch_memory_count",
        "scratch_memory_total_ms",
    ]

    deltas = []
    for case in cases:
        prev_label = None
        prev_row = None
        base_row = by_key.get(("pre_tuning", case))
        for label in labels:
            cur = by_key.get((label, case))
            if not cur:
                continue
            row = {
                "case": case,
                "label": label,
                "previous_label": prev_label or "",
                "status": cur.get("status", ""),
                "nIter": cur.get("nIter", ""),
            }
            for m in metrics:
                cv = fnum(cur, m)
                pv = fnum(prev_row, m) if prev_row else None
                bv = fnum(base_row, m) if base_row else None
                row[m] = "" if cv is None else cv
                row[f"delta_pct_vs_previous_{m}"] = delta_pct(cv, pv)
                row[f"delta_pct_vs_pre_tuning_{m}"] = delta_pct(cv, bv)
            deltas.append(row)
            prev_label = label
            prev_row = cur

    delta_fields = ["case", "label", "previous_label", "status", "nIter"]
    for m in metrics:
        delta_fields += [m, f"delta_pct_vs_previous_{m}", f"delta_pct_vs_pre_tuning_{m}"]
    write_csv(root / "trace_milestone_deltas.csv", deltas, delta_fields)

    md = root / "trace_milestone_summary.md"
    with md.open("w") as f:
        f.write("# ROCm rocprofv3 tuning milestone trace summary\n\n")
        f.write(f"Run dir: `{root}`\n\n")
        f.write("Trace mode: `rocprofv3 --runtime-trace --output-format csv`.\n\n")
        f.write("Milestone order:\n\n")
        for label in labels:
            f.write(f"- `{label}`\n")
        f.write("\nThe percentage columns use `(current / reference - 1) * 100`.\n\n")

        for case in cases:
            f.write(f"## `{case}`\n\n")
            f.write("| milestone | status | nIter | solve s | solve Δ% prev | solve Δ% pre | matvec s | HIP calls | HIP time ms | kernel dispatches | kernel time ms | memcpy count | memcpy time ms | memalloc count | memalloc time ms |\n")
            f.write("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
            for label in labels:
                r = next((x for x in deltas if x["case"] == case and x["label"] == label), None)
                if not r:
                    continue
                f.write(
                    f"| `{label}` | {r.get('status','')} | {r.get('nIter','')} | "
                    f"{fmt(r.get('solve_time_sec'), 6)} | "
                    f"{fmt(r.get('delta_pct_vs_previous_solve_time_sec'))} | "
                    f"{fmt(r.get('delta_pct_vs_pre_tuning_solve_time_sec'))} | "
                    f"{fmt(r.get('DeviceMatVecProdTime_sec'), 6)} | "
                    f"{fmt(r.get('hip_api_calls'), 0)} | "
                    f"{fmt(r.get('hip_api_total_ms'), 3)} | "
                    f"{fmt(r.get('kernel_dispatches'), 0)} | "
                    f"{fmt(r.get('kernel_total_ms'), 3)} | "
                    f"{fmt(r.get('memory_copy_count'), 0)} | "
                    f"{fmt(r.get('memory_copy_total_ms'), 3)} | "
                    f"{fmt(r.get('memory_allocation_count'), 0)} | "
                    f"{fmt(r.get('memory_allocation_total_ms'), 3)} |\n"
                )
            f.write("\n")

        f.write("## Interpretation checklist\n\n")
        f.write("- `remove_sync`: check whether HIP API time or synchronization-like API count/time drops.\n")
        f.write("- `cache_attrs`: check whether HIP API calls around device attributes drop, especially on short cases.\n")
        f.write("- `fused_average`: check whether kernel dispatch count changes and whether vector-update kernels change in `trace_kernel_top.csv`.\n")
        f.write("- `reduce_scalar_copies`: check whether memory copy count/time or HIP API time drops.\n")
        f.write("- `current`: check whether engineering compatibility changes preserve similar trace structure.\n")

    print(root / "trace_summary_by_run.csv")
    print(root / "trace_milestone_deltas.csv")
    print(root / "trace_milestone_summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
