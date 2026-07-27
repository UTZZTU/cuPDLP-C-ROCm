# ROCm workflow 指南

> English version: [`ROCM_WORKFLOW.md`](ROCM_WORKFLOW.md)

本文总结 `cuPDLP-C-ROCm` fork 的日常命令。

本仓库当前提供：

- CPU 构建路径；
- 上游兼容 CUDA 构建路径；
- ROCm/HIP 构建路径；
- smoke validation；
- extended Netlib validation；
- ROCm port hygiene checks；
- CTest 集成；
- `rocprofv3` profiling helper；
- profiling summary helper；
- copy-trace analysis helper；
- cross-device 和 large MPS benchmark workflow。

当前已验证 ROCm 目标包括 AMD Radeon 890M / `gfx1150` 和 Radeon PRO W7900 / `gfx1100`。W7900 已完成 P10 targeted profiling、P11 SpMV tuning 与 P12 rejected experiment note。

## 1. 仓库健康检查

修改 ROCm/HIP 代码、validation 脚本、profiling 脚本或公开文档后使用：

```bash
cd ~/rocm_dir/pdlp/cuPDLP-C-ROCm
git status --short
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

期望结果：

```text
== cuPDLP-C-ROCm full port check: PASS ==
100% tests passed
```

完整检查会运行 ROCm port hygiene checks 和 CPU-vs-ROCm smoke validation。

## 2. ROCm 构建

Radeon 890M / `gfx1150`：

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

Radeon PRO W7900 使用相同命令，但切换为：

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

## 3. 只运行 ROCm port hygiene

修改命名、CMake 逻辑、公开日志或 ROCm/HIP wrapper 时使用：

```bash
./scripts/check_rocm_port_hygiene.sh
```

以下兼容符号当前仍然被允许：

```text
cuda_csr_Ax
cuda_csc_ATy
cuda_alloc_MVbuffer
```

它们暂时是内部兼容边界。不要在没有专门兼容性 pass 的情况下随意重命名。

## 4. Smoke validation

```bash
./scripts/run_validation.sh
```

默认 smoke case 定义在：

```text
validation/cases.txt
```

当前 smoke 覆盖：

```text
afiro
sc50b
```

结果写入：

```text
validation/results/latest/
```

常用摘要命令：

```bash
grep -R "Overall result" validation/results/latest/*/*_compare.md
```

期望结果：

```text
afiro: PASS
sc50b: PASS
```

## 5. Extended Netlib validation

算法相关变化、kernel fusion、memory-copy 变化或较大 ROCm/HIP 重构后使用：

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt

grep -R "Overall result" validation/results/extended_netlib/*/*_compare.md
```

当前期望状态：

```text
afiro PASS
adlittle PASS
blend PASS
sc50a PASS
sc50b PASS
share2b INCOMPLETE
```

`share2b` 在当前限制下被视为 incomplete，而不是 hard correctness failure。

## 6. 准备 Netlib case

```bash
./scripts/prepare_netlib_cases.sh
```

生成的 Netlib 文件是本地验证 artifact，应保持 ignored。

检查本地 case：

```bash
find validation/netlib -maxdepth 1 -name '*.mps' -printf '%f\n' | sort
```

## 7. Profiling smoke workflow

性能相关变化后使用：

```bash
RESULT_ROOT=profiling/results/current \
  ./scripts/profile_rocm_smoke.sh
```

汇总 `rocprofv3` CSV trace：

```bash
python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

常用快速查看：

```bash
grep -nE 'Top HIP API|Top kernels|Kernel categories|hipLaunchKernel|hipMemcpy|copyBuffer|rocblas|rocSPARSE' \
  profiling/results/current/profile_summary.md | head -260
```

Profiling 结果是生成 artifact，不应提交。

## 8. Copy/copyBuffer 分析

当 `hipMemcpy`、`hipMemcpyAsync` 或 `__amd_rocclr_copyBuffer` 是热点时使用：

```bash
python3 scripts/analyze_rocm_copy_trace.py \
  --input profiling/results/current/sc50b_rocprofv3 \
  | tee profiling/results/current/sc50b_copy_analysis.md
```

该 helper 会报告 HIP memcpy 计数/时间、ROCclr copy/fill buffer dispatch 计数/时间，以及 copyBuffer dispatch 是否和 HIP memcpy 调用相关。

## 9. 跨设备 benchmark workflow

Netlib benchmark matrix：

```bash
CASE_TIMEOUT_SEC=3600 ./scripts/run_benchmark_890m_full.sh
./scripts/summarize_benchmark.py
```

CUDA baseline 机器使用相同 case list 和高层设置：

```text
validation/cases_benchmark_200m.txt
nIterLim = 200000000
per-run timeout = 3600s
```

## 10. Large MPS workflow

Large MPS workflow 使用 H100 作为源数据集机器，并用百度网盘作为传输方式。每台目标机器在 benchmark 前必须通过 SHA256 校验。

详见：

```text
docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md
```

## 11. 什么时候运行什么命令

| 场景 | 推荐命令 |
|---|---|
| 修改 ROCm/HIP 源码 | `./scripts/check_rocm_port.sh && ctest --test-dir build-rocm-plc --output-on-failure` |
| 修改命名、CMake 或公开日志 | `./scripts/check_rocm_port_hygiene.sh` |
| 修改 validation 脚本 | `./scripts/run_validation.sh` |
| 修改算法相关 GPU 代码 | Extended Netlib validation |
| 修改性能敏感代码 | Profiling smoke + summary |
| 修改 memory-copy 行为 | Profiling smoke + copy analysis |
| 只修改文档 | `git diff`，可选运行 `./scripts/check_rocm_port_hygiene.sh` |
| 修改 benchmark case list | 重新生成 manifest/summary，并重跑受影响子集 |

## 12. 建议提交策略

通常提交：

```text
scripts/*.sh
scripts/*.py
docs/*.md
validation/cases*.txt
validation/*.csv
validation/datasets/*.sha256
validation/datasets/*.csv
tools/migration/*.py
```

通常不提交：

```text
validation/results/
profiling/results/
build-*/
validation/netlib/
validation/netlib_compressed/
tools/emps
tools/emps.c
large raw MPS files
```

## 13. 当前维护优先级

当前仓库范围内，原 large-MPS、W7900 migration、P10 profiling、P11 tuning、P12 negative experiment 和 P14-A1 repeated-validation 任务均已完成。

当前优先级是：

1. 保持中英文当前态文档和索引同步；
2. 日期化报告作为不可变证据保留，不再追加新的状态块；
3. 代码、ROCm、编译器或依赖变化后重新运行 W7900 validation；
4. 只有在回答明确问题时才增加 P14-B repeated ALG1-vs-ALG2 evidence；
5. 更深层 reduction 或 numerical-path 优化必须先设计新的验证协议。

纯文档工作可以在其他主机完成，但不能描述为 fresh W7900 性能复现。
