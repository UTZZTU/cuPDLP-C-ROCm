#!/usr/bin/env python3
from pathlib import Path

BLOCK_BEGIN = "<!-- REPRODUCIBILITY_20260614_BEGIN -->"
BLOCK_END = "<!-- REPRODUCIBILITY_20260614_END -->"

DOC_EN = Path("docs/REPRODUCIBILITY.md")
DOC_ZH = Path("docs/REPRODUCIBILITY.zh-CN.md")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")
    print("[ok] wrote", path)


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


def doc_en():
    return r"""# Reproducibility guide

> 中文: [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)

This document explains how to reproduce the repository results and how to recover the working environment on temporary AMD GPU machines.

## 1. Scope

The repository has three reproducibility layers:

| Layer | Goal | Hardware needed |
|---|---|---|
| Documentation/data check | Verify committed CSV/Markdown/SVG summaries | Any machine with Git and Python |
| 890M/gfx1150 validation | Reproduce local ROCm build and small validation on the 890M development machine | Radeon 890M / `gfx1150` |
| W7900/gfx1100 validation/profiling | Reproduce W7900 smoke, large-MPS summaries, and profiling workflow | Radeon PRO W7900 / `gfx1100` |

Raw large-MPS files are not committed to Git. The repository commits scripts, case lists, manifests, curated CSV summaries, Markdown summaries, and SVG charts.

## 2. Clone the W7900 branch

Recommended full clone:

```bash
git clone --recurse-submodules git@github.com:UTZZTU/cuPDLP-C-ROCm.git
cd cuPDLP-C-ROCm
git fetch --all --tags --prune
git switch rocm-w7900-gfx1100
git pull --ff-only origin rocm-w7900-gfx1100
git submodule update --init --recursive
```

If you already have the `rocm-gfx1150` worktree on the 890M machine, use a linked worktree instead:

```bash
cd ~/rocm_dir/pdlp/cuPDLP-C-ROCm
git fetch origin --prune

cd ~/rocm_dir/pdlp
git -C cuPDLP-C-ROCm worktree add \
  cuPDLP-C-ROCm-w7900-work \
  origin/rocm-w7900-gfx1100
```

## 3. Verify committed W7900 summaries without a W7900 machine

```bash
cd cuPDLP-C-ROCm

python3 - <<'PY'
import csv
from pathlib import Path

p = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
rows = list(csv.DictReader(p.open()))
print("rows:", len(rows))
print("termination:", sorted(set(r["terminationCode"] for r in rows)))
print("runtime:", sorted(set(r["runtime_status"] for r in rows)))
print("source groups:", sorted(set(r["source_group"] for r in rows)))
print("total wall:", sum(float(r["wall_seconds"]) for r in rows))
print("total solve:", sum(float(r["dSolvingTime"]) for r in rows))
PY
```

Expected output:

```text
rows: 23
termination: ['OPTIMAL']
runtime: ['DONE']
source groups: ['initial17_safe', 'near_optimal2_1800s', 'watchlist6_900s']
total wall: 2960.171115
total solve: 2742.940418
```

## 4. Fresh W7900 machine recovery

The W7900 cloud environment can be volatile. On a fresh machine:

```bash
mkdir -p /app/cupdlp_w7900/src
cd /app/cupdlp_w7900/src

GIT_TERMINAL_PROMPT=0 git clone \
  --depth 1 \
  --single-branch \
  --branch rocm-w7900-gfx1100 \
  --filter=blob:none \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git

cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

INSTALL_APT_PACKAGES=0 RUN_BUILD=0 RUN_SMOKE=0 \
bash scripts/bootstrap_w7900_workspace.sh
```

After recovery, verify the branch and key files:

```bash
git log --oneline --decorate -8
git status

ls -lh \
  docs/COMPETITION_README.md \
  docs/W7900_CURRENT_STATUS.md \
  docs/W7900_ROCM_PROFILING_PLAN.md \
  validation/w7900_large_mps_nonhard23_20260613.csv
```

## 5. Large-MPS data policy

Raw MPS files stay outside Git.

Expected W7900 data root:

```text
/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark
```

Expected subdirectories/files:

```text
mps/
h100_large_mps_inventory.csv
h100_large_mps_manifest.sha256
```

SHA256 check should be run from the `mps` directory because the manifest stores file names without the `mps/` prefix:

```bash
cd /app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark/mps

sha256sum -c ../h100_large_mps_manifest.sha256 \
  2>&1 | tee /app/cupdlp_w7900/logs/large_mps_sha256_check.log
```

Expected successful count:

```bash
grep -c ": OK$" /app/cupdlp_w7900/logs/large_mps_sha256_check.log
# expected: 26
```

## 6. Reproduce smoke validation

On W7900:

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

RUN_BUILD=1 RUN_SMOKE=1 \
bash scripts/bootstrap_w7900_workspace.sh
```

Expected interpretation:

```text
CPU and ROCm/W7900 smoke validation reached matching termination, primal, and dual statuses.
```

## 7. Reproduce current committed non-hard23 summary

The current committed non-hard23 CSV is a post-890M-tuning W7900 engineering baseline, not an unoptimized first-port baseline.

Check it with:

```bash
python3 scripts/parse_w7900_large_mps_results.py \
  /app/cupdlp_w7900/results/<your_result_dir>
```

Curated committed result:

```text
validation/w7900_large_mps_nonhard23_20260613.csv
validation/w7900_large_mps_nonhard23_20260613_runtime.csv
validation/w7900_large_mps_nonhard23_20260613.md
validation/w7900_large_mps_nonhard23_20260613.zh-CN.md
```

## 8. Reproduce starter profiling workflow

Starter case list:

```text
validation/cases_w7900_rocprof_starter3.txt
```

Cases:

```text
set-cover-model.mps
square41.mps
s100.mps
```

Run on W7900 after data and build are ready:

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

CASE_LIST=validation/cases_w7900_rocprof_starter3.txt \
RUN_TAG=w7900_rocprof_starter3 \
TIME_LIMIT=900 \
EXTERNAL_TIMEOUT=960 \
bash scripts/run_w7900_rocprof_smoke_matrix.sh
```

Expected output root:

```text
/app/cupdlp_w7900/results/w7900_rocprof/
```

The script detects `rocprofv3` first, then legacy `rocprof`, and falls back to baseline-only execution if no profiler exists.

## 9. Reproduce future before/current comparison

The true pre-tuning anchor is:

```text
ae3b683 / pre_tuning
```

The current W7900 non-hard23 result is:

```text
current post-890M-tuning engineering baseline
```

Core6 case list:

```text
validation/cases_w7900_large_mps_before_after_core6.txt
```

Use this before attempting a full non-hard23 before/after rerun.

## 10. Files that should not be committed

Do not commit:

- raw `.mps` files;
- raw large profiler traces;
- temporary W7900 result directories;
- machine-local build directories;
- credentials, cookies, or SSH keys.

Commit only:

- source code and scripts;
- case lists;
- manifests;
- curated CSV summaries;
- Markdown summaries;
- small SVG charts;
- compact profiler summaries.

## 11. Docker / container status

A dedicated Docker/Containerfile is not yet the primary reproduction path because the available W7900 environment uses a pre-installed ROCm/Python SDK layout. The current reproducible path is the documented bootstrap workflow.

Future work should add:

```text
docker/Dockerfile.w7900
docker/README_DOCKER_W7900.md
```

This should describe the build environment while keeping raw MPS data outside the image.

## 12. Quick reviewer checklist

```bash
git status
git log --oneline --decorate -8

python3 -m py_compile \
  scripts/document_competition_readme_20260614.py \
  scripts/document_reproducibility_20260614.py \
  scripts/document_w7900_optimization_baselines_20260614.py

python3 - <<'PY'
import csv
from pathlib import Path
p = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
rows = list(csv.DictReader(p.open()))
assert len(rows) == 23
assert set(r["terminationCode"] for r in rows) == {"OPTIMAL"}
print("W7900 non-hard23 summary check: OK")
PY
```
"""


