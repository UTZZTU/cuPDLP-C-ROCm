#!/usr/bin/env python3
from pathlib import Path
import csv
import shutil
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"
LATEST = ROOT / "validation" / "results" / "latest_w7900_p10_current_targeted_rocprof.txt"

PREFIX = "w7900_p10_current_targeted_rocprof_20260617"

OUT_RUNTIME = VALIDATION / f"{PREFIX}_runtime.csv"
OUT_KERNEL = VALIDATION / f"{PREFIX}_kernel_top.csv"
OUT_HIP = VALIDATION / f"{PREFIX}_hip_api_top.csv"
OUT_MEMCPY = VALIDATION / f"{PREFIX}_memory_copy_top.csv"
OUT_DELTAS = VALIDATION / f"{PREFIX}_milestone_deltas.csv"
OUT_MD = VALIDATION / f"{PREFIX}_summary.md"
OUT_ZH = VALIDATION / f"{PREFIX}_summary.zh-CN.md"

def read_latest_result_root() -> Path:
    if not LATEST.exists():
        raise FileNotFoundError(f"missing latest result pointer: {LATEST}")
    result_root = Path(LATEST.read_text(encoding="utf-8").strip())
    if not result_root.exists():
        raise FileNotFoundError(f"result root does not exist: {result_root}")
    return result_root

def copy_file(src: Path, dst: Path):
    if not src.exists():
        raise FileNotFoundError(src)
    shutil.copyfile(src, dst)
    print(f"[OK] copied {src} -> {dst.relative_to(ROOT)}")

def read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))

def fmt_float(x, digits=3):
    if x in ("", None):
        return ""
    try:
        v = float(x)
    except Exception:
        return str(x)
    if abs(v) >= 1000:
        return f"{v:.1f}"
    if abs(v) >= 1:
        return f"{v:.3f}"
    return f"{v:.6f}"

