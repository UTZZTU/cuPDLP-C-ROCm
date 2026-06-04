#!/usr/bin/env python3
"""
Summarize rocprofv3 CSV traces for cuPDLP-C-ROCm.

This script is intentionally defensive because rocprofv3 CSV column names can
vary across ROCm versions and trace domains. It discovers common duration/name
columns and produces a Markdown summary rather than failing on one exact schema.

Example:

    python3 scripts/summarize_rocm_profile.py \
      --input profiling/results/latest \
      --output profiling/results/latest/profile_summary.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


TRACE_SUFFIXES = {
    "hip_api": "_hip_api_trace.csv",
    "kernel": "_kernel_trace.csv",
    "memory_allocation": "_memory_allocation_trace.csv",
    "memory_copy": "_memory_copy_trace.csv",
}


NAME_CANDIDATES = [
    "Name",
    "name",
    "Function",
    "function",
    "FunctionName",
    "function_name",
    "Operation",
    "operation",
    "API",
    "api",
    "KernelName",
    "kernel_name",
    "Kernel_Name",
    "kernel",
    "Symbol",
    "symbol",
]


DURATION_CANDIDATES = [
    "Duration",
    "duration",
    "DurationNs",
    "duration_ns",
    "Duration_ns",
    "Duration (ns)",
    "DurationNs",
    "DurationUs",
    "duration_us",
    "Duration_us",
    "Duration (us)",
    "DurationMs",
    "duration_ms",
    "Duration_ms",
    "Duration (ms)",
]


START_CANDIDATES = [
    "Start",
    "start",
    "StartNs",
    "start_ns",
    "Start_Timestamp",
    "start_timestamp",
    "Begin",
    "begin",
    "BeginNs",
    "begin_ns",
]


END_CANDIDATES = [
    "End",
    "end",
    "EndNs",
    "end_ns",
    "End_Timestamp",
    "end_timestamp",
    "Stop",
    "stop",
    "StopNs",
    "stop_ns",
]


@dataclass
class GroupStats:
    count: int = 0
    total_ns: float = 0.0
    min_ns: float = math.inf
    max_ns: float = 0.0

    def add(self, duration_ns: float) -> None:
        self.count += 1
        self.total_ns += duration_ns
        self.min_ns = min(self.min_ns, duration_ns)
        self.max_ns = max(self.max_ns, duration_ns)

    @property
    def avg_ns(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total_ns / self.count


def clean_key(key: str) -> str:
    return key.strip().strip('"').strip("'")


def clean_value(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().strip('"').strip("'")


def parse_float(value: object) -> Optional[float]:
    text = clean_value(value)
    if not text:
        return None

    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def lookup(row: Dict[str, str], candidates: Iterable[str]) -> Tuple[Optional[str], Optional[str]]:
    normalized = {clean_key(k): v for k, v in row.items()}

    for key in candidates:
        if key in normalized and clean_value(normalized[key]) != "":
            return key, normalized[key]

    lower_map = {clean_key(k).lower(): (clean_key(k), v) for k, v in row.items()}

    for key in candidates:
        found = lower_map.get(key.lower())
        if found and clean_value(found[1]) != "":
            return found

    return None, None


def infer_duration_ns(row: Dict[str, str]) -> Optional[float]:
    key, value = lookup(row, DURATION_CANDIDATES)
    parsed = parse_float(value)

    if parsed is not None and key:
        key_lower = key.lower()
        if "ms" in key_lower:
            return parsed * 1_000_000.0
        if "us" in key_lower or "µs" in key_lower:
            return parsed * 1_000.0
        if "sec" in key_lower or key_lower.endswith("(s)") or key_lower.endswith("_s"):
            return parsed * 1_000_000_000.0
        return parsed

    start_key, start_value = lookup(row, START_CANDIDATES)
    end_key, end_value = lookup(row, END_CANDIDATES)

    start = parse_float(start_value)
    end = parse_float(end_value)

    if start is not None and end is not None and end >= start:
        return end - start

    return None


def infer_name(row: Dict[str, str], default: str) -> str:
    _, value = lookup(row, NAME_CANDIDATES)
    name = clean_value(value)
    return name if name else default


def infer_case_name(path: Path, suffix: str) -> str:
    name = path.name
    if name.endswith(suffix):
        return name[: -len(suffix)]
    return path.stem


def ms(ns: float) -> float:
    return ns / 1_000_000.0


def pct(part: float, whole: float) -> float:
    if whole <= 0:
        return 0.0
    return 100.0 * part / whole


def kernel_category(name: str) -> str:
    lower = name.lower()

    if "__amd_rocclr_copybuffer" in lower:
        return "ROCclr copy buffer"
    if "__amd_rocclr_fillbuffer" in lower:
        return "ROCclr fill buffer"
    if "rocsparse" in lower or "csrmv" in lower or "spmv" in lower:
        return "rocSPARSE / SpMV"
    if "rocblas" in lower:
        return "rocBLAS"
    if "hip" in lower and "mem" in lower:
        return "HIP memory"
    if any(token in lower for token in ["primal", "dual", "movement", "proj", "feas", "pdlp", "cupdlp"]):
        return "cuPDLP custom kernel"
    return "Other"


def summarize_csv(path: Path, default_name: str) -> Tuple[Dict[str, GroupStats], int, int, List[str]]:
    groups: Dict[str, GroupStats] = defaultdict(GroupStats)
    total_rows = 0
    rows_with_duration = 0
    fieldnames: List[str] = []

    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = [clean_key(x) for x in (reader.fieldnames or [])]

        for row in reader:
            total_rows += 1
            duration_ns = infer_duration_ns(row)
            if duration_ns is None:
                continue

            rows_with_duration += 1
            name = infer_name(row, default=default_name)
            groups[name].add(duration_ns)

    return groups, total_rows, rows_with_duration, fieldnames


def merge_groups(items: Iterable[Tuple[str, GroupStats]]) -> Dict[str, GroupStats]:
    merged: Dict[str, GroupStats] = defaultdict(GroupStats)
    for name, stats in items:
        target = merged[name]
        target.count += stats.count
        target.total_ns += stats.total_ns
        target.min_ns = min(target.min_ns, stats.min_ns)
        target.max_ns = max(target.max_ns, stats.max_ns)
    return merged


def top_by_total(groups: Dict[str, GroupStats], limit: int) -> List[Tuple[str, GroupStats]]:
    return sorted(groups.items(), key=lambda kv: kv[1].total_ns, reverse=True)[:limit]


def top_by_count(groups: Dict[str, GroupStats], limit: int) -> List[Tuple[str, GroupStats]]:
    return sorted(groups.items(), key=lambda kv: kv[1].count, reverse=True)[:limit]


def table_for_groups(groups: Dict[str, GroupStats], limit: int, sort_by: str) -> str:
    if not groups:
        return "_No rows with recognized duration columns._\n"

    rows = top_by_total(groups, limit) if sort_by == "total" else top_by_count(groups, limit)
    total_ns = sum(stats.total_ns for stats in groups.values())

    lines = [
        "| Name | Count | Total ms | Avg us | Max us | Share |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for name, stats in rows:
        lines.append(
            "| `{}` | {} | {:.3f} | {:.3f} | {:.3f} | {:.2f}% |".format(
                name.replace("|", "\\|"),
                stats.count,
                ms(stats.total_ns),
                stats.avg_ns / 1_000.0,
                stats.max_ns / 1_000.0,
                pct(stats.total_ns, total_ns),
            )
        )

    return "\n".join(lines) + "\n"


def summarize_kernel_categories(groups: Dict[str, GroupStats]) -> Dict[str, GroupStats]:
    categorized: Dict[str, GroupStats] = defaultdict(GroupStats)

    for name, stats in groups.items():
        category = kernel_category(name)
        target = categorized[category]
        target.count += stats.count
        target.total_ns += stats.total_ns
        target.min_ns = min(target.min_ns, stats.min_ns)
        target.max_ns = max(target.max_ns, stats.max_ns)

    return categorized


def load_json_summary(path: Path) -> Dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def collect_json_summaries(root: Path) -> Dict[str, Dict[str, object]]:
    summaries: Dict[str, Dict[str, object]] = {}

    for path in sorted(root.glob("*_rocm_baseline.json")):
        case = path.name.replace("_rocm_baseline.json", "")
        data = load_json_summary(path)
        if data:
            summaries[f"{case} baseline"] = data

    for path in sorted(root.glob("*_rocm_profiled.json")):
        case = path.name.replace("_rocm_profiled.json", "")
        data = load_json_summary(path)
        if data:
            summaries[f"{case} profiled"] = data

    return summaries


def solver_summary_table(summaries: Dict[str, Dict[str, object]]) -> str:
    if not summaries:
        return "_No solver JSON summaries found._\n"

    fields = [
        "terminationCode",
        "nIter",
        "dSolvingTime",
        "DeviceMatVecProdTime",
        "AllocMem_CopyMatToDeviceTime",
        "CopyVecToDeviceTime",
        "CopyVecToHostTime",
    ]

    lines = [
        "| Run | terminationCode | nIter | Solving s | DeviceMatVec s | Alloc/copy matrix s | Copy vec to device s | Copy vec to host s |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for name, data in summaries.items():
        values = {field: data.get(field, "") for field in fields}
        lines.append(
            "| {} | `{}` | {} | {} | {} | {} | {} | {} |".format(
                name,
                values["terminationCode"],
                values["nIter"],
                fmt_num(values["dSolvingTime"]),
                fmt_num(values["DeviceMatVecProdTime"]),
                fmt_num(values["AllocMem_CopyMatToDeviceTime"]),
                fmt_num(values["CopyVecToDeviceTime"]),
                fmt_num(values["CopyVecToHostTime"]),
            )
        )

    return "\n".join(lines) + "\n"


def fmt_num(value: object) -> str:
    try:
        return f"{float(value):.6g}"
    except Exception:
        return "—"


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize rocprofv3 CSV traces.")
    parser.add_argument("--input", default="profiling/results/latest", help="Profiling result root")
    parser.add_argument("--output", default=None, help="Markdown output path")
    parser.add_argument("--top", type=int, default=20, help="Number of top rows per table")
    args = parser.parse_args()

    root = Path(args.input)
    if not root.exists():
        raise SystemExit(f"input directory not found: {root}")

    output = Path(args.output) if args.output else root / "profile_summary.md"

    found_files: Dict[str, List[Path]] = {kind: [] for kind in TRACE_SUFFIXES}

    for kind, suffix in TRACE_SUFFIXES.items():
        found_files[kind] = sorted(root.rglob(f"*{suffix}"))

    reports: Dict[str, Dict[str, Dict[str, GroupStats]]] = defaultdict(dict)
    metadata_lines: List[str] = []

    for kind, files in found_files.items():
        suffix = TRACE_SUFFIXES[kind]
        for path in files:
            case = infer_case_name(path, suffix)
            default_name = kind
            groups, total_rows, rows_with_duration, fieldnames = summarize_csv(path, default_name)
            reports[case][kind] = groups
            metadata_lines.append(
                f"- `{path}`: {total_rows} rows, {rows_with_duration} rows with recognized duration, columns: `{', '.join(fieldnames)}`"
            )

    lines: List[str] = []
    lines.append("# ROCm profiling summary")
    lines.append("")
    lines.append(f"Input directory: `{root}`")
    lines.append("")
    lines.append("Generated by:")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 scripts/summarize_rocm_profile.py \\")
    lines.append(f"  --input {root} \\")
    lines.append(f"  --output {output}")
    lines.append("```")
    lines.append("")
    lines.append("## Solver JSON summary")
    lines.append("")
    lines.append(solver_summary_table(collect_json_summaries(root)))
    lines.append("")
    lines.append("## Trace files")
    lines.append("")
    if metadata_lines:
        lines.extend(metadata_lines)
    else:
        lines.append("_No rocprofv3 CSV trace files found._")
    lines.append("")

    all_cases = sorted(reports.keys())

    if not all_cases:
        lines.append("## No trace data found")
        lines.append("")
        lines.append("Run:")
        lines.append("")
        lines.append("```bash")
        lines.append("./scripts/profile_rocm_smoke.sh")
        lines.append("```")
    else:
        for case in all_cases:
            lines.append(f"## Case: `{case}`")
            lines.append("")

            hip_groups = reports[case].get("hip_api", {})
            kernel_groups = reports[case].get("kernel", {})
            mem_alloc_groups = reports[case].get("memory_allocation", {})
            mem_copy_groups = reports[case].get("memory_copy", {})

            lines.append("### Top HIP API by total time")
            lines.append("")
            lines.append(table_for_groups(hip_groups, args.top, "total"))
            lines.append("")

            lines.append("### Top HIP API by call count")
            lines.append("")
            lines.append(table_for_groups(hip_groups, args.top, "count"))
            lines.append("")

            lines.append("### Top kernels by total time")
            lines.append("")
            lines.append(table_for_groups(kernel_groups, args.top, "total"))
            lines.append("")

            lines.append("### Top kernels by dispatch count")
            lines.append("")
            lines.append(table_for_groups(kernel_groups, args.top, "count"))
            lines.append("")

            lines.append("### Kernel categories by total time")
            lines.append("")
            lines.append(table_for_groups(summarize_kernel_categories(kernel_groups), args.top, "total"))
            lines.append("")

            lines.append("### Memory allocation activity")
            lines.append("")
            lines.append(table_for_groups(mem_alloc_groups, args.top, "total"))
            lines.append("")

            if mem_copy_groups:
                lines.append("### Memory copy activity")
                lines.append("")
                lines.append(table_for_groups(mem_copy_groups, args.top, "total"))
                lines.append("")

    lines.append("## Initial interpretation checklist")
    lines.append("")
    lines.append("Look for:")
    lines.append("")
    lines.append("- High `hipLaunchKernel` count: possible tiny-kernel or fusion opportunity.")
    lines.append("- High `hipMemcpy` / `hipMemcpyAsync` count: possible data movement or scalar readback issue.")
    lines.append("- High `hipDeviceSynchronize` / `hipStreamSynchronize` count: possible synchronization bottleneck.")
    lines.append("- High `__amd_rocclr_copyBuffer` share: possible device-to-device copy/fill overhead.")
    lines.append("- High rocSPARSE SpMV share: sparse matrix-vector product is likely the main algorithmic bottleneck.")
    lines.append("- High rocBLAS level-1 share: repeated vector operations or reductions may be worth fusing later.")
    lines.append("")
    lines.append("Do not optimize solely from one smoke case. Use this summary to pick a small, testable optimization target.")
    lines.append("")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