def doc_zh():
    return r"""# 可复现性指南

> English: [REPRODUCIBILITY.md](REPRODUCIBILITY.md)

本文说明如何复现仓库结果，以及如何在临时 AMD GPU 机器上恢复工作环境。

## 1. 范围

仓库有三层可复现性：

| 层次 | 目标 | 需要的硬件 |
|---|---|---|
| 文档/数据检查 | 验证已提交 CSV/Markdown/SVG summaries | 任意带 Git 和 Python 的机器 |
| 890M/gfx1150 验证 | 在 890M 开发机上复现 ROCm build 和小型验证 | Radeon 890M / `gfx1150` |
| W7900/gfx1100 验证/profiling | 复现 W7900 smoke、large-MPS summaries 和 profiling workflow | Radeon PRO W7900 / `gfx1100` |

raw large-MPS 文件不进入 Git。仓库只提交 scripts、case lists、manifests、curated CSV summaries、Markdown summaries 和 SVG charts。

## 2. 拉取 W7900 分支

推荐完整 clone：

```bash
git clone --recurse-submodules git@github.com:UTZZTU/cuPDLP-C-ROCm.git
cd cuPDLP-C-ROCm
git fetch --all --tags --prune
git switch rocm-w7900-gfx1100
git pull --ff-only origin rocm-w7900-gfx1100
git submodule update --init --recursive
```

如果 890M 机器上已经有 `rocm-gfx1150` worktree，建议使用 linked worktree：

```bash
cd ~/rocm_dir/pdlp/cuPDLP-C-ROCm
git fetch origin --prune

cd ~/rocm_dir/pdlp
git -C cuPDLP-C-ROCm worktree add \
  cuPDLP-C-ROCm-w7900-work \
  origin/rocm-w7900-gfx1100
```

## 3. 没有 W7900 机器时验证已提交 summary

```bash
cd cuPDLP-C-ROCm

python3 - <<'PY'
import csv
from pathlib import Path

p = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
rows = list(csv.DictReader(p.open()))
print("rows:", len(rows))
print("termination:", sorted(set(r["terminationCode"] for r in rows)))
print("runtime:", sorted(set(r["runtime_status"] for r in rows)))
print("source groups:", sorted(set(r["source_group"] for r in rows)))
print("total wall:", sum(float(r["wall_seconds"]) for r in rows))
print("total solve:", sum(float(r["dSolvingTime"]) for r in rows))
PY
```

期望输出：

```text
rows: 23
termination: ['OPTIMAL']
runtime: ['DONE']
source groups: ['initial17_safe', 'near_optimal2_1800s', 'watchlist6_900s']
total wall: 2960.171115
total solve: 2742.940418
```

## 4. Fresh W7900 机器恢复

W7900 云环境可能会重置。fresh machine 上执行：

```bash
mkdir -p /app/cupdlp_w7900/src
cd /app/cupdlp_w7900/src

GIT_TERMINAL_PROMPT=0 git clone \
  --depth 1 \
  --single-branch \
  --branch rocm-w7900-gfx1100 \
  --filter=blob:none \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git

cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

INSTALL_APT_PACKAGES=0 RUN_BUILD=0 RUN_SMOKE=0 \
bash scripts/bootstrap_w7900_workspace.sh
```

恢复后检查：

```bash
git log --oneline --decorate -8
git status

ls -lh \
  docs/COMPETITION_README.md \
  docs/W7900_CURRENT_STATUS.md \
  docs/W7900_ROCM_PROFILING_PLAN.md \
  validation/w7900_large_mps_nonhard23_20260613.csv
```

## 5. Large-MPS 数据策略

raw MPS 文件保存在 Git 外部。

W7900 预期数据根目录：

```text
/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark
```

预期结构：

```text
mps/
h100_large_mps_inventory.csv
h100_large_mps_manifest.sha256
```

由于 manifest 只记录文件名、不带 `mps/` 前缀，sha256 校验应从 `mps` 目录执行：

```bash
cd /app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark/mps

sha256sum -c ../h100_large_mps_manifest.sha256 \
  2>&1 | tee /app/cupdlp_w7900/logs/large_mps_sha256_check.log
```

期望成功数量：

```bash
grep -c ": OK$" /app/cupdlp_w7900/logs/large_mps_sha256_check.log
# expected: 26
```

## 6. 复现 smoke validation

W7900 上执行：

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

RUN_BUILD=1 RUN_SMOKE=1 \
bash scripts/bootstrap_w7900_workspace.sh
```

期望解释：

```text
CPU and ROCm/W7900 smoke validation reached matching termination, primal, and dual statuses.
```

## 7. 复现当前 non-hard23 summary

当前提交的 non-hard23 CSV 是 post-890M-tuning W7900 engineering baseline，不是未优化 first-port baseline。

解析结果目录：

```bash
python3 scripts/parse_w7900_large_mps_results.py \
  /app/cupdlp_w7900/results/<your_result_dir>
```

已提交 curated result：

```text
validation/w7900_large_mps_nonhard23_20260613.csv
validation/w7900_large_mps_nonhard23_20260613_runtime.csv
validation/w7900_large_mps_nonhard23_20260613.md
validation/w7900_large_mps_nonhard23_20260613.zh-CN.md
```

## 8. 复现 starter profiling workflow

Starter case list：

```text
validation/cases_w7900_rocprof_starter3.txt
```

Cases：

```text
set-cover-model.mps
square41.mps
s100.mps
```

数据和 build 准备好后，在 W7900 上运行：

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

CASE_LIST=validation/cases_w7900_rocprof_starter3.txt \
RUN_TAG=w7900_rocprof_starter3 \
TIME_LIMIT=900 \
EXTERNAL_TIMEOUT=960 \
bash scripts/run_w7900_rocprof_smoke_matrix.sh
```

预期输出根目录：

```text
/app/cupdlp_w7900/results/w7900_rocprof/
```

脚本会优先检测 `rocprofv3`，其次 legacy `rocprof`，如果没有 profiler 则退化为 baseline-only execution。

## 9. 复现 future before/current comparison

真正 pre-tuning anchor 是：

```text
ae3b683 / pre_tuning
```

当前 W7900 non-hard23 结果是：

```text
current post-890M-tuning engineering baseline
```

Core6 case list：

```text
validation/cases_w7900_large_mps_before_after_core6.txt
```

在尝试完整 non-hard23 before/after 之前，先使用该 core6 子集。

## 10. 不应提交的文件

不要提交：

- raw `.mps` 文件；
- raw large profiler traces；
- 临时 W7900 result directories；
- 机器本地 build directories；
- credentials、cookies、SSH keys。

只提交：

- source code 和 scripts；
- case lists；
- manifests；
- curated CSV summaries；
- Markdown summaries；
- 小型 SVG charts；
- compact profiler summaries。

## 11. Docker / container 状态

目前 dedicated Docker/Containerfile 还不是主复现路径，因为 W7900 环境使用预安装 ROCm/Python SDK 布局。当前可复现路径是 bootstrap workflow。

后续应补：

```text
docker/Dockerfile.w7900
docker/README_DOCKER_W7900.md
```

Docker/Containerfile 应描述 build environment，但 raw MPS 数据不应进入镜像。

## 12. 评委快速检查

```bash
git status
git log --oneline --decorate -8

python3 -m py_compile \
  scripts/document_competition_readme_20260614.py \
  scripts/document_reproducibility_20260614.py \
  scripts/document_w7900_optimization_baselines_20260614.py

python3 - <<'PY'
import csv
from pathlib import Path
p = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
rows = list(csv.DictReader(p.open()))
assert len(rows) == 23
assert set(r["terminationCode"] for r in rows) == {"OPTIMAL"}
print("W7900 non-hard23 summary check: OK")
PY
```
"""


