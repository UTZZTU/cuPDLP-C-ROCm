#!/usr/bin/env python3
from pathlib import Path
import re

STAMP = "20260614"
BLOCK_BEGIN = "<!-- W7900_DOC_SWEEP_20260614_BEGIN -->"
BLOCK_END = "<!-- W7900_DOC_SWEEP_20260614_END -->"

def read(path):
    p = Path(path)
    return p.read_text() if p.exists() else ""

def write(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + "\n")
    print("[ok] wrote", path)

def replace_once(text, old, new):
    if old in text:
        return text.replace(old, new, 1), True
    return text, False

def insert_or_replace(path, block, anchors):
    p = Path(path)
    if not p.exists():
        print("[skip] missing", path)
        return
    s = p.read_text()
    if BLOCK_BEGIN in s and BLOCK_END in s:
        before = s.split(BLOCK_BEGIN)[0].rstrip()
        after = s.split(BLOCK_END, 1)[1].lstrip()
        p.write_text(before + "\n\n" + block.rstrip() + "\n\n" + after)
        print("[ok] replaced block in", path)
        return
    for anchor in anchors:
        if anchor in s:
            p.write_text(s.replace(anchor, block.rstrip() + "\n\n" + anchor, 1))
            print("[ok] inserted block in", path)
            return
    p.write_text(s.rstrip() + "\n\n" + block.rstrip() + "\n")
    print("[ok] appended block in", path)

def update_root_readmes():
    en_path = Path("README.md")
    zh_path = Path("README.zh-CN.md")

    if en_path.exists():
        s = en_path.read_text()
        changes = 0
        pairs = [
            ("| Additional ROCm target under validation | AMD Radeon PRO W7900 / `gfx1100` |",
             "| Additional validated ROCm target | AMD Radeon PRO W7900 / `gfx1100` |"),
            ("The W7900 / `gfx1100` branch has passed first-port CPU-vs-ROCm `afiro` smoke validation and is now in extended validation and tuning.",
             "The W7900 / `gfx1100` branch has completed smoke validation, Netlib 27-case validation, and a 23-case non-hard large-MPS baseline; the remaining large-MPS hard3 cases are tracked separately before full tuning."),
            ("- W7900 / `gfx1100` first-port build scripts and smoke validation notes.",
             "- W7900 / `gfx1100` build, smoke validation, Netlib 27-case validation, and large-MPS non-hard23 baseline notes."),
            ("| W7900 / `gfx1100` first-port record | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |",
             "| W7900 / `gfx1100` current status | [docs/W7900_CURRENT_STATUS.md](docs/W7900_CURRENT_STATUS.md) | [docs/W7900_CURRENT_STATUS.zh-CN.md](docs/W7900_CURRENT_STATUS.zh-CN.md) |\n| W7900 / `gfx1100` first-port record | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |"),
        ]
        for old, new in pairs:
            s2, ok = replace_once(s, old, new)
            changes += int(ok)
            s = s2
        en_path.write_text(s)
        print(f"[ok] refreshed README.md replacements={changes}")

    if zh_path.exists():
        s = zh_path.read_text()
        changes = 0
        pairs = [
            ("| 正在验证的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |",
             "| 已完成 baseline 验证的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |"),
            ("W7900 / `gfx1100` 分支已通过 first-port CPU-vs-ROCm `afiro` smoke validation，正在进入 extended validation 和 tuning 阶段。",
             "W7900 / `gfx1100` 分支已完成 smoke validation、Netlib 27-case validation，以及 23-case non-hard large-MPS baseline；剩余 large-MPS hard3 case 将在完整调优前单独跟踪。"),
            ("- W7900 / `gfx1100` first-port 构建脚本和 smoke validation 记录。",
             "- W7900 / `gfx1100` build、smoke validation、Netlib 27-case validation，以及 large-MPS non-hard23 baseline 记录。"),
            ("| W7900 / `gfx1100` first-port 记录 | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |",
             "| W7900 / `gfx1100` current status | [docs/W7900_CURRENT_STATUS.md](docs/W7900_CURRENT_STATUS.md) | [docs/W7900_CURRENT_STATUS.zh-CN.md](docs/W7900_CURRENT_STATUS.zh-CN.md) |\n| W7900 / `gfx1100` first-port 记录 | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |"),
        ]
        for old, new in pairs:
            s2, ok = replace_once(s, old, new)
            changes += int(ok)
            s = s2
        zh_path.write_text(s)
        print(f"[ok] refreshed README.zh-CN.md replacements={changes}")

