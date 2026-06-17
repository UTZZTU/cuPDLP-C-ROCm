#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

REPRO_EN = dedent("""
    ## 10. Reproduce or inspect P14-A1 quick6 repeated validation

    P14-A1 is the final repeated validation added for the current W7900 project
    closure. It repeats the earlier 890M-style quick6 protocol on W7900 /
    `gfx1100` and compares `pre_tuning` (`ae3b683`) with current
    `rocm-w7900-gfx1100` HEAD.

    Committed artifacts:

    ```text
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md
    ```

    Check the committed result without W7900 access:

    ```bash
    cd cuPDLP-C-ROCm

    python3 - <<'PY'
    import csv
    from pathlib import Path

    p = Path("validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv")
    rows = list(csv.DictReader(p.open()))
    speedups = [float(r["median_speedup_pre_over_current"]) for r in rows]
    print("rows:", len(rows))
    print("wins current faster:", sum(x > 1.0 for x in speedups), "/", len(speedups))
    print("min speedup:", min(speedups))
    print("max speedup:", max(speedups))
    print("cases:", ", ".join(r["case"] for r in rows))
    PY
    ```

    Expected interpretation:

    ```text
    rows: 6
    wins current faster: 6 / 6
    all speedups are greater than 1
    ```

    The summary reports geometric-mean speedup `1.18889` and median speedup
    `1.19502`, with preserved iteration counts across compared versions.

    To rerun P14-A1 on a W7900 machine after the environment and quick6 MPS files
    are available:

    ```bash
    cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm
    source /app/cupdlp_w7900/activate_w7900.sh

    ./scripts/run_w7900_p14a1_quick6_current_vs_pretuning_repeats.sh \\
      2>&1 | tee /app/cupdlp_w7900/logs/run_w7900_p14a1_quick6_current_vs_pretuning_$(date +%Y%m%d_%H%M%S).log

    python3 scripts/analysis/archive_w7900_p14a1_quick6_current_vs_pretuning_20260618.py
    ```

    Raw run directories and local result pointers under `validation/results/` are
    not committed. Only compact CSV/Markdown summaries are committed.
""").strip()

REPRO_ZH = dedent("""
    ## 10. 复现或检查 P14-A1 quick6 repeated validation

    P14-A1 是当前 W7900 项目收口阶段补充的最终 repeated validation。它在
    W7900 / `gfx1100` 上复用此前 890M-style quick6 protocol，对比
    `pre_tuning`（`ae3b683`）与当前 `rocm-w7900-gfx1100` HEAD。

    已提交 artifacts：

    ```text
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_raw.csv
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_aggregated.csv
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md
    validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.zh-CN.md
    ```

    没有 W7900 机器时，可以直接检查已提交结果：

    ```bash
    cd cuPDLP-C-ROCm

    python3 - <<'PY'
    import csv
    from pathlib import Path

    p = Path("validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv")
    rows = list(csv.DictReader(p.open()))
    speedups = [float(r["median_speedup_pre_over_current"]) for r in rows]
    print("rows:", len(rows))
    print("wins current faster:", sum(x > 1.0 for x in speedups), "/", len(speedups))
    print("min speedup:", min(speedups))
    print("max speedup:", max(speedups))
    print("cases:", ", ".join(r["case"] for r in rows))
    PY
    ```

    期望解释：

    ```text
    rows: 6
    wins current faster: 6 / 6
    all speedups are greater than 1
    ```

    summary 记录的几何平均 speedup 为 `1.18889`，中位数 speedup 为
    `1.19502`，且 pre/current 迭代数保持一致。

    若要在 W7900 机器上重跑 P14-A1，先恢复环境并准备 quick6 MPS 文件，然后运行：

    ```bash
    cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm
    source /app/cupdlp_w7900/activate_w7900.sh

    ./scripts/run_w7900_p14a1_quick6_current_vs_pretuning_repeats.sh \\
      2>&1 | tee /app/cupdlp_w7900/logs/run_w7900_p14a1_quick6_current_vs_pretuning_$(date +%Y%m%d_%H%M%S).log

    python3 scripts/analysis/archive_w7900_p14a1_quick6_current_vs_pretuning_20260618.py
    ```

    raw run directories 和 `validation/results/` 下的本地 pointer 不提交到 Git。
    Git 中只提交 compact CSV/Markdown summaries。
""").strip()

