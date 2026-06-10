# cuPDLPx vs cuPDLP-C：RTX 4090D short13 对比

日期：2026-06-10  
平台：RTX 4090D，物理 GPU 2  
数据集：从 large MPS 26 case 中选出的 13 个短/中等代表 case。  
目的：在同一台 4090D、同一批 MPS 数据上，初步比较 upstream cuPDLP-C 与 cuPDLPx 的性能和稳定性。

## 背景

cuPDLP-C 是本项目 ROCm/HIP 迁移的主线 baseline。cuPDLPx 是 MIT-Lu-Lab 发布的新一代 GPU LP solver，基于 restarted Halpern PDHG，并加入 adaptive restart、PID-controlled primal weight 等机制。cuPDLPx 论文报告了相对 cuPDLP 的显著经验加速，因此本实验用于判断它是否值得作为后续算法路线或迁移候选。

## 测试口径

cuPDLP-C 结果来自已经提交的 4090D CUDA baseline：

```text
run_dir = /home/omnisky/cuPDLP-C/test_data_large_mps/large_mps_4090_upstream_26cases_niter1b_dtimelim7200_20260610_162424
nIterLim = 1000000000
dTimeLim = 7200
external timeout = 7500s
```

cuPDLPx 结果来自 short13 运行：

```text
run_dir = /home/omnisky/cuPDLP-C/test_data_large_mps/cupdlpx_4090_short13_iter1b_timelim7200_20260610_203434
cuPDLPx version = v0.2.9
commit = 931c94c
iter_limit = 1000000000
time_limit = 7200
external timeout = 7500s
eps_opt = 1e-4
eps_feas = 1e-4
CUDA Toolkit = /usr/local/cuda-12.8
CMAKE_CUDA_ARCHITECTURES = 89
```

cuPDLPx 的原始自动脚本 `summary.csv` 中 `status_guess/time_guess/gap_guess` 是宽泛 grep 得到的，不用于本文结论。本文使用每个 `logs/*_cupdlpx.log` 中最终 `Solution Summary` 块里的真实字段。

## 汇总结果

| metric | value |
| --- | --- |
| cases | 13 |
| cuPDLP-C OPTIMAL | 13/13 |
| cuPDLPx OPTIMAL | 13/13 |
| cuPDLPx solve-time wins | 10/13 |
| cuPDLPx wall-time wins | 11/13 |
| median solve-time speedup (cuPDLP-C / cuPDLPx) | 1.55x |
| geomean solve-time speedup (cuPDLP-C / cuPDLPx) | 1.60x |
| median wall-time speedup (cuPDLP-C / cuPDLPx) | 1.60x |
| geomean wall-time speedup (cuPDLP-C / cuPDLPx) | 1.60x |

## 逐 case 性能对比

`solve speedup` 和 `wall speedup` 均定义为 `cuPDLP-C time / cuPDLPx time`。大于 1 表示 cuPDLPx 更快。

| case | tier | C status | C iter | C wall | C solve | x status | x iter | x wall | x solve | solve speedup | wall speedup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qap15.mps | M | OPTIMAL | 2840 | 1.44 | 0.291 | OPTIMAL | 2800 | 0.44 | 0.068 | 4.26x | 3.27x |
| supportcase10.mps | M | OPTIMAL | 21560 | 5.74 | 3.206 | OPTIMAL | 12800 | 6.49 | 0.442 | 7.25x | 0.88x |
| neos-5251015.mps | L | OPTIMAL | 920 | 6.61 | 0.226 | OPTIMAL | 1200 | 6.14 | 0.146 | 1.55x | 1.08x |
| neos-5052403-cygnet.mps | L | OPTIMAL | 8400 | 9.60 | 2.361 | OPTIMAL | 7600 | 11.03 | 0.564 | 4.19x | 0.87x |
| ex10.mps | M | OPTIMAL | 280 | 11.34 | 0.068 | OPTIMAL | 600 | 6.70 | 0.047 | 1.45x | 1.69x |
| savsched1.mps | L | OPTIMAL | 560 | 12.23 | 0.187 | OPTIMAL | 800 | 6.87 | 0.102 | 1.83x | 1.78x |
| rmine15.mps | M | OPTIMAL | 19320 | 12.82 | 2.930 | OPTIMAL | 22200 | 5.95 | 1.560 | 1.88x | 2.15x |
| irish-electricity.mps | M | OPTIMAL | 57880 | 16.35 | 7.374 | OPTIMAL | 39600 | 5.37 | 1.300 | 5.67x | 3.04x |
| s250r10.mps | L | OPTIMAL | 5240 | 16.92 | 0.903 | OPTIMAL | 76200 | 11.89 | 5.360 | 0.17x | 1.42x |
| graph40-40.mps | L | OPTIMAL | 80 | 18.85 | 0.042 | OPTIMAL | 400 | 14.60 | 0.050 | 0.85x | 1.29x |
| scpm1.mps | L | OPTIMAL | 1360 | 44.57 | 0.556 | OPTIMAL | 8000 | 22.79 | 1.880 | 0.30x | 1.96x |
| s100.mps | L | OPTIMAL | 578520 | 125.13 | 111.009 | OPTIMAL | 883600 | 84.46 | 74.200 | 1.50x | 1.48x |
| fhnw-binschedule1.mps | L | OPTIMAL | 142240 | 192.59 | 82.821 | OPTIMAL | 156200 | 120.52 | 63.800 | 1.30x | 1.60x |

