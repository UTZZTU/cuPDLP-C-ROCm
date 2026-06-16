#!/usr/bin/env python3
from pathlib import Path
import csv
import re
from collections import Counter, defaultdict
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"

OUT_CSV = VALIDATION / "w7900_p11_runtime_callsite_inventory_20260617.csv"
OUT_MD = VALIDATION / "w7900_p11_runtime_callsite_inventory_20260617.md"
OUT_ZH = VALIDATION / "w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md"

SKIP_DIRS = {
    ".git",
    "build",
    "build-cpu",
    "build-rocm",
    "build-rocm-w7900",
    "build-rocm-gfx1150",
    "__pycache__",
    ".cache",
}

SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".cu",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
}

PATTERNS = [
    ("hip_memcpy_sync", re.compile(r"\bhipMemcpy\s*\(")),
    ("hip_memcpy_async", re.compile(r"\bhipMemcpyAsync\s*\(")),
    ("hip_memset", re.compile(r"\bhipMemset(?:Async)?\s*\(")),
    ("hip_malloc_free", re.compile(r"\bhip(?:Malloc|MallocAsync|Free|FreeAsync)\s*\(")),
    ("hip_sync", re.compile(r"\bhip(?:DeviceSynchronize|StreamSynchronize)\s*\(")),
    ("hip_device_query", re.compile(r"\bhip(?:GetDevice|GetDeviceCount|GetDeviceProperties|DeviceGetAttribute)\s*\(")),
    ("hip_kernel_macro", re.compile(r"\bhipLaunchKernelGGL\s*\(")),
    ("cuda_kernel_syntax", re.compile(r"<<<.*>>>")),
    ("rocsparse_api", re.compile(r"\brocsparse[A-Za-z0-9_]*\s*\(")),
    ("hipsparse_api", re.compile(r"\bhipsparse[A-Za-z0-9_]*\s*\(")),
    ("cusparse_compat_api", re.compile(r"\bcusparse[A-Za-z0-9_]*\s*\(")),
    ("rocblas_api", re.compile(r"\brocblas[A-Za-z0-9_]*\s*\(")),
    ("hipblas_api", re.compile(r"\bhipblas[A-Za-z0-9_]*\s*\(")),
    ("cublas_compat_api", re.compile(r"\bcublas[A-Za-z0-9_]*\s*\(")),
]

PRIORITY = {
    "hip_memcpy_sync": "P0",
    "hip_memcpy_async": "P0",
    "rocsparse_api": "P0",
    "hipsparse_api": "P0",
    "cusparse_compat_api": "P0",
    "cuda_kernel_syntax": "P1",
    "hip_kernel_macro": "P1",
    "hip_sync": "P1",
    "rocblas_api": "P1",
    "hipblas_api": "P1",
    "cublas_compat_api": "P1",
    "hip_device_query": "P2",
    "hip_malloc_free": "P2",
    "hip_memset": "P2",
}

def should_skip(path: Path) -> bool:
    parts = set(path.relative_to(ROOT).parts)
    if parts & SKIP_DIRS:
        return True
    return path.suffix not in SOURCE_SUFFIXES

def classify_role(rel: str) -> str:
    lower = rel.lower()
    if "/hip/" in lower or lower.startswith("cupdlp/hip/"):
        return "hip-port"
    if "cupdlp_linalg" in lower or "linalg" in lower:
        return "linalg"
    if "kernel" in lower:
        return "kernel"
    if "interface" in lower or "wrapper" in lower:
        return "interface"
    if lower.startswith("third_party/") or "pybind" in lower:
        return "third-party"
    return "other"

def collect_rows():
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or should_skip(path):
            continue

        rel = path.relative_to(ROOT).as_posix()
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue

            for category, pattern in PATTERNS:
                if pattern.search(line):
                    prev_line = lines[idx - 2].strip() if idx >= 2 else ""
                    next_line = lines[idx].strip() if idx < len(lines) else ""
                    rows.append({
                        "priority": PRIORITY.get(category, "P3"),
                        "category": category,
                        "file": rel,
                        "line": idx,
                        "role": classify_role(rel),
                        "snippet": stripped[:240],
                        "prev": prev_line[:180],
                        "next": next_line[:180],
                    })
    return rows

def write_csv(rows):
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["priority", "category", "file", "line", "role", "snippet", "prev", "next"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] wrote {OUT_CSV.relative_to(ROOT)}")

def md_table(rows, limit=120):
    out = [
        "| priority | category | file:line | role | snippet |",
        "|---|---|---|---|---|",
    ]
    for r in rows[:limit]:
        snippet = r["snippet"].replace("|", "\\|")
        out.append(
            f"| {r['priority']} | `{r['category']}` | `{r['file']}:{r['line']}` | {r['role']} | `{snippet}` |"
        )
    if len(rows) > limit:
        out.append(f"| ... | ... | ... | ... | truncated; see CSV for all {len(rows)} rows |")
    return "\n".join(out)

