#!/usr/bin/env python3
"""Result validation and post-processing for the W7900 final-sprint harness v2.1."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

SAMPLE_RE = re.compile(r"^===== sample (.+?) =====$")
TEMP_RE = re.compile(r"Temperature \(Sensor (edge|junction|memory)\) \(C\):\s*([0-9.]+)", re.I)
CLOCK_RE = re.compile(r"(dcefclk|fclk|mclk|sclk|socclk) clock level:.*?\(([0-9.]+)Mhz\)", re.I)
POWER_RE = re.compile(r"Average Graphics Package Power \(W\):\s*([0-9.]+)", re.I)
GPU_UTIL_RE = re.compile(r"GPU use \(%\):\s*([0-9.]+)", re.I)
MEM_UTIL_RE = re.compile(r"(?:GPU Memory Allocated|Memory use) \(%\):\s*([0-9.]+)", re.I)
VRAM_TOTAL_RE = re.compile(r"VRAM Total Memory \(B\):\s*([0-9]+)", re.I)
VRAM_USED_RE = re.compile(r"VRAM Total Used Memory \(B\):\s*([0-9]+)", re.I)
GNU_TIME_PATTERNS = {
    "user_seconds": re.compile(r"^\s*User time \(seconds\):\s*(.+?)\s*$"),
    "system_seconds": re.compile(r"^\s*System time \(seconds\):\s*(.+?)\s*$"),
    "elapsed_text": re.compile(r"^\s*Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(.+?)\s*$"),
    "max_rss_kbytes": re.compile(r"^\s*Maximum resident set size \(kbytes\):\s*(.+?)\s*$"),
    "time_exit_status": re.compile(r"^\s*Exit status:\s*(.+?)\s*$"),
}
SOLVER_KEYS = [
    "solver", "terminationCode", "terminationIterate", "terminationInfeasIterate",
    "primalCode", "dualCode", "nIter", "nAxCalls", "nAtyCalls",
    "dSolvingBeg", "dSolvingTime", "dPresolveTime", "dScalingTime",
    "AllocMem_CopyMatToDeviceTime", "CopyVecToDeviceTime", "CopyVecToHostTime",
    "DeviceMatVecProdTime", "dPrimalObj", "dDualObj", "dPrimalFeas",
    "dDualFeas", "dDualityGap", "dRelPrimalFeas", "dRelDualFeas",
    "dRelDualityGap", "dPrimalObjAverage", "dDualObjAverage",
    "dPrimalFeasAverage", "dDualFeasAverage", "dDualityGapAverage",
]


def now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def nonempty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def to_float(value: Any) -> float | None:
    if not nonempty(value):
        return None
    try:
        number = float(str(value).strip())
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def normalize(value: Any) -> str:
    if not nonempty(value):
        return ""
    number = to_float(value)
    return f"{number:.17g}" if number is not None else str(value).strip()


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def update_env(path: Path, updates: dict[str, Any], prefix: str) -> None:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.is_file() else []
    kept = [line for line in lines if not line.split("=", 1)[0].startswith(prefix)]
    for key, value in updates.items():
        kept.append(f"{key}={value}")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(kept) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> tuple[dict[str, Any], str]:
    if not path.is_file() or path.stat().st_size == 0:
        return {}, "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {}, f"ERROR:{type(exc).__name__}:{exc}"
    return (payload, "OK") if isinstance(payload, dict) else ({}, f"NON_OBJECT:{type(payload).__name__}")


def resolve_artifact(run_root: Path, stored: str, sibling_of: Path | None = None, suffix: str = "") -> Path | None:
    if nonempty(stored):
        candidate = Path(str(stored))
        if candidate.is_file():
            return candidate.resolve()
        if candidate.is_absolute() and run_root.name in candidate.parts:
            idx = candidate.parts.index(run_root.name)
            mapped = run_root / Path(*candidate.parts[idx + 1 :])
            if mapped.is_file():
                return mapped.resolve()
        local = run_root / candidate
        if local.is_file():
            return local.resolve()
    if sibling_of is not None:
        candidate = Path(str(sibling_of.with_suffix("")) + suffix)
        if candidate.is_file():
            return candidate.resolve()
    return None


def relative(run_root: Path, path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(run_root))
    except ValueError:
        return str(path)


def parse_elapsed_seconds(text: str) -> float | None:
    try:
        parts = [float(x) for x in text.strip().split(":")]
    except ValueError:
        return None
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 1:
        return parts[0]
    return None


def parse_gnu_time(path: Path | None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if path is None or not path.is_file():
        return result
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        for key, pattern in GNU_TIME_PATTERNS.items():
            match = pattern.match(line)
            if match:
                result[key] = match.group(1).strip()
    if "elapsed_text" in result:
        result["elapsed_seconds_from_time"] = parse_elapsed_seconds(result["elapsed_text"])
    return result


def parse_resource_samples(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.is_file():
        return []
    samples: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = SAMPLE_RE.match(line)
        if match:
            if current is not None:
                samples.append(current)
            current = {"timestamp": match.group(1)}
            continue
        if current is None:
            continue
        for pattern, setter in (
            (TEMP_RE, lambda m: current.__setitem__(f"temp_{m.group(1).lower()}_c", float(m.group(2)))),
            (CLOCK_RE, lambda m: current.__setitem__(f"{m.group(1).lower()}_mhz", float(m.group(2)))),
            (POWER_RE, lambda m: current.__setitem__("power_w", float(m.group(1)))),
            (GPU_UTIL_RE, lambda m: current.__setitem__("gpu_util_pct", float(m.group(1)))),
            (MEM_UTIL_RE, lambda m: current.__setitem__("memory_util_pct", float(m.group(1)))),
            (VRAM_TOTAL_RE, lambda m: current.__setitem__("vram_total_bytes", int(m.group(1)))),
            (VRAM_USED_RE, lambda m: current.__setitem__("vram_used_bytes", int(m.group(1)))),
        ):
            match = pattern.search(line)
            if match:
                setter(match)
                break
    if current is not None:
        samples.append(current)
    return samples


def aggregate_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    def values(key: str) -> list[float]:
        return [float(s[key]) for s in samples if key in s and s[key] is not None]

    out: dict[str, Any] = {"resource_sample_count": len(samples)}
    for key, prefix in (
        ("vram_used_bytes", "vram_used_bytes"),
        ("power_w", "power_w"),
        ("gpu_util_pct", "gpu_util_pct"),
        ("memory_util_pct", "memory_util_pct"),
        ("sclk_mhz", "sclk_mhz"),
        ("mclk_mhz", "mclk_mhz"),
        ("fclk_mhz", "fclk_mhz"),
        ("temp_edge_c", "temp_edge_c"),
        ("temp_junction_c", "temp_junction_c"),
        ("temp_memory_c", "temp_memory_c"),
    ):
        vals = values(key)
        if vals:
            out[f"{prefix}_first"] = vals[0]
            out[f"{prefix}_min"] = min(vals)
            out[f"{prefix}_max"] = max(vals)
            out[f"{prefix}_avg"] = sum(vals) / len(vals)
    vram = values("vram_used_bytes")
    if vram:
        out["vram_peak_minus_min_bytes"] = max(vram) - min(vram)
    return out


def validate_solver_data(status: dict[str, str], payload: dict[str, Any], relative_factor: float) -> tuple[str, list[str], dict[str, Any]]:
    reasons: list[str] = []
    runtime = status.get("runtime_status", "")
    exit_code = status.get("exit_code", "")
    if runtime != "DONE":
        reasons.append(f"runtime_status={runtime or '[empty]'}")
    if str(exit_code) != "0":
        reasons.append(f"exit_code={exit_code or '[empty]'}")

    termination = str(payload.get("terminationCode", ""))
    primal = str(payload.get("primalCode", ""))
    dual = str(payload.get("dualCode", ""))
    if termination.upper() != "OPTIMAL":
        reasons.append(f"terminationCode={termination or '[empty]'}")
    if primal.upper() != "FEASIBLE":
        reasons.append(f"primalCode={primal or '[empty]'}")
    if dual.upper() != "FEASIBLE":
        reasons.append(f"dualCode={dual or '[empty]'}")

    tolerance = to_float(status.get("tolerance"))
    threshold = max((tolerance or 0.0) * relative_factor, 1e-12)
    metrics: dict[str, Any] = {
        "terminationCode": termination,
        "primalCode": primal,
        "dualCode": dual,
        "validation_threshold": threshold,
    }
    for key in ("dRelPrimalFeas", "dRelDualFeas", "dRelDualityGap"):
        value = to_float(payload.get(key))
        metrics[key] = value
        if value is None:
            reasons.append(f"{key}=missing_or_nonfinite")
        elif value > threshold:
            reasons.append(f"{key}={value:.6g}>threshold={threshold:.6g}")

    return ("PASS" if not reasons else "FAIL"), reasons, metrics


def command_validate_solver(args: argparse.Namespace) -> int:
    status_path = Path(args.status_file).resolve()
    json_path = Path(args.json_file).resolve()
    status = parse_env(status_path)
    payload, parse_status = read_json(json_path)
    if parse_status != "OK":
        result = "FAIL"
        reasons = [f"json_parse_status={parse_status}"]
        metrics: dict[str, Any] = {}
    else:
        result, reasons, metrics = validate_solver_data(status, payload, args.relative_factor)
    updates = {
        "solver_validation_status": result,
        "solver_validation_checked_at": now_iso(),
        "solver_validation_reasons_json": json.dumps(reasons, ensure_ascii=False, separators=(",", ":")),
        "solver_validation_termination": metrics.get("terminationCode", ""),
        "solver_validation_primal_code": metrics.get("primalCode", ""),
        "solver_validation_dual_code": metrics.get("dualCode", ""),
        "solver_validation_threshold": normalize(metrics.get("validation_threshold")),
    }
    if args.update_status:
        update_env(status_path, updates, "solver_validation_")
    if not args.quiet:
        print(json.dumps({"status": result, "reasons": reasons, **metrics}, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


def find_trace_files(trace_dir: Path) -> list[Path]:
    return sorted(p for p in trace_dir.rglob("*.csv") if p.is_file() and p.stat().st_size > 0)


def command_validate_profile(args: argparse.Namespace) -> int:
    status_path = Path(args.status_file).resolve()
    json_path = Path(args.json_file).resolve()
    exit_file = Path(args.exit_file).resolve()
    trace_dir = Path(args.trace_dir).resolve()
    reasons: list[str] = []
    if not exit_file.is_file() or exit_file.read_text(encoding="utf-8", errors="replace").strip() != "0":
        reasons.append("profiler_exit_code_not_zero")
    status = parse_env(status_path)
    payload, parse_status = read_json(json_path)
    if parse_status != "OK":
        reasons.append(f"json_parse_status={parse_status}")
    else:
        solver_result, solver_reasons, _ = validate_solver_data(status, payload, args.relative_factor)
        if solver_result != "PASS":
            reasons.extend(f"solver:{reason}" for reason in solver_reasons)
    traces = find_trace_files(trace_dir) if trace_dir.is_dir() else []
    kernel_traces = [p for p in traces if "kernel_trace" in p.name]
    if not traces:
        reasons.append("no_nonempty_trace_csv")
    if not kernel_traces:
        reasons.append("no_nonempty_kernel_trace_csv")
    result = "PASS" if not reasons else "FAIL"
    updates = {
        "profile_validation_status": result,
        "profile_validation_checked_at": now_iso(),
        "profile_validation_reasons_json": json.dumps(reasons, ensure_ascii=False, separators=(",", ":")),
        "profile_validation_trace_csv_count": len(traces),
        "profile_validation_kernel_trace_count": len(kernel_traces),
    }
    if args.update_status:
        update_env(status_path, updates, "profile_validation_")
    if not args.quiet:
        print(json.dumps({"status": result, "reasons": reasons, "trace_csv_count": len(traces), "kernel_trace_count": len(kernel_traces)}, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


def planned_case_names(path: Path) -> list[str]:
    names: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        name = raw.strip()
        if not name or name.startswith("#"):
            continue
        names.append(name[:-4] if name.endswith(".mps") else name)
    return names


def manifest_hashes(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = raw.strip().split(maxsplit=1)
        if len(parts) != 2:
            continue
        stored = parts[1].lstrip("*").removeprefix("./").removeprefix("mps/")
        result[Path(stored).name] = parts[0]
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def command_verify_dataset(args: argparse.Namespace) -> int:
    cases_file = Path(args.cases_file).resolve()
    mps_dir = Path(args.mps_dir).resolve()
    manifest = Path(args.manifest).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = planned_case_names(cases_file)
    expected = manifest_hashes(manifest)
    rows: list[dict[str, Any]] = []
    for case in cases:
        filename = f"{case}.mps"
        path = mps_dir / filename
        actual = sha256_file(path) if path.is_file() else ""
        exp = expected.get(filename, "")
        status = "OK" if exp and actual == exp else "FAIL"
        rows.append({"case": case, "filename": filename, "status": status, "expected_sha256": exp, "actual_sha256": actual, "bytes": path.stat().st_size if path.is_file() else 0, "path": str(path)})
    tsv = output_dir / f"dataset_verification_{args.scope}.tsv"
    with tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["case"], delimiter="\t")
        writer.writeheader(); writer.writerows(rows)
    summary = {"scope": args.scope, "checked_at": now_iso(), "expected_cases": len(cases), "verified_cases": sum(r["status"] == "OK" for r in rows), "failed_cases": sum(r["status"] != "OK" for r in rows), "cases_file": str(cases_file), "manifest": str(manifest), "report_tsv": str(tsv)}
    (output_dir / f"dataset_verification_{args.scope}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["failed_cases"] == 0 else 1


def iter_solver_statuses(run_root: Path) -> Iterable[Path]:
    for path in sorted(run_root.rglob("*.status.env")):
        if path.name.endswith(".profile.status.env"):
            continue
        yield path


def command_parse_run(args: argparse.Namespace) -> int:
    run_root = Path(args.run_root).resolve()
    output_csv = Path(args.output_csv).resolve()
    samples_csv = Path(args.resource_samples_csv).resolve()
    validation_json = Path(args.validation_json).resolve()
    rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for status_path in iter_solver_statuses(run_root):
        status = parse_env(status_path)
        json_path = resolve_artifact(run_root, status.get("json", ""), status_path, ".json")
        log_path = resolve_artifact(run_root, status.get("log", ""), status_path, ".log")
        time_path = resolve_artifact(run_root, status.get("time_log", ""), status_path, ".time.txt")
        metrics_path = resolve_artifact(run_root, status.get("metrics", ""), status_path, ".rocm_smi_raw.txt")
        command_path = resolve_artifact(run_root, status.get("command_file", ""), status_path, ".command.txt")
        payload, parse_status = read_json(json_path) if json_path else ({}, "MISSING")
        time_data = parse_gnu_time(time_path)
        samples = parse_resource_samples(metrics_path)
        aggregate = aggregate_samples(samples)
        validation_status = status.get("solver_validation_status", "")
        if not validation_status and parse_status == "OK":
            validation_status, reasons, _ = validate_solver_data(status, payload, args.relative_factor)
        else:
            reasons = []
        if validation_status != "PASS":
            issues.append({"case": status.get("case", ""), "tolerance": status.get("tolerance", ""), "repeat": status.get("repeat", ""), "issue": "solver_validation_not_pass", "detail": status.get("solver_validation_reasons_json", json.dumps(reasons))})

        row: dict[str, Any] = dict(status)
        row.update({key: payload.get(key, "") for key in SOLVER_KEYS})
        row.update({key: normalize(value) for key, value in time_data.items()})
        row.update({key: normalize(value) for key, value in aggregate.items()})
        wall = to_float(status.get("wall_seconds")); solve = to_float(payload.get("dSolvingTime")); elapsed = to_float(time_data.get("elapsed_seconds_from_time"))
        row["overhead_seconds"] = normalize(wall - solve if wall is not None and solve is not None else None)
        row["wall_minus_gnu_time_seconds"] = normalize(wall - elapsed if wall is not None and elapsed is not None else None)
        row["solver_validation_status"] = validation_status
        row["json_parse_status"] = parse_status
        row["status_path"] = relative(run_root, status_path)
        row["json_path_relative"] = relative(run_root, json_path)
        row["log_path_relative"] = relative(run_root, log_path)
        row["time_path_relative"] = relative(run_root, time_path)
        row["metrics_path_relative"] = relative(run_root, metrics_path)
        row["command_path_relative"] = relative(run_root, command_path)
        rows.append(row)

        for index, sample in enumerate(samples, 1):
            sample_rows.append({"group": status.get("group", ""), "case": status.get("case", ""), "tolerance": status.get("tolerance", ""), "repeat": status.get("repeat", ""), "gpu_id": status.get("gpu_id", ""), "sample_index": index, **sample, "metrics_path_relative": relative(run_root, metrics_path)})

    identity_counts = Counter((r.get("group", ""), r.get("case", ""), r.get("tolerance", ""), r.get("repeat", "")) for r in rows)
    duplicates = [identity for identity, count in identity_counts.items() if count > 1]
    if duplicates:
        issues.append({"issue": "duplicate_run_identities", "detail": duplicates})

    fields = [
        "group", "case", "tolerance", "repeat", "gpu_id", "start", "end",
        "runtime_status", "exit_code", "solver_validation_status", "json_parse_status",
        *SOLVER_KEYS, "wall_seconds", "elapsed_seconds_from_time", "wall_minus_gnu_time_seconds",
        "user_seconds", "system_seconds", "max_rss_kbytes", "time_exit_status", "overhead_seconds",
        "resource_sample_count", "vram_used_bytes_first", "vram_used_bytes_min", "vram_used_bytes_max",
        "vram_used_bytes_avg", "vram_peak_minus_min_bytes", "power_w_avg", "power_w_max",
        "gpu_util_pct_avg", "gpu_util_pct_max", "memory_util_pct_avg", "memory_util_pct_max",
        "sclk_mhz_avg", "sclk_mhz_max", "mclk_mhz_avg", "mclk_mhz_max", "fclk_mhz_avg",
        "fclk_mhz_max", "temp_edge_c_max", "temp_junction_c_max", "temp_memory_c_max",
        "mps", "status_path", "json_path_relative", "log_path_relative", "time_path_relative",
        "metrics_path_relative", "command_path_relative",
    ]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)
    sample_fields = ["group", "case", "tolerance", "repeat", "gpu_id", "sample_index", "timestamp", "vram_total_bytes", "vram_used_bytes", "gpu_util_pct", "memory_util_pct", "power_w", "sclk_mhz", "mclk_mhz", "fclk_mhz", "socclk_mhz", "dcefclk_mhz", "temp_edge_c", "temp_junction_c", "temp_memory_c", "metrics_path_relative"]
    samples_csv.parent.mkdir(parents=True, exist_ok=True)
    with samples_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sample_fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(sample_rows)
    summary = {"generated_at": now_iso(), "run_root": str(run_root), "solver_rows": len(rows), "resource_samples": len(sample_rows), "validation_pass_rows": sum(r.get("solver_validation_status") == "PASS" for r in rows), "issues": issues}
    validation_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] parsed_rows={len(rows)}")
    print(f"[OK] resource_samples={len(sample_rows)}")
    print(f"[OK] validation_pass_rows={summary['validation_pass_rows']}")
    print(f"[OK] summary={output_csv}")
    return 0


def command_throughput(args: argparse.Namespace) -> int:
    run_root = Path(args.run_root).resolve()
    summary_csv = Path(args.summary_csv).resolve()
    output_csv = Path(args.output_csv).resolve()
    with summary_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    group_scope = {"nonhard23_baseline": "nonhard23", "mini_baseline": "mini", "large_mps_pilot_baseline": "pilot"}
    out_rows: list[dict[str, Any]] = []
    for group, scope in group_scope.items():
        plan = run_root / "00_manifest" / f"planned_cases_{scope}.txt"
        if not plan.is_file():
            continue
        expected = planned_case_names(plan)
        by_repeat: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            if row.get("group") == group:
                by_repeat[row.get("repeat", "")].append(row)
        for repeat, items in sorted(by_repeat.items()):
            observed = [r.get("case", "") for r in items]
            counts = Counter(observed)
            missing = sorted(set(expected) - set(observed))
            unexpected = sorted(set(observed) - set(expected))
            duplicates = sorted(case for case, count in counts.items() if count > 1)
            pass_items = [r for r in items if r.get("runtime_status") == "DONE" and r.get("solver_validation_status") == "PASS"]
            valid = not missing and not unexpected and not duplicates and len(pass_items) == len(expected)
            wall = sum(to_float(r.get("wall_seconds")) or 0.0 for r in pass_items)
            solve = sum(to_float(r.get("dSolvingTime")) or 0.0 for r in pass_items)
            out_rows.append({"group": group, "scope": scope, "repeat": repeat, "expected_cases": len(expected), "observed_rows": len(items), "unique_observed_cases": len(set(observed)), "validated_optimal_cases": len(pass_items), "missing_cases": ";".join(missing), "unexpected_cases": ";".join(unexpected), "duplicate_cases": ";".join(duplicates), "matrix_complete": str(not missing and not unexpected and not duplicates).lower(), "throughput_valid": str(valid).lower(), "wall_seconds_sum": normalize(wall), "solve_seconds_sum": normalize(solve), "cases_per_hour": normalize(len(pass_items) * 3600 / wall if valid and wall else None), "solve_seconds_per_elapsed_hour": normalize(solve * 3600 / wall if valid and wall else None)})
    fields = ["group", "scope", "repeat", "expected_cases", "observed_rows", "unique_observed_cases", "validated_optimal_cases", "missing_cases", "unexpected_cases", "duplicate_cases", "matrix_complete", "throughput_valid", "wall_seconds_sum", "solve_seconds_sum", "cases_per_hour", "solve_seconds_per_elapsed_hour"]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(out_rows)
    print(output_csv)
    return 0


def command_validate_profiles(args: argparse.Namespace) -> int:
    run_root = Path(args.run_root).resolve(); output_json = Path(args.output_json).resolve(); output_csv = Path(args.output_csv).resolve()
    rows: list[dict[str, Any]] = []
    for status_path in sorted(run_root.rglob("*.profile.status.env")):
        status = parse_env(status_path)
        rows.append({"case": status.get("case", ""), "runtime_status": status.get("runtime_status", ""), "exit_code": status.get("exit_code", ""), "profile_validation_status": status.get("profile_validation_status", ""), "trace_csv_count": status.get("profile_validation_trace_csv_count", ""), "kernel_trace_count": status.get("profile_validation_kernel_trace_count", ""), "status_path": relative(run_root, status_path)})
    fields = ["case", "runtime_status", "exit_code", "profile_validation_status", "trace_csv_count", "kernel_trace_count", "status_path"]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    summary = {"generated_at": now_iso(), "profile_rows": len(rows), "pass_rows": sum(r["profile_validation_status"] == "PASS" for r in rows), "fail_rows": sum(r["profile_validation_status"] != "PASS" for r in rows), "rows": rows}
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def command_self_test(_: argparse.Namespace) -> int:
    temp = Path(tempfile.mkdtemp(prefix="w7900_results_selftest_"))
    try:
        status = temp / "case.status.env"; data = temp / "case.json"; metrics = temp / "case.rocm_smi_raw.txt"
        status.write_text("runtime_status=DONE\nexit_code=0\ntolerance=1e-4\n", encoding="utf-8")
        data.write_text(json.dumps({"terminationCode": "OPTIMAL", "primalCode": "FEASIBLE", "dualCode": "FEASIBLE", "dRelPrimalFeas": 1e-5, "dRelDualFeas": 2e-5, "dRelDualityGap": 3e-5}), encoding="utf-8")
        metrics.write_text("===== sample 2026-07-28T00:00:00.000000000+00:00 =====\nGPU[0]          : VRAM Total Used Memory (B): 100\nGPU[0]          : GPU use (%): 50\nGPU[0]          : Average Graphics Package Power (W): 100.0\nGPU[0]          : Temperature (Sensor edge) (C): 40.0\nGPU[0]          : Temperature (Sensor junction) (C): 50.0\nGPU[0]          : Temperature (Sensor memory) (C): 45.0\nGPU[0]          : sclk clock level: 1 (2000Mhz)\n===== sample 2026-07-28T00:00:00.500000000+00:00 =====\nGPU[0]          : VRAM Total Used Memory (B): 200\nGPU[0]          : GPU use (%): 90\nGPU[0]          : Average Graphics Package Power (W): 150.0\nGPU[0]          : Temperature (Sensor edge) (C): 41.0\nGPU[0]          : Temperature (Sensor junction) (C): 51.0\nGPU[0]          : Temperature (Sensor memory) (C): 46.0\nGPU[0]          : sclk clock level: 1 (2100Mhz)\n", encoding="utf-8")
        result, reasons, _ = validate_solver_data(parse_env(status), json.loads(data.read_text()), 50.0)
        assert result == "PASS", reasons
        samples = parse_resource_samples(metrics); assert len(samples) == 2
        agg = aggregate_samples(samples); assert agg["vram_peak_minus_min_bytes"] == 100
        assert agg["temp_junction_c_max"] == 51.0
    finally:
        shutil.rmtree(temp, ignore_errors=True)
    print("SELF_TEST_PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate-solver")
    p.add_argument("--status-file", required=True); p.add_argument("--json-file", required=True)
    p.add_argument("--relative-factor", type=float, default=float(os.environ.get("SOLVER_VALIDATION_FACTOR", "50")))
    p.add_argument("--update-status", action="store_true"); p.add_argument("--quiet", action="store_true"); p.set_defaults(func=command_validate_solver)
    p = sub.add_parser("validate-profile")
    p.add_argument("--status-file", required=True); p.add_argument("--json-file", required=True); p.add_argument("--exit-file", required=True); p.add_argument("--trace-dir", required=True)
    p.add_argument("--relative-factor", type=float, default=float(os.environ.get("SOLVER_VALIDATION_FACTOR", "50")))
    p.add_argument("--update-status", action="store_true"); p.add_argument("--quiet", action="store_true"); p.set_defaults(func=command_validate_profile)
    p = sub.add_parser("verify-dataset")
    p.add_argument("--scope", required=True); p.add_argument("--cases-file", required=True); p.add_argument("--mps-dir", required=True); p.add_argument("--manifest", required=True); p.add_argument("--output-dir", required=True); p.set_defaults(func=command_verify_dataset)
    p = sub.add_parser("parse-run")
    p.add_argument("--run-root", required=True); p.add_argument("--output-csv", required=True); p.add_argument("--resource-samples-csv", required=True); p.add_argument("--validation-json", required=True)
    p.add_argument("--relative-factor", type=float, default=float(os.environ.get("SOLVER_VALIDATION_FACTOR", "50"))); p.set_defaults(func=command_parse_run)
    p = sub.add_parser("throughput")
    p.add_argument("--run-root", required=True); p.add_argument("--summary-csv", required=True); p.add_argument("--output-csv", required=True); p.set_defaults(func=command_throughput)
    p = sub.add_parser("validate-profiles")
    p.add_argument("--run-root", required=True); p.add_argument("--output-json", required=True); p.add_argument("--output-csv", required=True); p.set_defaults(func=command_validate_profiles)
    p = sub.add_parser("self-test"); p.set_defaults(func=command_self_test)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
