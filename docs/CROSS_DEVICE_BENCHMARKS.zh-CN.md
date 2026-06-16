# 跨设备 benchmark 说明

> English version: [`CROSS_DEVICE_BENCHMARKS.md`](CROSS_DEVICE_BENCHMARKS.md)

本文总结 cuPDLP-C ROCm/HIP port 的当前跨设备 benchmark workflow。

## 目标

目标是在相同 LP case list 和相同高层 solver 设置下，比较上游兼容 CUDA baseline 和 ROCm/HIP port。

当前 Netlib benchmark matrix 覆盖：

- RTX 3090，上游兼容 cuPDLP-C CUDA baseline。
- RTX 4090D，上游兼容 cuPDLP-C CUDA baseline。
- AMD Radeon 890M / `gfx1150`，cuPDLP-C-ROCm。

每台设备都记录本机 CPU 和 GPU/ROCm run。CPU 结果是本机 baseline，不是跨机器绝对性能声明。

## Benchmark 设置

通用设置：

| 设置 | 值 |
|---|---|
| Case 来源 | Netlib MPS cases 加 `afiro`、`sc50b` 和 `lotfi` |
| 迭代限制 | `nIterLim = 200000000` |
| 单次 wall-clock timeout | Netlib matrix 使用 `3600s` |
| HiGHS 版本 | 1.6.0 |
| 结果风格 | 每台设备本地 CPU + GPU/ROCm run |

主要比较字段：

- termination status；
- iteration count；
- solve time；
- relative primal feasibility；
- relative dual feasibility；
- relative duality gap；
- 可用时记录 GPU timing breakdown。

大型原始结果目录、下载的 MPS 文件和 tar 包是本地 artifact，不应提交。

## 设备级状态

| 设备 | CPU 结果 | GPU/ROCm 结果 | 例外 |
|---|---:|---:|---|
| RTX 3090 / CUDA | `greenbea` 200M 补跑后 28/28 OPTIMAL | 27/28 OPTIMAL | `greenbea` CUDA 达到 solver 内部 3600s 限制 |
| RTX 4090D / CUDA | 28/28 OPTIMAL | 27/28 OPTIMAL | `greenbea` CUDA 命中外部 3600s timeout |
| Radeon 890M / ROCm | 28/28 OPTIMAL | 27/28 OPTIMAL | `greenbea` ROCm 命中外部 3600s timeout |

## 代表性性能 case

| Case | RTX 3090 CPU / CUDA 时间 | RTX 4090D CPU / CUDA 时间 | Radeon 890M CPU / ROCm 时间 | 说明 |
|---|---:|---:|---:|---|
| `afiro` | 0.000581s / 0.035574s | 0.000228s / 0.033316s | 0.000223s / 0.055775s | 极小 case；GPU overhead 主导 |
| `sc50b` | 0.002908s / 0.066647s | 0.000761s / 0.058011s | 0.000703s / 0.066212s | 极小 case；GPU overhead 主导 |
| `lotfi` | 0.721584s / 7.221900s | 0.541828s / 6.371220s | 0.339811s / 3.587740s | 虽然收敛，但 GPU path 更慢 |
| `80bau3b` | 1.941090s / 1.058330s | 1.675210s / 0.873151s | 0.908968s / 0.887086s | GPU/ROCm 开始具备竞争力 |
| `fit2d` | 1.824550s / 0.430777s | 1.981560s / 0.376708s | 1.004250s / 1.187790s | CUDA 明显更快；890M ROCm 接近但更慢 |
| `greenbeb` | 117.688s / 81.6909s | 103.155s / 72.3501s | 54.0035s / 152.025s | CUDA 更快；890M ROCm 更慢 |
| `maros-r7` | 0.277859s / 0.074724s | 0.289098s / 0.061516s | 0.157686s / 0.116644s | GPU/ROCm 更快或接近 |
| `pilot87` | 15.3384s / 7.98787s | 14.9857s / 8.00709s | 7.69941s / 7.91001s | CUDA 更快；ROCm 基本持平 |

## GPU/ROCm 快于 CPU 的 case

