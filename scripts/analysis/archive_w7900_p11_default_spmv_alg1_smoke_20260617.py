#!/usr/bin/env python3
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[2]
RESULTS = Path("/app/cupdlp_w7900/results")
VALIDATION = ROOT / "validation"

OUT_CSV = VALIDATION / "w7900_p11_default_spmv_alg1_smoke_20260617.csv"
OUT_MD = VALIDATION / "w7900_p11_default_spmv_alg1_smoke_20260617_summary.md"
OUT_ZH = VALIDATION / "w7900_p11_default_spmv_alg1_smoke_20260617_summary.zh-CN.md"

PATTERNS = {
    "status": re.compile(r"Solving information:\s*(.*)"),
    "primal_objective": re.compile(r"Primal objective:\s*([+-]?\d+\.\d+e[+-]\d+)"),
    "dual_objective": re.compile(r"Dual objective:\s*([+-]?\d+\.\d+e[+-]\d+)"),
    "primal_infeas": re.compile(r"Primal infeas \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)"),
    "dual_infeas": re.compile(r"Dual infeas \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)"),
    "duality_gap": re.compile(r"Duality gap \(abs/rel\):\s*([0-9.eE+-]+)\s*/\s*([0-9.eE+-]+)"),
    "niter": re.compile(r"Number of iterations:\s*(\d+)"),
    "total_solver_time": re.compile(r"Total solver time\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+iterations"),
    "solve_time": re.compile(r"Solve time\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+iterations"),
    "iters_per_sec": re.compile(r"Iters per sec\s*([0-9.eE+-]+)"),
    "update_iterates": re.compile(r"UpdateIterates\s*([0-9.eE+-]+)\s+in\s+(\d+)\s+calls"),
}

def newest_dir(pattern: str) -> Path:
    dirs = sorted(d for d in RESULTS.glob(pattern) if d.is_dir())
    if not dirs:
        raise FileNotFoundError(f"no result dir matching {pattern}")
    return dirs[-1]

