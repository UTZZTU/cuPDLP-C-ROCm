#!/usr/bin/env python3
from pathlib import Path

BEGIN = "<!-- W7900_LATEST_EXPERIMENTS_20260616_BEGIN -->"
END = "<!-- W7900_LATEST_EXPERIMENTS_20260616_END -->"

def update_block(path, block):
    p = Path(path)
    text = p.read_text()
    if BEGIN in text and END in text:
        before = text.split(BEGIN)[0].rstrip()
        after = text.split(END, 1)[1].lstrip()
        new = before + "\n\n" + block.strip() + "\n\n" + after
    else:
        new = text.rstrip() + "\n\n" + block.strip() + "\n"
    p.write_text(new)
    print(f"updated {path}")

validation_en = f"""
{BEGIN}
## W7900 latest experiment summaries / 2026-06-16

These compact summaries record the latest W7900 / `gfx1100` experiment milestones. Raw MPS files, raw profiler traces, and large run directories stay outside Git.

| Milestone | Summary | Compact CSV outputs |
|---|---|---|
| P2: rocprof starter3 | [W7900 rocprof starter3 summary](w7900_rocprof_starter3_summary_20260616.md) | [runtime](w7900_rocprof_starter3_runtime_20260616.csv), [solver](w7900_rocprof_starter3_solver_20260616.csv), [HIP API top](w7900_rocprof_starter3_hip_api_top_20260616.csv), [kernel top](w7900_rocprof_starter3_kernel_top_20260616.csv) |
| P3: hard3 probe2 600s | [W7900 hard3 probe2 600s summary](w7900_large_mps_hard3_probe2_600s_summary_20260616.md) | [runtime](w7900_large_mps_hard3_probe2_600s_runtime_20260616.csv), [solver](w7900_large_mps_hard3_probe2_600s_solver_20260616.csv), [case list](cases_w7900_large_mps_hard3_probe2.txt) |
| P4: before/current fast-core6 | [W7900 before/current fast-core6 summary](w7900_before_current_core6_fast_summary_20260616.md) | [comparison](w7900_before_current_core6_fast_comparison_20260616.csv), [current solver](w7900_before_current_core6_fast_current_solver_20260616.csv), [pre-tuning solver](w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv), [case list](cases_w7900_large_mps_before_after_core6_fast.txt) |
| P5: 8-card fast8 batch throughput | [W7900 8-card fast8 batch summary](w7900_8card_batch_fast8_summary_20260616.md) | [comparison](w7900_8card_batch_fast8_comparison_20260616.csv), [concurrent solver](w7900_8card_batch_fast8_concurrent_solver_20260616.csv), [single-GPU sequential solver](w7900_8card_batch_fast8_single_gpu_seq_solver_20260616.csv), [case list](cases_w7900_8card_batch_fast8.txt) |

Key result highlights:

- P2 records compact W7900 `rocprof` starter3 evidence; raw trace files are intentionally not committed.
- P3 confirms `dlr1` and `fhnw-binschedule1` remain hard under a 600-second diagnostic budget.
- P4 shows both `ae3b683 / pre_tuning` and current `rocm-w7900-gfx1100` reach 6/6 `OPTIMAL` on fast-core6, with mixed performance rather than a blanket speedup claim.
- P5 shows 8 independent MPS tasks complete in 146s on 8 W7900 GPUs versus 558s sequentially on one W7900 GPU, giving about 3.82x measured batch makespan speedup.
{END}
"""