| 设备 | GPU/ROCm 更快的 case |
|---|---|
| RTX 3090 / CUDA | `80bau3b`、`fit2d`、5M iteration-limited run 下的 `greenbea`、`greenbeb`、`maros-r7`、`pilot87` |
| RTX 4090D / CUDA | `80bau3b`、`fit2d`、`greenbeb`、`maros-r7`、`pilot87` |
| Radeon 890M / ROCm | `80bau3b`、`maros-r7` |

## `greenbea` 收敛敏感行为

| 设备 | CPU 结果 | GPU/ROCm 结果 | 解释 |
|---|---|---|---|
| RTX 3090 / CUDA | 200M 补跑中 CPU 在 1286.92s 达到 OPTIMAL | CUDA 在 41.6M iterations 后达到 solver 内部 3600s time limit | 上游 CUDA 已经表现出 GPU convergence sensitivity |
| RTX 4090D / CUDA | CPU 在 1178.48s 达到 OPTIMAL | CUDA 在写出 JSON 前命中外部 3600s timeout | 新一代 CUDA GPU 上同样困难 |
| Radeon 890M / ROCm | CPU 在 592.58s 达到 OPTIMAL | ROCm 在写出 JSON 前命中外部 3600s timeout | 应作为收敛敏感 case 记录，不视为 ROCm 构建失败 |

## 解释

Benchmark 表明 ROCm/HIP port 在 Radeon 890M 上具备求解共享 benchmark set 的功能能力。

除 `greenbea` 外，所有已测试 ROCm case 都达到 `OPTIMAL`。小 case 通常 GPU/ROCm 比 CPU 慢，这是预期现象，因为 GPU path 需要承担 device initialization、kernel launch、synchronization 和 vector update 等额外开销。

这种行为在上游 CUDA baseline 中也存在，因此小 case 变慢不应被解读为 ROCm-specific failure。部分更大或更适合 GPU 的 case 显示出 GPU 优势。

`greenbea` 应保留为 convergence-sensitive case。上游 CUDA 在该 case 上已经出现困难 GPU 收敛行为，因此 RTX 4090D 和 Radeon 890M 上的 timeout 应记录为 backend numerical trajectory / convergence sensitivity，而不是 ROCm porting failure。

## 当前结论

当前 ROCm/HIP port 已经在 Radeon 890M / `gfx1150` 上通过跨设备功能 benchmark 阶段。它仍不是完全调优的 ROCm 求解器。

下一阶段是：

1. 收集 large MPS benchmark 结果；
2. 在 Radeon 890M 上记录 pre-tuning ROCm baseline；
3. 使用最好的已验证 tuning 版本复测 Radeon 890M；
4. 比较 RTX 3090、RTX 4090D 和 H100 上的 CUDA baseline；
5. 用 profiling 解释性能差异。

## 文件

Netlib benchmark workflow 使用：

```text
validation/cases_benchmark_200m.txt
scripts/run_benchmark_890m_full.sh
scripts/summarize_benchmark.py
validation/cross_device_summary.csv
```

Large MPS workflow 见：

```text
docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md
```

不应提交到 Git 的生成 artifact：

```text
validation/netlib/
validation/results/
profiling/results/
build-*/
*.tar.gz
large raw MPS files
```

## W7900 完成状态更新 / 2026-06-17

cross-device 叙事已经从最初的 Netlib 和 890M-only benchmark 阶段扩展到
W7900 / `gfx1100`。当前分支已经包含 W7900 validation、large-MPS summaries、
targeted profiling 和 P11 SpMV tuning 文档。

之前写作“下一阶段”的事项，在当前项目范围内已经部分或全部完成。当前终点是：

- W7900 first-port 和 baseline 文档已完成。
- P10 targeted rocprof 证据已收集。
- P11 opt-in SpMV algorithm switch 已实现。
- W7900 默认 SpMV algorithm 已设为 `HIPSPARSE_SPMV_CSR_ALG1`。
- 旧默认可通过 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退。

详见 `docs/W7900_CURRENT_STATUS.zh-CN.md` 和
`validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md`。
