#!/usr/bin/env python3
from pathlib import Path
import csv
from collections import defaultdict
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"

RUNTIME = VALIDATION / "w7900_p10_current_targeted_rocprof_20260617_runtime.csv"
HIP_TOP = VALIDATION / "w7900_p10_current_targeted_rocprof_20260617_hip_api_top.csv"
KERNEL_TOP = VALIDATION / "w7900_p10_current_targeted_rocprof_20260617_kernel_top.csv"
INVENTORY = VALIDATION / "w7900_p11_runtime_callsite_inventory_20260617.csv"

OUT_MD = VALIDATION / "w7900_p11_first_patch_candidates_20260617.md"
OUT_ZH = VALIDATION / "w7900_p11_first_patch_candidates_20260617.zh-CN.md"
OUT_CSV = VALIDATION / "w7900_p11_first_patch_candidates_20260617.csv"

def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))

def f(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def i(x):
    try:
        return int(float(x))
    except Exception:
        return 0

def fmt(x, digits=3):
    try:
        v = float(x)
    except Exception:
        return str(x)
    if abs(v) >= 1000:
        return f"{v:.1f}"
    if abs(v) >= 1:
        return f"{v:.{digits}f}"
    return f"{v:.6f}"

def short_kernel(name):
    if "rocsparse::csrmvn_general_kernel" in name:
        return "rocsparse::csrmvn_general_kernel"
    if len(name) > 80:
        return name[:77] + "..."
    return name

def summarize_runtime(runtime_rows):
    rows = []
    for r in runtime_rows:
        solve = f(r["solve_time_sec"])
        hip_ms = f(r["hip_api_total_ms"])
        kernel_ms = f(r["kernel_total_ms"])
        memcpy_ms = f(r["memory_copy_total_ms"])
        rows.append({
            "case": r["case"],
            "status": r["status"],
            "nIter": r["nIter"],
            "solve_s": solve,
            "hip_api_calls": i(r["hip_api_calls"]),
            "hip_api_ms": hip_ms,
            "kernel_dispatches": i(r["kernel_dispatches"]),
            "kernel_ms": kernel_ms,
            "memcpy_count": i(r["memory_copy_count"]),
            "memcpy_ms": memcpy_ms,
            "hip_ms_per_iter": hip_ms / max(1, i(r["nIter"])),
            "kernel_dispatches_per_iter": i(r["kernel_dispatches"]) / max(1, i(r["nIter"])),
        })
    return rows

def top_by_case(rows, key_name):
    out = {}
    for r in rows:
        if r.get("rank") == "1":
            out[r["case"]] = r.get(key_name, "")
    return out

def inventory_matches(inv_rows, categories):
    return [r for r in inv_rows if r["category"] in categories]

def write_candidate_csv(candidates):
    fields = [
        "rank",
        "candidate",
        "expected_effect",
        "risk",
        "why_now",
        "first_validation",
        "recommendation",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(candidates)
    print(f"[OK] wrote {OUT_CSV.relative_to(ROOT)}")

def candidate_table(candidates, zh=False):
    out = [
        "| rank | candidate | expected effect | risk | recommendation |",
        "|---:|---|---|---|---|",
    ]
    for c in candidates:
        out.append(
            "| {rank} | {candidate} | {effect} | {risk} | {rec} |".format(
                rank=c["rank"],
                candidate=c["candidate"],
                effect=c["expected_effect"],
                risk=c["risk"],
                rec=c["recommendation"],
            )
        )
    return "\n".join(out)

def runtime_table(rows):
    out = [
        "| case | status | nIter | solve s | HIP API calls | HIP ms | kernel dispatches | kernel ms | kernel dispatches / iter | HIP ms / iter |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        out.append(
            "| {case} | {status} | {nIter} | {solve} | {hip_calls} | {hip_ms} | {kdisp} | {kms} | {kpi} | {hpi} |".format(
                case=r["case"],
                status=r["status"],
                nIter=r["nIter"],
                solve=fmt(r["solve_s"]),
                hip_calls=r["hip_api_calls"],
                hip_ms=fmt(r["hip_api_ms"]),
                kdisp=r["kernel_dispatches"],
                kms=fmt(r["kernel_ms"]),
                kpi=fmt(r["kernel_dispatches_per_iter"]),
                hpi=fmt(r["hip_ms_per_iter"]),
            )
        )
    return "\n".join(out)

def callsite_table(rows, limit=40):
    out = [
        "| priority | category | file:line | role | snippet |",
        "|---|---|---|---|---|",
    ]
    for r in rows[:limit]:
        snippet = r["snippet"].replace("|", "\\|").replace("`", "'")
        out.append(
            f"| {r['priority']} | `{r['category']}` | `{r['file']}:{r['line']}` | {r['role']} | `{snippet}` |"
        )
    if len(rows) > limit:
        out.append(f"| ... | ... | ... | ... | truncated; see CSV for all {len(rows)} rows |")
    return "\n".join(out)

def main():
    runtime = summarize_runtime(read_csv(RUNTIME))
    hip_top = read_csv(HIP_TOP)
    kernel_top = read_csv(KERNEL_TOP)
    inv = read_csv(INVENTORY)

    top_hip = top_by_case(hip_top, "hip_api")
    top_kernel = top_by_case(kernel_top, "kernel")

    copy_callsites = inventory_matches(inv, {"hip_memcpy_sync", "hip_memcpy_async"})
    spmv_callsites = inventory_matches(inv, {"hipsparse_api", "cusparse_compat_api", "rocsparse_api"})
    launch_callsites = inventory_matches(inv, {"cuda_kernel_syntax", "hip_kernel_macro"})
    sync_callsites = inventory_matches(inv, {"hip_sync"})

    cases = [r["case"] for r in runtime]
    all_ok = all(r["status"] == "OPTIMAL" for r in runtime)

    candidates = [
        {
            "rank": 1,
            "candidate": "copy-reduction triage around scalar host reads",
            "expected_effect": "reduce hipMemcpy time/count if repeated scalar D2H copies are confirmed",
            "risk": "high if tied to residual/restart/termination decisions",
            "why_now": "P10 shows hipMemcpy as rank-1 HIP API on all targeted cases",
            "first_validation": "P10 five-case targeted set plus fast-core6 derived metrics",
            "recommendation": "inspect callsites first; do not remove numerical host reads blindly",
        },
        {
            "rank": 2,
            "candidate": "SpMV profiling and algorithm sweep",
            "expected_effect": "reduce dominant rocsparse CSR SpMV kernel time",
            "risk": "medium because SpMV algorithm can alter determinism or summation order",
            "why_now": "P10 shows rocsparse::csrmvn_general_kernel as rank-1 kernel",
            "first_validation": "run one-case micro sweep first, then P10 five-case set",
            "recommendation": "make an opt-in experiment flag before changing default behavior",
        },
        {
            "rank": 3,
            "candidate": "kernel launch volume cleanup for vector/reduction helper kernels",
            "expected_effect": "reduce launch count and small-kernel overhead",
            "risk": "medium if fusion changes floating-point order",
            "why_now": "P10 long cases show very high kernel dispatch counts",
            "first_validation": "compare kernel dispatches/iter and gap/primal/dual",
            "recommendation": "only fuse execution-equivalent helper kernels with identical update order",
        },
        {
            "rank": 4,
            "candidate": "device-query and allocation cleanup",
            "expected_effect": "reduce startup overhead on short cases",
            "risk": "low",
            "why_now": "P10 short case shows visible one-time hipGetDevice/init costs",
            "first_validation": "L2CTA3D and set-cover-model smoke profiling",
            "recommendation": "lower priority because long cases are dominated by copy/SpMV/launch",
        },
    ]

    write_candidate_csv(candidates)

    md = f"""# W7900 P11 first patch candidates

This report combines P10 targeted rocprof data with the P11 runtime callsite inventory to choose the first safe optimization direction.

## Input evidence

- P10 runtime CSV: `{RUNTIME.name}`
- P10 HIP API top CSV: `{HIP_TOP.name}`
- P10 kernel top CSV: `{KERNEL_TOP.name}`
- P11 inventory CSV: `{INVENTORY.name}`

All targeted cases OPTIMAL: `{all_ok}`

Targeted cases: `{", ".join(cases)}`

## Runtime pressure points

{runtime_table(runtime)}

## Rank-1 hotspots by case

| case | rank-1 HIP API | rank-1 kernel |
|---|---|---|
""" 
    for case in cases:
        md += f"| {case} | `{top_hip.get(case, '')}` | `{short_kernel(top_kernel.get(case, ''))}` |\n"

    md += f"""
## Candidate ranking

{candidate_table(candidates)}

## Relevant callsites

### Copy callsites

{callsite_table(copy_callsites)}

### SpMV / sparse-BLAS callsites

{callsite_table(spmv_callsites)}

### Kernel launch callsites

{callsite_table(launch_callsites)}

### Synchronization callsites

{callsite_table(sync_callsites)}

## Recommendation

The first real P11 patch should not blindly delete `hipMemcpy` callsites. The safest next step is to inspect whether the repeated `hipMemcpy` pressure comes from scalar host reads required by residual, restart, or termination logic. If yes, those copies are numerically meaningful and should only be reduced through a guarded experiment with explicit validation. In parallel, SpMV algorithm tuning should be implemented as an opt-in experiment flag rather than a default behavior change, because it may affect determinism or floating-point summation order.

Therefore, the next code patch should be one of:

1. an opt-in profiling/experiment switch for SpMV algorithm selection; or
2. a narrow scalar-copy experiment behind a compile-time/runtime flag, with P10 and fast-core6 validation.
"""
    OUT_MD.write_text(md, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_MD.relative_to(ROOT)}")

    zh = f"""# W7900 P11 第一轮优化候选

本报告把 P10 targeted rocprof 数据和 P11 runtime 调用点清单结合起来，用于选择第一个安全优化方向。

## 输入依据

- P10 runtime CSV：`{RUNTIME.name}`
- P10 HIP API top CSV：`{HIP_TOP.name}`
- P10 kernel top CSV：`{KERNEL_TOP.name}`
- P11 inventory CSV：`{INVENTORY.name}`

targeted cases 是否全部 OPTIMAL：`{all_ok}`

targeted cases：`{", ".join(cases)}`

## 运行压力点

{runtime_table(runtime)}

## 每个 case 的 rank-1 热点

| case | rank-1 HIP API | rank-1 kernel |
|---|---|---|
"""
    for case in cases:
        zh += f"| {case} | `{top_hip.get(case, '')}` | `{short_kernel(top_kernel.get(case, ''))}` |\n"

    zh += f"""
## 候选优化排序

{candidate_table(candidates, zh=True)}

## 相关调用点

### Copy 调用点

{callsite_table(copy_callsites)}

### SpMV / sparse-BLAS 调用点

{callsite_table(spmv_callsites)}

### Kernel launch 调用点

{callsite_table(launch_callsites)}

### Synchronization 调用点

{callsite_table(sync_callsites)}

## 建议

第一个真正的 P11 patch 不应盲目删除 `hipMemcpy` 调用点。更安全的做法是先确认重复的 `hipMemcpy` 压力是否来自 residual、restart 或 termination 所需的 scalar host read。如果是，这些 copy 具有数值意义，只能通过带开关的实验谨慎降低，并且必须明确验证 gap、primal infeasibility、dual infeasibility 和迭代数。

因此下一步代码 patch 建议二选一：

1. 增加一个可选的 SpMV algorithm profiling/experiment 开关；或
2. 增加一个窄范围 scalar-copy experiment 开关，并用 P10 五个 case 和 fast-core6 验证。
"""
    OUT_ZH.write_text(zh, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_ZH.relative_to(ROOT)}")
    print("[DONE] W7900 P11 first patch candidate report complete")

if __name__ == "__main__":
    main()