def write_md(rows):
    by_category = Counter(r["category"] for r in rows)
    by_priority = Counter(r["priority"] for r in rows)
    by_role = Counter(r["role"] for r in rows)

    p0_rows = [r for r in rows if r["priority"] == "P0"]
    p1_rows = [r for r in rows if r["priority"] == "P1"]

    cat_lines = "\n".join(f"- `{k}`: {v}" for k, v in sorted(by_category.items()))
    pri_lines = "\n".join(f"- `{k}`: {v}" for k, v in sorted(by_priority.items()))
    role_lines = "\n".join(f"- `{k}`: {v}" for k, v in sorted(by_role.items()))

    md = f"""# W7900 P11 runtime callsite inventory

This inventory maps source-level HIP/runtime and sparse-BLAS callsites after the P10 targeted rocprof run.

P10 showed that the rank-1 HIP API cost is `hipMemcpy` on all five targeted cases and the rank-1 GPU kernel is `rocsparse::csrmvn_general_kernel`. This inventory is a pre-patch triage step: it identifies candidate callsites before changing code.

## Summary

Total matched callsites: `{len(rows)}`

By priority:

{pri_lines}

By category:

{cat_lines}

By source role:

{role_lines}

## P0 callsites

P0 includes synchronous/asynchronous host-device copies and sparse SpMV-related API calls. These are the first places to inspect, but not necessarily the first places to modify.

{md_table(p0_rows, limit=160)}

## P1 callsites

P1 includes kernel launch syntax, synchronization calls, and BLAS calls that may explain launch volume or reduction overhead.

{md_table(p1_rows, limit=160)}

## Tuning interpretation

Do not blindly remove copies or synchronizations. For PDLP, residual checks, restart logic, termination checks, scaling, and objective/gap reporting can depend on the timing of host-visible values. The first safe P11 optimization candidate should therefore satisfy all of the following:

1. It is execution-layer only.
2. It does not change residual, restart, termination, scaling, or floating-point update order.
3. It can be validated on the P10 five-case set and the fast-core6 set.
4. It improves at least one of: HIP API calls, `hipMemcpy` time/count, kernel dispatch count, or ms/iter.
5. It preserves status, gap, primal infeasibility, and dual infeasibility.

## Files

- `w7900_p11_runtime_callsite_inventory_20260617.csv`
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"[OK] wrote {OUT_MD.relative_to(ROOT)}")

    zh = f"""# W7900 P11 runtime 调用点清单

本清单基于 P10 targeted rocprof 结果，对源码中的 HIP/runtime 与 sparse-BLAS 相关调用点进行定位。

P10 显示，5 个 targeted case 的 rank-1 HIP API 成本均为 `hipMemcpy`，rank-1 GPU kernel 均为 `rocsparse::csrmvn_general_kernel`。本清单是正式改代码前的 triage 步骤：先定位候选调用点，再决定是否修改。

## 汇总

匹配到的调用点总数：`{len(rows)}`

按优先级：

{pri_lines}

按类别：

{cat_lines}

按源码角色：

{role_lines}

## P0 调用点

P0 包括同步/异步 host-device copy 和 sparse SpMV 相关 API 调用。这些位置需要优先检查，但不代表一定要优先修改。

{md_table(p0_rows, limit=160)}

## P1 调用点

P1 包括 kernel launch 语法、同步调用和 BLAS 调用，可用于解释 kernel launch 数量或 reduction 开销。

{md_table(p1_rows, limit=160)}

## 调优解释

不要盲目删除 copy 或同步。对于 PDLP，residual 检查、restart 逻辑、termination 判断、scaling 和 objective/gap 输出都可能依赖 host 可见值的时序。因此第一个安全的 P11 优化候选应满足：

1. 只属于执行层优化。
2. 不改变 residual、restart、termination、scaling 或浮点更新顺序。
3. 能在 P10 五个 targeted case 和 fast-core6 集合上验证。
4. 至少改善 HIP API calls、`hipMemcpy` time/count、kernel dispatch count 或 ms/iter 中的一项。
5. 保持 status、gap、primal infeasibility 和 dual infeasibility 正常。

## 文件

- `w7900_p11_runtime_callsite_inventory_20260617.csv`
"""
    OUT_ZH.write_text(zh, encoding="utf-8")
    print(f"[OK] wrote {OUT_ZH.relative_to(ROOT)}")

def main():
    rows = collect_rows()
    rows.sort(key=lambda r: (r["priority"], r["category"], r["file"], r["line"]))
    write_csv(rows)
    write_md(rows)
    print("[DONE] W7900 P11 runtime callsite inventory complete")

if __name__ == "__main__":
    main()
