#!/usr/bin/env python3
from pathlib import Path
import csv
import io
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "validation"

CSV_PATH = VALIDATION / "w7900_p11_runtime_callsite_inventory_20260617.csv"
MD_PATH = VALIDATION / "w7900_p11_runtime_callsite_inventory_20260617.md"
ZH_PATH = VALIDATION / "w7900_p11_runtime_callsite_inventory_20260617.zh-CN.md"

FIELDS = ["priority", "category", "file", "line", "role", "snippet", "prev", "next"]

def read_rows():
    text = CSV_PATH.read_text(encoding="utf-8", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise RuntimeError(f"no rows parsed from {CSV_PATH}")
    for row in rows:
        for field in FIELDS:
            row.setdefault(field, "")
    return rows

def write_csv(rows):
    with CSV_PATH.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] rewrote {CSV_PATH.relative_to(ROOT)} with LF line endings")

def esc(value):
    return str(value).replace("\n", " ").replace("|", "\\|").replace("`", "'")

def md_table(rows, limit=160):
    out = [
        "| priority | category | file:line | role | snippet |",
        "|---|---|---|---|---|",
    ]
    for row in rows[:limit]:
        out.append(
            "| {priority} | `{category}` | `{file}:{line}` | {role} | `{snippet}` |".format(
                priority=esc(row["priority"]),
                category=esc(row["category"]),
                file=esc(row["file"]),
                line=esc(row["line"]),
                role=esc(row["role"]),
                snippet=esc(row["snippet"]),
            )
        )
    if len(rows) > limit:
        out.append(f"| ... | ... | ... | ... | truncated; see CSV for all {len(rows)} rows |")
    return "\n".join(out)

def summary(counter):
    return "\n".join(f"- `{key}`: {counter[key]}" for key in sorted(counter))

def write_md(rows):
    rows = sorted(rows, key=lambda r: (r["priority"], r["category"], r["file"], int(r["line"])))
    by_priority = Counter(r["priority"] for r in rows)
    by_category = Counter(r["category"] for r in rows)
    by_role = Counter(r["role"] for r in rows)

    p0_rows = [r for r in rows if r["priority"] == "P0"]
    p1_rows = [r for r in rows if r["priority"] == "P1"]

    md = [
        "# W7900 P11 runtime callsite inventory",
        "",
        "This inventory maps source-level HIP/runtime and sparse-BLAS callsites after the P10 targeted rocprof run.",
        "",
        "P10 showed that the rank-1 HIP API cost is `hipMemcpy` on all five targeted cases and the rank-1 GPU kernel is `rocsparse::csrmvn_general_kernel`. This inventory is a pre-patch triage step: it identifies candidate callsites before changing code.",
        "",
        "## Summary",
        "",
        f"Total matched callsites: `{len(rows)}`",
        "",
        "By priority:",
        "",
        summary(by_priority),
        "",
        "By category:",
        "",
        summary(by_category),
        "",
        "By source role:",
        "",
        summary(by_role),
        "",
        "## P0 callsites",
        "",
        "P0 includes synchronous/asynchronous host-device copies and sparse SpMV-related API calls. These are the first places to inspect, but not necessarily the first places to modify.",
        "",
        md_table(p0_rows, limit=160),
        "",
        "## P1 callsites",
        "",
        "P1 includes kernel launch syntax, synchronization calls, and BLAS calls that may explain launch volume or reduction overhead.",
        "",
        md_table(p1_rows, limit=160),
        "",
        "## Tuning interpretation",
        "",
        "Do not blindly remove copies or synchronizations. For PDLP, residual checks, restart logic, termination checks, scaling, and objective/gap reporting can depend on the timing of host-visible values. The first safe P11 optimization candidate should therefore satisfy all of the following:",
        "",
        "1. It is execution-layer only.",
        "2. It does not change residual, restart, termination, scaling, or floating-point update order.",
        "3. It can be validated on the P10 five-case set and the fast-core6 set.",
        "4. It improves at least one of: HIP API calls, `hipMemcpy` time/count, kernel dispatch count, or ms/iter.",
        "5. It preserves status, gap, primal infeasibility, and dual infeasibility.",
        "",
        "## Files",
        "",
        "- `w7900_p11_runtime_callsite_inventory_20260617.csv`",
        "",
    ]
    MD_PATH.write_text("\n".join(md), encoding="utf-8", newline="\n")
    print(f"[OK] rewrote {MD_PATH.relative_to(ROOT)}")

    zh = [
        "# W7900 P11 runtime 调用点清单",
        "",
        "本清单基于 P10 targeted rocprof 结果，对源码中的 HIP/runtime 与 sparse-BLAS 相关调用点进行定位。",
        "",
        "P10 显示，5 个 targeted case 的 rank-1 HIP API 成本均为 `hipMemcpy`，rank-1 GPU kernel 均为 `rocsparse::csrmvn_general_kernel`。本清单是正式改代码前的 triage 步骤：先定位候选调用点，再决定是否修改。",
        "",
        "## 汇总",
        "",
        f"匹配到的调用点总数：`{len(rows)}`",
        "",
        "按优先级：",
        "",
        summary(by_priority),
        "",
        "按类别：",
        "",
        summary(by_category),
        "",
        "按源码角色：",
        "",
        summary(by_role),
        "",
        "## P0 调用点",
        "",
        "P0 包括同步/异步 host-device copy 和 sparse SpMV 相关 API 调用。这些位置需要优先检查，但不代表一定要优先修改。",
        "",
        md_table(p0_rows, limit=160),
        "",
        "## P1 调用点",
        "",
        "P1 包括 kernel launch 语法、同步调用和 BLAS 调用，可用于解释 kernel launch 数量或 reduction 开销。",
        "",
        md_table(p1_rows, limit=160),
        "",
        "## 调优解释",
        "",
        "不要盲目删除 copy 或同步。对于 PDLP，residual 检查、restart 逻辑、termination 判断、scaling 和 objective/gap 输出都可能依赖 host 可见值的时序。因此第一个安全的 P11 优化候选应满足：",
        "",
        "1. 只属于执行层优化。",
        "2. 不改变 residual、restart、termination、scaling 或浮点更新顺序。",
        "3. 能在 P10 五个 targeted case 和 fast-core6 集合上验证。",
        "4. 至少改善 HIP API calls、`hipMemcpy` time/count、kernel dispatch count 或 ms/iter 中的一项。",
        "5. 保持 status、gap、primal infeasibility 和 dual infeasibility 正常。",
        "",
        "## 文件",
        "",
        "- `w7900_p11_runtime_callsite_inventory_20260617.csv`",
        "",
    ]
    ZH_PATH.write_text("\n".join(zh), encoding="utf-8", newline="\n")
    print(f"[OK] rewrote {ZH_PATH.relative_to(ROOT)}")

def main():
    rows = read_rows()
    write_csv(rows)
    write_md(rows)
    print("[DONE] fixed P11 inventory formatting for remote GitHub rendering")

if __name__ == "__main__":
    main()