def create_hard3_notes():
    en = """# W7900 large-MPS hard3 notes

> 中文: [W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md](W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md)

This note records why the remaining three large-MPS cases are intentionally separated from the W7900 non-hard23 baseline.

## Hard3 cases

- `dlr1.mps`
- `Dual2_5000.mps`
- `fhnw-binschedule1.mps`

## Current policy

These cases should not be mixed into the primary W7900 large-MPS baseline until they have separate convergence-trajectory analysis.

The primary baseline is now:

- `initial17_safe`: 17/17 `OPTIMAL`
- `watchlist6`: 4/6 `OPTIMAL` under 900 seconds
- `near_optimal2`: the remaining 2/6 watchlist cases reached `OPTIMAL` under 1800 seconds
- Combined `non-hard23`: 23/23 `OPTIMAL`

## Why hard3 is separated

PDLP total runtime depends on both per-iteration cost and iteration count:

```text
total time ≈ per-iteration cost × number of iterations
```

For difficult LP/MPS instances, a GPU may be fast per iteration while still requiring many iterations or showing unstable gap trajectories. Hard3 should therefore be reported as numerical/convergence behavior, not as ordinary benchmark failures.

## Next use

Before ROCm/gfx1100 tuning, use hard3 only for short diagnostic runs and convergence-trajectory notes. After tuning stabilizes, rerun hard3 as a separate final stress-test group.
"""
    zh = """# W7900 large-MPS hard3 记录

> English: [W7900_LARGE_MPS_HARD3_NOTES.md](W7900_LARGE_MPS_HARD3_NOTES.md)

本文记录为什么剩余 3 个 large-MPS case 要从 W7900 non-hard23 baseline 中单独拆出。

## Hard3 cases

- `dlr1.mps`
- `Dual2_5000.mps`
- `fhnw-binschedule1.mps`

## 当前策略

在完成单独的收敛轨迹分析前，这些 case 不应混入 W7900 主要 large-MPS baseline。

当前主 baseline 是：

- `initial17_safe`：17/17 `OPTIMAL`
- `watchlist6`：4/6 在 900 秒内达到 `OPTIMAL`
- `near_optimal2`：watchlist 剩余 2 个 case 在 1800 秒内达到 `OPTIMAL`
- 合并后的 `non-hard23`：23/23 `OPTIMAL`

## 为什么单独拆出 hard3

PDLP 总耗时同时取决于单次迭代开销和迭代次数：

```text
total time ≈ per-iteration cost × number of iterations
```

对于困难 LP/MPS 实例，GPU 单次迭代可能很快，但仍可能需要大量迭代，或出现 gap 轨迹不稳定。因此 hard3 应作为数值/收敛行为单独报告，而不是简单归为普通 benchmark failure。

## 后续用途

在 ROCm/gfx1100 调优前，hard3 只用于短时间诊断和收敛轨迹记录。等调优稳定后，再把 hard3 作为单独的最终压力测试组。
"""
    write("docs/W7900_LARGE_MPS_HARD3_NOTES.md", en)
    write("docs/W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md", zh)

