from pathlib import Path

def replace_tail(path, old_heading, new_tail, already_heading):
    p = Path(path)
    s = p.read_text()

    if already_heading in s:
        print(f"{path}: already updated")
        return

    idx = s.find(old_heading)
    if idx < 0:
        raise SystemExit(f"{path}: heading not found: {old_heading}")

    s = s[:idx] + new_tail
    p.write_text(s)
    print(f"{path}: updated")

new_en = """## Next actions

1. Run W7900 `rocprof` starter3 on `set-cover-model.mps`, `square41.mps`, and `s100.mps`.
2. Run hard3 probe2 for `dlr1.mps` and `fhnw-binschedule1.mps`; keep `Dual2_5000.mps` as already-known hard behavior unless new evidence suggests otherwise.
3. Run the true before/current core6 comparison: `ae3b683 / pre_tuning` versus current `rocm-w7900-gfx1100`.
4. Generate curated profiling result summaries and commit only compact CSV/Markdown outputs, not raw profiler traces.
5. Decide the first W7900-specific tuning target only after the profiling data identifies a bottleneck.
"""

new_zh = """## 后续动作

1. 在 `set-cover-model.mps`、`square41.mps`、`s100.mps` 上运行 W7900 `rocprof` starter3。
2. 对 `dlr1.mps` 和 `fhnw-binschedule1.mps` 运行 hard3 probe2；`Dual2_5000.mps` 先作为已有强 hard 行为记录保留，除非后续出现新证据。
3. 运行 true before/current core6 对比：`ae3b683 / pre_tuning` 对比当前 `rocm-w7900-gfx1100`。
4. 生成整理后的 profiling 结果摘要，只提交 compact CSV/Markdown，不提交 raw profiler traces。
5. 只有在 profiling 数据明确瓶颈后，再决定第一轮 W7900-specific tuning 目标。
"""

replace_tail(
    "docs/W7900_CURRENT_STATUS.md",
    "## Next documentation tasks",
    new_en,
    "## Next actions",
)

replace_tail(
    "docs/W7900_CURRENT_STATUS.zh-CN.md",
    "## 下一步文档任务",
    new_zh,
    "## 后续动作",
)

print("done")