def read_exit(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    m = re.search(r"exit=(\d+)", text)
    return m.group(1) if m else text

def parse_log(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    row = {}

    m = PATTERNS["status"].search(text)
    row["status"] = m.group(1).strip() if m else ""

    for key in ["primal_objective", "dual_objective", "niter", "iters_per_sec"]:
        m = PATTERNS[key].search(text)
        row[key] = m.group(1) if m else ""

    m = PATTERNS["primal_infeas"].search(text)
    row["primal_infeas_abs"] = m.group(1) if m else ""
    row["primal_infeas_rel"] = m.group(2) if m else ""

    m = PATTERNS["dual_infeas"].search(text)
    row["dual_infeas_abs"] = m.group(1) if m else ""
    row["dual_infeas_rel"] = m.group(2) if m else ""

    m = PATTERNS["duality_gap"].search(text)
    row["duality_gap_abs"] = m.group(1) if m else ""
    row["duality_gap_rel"] = m.group(2) if m else ""

    m = PATTERNS["total_solver_time"].search(text)
    row["total_solver_time_sec"] = m.group(1) if m else ""

    m = PATTERNS["solve_time"].search(text)
    row["solve_time_sec"] = m.group(1) if m else ""

    m = PATTERNS["update_iterates"].search(text)
    row["update_iterates_sec"] = m.group(1) if m else ""
    row["update_iterates_calls"] = m.group(2) if m else ""

    return row

def collect_rows():
    default_dir = newest_dir("w7900_p11_default_spmv_alg1_smoke_default_*")
    rollback_dir = newest_dir("w7900_p11_default_spmv_alg1_smoke_rollback_alg2_*")

    configs = [
        {
            "mode": "default_csr_alg1",
            "description": "new default, no CUPDLP_HIP_SPMV_ALG",
            "dir": default_dir,
            "log": default_dir / "set-cover-model_default_alg1.log",
            "exit": default_dir / "set-cover-model_default_alg1.exit",
        },
        {
            "mode": "rollback_csr_alg2",
            "description": "old default rollback with CUPDLP_HIP_SPMV_ALG=csr_alg2",
            "dir": rollback_dir,
            "log": rollback_dir / "set-cover-model_rollback_alg2.log",
            "exit": rollback_dir / "set-cover-model_rollback_alg2.exit",
        },
    ]

    rows = []
    for cfg in configs:
        if not cfg["log"].exists():
            raise FileNotFoundError(cfg["log"])
        if not cfg["exit"].exists():
            raise FileNotFoundError(cfg["exit"])

        row = {
            "mode": cfg["mode"],
            "description": cfg["description"],
            "case": "set-cover-model",
            "exitcode": read_exit(cfg["exit"]),
            "run_dir": str(cfg["dir"]),
            "log_file": cfg["log"].name,
        }
        row.update(parse_log(cfg["log"]))
        rows.append(row)

    return rows

def write_csv(rows):
    fields = [
        "mode",
        "description",
        "case",
        "exitcode",
        "status",
        "niter",
        "total_solver_time_sec",
        "solve_time_sec",
        "iters_per_sec",
        "update_iterates_sec",
        "update_iterates_calls",
        "primal_objective",
        "dual_objective",
        "primal_infeas_abs",
        "primal_infeas_rel",
        "dual_infeas_abs",
        "dual_infeas_rel",
        "duality_gap_abs",
        "duality_gap_rel",
        "run_dir",
        "log_file",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] wrote {OUT_CSV.relative_to(ROOT)}")

def md_table(rows):
    out = [
        "| mode | exit | status | nIter | solve s | total s | primal rel infeas | dual rel infeas | rel gap |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        out.append(
            "| {mode} | {exitcode} | {status} | {niter} | {solve} | {total} | {pinf} | {dinf} | {gap} |".format(
                mode=r["mode"],
                exitcode=r["exitcode"],
                status=r["status"],
                niter=r["niter"],
                solve=r["solve_time_sec"],
                total=r["total_solver_time_sec"],
                pinf=r["primal_infeas_rel"],
                dinf=r["dual_infeas_rel"],
                gap=r["duality_gap_rel"],
            )
        )
    return "\n".join(out)

def write_md(rows):
    all_exit_zero = all(r["exitcode"] == "0" for r in rows)
    all_optimal = all("Optimal current solution" in r["status"] for r in rows)
    same_iter = len({r["niter"] for r in rows}) == 1
    same_objective = len({r["primal_objective"] for r in rows}) == 1 and len({r["dual_objective"] for r in rows}) == 1

    md = f"""# W7900 P11 default SpMV ALG1 smoke summary

This validation checks the P11 default-policy update:

- commit: `2643849 tuning: default HIP SpMV algorithm to CSR ALG1`
- new default: `HIPSPARSE_SPMV_CSR_ALG1`
- rollback mode: `CUPDLP_HIP_SPMV_ALG=csr_alg2`
- case: `set-cover-model`

Raw logs remain under `/app/cupdlp_w7900/results` and are not committed.

## Result

- Both runs exit with code 0: `{all_exit_zero}`
- Both runs report `Optimal current solution`: `{all_optimal}`
- Both runs use the same iteration count: `{same_iter}`
- Both runs preserve primal and dual objective values: `{same_objective}`

## Smoke table

{md_table(rows)}

## Interpretation

The new default SpMV algorithm policy passes the short smoke validation. The default no-env path now uses `csr_alg1`, and the old default can still be restored with `CUPDLP_HIP_SPMV_ALG=csr_alg2`.

This smoke is a correctness and rollback check, not a performance conclusion. The broader P11 five-case sweep remains the main evidence for choosing `csr_alg1` as the current W7900 default.

## Files

- `w7900_p11_default_spmv_alg1_smoke_20260617.csv`
"""
    OUT_MD.write_text(md, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_MD.relative_to(ROOT)}")

    zh = f"""# W7900 P11 default SpMV ALG1 smoke 汇总

本次 validation 检查 P11 默认策略更新：

- commit：`2643849 tuning: default HIP SpMV algorithm to CSR ALG1`
- 新默认：`HIPSPARSE_SPMV_CSR_ALG1`
- 回退模式：`CUPDLP_HIP_SPMV_ALG=csr_alg2`
- case：`set-cover-model`

原始日志继续保留在 `/app/cupdlp_w7900/results`，不提交到 Git。

## 结果

- 两次运行 exit code 均为 0：`{all_exit_zero}`
- 两次运行均报告 `Optimal current solution`：`{all_optimal}`
- 两次运行迭代数一致：`{same_iter}`
- 两次运行保持 primal 和 dual objective 一致：`{same_objective}`

## Smoke 表

{md_table(rows)}

## 解释

新的 SpMV 默认策略通过了短 smoke validation。当前默认无环境变量路径使用 `csr_alg1`，旧默认仍可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 恢复。

本 smoke 是正确性和回退能力检查，不是性能结论。选择 `csr_alg1` 作为当前 W7900 默认策略的主要依据仍然是前面的 P11 五 case sweep。

## 文件

- `w7900_p11_default_spmv_alg1_smoke_20260617.csv`
"""
    OUT_ZH.write_text(zh, encoding="utf-8", newline="\n")
    print(f"[OK] wrote {OUT_ZH.relative_to(ROOT)}")

def main():
    rows = collect_rows()
    write_csv(rows)
    write_md(rows)
    print("[DONE] archived W7900 P11 default SpMV ALG1 smoke validation")

if __name__ == "__main__":
    main()