def update_first_port_docs():
    en_block = f"""{BLOCK_BEGIN}
## Updated status after large-MPS baseline

This first-port note is preserved as the historical record of the first W7900 / `gfx1100` smoke milestone.

The current branch status has moved beyond first-port smoke validation:

- smoke validation: completed
- Netlib 27-case W7900 validation: completed
- large-MPS `initial17_safe`: completed
- large-MPS `watchlist6` diagnostic and near-optimal follow-up: completed
- combined large-MPS `non-hard23`: 23/23 `OPTIMAL`
- remaining hard3: `dlr1.mps`, `Dual2_5000.mps`, `fhnw-binschedule1.mps`, tracked separately

Current status page: [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md)

Hard3 note: [W7900_LARGE_MPS_HARD3_NOTES.md](W7900_LARGE_MPS_HARD3_NOTES.md)
{BLOCK_END}"""
    zh_block = f"""{BLOCK_BEGIN}
## large-MPS baseline 之后的状态更新

本文保留为 W7900 / `gfx1100` first-port smoke milestone 的历史记录。

当前分支状态已经超过 first-port smoke validation：

- smoke validation：已完成
- Netlib 27-case W7900 validation：已完成
- large-MPS `initial17_safe`：已完成
- large-MPS `watchlist6` diagnostic 与 near-optimal follow-up：已完成
- 合并后的 large-MPS `non-hard23`：23/23 `OPTIMAL`
- 剩余 hard3：`dlr1.mps`、`Dual2_5000.mps`、`fhnw-binschedule1.mps`，单独跟踪

当前状态页：[W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)

Hard3 说明：[W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md](W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md)
{BLOCK_END}"""
    insert_or_replace("docs/W7900_FIRST_PORT.md", en_block, ["## 9. Known Limitations", "## 10. Next Steps"])
    insert_or_replace("docs/W7900_FIRST_PORT.zh-CN.md", zh_block, ["## 9. Known Limitations", "## 10. Next Steps", "## 9. 已知限制"])

def update_platform_notes():
    block = f"""{BLOCK_BEGIN}
## Updated reproducibility notes after W7900 baseline

The W7900 environment is volatile: `/app` may be reset between sessions. The repository therefore keeps bootstrap and SSH helper scripts in git, while raw `.mps` benchmark files stay outside git.

Recommended recovery flow on a fresh machine:

```bash
mkdir -p /app/cupdlp_w7900/src
cd /app/cupdlp_w7900/src

GIT_TERMINAL_PROMPT=0 git clone \\
  --depth 1 \\
  --single-branch \\
  --branch rocm-w7900-gfx1100 \\
  --filter=blob:none \\
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git

cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm
INSTALL_APT_PACKAGES=0 RUN_BUILD=0 RUN_SMOKE=0 bash scripts/bootstrap_w7900_workspace.sh
```

Large-MPS benchmark policy:

- raw MPS files are downloaded to `/app/cupdlp_w7900/datasets/large_mps_baidu`
- raw MPS files are not committed
- curated CSV, Markdown summaries, scripts, and SVG charts are committed
- current stable W7900 large-MPS baseline is `non-hard23`
- hard3 is tracked separately before full tuning
{BLOCK_END}"""
    insert_or_replace("docs/platforms/W7900_PLATFORM_NOTES.md", block, ["## Next steps", "## First-stage acceptance criteria"])

def update_docs_readme():
    block = f"""{BLOCK_BEGIN}
| W7900 hard3 notes / W7900 hard3 说明 | [W7900_LARGE_MPS_HARD3_NOTES.md](W7900_LARGE_MPS_HARD3_NOTES.md) | [W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md](W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md) | hard3 split for `dlr1`, `Dual2_5000`, and `fhnw-binschedule1` |
{BLOCK_END}"""
    insert_or_replace("docs/README.md", block, ["| W7900 current status / W7900 当前状态", "## Validation data directory / Validation 数据目录"])

def update_validation_readmes():
    en_block = f"""{BLOCK_BEGIN}
## W7900 hard3 follow-up

| File | Description |
|---|---|
| [../docs/W7900_LARGE_MPS_HARD3_NOTES.md](../docs/W7900_LARGE_MPS_HARD3_NOTES.md) | Hard3 policy and convergence-behavior notes for `dlr1`, `Dual2_5000`, and `fhnw-binschedule1` |
{BLOCK_END}"""
    zh_block = f"""{BLOCK_BEGIN}
## W7900 hard3 后续说明

| 文件 | 说明 |
|---|---|
| [../docs/W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md](../docs/W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md) | `dlr1`、`Dual2_5000`、`fhnw-binschedule1` 的 hard3 策略与收敛行为说明 |
{BLOCK_END}"""
    insert_or_replace("validation/README.md", en_block, ["## Related project docs"])
    insert_or_replace("validation/README.zh-CN.md", zh_block, ["## 相关项目文档"])

def main():
    update_root_readmes()
    create_hard3_notes()
    update_first_port_docs()
    update_platform_notes()
    update_docs_readme()
    update_validation_readmes()
    print("[done] W7900 documentation sweep completed")

if __name__ == "__main__":
    main()
