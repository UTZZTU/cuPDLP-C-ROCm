# 可复现性指南

> English: [REPRODUCIBILITY.md](REPRODUCIBILITY.md)

本文说明如何在没有 W7900 时检查已提交证据，以及如何在 Radeon PRO W7900 / `gfx1100` 主机上恢复环境、构建、验证和重跑关键实验。

## 1. 可复现性层级

| 层级 | 可以完成的工作 | 硬件要求 |
|---|---|---|
| 文档与数据检查 | 检查 CSV、Markdown、SVG、Git 提交和脚本 | 任意 Linux 主机 |
| CPU/CUDA 工程检查 | 构建 CPU 或 CUDA 路径，验证通用命令 | 对应编译环境；CUDA 需要 NVIDIA GPU/Toolkit |
| W7900 ROCm 验证 | build、smoke、large-MPS、profiling、tuning repeats | W7900 / `gfx1100` 与匹配 ROCm 环境 |

在非 W7900 主机上整理或检查文档是有效的，但不能写成“重新验证了 W7900 性能”。

## 2. 克隆固定分支

```bash
git clone --recurse-submodules \
  --branch rocm-w7900-gfx1100 \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git

cd cuPDLP-C-ROCm
git pull --ff-only origin rocm-w7900-gfx1100
git submodule update --init --recursive
```

记录基线：

```bash
git branch --show-current
git rev-parse HEAD
git status
```

## 3. 无 W7900 时检查已提交结果

### 3.1 non-hard23

```bash
python3 - <<'PY'
import csv
from pathlib import Path

p = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
rows = list(csv.DictReader(p.open()))
print("rows:", len(rows))
print("termination:", sorted({r["terminationCode"] for r in rows}))
print("runtime:", sorted({r["runtime_status"] for r in rows}))
print("groups:", sorted({r["source_group"] for r in rows}))
print("total wall:", sum(float(r["wall_seconds"]) for r in rows))
print("total solve:", sum(float(r["dSolvingTime"]) for r in rows))
PY
```

期望：

```text
rows: 23
termination: ['OPTIMAL']
runtime: ['DONE']
total wall: approximately 2960.171
total solve: approximately 2742.940
```

### 3.2 P14-A1 quick6

```bash
python3 - <<'PY'
import csv
from pathlib import Path

p = Path("validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv")
rows = list(csv.DictReader(p.open()))
speedups = [float(r["median_speedup_pre_over_current"]) for r in rows]
print("rows:", len(rows))
print("current wins:", sum(x > 1 for x in speedups), "/", len(speedups))
print("min:", min(speedups))
print("max:", max(speedups))
PY
```

期望为 6 行、current 6/6 胜出，summary 中 geomean 为 `1.18889`，median 为 `1.19502`。

## 4. Fresh W7900 环境恢复

仓库脚本默认使用项目既有的 W7900 目录布局。fresh machine 上：

```bash
mkdir -p /app/cupdlp_w7900/src
cd /app/cupdlp_w7900/src

git clone \
  --depth 1 \
  --single-branch \
  --branch rocm-w7900-gfx1100 \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git

cd cuPDLP-C-ROCm

INSTALL_APT_PACKAGES=0 RUN_BUILD=0 RUN_SMOKE=0 \
bash scripts/bootstrap_w7900_workspace.sh
```

恢复后检查：

```bash
git status
git log --oneline --decorate -8
command -v hipcc rocprofv3 rocprof rocm-smi amd-smi || true
rocminfo | grep -E "Name:|Marketing Name|gfx" || true
```

实际路径与默认布局不同时，先检查：

```text
scripts/env/w7900_python_rocm_env.sh
scripts/build_w7900_cpu.sh
scripts/build_w7900_rocm.sh
```

再通过环境变量或本地配置适配，不要把机器私有绝对路径写回通用文档。

## 5. Large-MPS 数据策略

原始 MPS 保存在 Git 外部。W7900 历史实验使用的数据根目录为：

```text
/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark
```

预期包含：

```text
mps/
h100_large_mps_inventory.csv
h100_large_mps_manifest.sha256
```

从 `mps` 目录执行 SHA256：

```bash
cd /app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark/mps

sha256sum -c ../h100_large_mps_manifest.sha256 \
  2>&1 | tee /app/cupdlp_w7900/logs/large_mps_sha256_check.log

grep -c ": OK$" /app/cupdlp_w7900/logs/large_mps_sha256_check.log
```

历史 manifest 预期 26 个文件。只有通过校验的输入才能进入 benchmark。

## 6. 构建与 smoke

直接使用维护脚本：

```bash
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

预期二进制：

```text
build-cpu/bin/plc
build-rocm-w7900/bin/plc
```

也可用 bootstrap 一次完成 build 与 smoke：

```bash
RUN_BUILD=1 RUN_SMOKE=1 \
bash scripts/bootstrap_w7900_workspace.sh
```

结果应显示 CPU 与 ROCm/W7900 的 termination、primal 和 dual 状态一致；若不一致，应检查 JSON 和日志，不能直接判 PASS。

## 7. non-hard23 重跑与解析

case list：

```text
validation/cases_w7900_large_mps_before_after_nonhard23.txt
```

运行入口和环境参数见：

```text
scripts/run_w7900_large_mps_baseline.sh
scripts/parse_w7900_large_mps_results.py
```

解析一个本地结果目录：

```bash
python3 scripts/parse_w7900_large_mps_results.py \
  /app/cupdlp_w7900/results/<result-directory>
