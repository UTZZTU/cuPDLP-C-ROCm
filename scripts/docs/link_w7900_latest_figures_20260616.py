#!/usr/bin/env python3
from pathlib import Path

BEGIN = "<!-- W7900_LATEST_FIGURES_20260616_BEGIN -->"
END = "<!-- W7900_LATEST_FIGURES_20260616_END -->"

def update(path, block):
    p = Path(path)
    s = p.read_text()

    if BEGIN in s and END in s:
        before = s.split(BEGIN)[0].rstrip()
        after = s.split(END, 1)[1].lstrip()
        s = before + "\n\n" + block.strip() + "\n\n" + after
    else:
        s = s.rstrip() + "\n\n" + block.strip() + "\n"

    p.write_text(s)
    print("updated", path)

validation_en = f"""
{BEGIN}
## W7900 latest experiment figures / 2026-06-16

| Figure index | Description |
|---|---|
| [W7900 latest experiment figures](w7900_latest_experiment_figures_20260616.md) | SVG figures for 8-card fast8 throughput, before/current fast-core6, hard3 probe2, and rocprof kernel share |
{END}
"""

validation_zh = f"""
{BEGIN}
## W7900 最新实验图表 / 2026-06-16

| 图表索引 | 说明 |
|---|---|
| [W7900 最新实验图表](w7900_latest_experiment_figures_20260616.zh-CN.md) | 包含 8-card fast8 吞吐、before/current fast-core6、hard3 probe2、rocprof kernel 占比等 SVG 图 |
{END}
"""

status_en = f"""
{BEGIN}
## Latest W7900 figures / 2026-06-16

The latest W7900 figure index is available here:

- [W7900 latest experiment figures](../validation/w7900_latest_experiment_figures_20260616.md)

The strongest visual result is the 8-card fast8 batch throughput figure: 8 independent MPS tasks completed in 146s concurrently on 8 W7900 GPUs versus 558s sequentially on one W7900 GPU.
{END}
"""

status_zh = f"""
{BEGIN}
## 最新 W7900 图表 / 2026-06-16

最新 W7900 图表索引如下：

- [W7900 最新实验图表](../validation/w7900_latest_experiment_figures_20260616.zh-CN.md)

最适合作为材料亮点的是 8-card fast8 批处理吞吐图：8 个独立 MPS 任务在 8 张 W7900 上并发完成时间为 146s，而单张 W7900 顺序运行需要 558s。
{END}
"""

update("validation/README.md", validation_en)
update("validation/README.zh-CN.md", validation_zh)
update("docs/W7900_CURRENT_STATUS.md", status_en)
update("docs/W7900_CURRENT_STATUS.zh-CN.md", status_zh)