validation_zh = f"""
{BEGIN}
## W7900 最新实验摘要 / 2026-06-16

这些 compact summary 记录最新的 W7900 / `gfx1100` 实验里程碑。raw MPS 文件、raw profiler traces 和大型运行目录均保存在 Git 外部。

| 里程碑 | 摘要 | Compact CSV 输出 |
|---|---|---|
| P2: rocprof starter3 | [W7900 rocprof starter3 摘要](w7900_rocprof_starter3_summary_20260616.zh-CN.md) | [runtime](w7900_rocprof_starter3_runtime_20260616.csv), [solver](w7900_rocprof_starter3_solver_20260616.csv), [HIP API top](w7900_rocprof_starter3_hip_api_top_20260616.csv), [kernel top](w7900_rocprof_starter3_kernel_top_20260616.csv) |
| P3: hard3 probe2 600s | [W7900 hard3 probe2 600s 摘要](w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) | [runtime](w7900_large_mps_hard3_probe2_600s_runtime_20260616.csv), [solver](w7900_large_mps_hard3_probe2_600s_solver_20260616.csv), [case list](cases_w7900_large_mps_hard3_probe2.txt) |
| P4: before/current fast-core6 | [W7900 before/current fast-core6 摘要](w7900_before_current_core6_fast_summary_20260616.zh-CN.md) | [comparison](w7900_before_current_core6_fast_comparison_20260616.csv), [current solver](w7900_before_current_core6_fast_current_solver_20260616.csv), [pre-tuning solver](w7900_before_current_core6_fast_pre_tuning_solver_20260616.csv), [case list](cases_w7900_large_mps_before_after_core6_fast.txt) |
| P5: 8-card fast8 batch throughput | [W7900 8-card fast8 batch 摘要](w7900_8card_batch_fast8_summary_20260616.zh-CN.md) | [comparison](w7900_8card_batch_fast8_comparison_20260616.csv), [concurrent solver](w7900_8card_batch_fast8_concurrent_solver_20260616.csv), [single-GPU sequential solver](w7900_8card_batch_fast8_single_gpu_seq_solver_20260616.csv), [case list](cases_w7900_8card_batch_fast8.txt) |

关键结果：

- P2 记录 W7900 `rocprof` starter3 的 compact profiling 证据；raw trace 文件不进入 Git。
- P3 确认 `dlr1` 和 `fhnw-binschedule1` 在 600 秒诊断预算下仍属于 hard case。
- P4 显示 `ae3b683 / pre_tuning` 与当前 `rocm-w7900-gfx1100` 在 fast-core6 上均达到 6/6 `OPTIMAL`，但性能结果是混合的，不能写成笼统加速结论。
- P5 显示 8 个独立 MPS 任务在 8 张 W7900 上并发完成时间为 146s，而单张 W7900 顺序运行需要 558s，实测 batch makespan speedup 约为 3.82x。
{END}
"""

docs_index = f"""
{BEGIN}
## Latest W7900 experiment summaries / 最新 W7900 实验摘要

| Topic / 主题 | English | 中文 | Notes / 说明 |
|---|---|---|---|
| W7900 rocprof starter3 | [summary](../validation/w7900_rocprof_starter3_summary_20260616.md) | [摘要](../validation/w7900_rocprof_starter3_summary_20260616.zh-CN.md) | Compact profiling evidence; raw traces stay outside Git |
| W7900 hard3 probe2 600s | [summary](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md) | [摘要](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) | 600s diagnostic for hard cases |
| W7900 before/current fast-core6 | [summary](../validation/w7900_before_current_core6_fast_summary_20260616.md) | [摘要](../validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md) | `ae3b683 / pre_tuning` versus current branch |
| W7900 8-card fast8 throughput | [summary](../validation/w7900_8card_batch_fast8_summary_20260616.md) | [摘要](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md) | 8 independent MPS tasks: 146s concurrent versus 558s single-GPU sequential |
{END}
"""

submission_en = f"""
{BEGIN}
## W7900 experiment completion / 2026-06-16

| Item | Status | Evidence |
|---|---|---|
| rocprof starter3 | Done | [W7900 rocprof starter3 summary](../validation/w7900_rocprof_starter3_summary_20260616.md) |
| hard3 probe2 | Done | [W7900 hard3 probe2 600s summary](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md) |
| true before/current fast-core6 | Done | [W7900 before/current fast-core6 summary](../validation/w7900_before_current_core6_fast_summary_20260616.md) |
| 8-card independent-MPS batch throughput | Done | [W7900 8-card fast8 batch summary](../validation/w7900_8card_batch_fast8_summary_20260616.md) |
{END}
"""

submission_zh = f"""
{BEGIN}
## W7900 实验完成情况 / 2026-06-16

| 项目 | 状态 | 证据 |
|---|---|---|
| rocprof starter3 | 已完成 | [W7900 rocprof starter3 摘要](../validation/w7900_rocprof_starter3_summary_20260616.zh-CN.md) |
| hard3 probe2 | 已完成 | [W7900 hard3 probe2 600s 摘要](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) |
| true before/current fast-core6 | 已完成 | [W7900 before/current fast-core6 摘要](../validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md) |
| 8-card independent-MPS batch throughput | 已完成 | [W7900 8-card fast8 batch 摘要](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md) |
{END}
"""

competition_en = f"""
{BEGIN}
## Latest W7900 evidence / 2026-06-16

The latest committed W7900 evidence is available from the validation index:

- [rocprof starter3](../validation/w7900_rocprof_starter3_summary_20260616.md): compact profiling summary for three starter cases.
- [hard3 probe2 600s](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md): diagnostic results for hard cases.
- [before/current fast-core6](../validation/w7900_before_current_core6_fast_summary_20260616.md): `ae3b683 / pre_tuning` versus current branch.
- [8-card fast8 batch throughput](../validation/w7900_8card_batch_fast8_summary_20260616.md): 8 independent MPS tasks, 146s concurrent versus 558s single-GPU sequential.
{END}
"""