```

已提交的权威 compact artifacts：

```text
validation/w7900_large_mps_nonhard23_20260613.csv
validation/w7900_large_mps_nonhard23_20260613_runtime.csv
validation/w7900_large_mps_nonhard23_20260613.md
validation/w7900_large_mps_nonhard23_20260613.zh-CN.md
```

当前结果是 post-890M-tuning W7900 engineering baseline，不是 first-port baseline。

## 8. P10 targeted profiling

P10 使用 5 个 targeted cases：

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

主要执行入口：

```bash
bash scripts/run_w7900_p10_current_targeted_rocprof.sh
```

更早的通用 starter3 workflow 仍可用于历史比较：

```bash
CASE_LIST=validation/cases_w7900_rocprof_starter3.txt \
RUN_TAG=w7900_rocprof_starter3 \
TIME_LIMIT=900 \
EXTERNAL_TIMEOUT=960 \
bash scripts/run_w7900_rocprof_smoke_matrix.sh
```

不要把 starter3 写成 P10 case list。脚本优先检测 `rocprofv3`，其次 legacy `rocprof`；没有 profiler 时只能得到 baseline execution，不能声称完成 profiling。

P10 compact 结果：

```text
validation/w7900_p10_current_targeted_rocprof_20260617_*.csv
validation/w7900_p10_current_targeted_rocprof_20260617_summary*.md
```

Raw traces 不提交。

## 9. P11 SpMV algorithm tuning

P11 sweep 入口：

```bash
bash scripts/run_w7900_p11_spmv_alg_sweep.sh
```

当前策略：

```text
default: HIPSPARSE_SPMV_CSR_ALG1
fallback: CUPDLP_HIP_SPMV_ALG=csr_alg2
```

测试回退路径时：

```bash
CUPDLP_HIP_SPMV_ALG=csr_alg2 \
./build-rocm-w7900/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_csr_alg2.json \
  -nIterLim 200
```

必须同时比较 termination、feasibility、gap、`nIter` 和运行时间。

## 10. P14-A1 repeated validation

先恢复 W7900 环境并准备 quick6 MPS，然后：

```bash
source /app/cupdlp_w7900/activate_w7900.sh

bash scripts/run_w7900_p14a1_quick6_current_vs_pretuning_repeats.sh \
  2>&1 | tee /app/cupdlp_w7900/logs/p14a1_$(date +%Y%m%d_%H%M%S).log

python3 scripts/analysis/archive_w7900_p14a1_quick6_current_vs_pretuning_20260618.py
```

提交 compact CSV/Markdown，不提交 raw run directories。

## 11. hard3 与 8 卡结果

hard3 的 probe2 证据已经提交，但困难 case 不进入 non-hard23 主结果：

- [hard3 说明](W7900_LARGE_MPS_HARD3_NOTES.zh-CN.md)
- [probe2 summary](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.zh-CN.md)

8 卡 fast8 summary 是 8 个独立 MPS 任务的并发吞吐：

- [8-card fast8 summary](../validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md)

它不复现单个 LP 的分布式多 GPU 求解。

## 12. 不应提交的文件

不要提交：

- raw `.mps` / `.mps.gz`；
- raw profiler trace directories；
- 临时 W7900 result directories；
- 本机构建目录；
- credentials、cookies、SSH keys；
- 与机器绑定的私有环境文件。

允许提交：

- source code 和 scripts；
- case lists 和 manifests；
- curated CSV；
- Markdown summaries；
- 小型 SVG；
- compact profiler summaries。

## 13. Docker 状态

当前 Docker 文件是环境声明骨架：

```text
docker/Dockerfile.w7900
docker/README_DOCKER_W7900.md
docker/README_DOCKER_W7900.zh-CN.md
```

它不是当前 W7900 性能数字的来源，也没有替代实际 ROCm 主机验证。

## 14. 分享前检查

运行仓库已有检查：

```bash
git status
git diff --check
python3 scripts/docs/scan_markdown_format_issues_20260616.py
```

仓库当前没有独立的 `scripts/docs/check_markdown_links.py`。检查本地相对链接可运行：

```bash
python3 - <<'PY'
import re
from pathlib import Path
from urllib.parse import unquote

root = Path(".").resolve()
bad = []
pat = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)")
for src in root.rglob("*.md"):
    if ".git" in src.parts:
        continue
    text = src.read_text(encoding="utf-8", errors="replace")
    for match in pat.finditer(text):
        raw = next(x for x in match.groups() if x).strip().split()[0].strip("<>")
        if raw.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = unquote(raw.split("#", 1)[0])
        if target and not (src.parent / target).resolve().exists():
            bad.append((src.relative_to(root), raw))
if bad:
    for src, target in bad:
        print(f"{src}: {target}")
    raise SystemExit(1)
print("[OK] repository-internal Markdown links")
PY
```

确认：

- 分支和提交已记录；
- 输入数据通过 SHA256；
- 所有比较使用相同 case list 与限制；
- non-hard23、hard3、8-card 含义没有混淆；
- 中英文当前态文档同步；
- raw 数据和凭据未进入 Git；
- 非 W7900 主机上的文档检查没有写成 fresh W7900 性能复现。
