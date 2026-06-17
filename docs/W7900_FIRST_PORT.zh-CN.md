# W7900 / gfx1100 首次移植记录

本文记录 cuPDLP-C-ROCm 在 AMD Radeon PRO W7900 / `gfx1100` 平台上的首次构建、运行与 smoke validation 结果。

## 1. 阶段目标

本阶段目标不是性能调优，而是完成 W7900 平台上的可复现 ROCm/HIP 构建路径，并验证 `plc` 可执行文件能够在 CPU baseline 与 ROCm backend 下运行同一个 MPS 测试问题。

当前阶段结论：

* CPU baseline 构建成功。
* ROCm/HIP W7900 构建成功。
* `example/afiro.mps` 在 CPU 与 ROCm 路径下均运行成功。
* CPU 与 ROCm 结果均为 `OPTIMAL`，且 primal/dual 状态均为 `FEASIBLE`。
* W7900 / `gfx1100` 后续进入 extended validation、profiling 与 tuning 阶段。

## 2. 平台概况

测试平台：

* CPU：2 × AMD EPYC 9334
* 逻辑 CPU：128
* 内存：约 1 TiB
* GPU：8 × AMD GPU，PCI ID `1002:744B`
* ROCm 架构：`gfx1100`
* GPU runtime 名称：`AMD Radeon Graphics`
* NUMA：

  * NUMA node 0：card1-card4
  * NUMA node 1：card5-card8

GPU 识别结果：

* `rocm_agent_enumerator` 输出 8 个 `gfx1100`
* `rocminfo` 可识别 8 个 AMD GPU agent
* `rocm-smi` 可看到 8 张 AMD GPU

## 3. ROCm SDK 特殊路径

该平台未使用标准 `/opt/rocm` 安装路径，而是使用 `/opt/python` 中提供的 ROCm SDK：

* `hipcc`: `/opt/python/bin/hipcc`
* ROCm SDK core: `/opt/python/lib/python3.12/site-packages/_rocm_sdk_core`
* ROCm SDK devel: `/opt/python/lib/python3.12/site-packages/_rocm_sdk_devel`

关键头文件位于：

* `.../_rocm_sdk_devel/include/hipblas/hipblas.h`
* `.../_rocm_sdk_devel/include/hipsparse/hipsparse.h`
* `.../_rocm_sdk_devel/include/rocblas/rocblas.h`

因此 W7900 ROCm 构建需要显式传入：

* `CMAKE_PREFIX_PATH`
* `CMAKE_C_FLAGS`
* `CMAKE_CXX_FLAGS`
* `CMAKE_HIP_FLAGS`

否则 C 编译阶段可能会因为默认查找 `/opt/rocm/include` 而找不到 `hipblas/hipblas.h`。

## 4. 依赖

HiGHS 使用 1.6.0 版本，并安装到：

```bash
/app/cupdlp_w7900/deps/install/highs-1.6.0
```

环境变量：

```bash
export HIGHS_HOME=/app/cupdlp_w7900/deps/install/highs-1.6.0
```

## 5. 构建脚本

CPU baseline 构建：

```bash
./scripts/build_w7900_cpu.sh
```

ROCm/W7900 构建：

```bash
./scripts/build_w7900_rocm.sh
```

ROCm 构建目录：

```bash
build-rocm-w7900
```

CPU 构建目录：

```bash
build-cpu
```

## 6. CPU smoke validation

运行命令：

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /app/cupdlp_w7900/results/afiro_cpu.json \
  -nIterLim 200
```

结果摘要：

| 字段                |                   值 |
| ----------------- | ------------------: |
| `nIter`           |                 199 |
| `nAxCalls`        |                 216 |
| `nAtyCalls`       |                 216 |
| `dPrimalObj`      | -464.76346304245351 |
| `dDualObj`        | -464.83426216130988 |
| `dRelPrimalFeas`  |    0.00003926084712 |
| `dRelDualFeas`    |    0.00000566716996 |
| `dRelDualityGap`  |    0.00007607918754 |
| `terminationCode` |           `OPTIMAL` |
| `primalCode`      |          `FEASIBLE` |
| `dualCode`        |          `FEASIBLE` |

## 7. ROCm/W7900 smoke validation

运行命令：

```bash
HIP_VISIBLE_DEVICES=0 ./build-rocm-w7900/bin/plc \
  -fname ./example/afiro.mps \
  -out /app/cupdlp_w7900/results/afiro_rocm_w7900.json \
  -nIterLim 200