## cuPDLPx 解质量摘要

| case | cuPDLPx status | objective gap | primal infeas | dual infeas |
| --- | --- | --- | --- | --- |
| qap15.mps | OPTIMAL | 1.37e-05 | 9.467e-05 | 1.201e-05 |
| supportcase10.mps | OPTIMAL | 9.841e-06 | 7.832e-07 | 8.572e-05 |
| neos-5251015.mps | OPTIMAL | 3.829e-06 | 6.051e-09 | 3.152e-05 |
| neos-5052403-cygnet.mps | OPTIMAL | 8.802e-05 | 4.235e-05 | 8.706e-05 |
| ex10.mps | OPTIMAL | 2.781e-06 | 3.786e-05 | 5.482e-06 |
| savsched1.mps | OPTIMAL | 2.639e-06 | 1.214e-08 | 2.607e-08 |
| rmine15.mps | OPTIMAL | 3.307e-05 | 9.571e-05 | 2.746e-05 |
| irish-electricity.mps | OPTIMAL | 1.98e-05 | 1.601e-06 | 9.943e-05 |
| s250r10.mps | OPTIMAL | 7.898e-05 | 5.042e-08 | 1.367e-06 |
| graph40-40.mps | OPTIMAL | 7.265e-10 | 3.553e-05 | 1.343e-06 |
| scpm1.mps | OPTIMAL | 8.096e-07 | 9.872e-05 | 2.301e-07 |
| s100.mps | OPTIMAL | 9.959e-05 | 1.361e-08 | 1.312e-05 |
| fhnw-binschedule1.mps | OPTIMAL | 2.317e-05 | 7.365e-10 | 9.018e-05 |

## 初步结论

1. **稳定性：cuPDLPx short13 全部 13 个 case 均为 OPTIMAL**，没有程序级失败。
2. **solver 内部时间：cuPDLPx 在 10/13 个 case 上更快**，中位数 solve-time 加速约 **1.55x**，几何平均约 **1.60x**。
3. **端到端 wall time：cuPDLPx 在 10/13 个 case 上更快**，但对很小 case，presolve/IO/启动开销会显著影响 wall time。
4. cuPDLPx 在 `supportcase10`、`irish-electricity`、`neos-5052403-cygnet`、`qap15` 等 case 上 solve-time 加速明显。
5. cuPDLPx 在 `s250r10`、`scpm1`、`graph40-40` 上 solver-time 不占优，说明它不是所有 case 都更快。
6. 当前结果足以说明 cuPDLPx 作为算法升级路线值得继续评估，但它不应替代 cuPDLP-C-ROCm 主线：cuPDLP-C 已经完成 ROCm port 和跨平台 baseline，cuPDLPx 仍需要额外评估 MPS 兼容性、输出格式、长 case 表现和 ROCm 迁移成本。

## 建议后续实验

建议下一轮只追加 5 个长/大 case：

```text
a2864.mps
Primal2_1000.mps
L2CTA3D.mps
Dual2_5000.mps
dlr1.mps
```

如果这些 case 上 cuPDLPx 仍稳定且明显更快，再考虑写“cuPDLPx ROCm 移植可行性”技术评估。