def md_runtime_table(rows, zh=False):
    if zh:
        header = "| case | status | nIter | solve s | HIP API calls | HIP API ms | kernel dispatches | kernel ms | memcpy count | memcpy ms |"
    else:
        header = "| case | status | nIter | solve s | HIP API calls | HIP API ms | kernel dispatches | kernel ms | memcpy count | memcpy ms |"

    out = [
        header,
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for r in rows:
        out.append(
            "| {case} | {status} | {nIter} | {solve} | {hip_calls} | {hip_ms} | {kernels} | {kernel_ms} | {memcpy_count} | {memcpy_ms} |".format(
                case=r["case"],
                status=r["status"],
                nIter=r["nIter"],
                solve=fmt_float(r["solve_time_sec"]),
                hip_calls=r["hip_api_calls"],
                hip_ms=fmt_float(r["hip_api_total_ms"]),
                kernels=r["kernel_dispatches"],
                kernel_ms=fmt_float(r["kernel_total_ms"]),
                memcpy_count=r["memory_copy_count"],
                memcpy_ms=fmt_float(r["memory_copy_total_ms"]),
            )
        )
    return "\n".join(out)

def first_rank_by_case(rows):
    out = {}
    for r in rows:
        if r.get("rank") == "1" and r.get("case") not in out:
            out[r["case"]] = r
    return out

def md_rank1_table(kernel_rows, hip_rows, zh=False):
    k1 = first_rank_by_case(kernel_rows)
    h1 = first_rank_by_case(hip_rows)

    out = [
        "| case | top kernel | kernel calls | kernel total ms | top HIP API | HIP calls | HIP API total ms |",
        "|---|---|---:|---:|---|---:|---:|",
    ]

    for case in sorted(set(k1) | set(h1)):
        kr = k1.get(case, {})
        hr = h1.get(case, {})
        kernel = kr.get("kernel", "")
        if "rocsparse::csrmvn_general_kernel" in kernel:
            kernel_short = "rocsparse::csrmvn_general_kernel"
        elif len(kernel) > 80:
            kernel_short = kernel[:77] + "..."
        else:
            kernel_short = kernel

        out.append(
            "| {case} | `{kernel}` | {kcalls} | {kms} | `{hip}` | {hcalls} | {hms} |".format(
                case=case,
                kernel=kernel_short,
                kcalls=kr.get("calls", ""),
                kms=fmt_float(kr.get("total_ms", "")),
                hip=hr.get("hip_api", ""),
                hcalls=hr.get("calls", ""),
                hms=fmt_float(hr.get("total_ms", "")),
            )
        )
    return "\n".join(out)

def write_summaries(result_root: Path):
    runtime_rows = read_csv(OUT_RUNTIME)
    kernel_rows = read_csv(OUT_KERNEL)
    hip_rows = read_csv(OUT_HIP)

    cases = [r["case"] for r in runtime_rows]
    ok_count = sum(1 for r in runtime_rows if r["exitcode"] == "0" and r["status"] == "OPTIMAL")

    md = f"""# W7900 P10 current targeted rocprof summary

Run dir: `{result_root}`

Trace mode: `rocprofv3 --runtime-trace --output-format csv`.

This P10 run profiles the current W7900/gfx1100 branch on five targeted cases selected from the P9 derived-metric analysis:

- positive execution-efficiency sample: `thk_48`
- stable iteration-count sample: `square41`
- convergence-regression samples: `L2CTA3D`, `set-cover-model`, `tpl-tub-ws1617`

Raw rocprofv3 trace files remain under `/app/cupdlp_w7900/results` and are intentionally not committed. This validation entry commits only compact CSV/Markdown summaries.

## Runtime summary

- Cases: `{len(cases)}`
- Successful OPTIMAL cases: `{ok_count}/{len(cases)}`
- Cases: `{", ".join(cases)}`

{md_runtime_table(runtime_rows)}

## Top rank-1 hotspots by case

{md_rank1_table(kernel_rows, hip_rows)}

## Interpretation

The five targeted cases all complete successfully under current. The traces confirm that rocSPARSE CSR SpMV kernels are the dominant GPU kernel hotspot on several cases, especially `set-cover-model`, `square41`, and `thk_48`. HIP API time is dominated by `hipMemcpy` on the longer cases, while `hipLaunchKernel` and `hipMemcpyAsync` are also prominent. This supports the next tuning direction: keep profiling focused on SpMV behavior, kernel launch volume, and host-device copy reduction, while avoiding unvalidated changes to residual, restart, termination, or scaling logic.

## Files

- `{OUT_RUNTIME.name}`
- `{OUT_KERNEL.name}`
- `{OUT_HIP.name}`
- `{OUT_MEMCPY.name}`
- `{OUT_DELTAS.name}`
"""
    OUT_MD.write_text(md, encoding="utf-8")

    zh = f"""# W7900 P10 current targeted rocprof 汇总

运行目录：`{result_root}`

Trace 模式：`rocprofv3 --runtime-trace --output-format csv`。

本次 P10 对 current W7900/gfx1100 分支上的 5 个代表 case 做 targeted profiling，这些 case 来自 P9 派生指标分析：

- 正向执行效率样本：`thk_48`
- 迭代数稳定样本：`square41`
- 收敛迭代数回退样本：`L2CTA3D`、`set-cover-model`、`tpl-tub-ws1617`

原始 rocprofv3 trace 文件继续保留在 `/app/cupdlp_w7900/results`，不提交到 Git。本条 validation 只提交 compact CSV/Markdown 汇总。

## 运行汇总

- case 数：`{len(cases)}`
- 成功 OPTIMAL：`{ok_count}/{len(cases)}`
- case：`{", ".join(cases)}`

{md_runtime_table(runtime_rows, zh=True)}

## 每个 case 的 rank-1 热点

{md_rank1_table(kernel_rows, hip_rows, zh=True)}

## 解释

5 个 targeted case 在 current 下均成功完成。trace 结果确认，rocSPARSE CSR SpMV kernel 是多个 case 的主要 GPU kernel 热点，尤其是 `set-cover-model`、`square41` 和 `thk_48`。在较长 case 上，HIP API 时间主要由 `hipMemcpy` 主导，同时 `hipLaunchKernel` 和 `hipMemcpyAsync` 也很突出。这支持下一步调优方向：继续聚焦 SpMV 行为、kernel launch 数量和 host-device copy reduction，同时避免在没有明确数值验证的情况下改动 residual、restart、termination 或 scaling 逻辑。

## 文件

- `{OUT_RUNTIME.name}`
- `{OUT_KERNEL.name}`
- `{OUT_HIP.name}`
- `{OUT_MEMCPY.name}`
- `{OUT_DELTAS.name}`
"""
    OUT_ZH.write_text(zh, encoding="utf-8")

    print(f"[OK] wrote {OUT_MD.relative_to(ROOT)}")
    print(f"[OK] wrote {OUT_ZH.relative_to(ROOT)}")

def main():
    result_root = read_latest_result_root()

    copy_file(result_root / "trace_summary_by_run.csv", OUT_RUNTIME)
    copy_file(result_root / "trace_kernel_top.csv", OUT_KERNEL)
    copy_file(result_root / "trace_hip_api_top.csv", OUT_HIP)
    copy_file(result_root / "trace_memory_copy_top.csv", OUT_MEMCPY)
    copy_file(result_root / "trace_milestone_deltas.csv", OUT_DELTAS)

    write_summaries(result_root)

    print("[DONE] archived P10 compact outputs")

if __name__ == "__main__":
    main()