def update_indexes():
    docs_block = f"""{BLOCK_BEGIN}
| Reproducibility / 可复现性 | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md) | How to reproduce committed summaries, recover W7900 machines, check data, and run starter profiling |
{BLOCK_END}"""
    insert_or_replace(
        "docs/README.md",
        docs_block,
        ["| Competition README / 竞赛入口", "| W7900 optimization baselines / W7900 优化基线"],
    )

    comp_en = f"""{BLOCK_BEGIN}
## Reproducibility

For reviewer-oriented reproduction steps, see [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

It covers:

- checking committed W7900 non-hard23 summaries without W7900 access;
- recovering a fresh W7900 machine;
- large-MPS data placement and SHA256 verification;
- smoke validation;
- starter `rocprofv3` profiling workflow;
- file commit policy.
{BLOCK_END}"""
    insert_or_replace(
        "docs/COMPETITION_README.md",
        comp_en,
        ["## Submission-material mapping", "## 10. Submission-material mapping"],
    )

    comp_zh = f"""{BLOCK_BEGIN}
## 可复现性

评委导向的复现步骤见 [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)。

它覆盖：

- 没有 W7900 机器时检查已提交 W7900 non-hard23 summaries；
- fresh W7900 机器恢复；
- large-MPS 数据放置与 SHA256 校验；
- smoke validation；
- starter `rocprofv3` profiling workflow；
- 文件提交策略。
{BLOCK_END}"""
    insert_or_replace(
        "docs/COMPETITION_README.zh-CN.md",
        comp_zh,
        ["## 提交材料映射", "## 10. 提交材料映射"],
    )


def main():
    write(DOC_EN, doc_en())
    write(DOC_ZH, doc_zh())
    update_indexes()
    print("[done] reproducibility guide generated")


if __name__ == "__main__":
    main()
