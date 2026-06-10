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
/root/cupdlp_w7900/deps/install/highs-1.6.0
```

环境变量：

```bash
export HIGHS_HOME=/root/cupdlp_w7900/deps/install/highs-1.6.0
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
  -out /root/cupdlp_w7900/results/afiro_cpu.json \
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
  -out /root/cupdlp_w7900/results/afiro_rocm_w7900.json \
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

## 9. 已知限制

当前阶段仅完成 first-port smoke validation，尚未完成：

* extended Netlib validation
* large MPS benchmark
* W7900 profiling
* W7900 单卡调优
* 8 GPU 并发吞吐实验
* 跨设备 benchmark matrix 更新

因此当前状态应描述为：

```text
W7900 / gfx1100 first-port smoke validation passed.
Extended validation and tuning are in progress.
```

不应描述为完整生产级验证完成。

## 10. 下一步计划

后续计划：

1. 固化 W7900 CPU/ROCm 构建脚本。
2. 补充英文版 `W7900_FIRST_PORT.md`。
3. 更新 README 中 W7900 的状态描述。
4. 跑 W7900 smoke validation 脚本。
5. 跑 extended Netlib validation。
6. 使用 ROCm profiling 工具定位 W7900 单卡瓶颈。
7. 基于 profile 结果进行单卡调优。
8. 做 8 GPU single-GPU sweep 与多任务并发吞吐实验。
9. 将结果汇总到比赛报告。