COMP_EN = dedent("""
    ## Final reproducibility update after P14-A1 / 2026-06-18

    Competition-oriented reproducibility now includes P14-A1 quick6 repeated
    validation in addition to environment recovery, data checks, smoke
    validation, non-hard23 summary inspection, and starter profiling.

    The key no-W7900 check is:

    ```bash
    python3 - <<'PY'
    import csv
    from pathlib import Path
    rows = list(csv.DictReader(Path("validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv").open()))
    speedups = [float(r["median_speedup_pre_over_current"]) for r in rows]
    print(len(rows), sum(x > 1 for x in speedups), min(speedups), max(speedups))
    PY
    ```

    Expected interpretation: `6` rows, `6` current wins, all speedups greater
    than `1`. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the full command
    path.
""").strip()

COMP_ZH = dedent("""
    ## P14-A1 后的最终复现说明 / 2026-06-18

    面向竞赛的可复现性现在除了环境恢复、数据校验、smoke validation、
    non-hard23 summary inspection 和 starter profiling 外，还包括 P14-A1
    quick6 repeated validation。

    没有 W7900 机器时，关键检查命令为：

    ```bash
    python3 - <<'PY'
    import csv
    from pathlib import Path
    rows = list(csv.DictReader(Path("validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv").open()))
    speedups = [float(r["median_speedup_pre_over_current"]) for r in rows]
    print(len(rows), sum(x > 1 for x in speedups), min(speedups), max(speedups))
    PY
    ```

    期望解释：`6` 行、`6` 个 current wins、所有 speedup 均大于 `1`。
    完整命令路径见 [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)。
""").strip()

def append_once(rel, section):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    heading = section.splitlines()[0].strip()
    if heading in s:
        print("[SKIP]", rel, heading)
        return
    p.write_text(s.rstrip() + "\n\n" + section + "\n", encoding="utf-8", newline="\n")
    print("[OK]", rel, heading)

def replace_once(rel, old, new):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    if old not in s:
        print("[MISS]", rel, old[:80])
        return
    p.write_text(s.replace(old, new, 1).rstrip() + "\n", encoding="utf-8", newline="\n")
    print("[OK]", rel, "replace")

def main():
    append_once("docs/REPRODUCIBILITY.md", REPRO_EN)
    append_once("docs/REPRODUCIBILITY.zh-CN.md", REPRO_ZH)
    append_once("docs/COMPETITION_README.md", COMP_EN)
    append_once("docs/COMPETITION_README.zh-CN.md", COMP_ZH)

    replace_once(
        "docs/COMPETITION_README.md",
        "It covers: - checking committed W7900 non-hard23 summaries without W7900 access; - recovering a fresh W7900 machine; - large-MPS data placement and SHA256 verification; - smoke validation; - starter `rocprofv3` profiling workflow; - file commit policy.",
        "It covers: checking committed W7900 summaries without W7900 access, including non-hard23 and P14-A1 quick6 repeated validation; recovering a fresh W7900 machine; large-MPS data placement and SHA256 verification; smoke validation; starter `rocprofv3` profiling workflow; and file commit policy."
    )

    replace_once(
        "docs/COMPETITION_README.zh-CN.md",
        "它覆盖： - 没有 W7900 机器时检查已提交 W7900 non-hard23 summaries； - fresh W7900 机器恢复； - large-MPS 数据放置与 SHA256 校验； - smoke validation； - starter `rocprofv3` profiling workflow； - 文件提交策略。",
        "它覆盖：没有 W7900 机器时检查已提交 W7900 summaries，包括 non-hard23 和 P14-A1 quick6 repeated validation；fresh W7900 机器恢复；large-MPS 数据放置与 SHA256 校验；smoke validation；starter `rocprofv3` profiling workflow；以及文件提交策略。"
    )

if __name__ == "__main__":
    main()