```

运行时输出摘要：

```text
HIP runtime 71260610
HIP driver 71260610
hipSPARSE 400300
HIP device 0: AMD Radeon Graphics
```

结果摘要：

| 字段                |                   值 |
| ----------------- | ------------------: |
| `nIter`           |                 199 |
| `nAxCalls`        |                 216 |
| `nAtyCalls`       |                 216 |
| `dPrimalObj`      | -464.76346057035607 |
| `dDualObj`        | -464.83422735641489 |
| `dRelPrimalFeas`  |    0.00003927125321 |
| `dRelDualFeas`    |    0.00000565531500 |
| `dRelDualityGap`  |    0.00007604444646 |
| `terminationCode` |           `OPTIMAL` |
| `primalCode`      |          `FEASIBLE` |
| `dualCode`        |          `FEASIBLE` |

GPU timing 摘要：

| 字段                             |        值 |
| ------------------------------ | -------: |
| `AllocMem_CopyMatToDeviceTime` | 0.000337 |
| `CopyVecToDeviceTime`          | 0.000085 |
| `CopyVecToHostTime`            | 0.000000 |
| `DeviceMatVecProdTime`         | 0.040984 |
| `dSolvingTime`                 | 0.111312 |

## 8. CPU 与 ROCm 结果对比

| 指标                |                 CPU |          ROCm/W7900 |
| ----------------- | ------------------: | ------------------: |
| `nIter`           |                 199 |                 199 |
| `terminationCode` |           `OPTIMAL` |           `OPTIMAL` |
| `primalCode`      |          `FEASIBLE` |          `FEASIBLE` |
| `dualCode`        |          `FEASIBLE` |          `FEASIBLE` |
| `dPrimalObj`      | -464.76346304245351 | -464.76346057035607 |
| `dDualObj`        | -464.83426216130988 | -464.83422735641489 |
| `dRelPrimalFeas`  |    0.00003926084712 |    0.00003927125321 |
| `dRelDualFeas`    |    0.00000566716996 |    0.00000565531500 |
| `dRelDualityGap`  |    0.00007607918754 |    0.00007604444646 |

该结果说明 W7900 / `gfx1100` ROCm backend 在 `afiro` smoke case 上与 CPU baseline 的终止状态一致，数值误差处于合理范围内。

<!-- W7900_DOC_SWEEP_20260614_BEGIN -->
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
<!-- W7900_DOC_SWEEP_20260614_END -->

## 9. 已知限制与当前完成状态

本文是 W7900 / `gfx1100` first-port smoke milestone 的历史记录。原始
first-port 限制已经由后续 W7900 文档取代：

* extended Netlib validation：已完成。
* large MPS benchmark：non-hard23 baseline 已完成，hard3 单独记录。
* W7900 profiling：P10 targeted rocprof 已归档。
* W7900 单卡调优：P11 SpMV tuning 已完成，当前默认
  `HIPSPARSE_SPMV_CSR_ALG1`。
* 8 GPU 并发吞吐实验：fast8 batch throughput 已归档。
* 跨设备 benchmark matrix：已有 curated summaries。

当前仍不应描述为生产级 solver release，但已经超过 first-port smoke 阶段。
权威状态见 [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)。

## 10. 后续计划状态

原下一步计划已基本完成。当前仅保留可选增强：

1. W7900 P14-A：current-vs-before representative repeated validation。
2. W7900 P14-B：CSR ALG1-vs-ALG2 representative repeated validation。

其他深层数值路径优化不纳入当前项目终点。