competition_zh = f"""
{BEGIN}
## 最新 W7900 证据 / 2026-06-16

最新提交的 W7900 证据可从 validation 索引进入：

- [rocprof starter3](../validation/w7900_rocprof_starter3_summary_20260616.zh-CN.md)：三个 starter case 的 compact profiling 摘要。
- [hard3 probe2 600s](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md)：hard case 诊断结果。
- [before/current fast-core6](../validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md)：`ae3b683 / pre_tuning` 与当前分支对比。
- [8-card fast8 batch throughput](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md)：8 个独立 MPS 任务，8 卡并发 146s，对比单 GPU 顺序 558s。
{END}
"""

scorecard_en = f"""
{BEGIN}
## 2026-06-16 W7900 evidence update

The W7900 evidence set now includes:

| Requirement area | Latest evidence |
|---|---|
| Profiling and bottleneck evidence | [W7900 rocprof starter3 summary](../validation/w7900_rocprof_starter3_summary_20260616.md) |
| Hard-case handling | [W7900 hard3 probe2 600s summary](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md) |
| Before/current comparison | [W7900 before/current fast-core6 summary](../validation/w7900_before_current_core6_fast_summary_20260616.md) |
| Multi-GPU throughput | [W7900 8-card fast8 batch summary](../validation/w7900_8card_batch_fast8_summary_20260616.md) |
{END}
"""

scorecard_zh = f"""
{BEGIN}
## 2026-06-16 W7900 证据更新

W7900 证据集现在包括：

| 评分/证据方向 | 最新证据 |
|---|---|
| Profiling 与瓶颈证据 | [W7900 rocprof starter3 摘要](../validation/w7900_rocprof_starter3_summary_20260616.zh-CN.md) |
| Hard-case 处理 | [W7900 hard3 probe2 600s 摘要](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md) |
| Before/current 对比 | [W7900 before/current fast-core6 摘要](../validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md) |
| 多 GPU 批处理吞吐 | [W7900 8-card fast8 batch 摘要](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md) |
{END}
"""

status_en = f"""
{BEGIN}
## Latest W7900 experiment status / 2026-06-16

The W7900 / `gfx1100` experiment set has been updated with four committed compact summaries:

- [rocprof starter3](../validation/w7900_rocprof_starter3_summary_20260616.md)
- [hard3 probe2 600s](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md)
- [before/current fast-core6](../validation/w7900_before_current_core6_fast_summary_20260616.md)
- [8-card fast8 batch throughput](../validation/w7900_8card_batch_fast8_summary_20260616.md)

The 8-card fast8 experiment solved all 8 cases to `OPTIMAL` in both concurrent and single-GPU sequential modes, with 146s concurrent makespan versus 558s single-GPU sequential makespan.
{END}
"""

status_zh = f"""
{BEGIN}
## 最新 W7900 实验状态 / 2026-06-16

W7900 / `gfx1100` 实验集已更新四组 compact summary：

- [rocprof starter3](../validation/w7900_rocprof_starter3_summary_20260616.zh-CN.md)
- [hard3 probe2 600s](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md)
- [before/current fast-core6](../validation/w7900_before_current_core6_fast_summary_20260616.zh-CN.md)
- [8-card fast8 batch throughput](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md)

8-card fast8 实验在 8 卡并发和单 GPU 顺序两种模式下均达到 8/8 `OPTIMAL`，其中 8 卡并发 makespan 为 146s，单 GPU 顺序 makespan 为 558s。
{END}
"""

update_block("validation/README.md", validation_en)
update_block("validation/README.zh-CN.md", validation_zh)
update_block("docs/README.md", docs_index)
update_block("docs/SUBMISSION_CHECKLIST.md", submission_en)
update_block("docs/SUBMISSION_CHECKLIST.zh-CN.md", submission_zh)
update_block("docs/COMPETITION_README.md", competition_en)
update_block("docs/COMPETITION_README.zh-CN.md", competition_zh)
update_block("docs/COMPETITION_SCORECARD.md", scorecard_en)
update_block("docs/COMPETITION_SCORECARD.zh-CN.md", scorecard_zh)
update_block("docs/W7900_CURRENT_STATUS.md", status_en)
update_block("docs/W7900_CURRENT_STATUS.zh-CN.md", status_zh)
