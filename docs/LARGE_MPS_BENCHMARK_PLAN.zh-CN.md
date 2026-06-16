# Large MPS benchmark 计划

> English version: [`LARGE_MPS_BENCHMARK_PLAN.md`](LARGE_MPS_BENCHMARK_PLAN.md)

本文记录 `cuPDLP-C-ROCm` 的 large MPS benchmark workflow。

## 目标

Netlib benchmark matrix 对验证很有用，但很多 case 太小，GPU overhead 容易主导运行时间。Large MPS workflow 用于测试更大的 LP 实例，让 sparse matrix-vector product 和 vector operation 更充分地暴露 GPU 行为。

目标是：

1. 所有机器使用同一 large MPS 数据集。
2. 每个下载文件在运行 solver 前通过 SHA256 校验。
3. 比较 RTX 3090、RTX 4090D 和 H100 上的 CUDA baseline。
4. 记录 Radeon 890M ROCm pre-tuning baseline。
5. 后续用最好的已验证 tuned ROCm 版本复测 Radeon 890M。
6. 原始 MPS 文件不进入 Git，只提交 manifest 和整理后的 summary。

## 数据集来源和传输

源数据集位于 H100 服务器：

```text
~/cuPDLP-C/test_data/*.mps
```

上传到百度网盘：

```text
/cupdlp-large-mps-benchmark/
/cupdlp-large-mps-benchmark/mps/
```

`mps/` 同级目录应保存两个元数据文件：

```text
h100_large_mps_inventory.csv
h100_large_mps_manifest.sha256
```

Manifest 在源机器上生成：

```bash
cd ~/cuPDLP-C/test_data
sha256sum *.mps > ~/h100_large_mps_manifest.sha256
```

## 本地目标路径

每台目标机器使用相同本地结构：

```text
~/cuPDLP-C/test_data_large_mps/
├── h100_large_mps_inventory.csv
├── h100_large_mps_manifest.sha256
└── mps/
    ├── a2864.mps
    ├── ...
```

## 下载和校验策略

下载后校验数据集：

```bash
DATA_ROOT="$HOME/cuPDLP-C/test_data_large_mps"
cd "$DATA_ROOT/mps"
sha256sum -c "$DATA_ROOT/h100_large_mps_manifest.sha256"
```

只有每个 case 都报告 `OK` 后才能 benchmark。

如果下载中断，应根据 manifest 重新生成缺失/损坏文件列表，只下载失败文件。只有通过 SHA256 的文件才算存在。

## 当前 case 数量

当前 H100 来源数据集包含 26 个 `.mps` 文件；RTX 3090 本地副本大小约 22 GiB。准确来源以 SHA256 manifest 为准，而不是手写列表。

从 manifest 生成 case list：

```bash
DATA_ROOT="$HOME/cuPDLP-C/test_data_large_mps"
awk '{print $2}' "$DATA_ROOT/h100_large_mps_manifest.sha256" \
  | sed 's#^\./##' \
  | sort > ~/large_mps_all26.txt
```

## 各设备 benchmark 策略

| 设备 | Backend 策略 | 用途 |
|---|---|---|
| RTX 3090 | 上游兼容 cuPDLP-C CUDA，全量跑一次 | CUDA baseline |
| RTX 4090D | 上游兼容 cuPDLP-C CUDA，全量跑一次 | CUDA baseline |
| H100 | 上游兼容 cuPDLP-C CUDA，全量跑一次 | 高端 CUDA baseline |
| Radeon 890M | ROCm/HIP pre-tuning baseline，之后 tuned rerun | ROCm baseline 和 tuning 对比 |
| Radeon PRO W7900 | 后续 ROCm/HIP `gfx1100` run | 比赛目标平台 |

CUDA 平台不需要像 ROCm 那样做 repeated tuning run。Radeon 890M 应测两次：一次用可用但未调优的 ROCm commit，一次用最好的已验证 tuned 版本。

## 推荐单次运行限制

Large MPS benchmark 使用：

```text
nIterLim = 200000000
external timeout = 7200s
```

Timeout 也是有效结果，只要日志记录：

- case name；
- backend；
- device；
- commit 或 upstream source；
- timeout value；
- exit status；
- 可用时记录 terminationCode；
- 可用时记录 iteration count；
- primal feasibility；
- dual feasibility；
- duality gap；
- wall-clock time；
- solve time；
- log path。

不要静默删除困难 case。

## 3090 CUDA baseline 命令形态

使用原始 cuPDLP-C 构建出的上游兼容 `plc`。Large MPS 目录应为：

```text
~/cuPDLP-C/test_data_large_mps/mps
```

Benchmark 脚本应写出：

```text
runtime_summary.csv
run_info.txt
logs/*.log
json/*.json
```

Summary 至少包含：

```text
case,status,wall_seconds,log,json
```

后续 parser 可以从 JSON 和 log 里提取 solver-level metrics。

## 890M ROCm baseline 命令形态

Pre-tuning ROCm baseline 使用可构建且位于后续 tuning pass 之前的 commit。预期 baseline commit 是：

```text
ae3b683 Add ROCm profiling summary script
```

构建命令：

```bash
cmake -S . -B build-rocm-plc -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

之后用同一已校验 large MPS case list 和同一高层限制运行。

## 应提交什么

只提交整理后的元数据和 summary：

```text
validation/datasets/h100_large_mps_inventory.csv
validation/datasets/h100_large_mps_manifest.sha256
validation/cases/h100_large_mps_cases.txt
validation/large_mps_*_summary.csv
docs/LARGE_MPS_BENCHMARK_PLAN.md
docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md
```

不要提交：

```text
*.mps
*.mps.gz
raw solver output directories
BaiduPCS-Go temporary files
large tar archives
```

## 解释策略

Large MPS benchmark 应回答三个问题：

1. CUDA 和 ROCm backend 是否运行同一批已验证输入？
2. 哪些更大 case 能从 GPU 加速受益？
3. Radeon 890M 在 tuning 前后主要 ROCm 开销在哪里？

结果应结合 profiling 解释。单个 timeout 或 convergence-sensitive case 应记录，而不是隐藏。

## 完成状态更新 / 2026-06-17

原始 benchmark plan 已经不再只是计划阶段。CUDA baselines、Radeon 890M
ROCm baselines、W7900 / `gfx1100` baselines、targeted profiling 和 P11
SpMV tuning summaries 都已经作为整理后的 validation artifacts 提交。

在当前分支中，W7900 不应再写成未来平台。它已经是当前项目阶段完成的第二个
ROCm 目标。原始 `.mps` 文件和 raw solver logs 仍不提交到 Git；整理后的
summaries 和入口位于 `validation/` 与 `docs/W7900_CURRENT_STATUS.zh-CN.md`。
