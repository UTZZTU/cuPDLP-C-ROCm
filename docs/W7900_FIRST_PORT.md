# W7900 / gfx1100 First-Port Notes

This document records the first successful build, run, and smoke validation of cuPDLP-C-ROCm on an AMD Radeon PRO W7900 / `gfx1100` platform.

## 1. Stage Goal

The goal of this stage is not performance tuning. The goal is to establish a reproducible ROCm/HIP build path for the W7900 platform and verify that the `plc` executable can run the same MPS test case through both the CPU baseline and the ROCm backend.

Current stage result:

* CPU baseline build passed.
* ROCm/HIP W7900 build passed.
* `example/afiro.mps` ran successfully with both CPU and ROCm paths.
* Both CPU and ROCm runs reported `OPTIMAL`, with primal and dual status reported as `FEASIBLE`.
* W7900 / `gfx1100` is ready for extended validation, profiling, and tuning.

## 2. Platform Summary

Test platform:

* CPU: 2 × AMD EPYC 9334
* Logical CPUs: 128
* Memory: approximately 1 TiB
* GPU: 8 × AMD GPU, PCI ID `1002:744B`
* ROCm architecture: `gfx1100`
* GPU runtime name: `AMD Radeon Graphics`
* NUMA layout:

  * NUMA node 0: card1-card4
  * NUMA node 1: card5-card8

GPU detection summary:

* `rocm_agent_enumerator` reports 8 `gfx1100` agents.
* `rocminfo` detects 8 AMD GPU agents.
* `rocm-smi` detects 8 AMD GPUs.

## 3. ROCm SDK Path

This platform does not use a standard `/opt/rocm` installation. Instead, it uses a ROCm SDK provided under `/opt/python`:

* `hipcc`: `/opt/python/bin/hipcc`
* ROCm SDK core: `/opt/python/lib/python3.12/site-packages/_rocm_sdk_core`
* ROCm SDK devel: `/opt/python/lib/python3.12/site-packages/_rocm_sdk_devel`

Important headers are located under the devel SDK path:

* `.../_rocm_sdk_devel/include/hipblas/hipblas.h`
* `.../_rocm_sdk_devel/include/hipsparse/hipsparse.h`
* `.../_rocm_sdk_devel/include/rocblas/rocblas.h`

Therefore, the W7900 ROCm build must explicitly pass:

* `CMAKE_PREFIX_PATH`
* `CMAKE_C_FLAGS`
* `CMAKE_CXX_FLAGS`
* `CMAKE_HIP_FLAGS`

Without these paths, the C compilation stage may fall back to `/opt/rocm/include` and fail to find `hipblas/hipblas.h`.

## 4. Dependency

HiGHS version 1.6.0 is used and installed at:

```bash
/app/cupdlp_w7900/deps/install/highs-1.6.0
```

Environment variable:

```bash
export HIGHS_HOME=/app/cupdlp_w7900/deps/install/highs-1.6.0
```

## 5. Build Scripts

CPU baseline build:

```bash
./scripts/build_w7900_cpu.sh
```

ROCm/W7900 build:

```bash
./scripts/build_w7900_rocm.sh
```

ROCm build directory:

```bash
build-rocm-w7900
```

CPU build directory:

```bash
build-cpu
```

## 6. CPU Smoke Validation

Command:

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /app/cupdlp_w7900/results/afiro_cpu.json \
  -nIterLim 200
```

Result summary:

| Field             |               Value |
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

## 7. ROCm/W7900 Smoke Validation

Command:

```bash
HIP_VISIBLE_DEVICES=0 ./build-rocm-w7900/bin/plc \
  -fname ./example/afiro.mps \
  -out /app/cupdlp_w7900/results/afiro_rocm_w7900.json \
  -nIterLim 200
```

Runtime output summary:

```text
HIP runtime 71260610
HIP driver 71260610
hipSPARSE 400300
HIP device 0: AMD Radeon Graphics
```

Result summary:

| Field             |               Value |
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

GPU timing summary:

| Field                          |    Value |
| ------------------------------ | -------: |
| `AllocMem_CopyMatToDeviceTime` | 0.000337 |
| `CopyVecToDeviceTime`          | 0.000085 |
| `CopyVecToHostTime`            | 0.000000 |
| `DeviceMatVecProdTime`         | 0.040984 |
| `dSolvingTime`                 | 0.111312 |

## 8. CPU vs ROCm Result Comparison

| Metric            |                 CPU |          ROCm/W7900 |
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

The W7900 / `gfx1100` ROCm backend matches the CPU baseline termination state on the `afiro` smoke case, and the numerical differences are within a reasonable range for this first-port validation stage.

<!-- W7900_DOC_SWEEP_20260614_BEGIN -->
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
<!-- W7900_DOC_SWEEP_20260614_END -->

## 9. Known Limitations

This stage only completes first-port smoke validation. The following items are not completed yet:

* extended Netlib validation
* large MPS benchmark
* W7900 profiling
* W7900 single-GPU tuning
* 8-GPU concurrent throughput experiment
* cross-device benchmark matrix update

The current status should therefore be described as:

```text
W7900 / gfx1100 first-port smoke validation passed.
Extended validation and tuning are in progress.
```

It should not be described as a fully production-certified ROCm solver release.

## 10. Next Steps

Planned next steps:

1. Keep W7900 CPU/ROCm build scripts reproducible.
2. Update the README W7900 status description.
3. Run W7900 smoke validation through scripted workflows.
4. Run extended Netlib validation.
5. Profile W7900 single-GPU execution with ROCm profiling tools.
6. Tune the ROCm backend based on profiling evidence.
7. Run 8-GPU single-device sweep and multi-process throughput experiments.
8. Summarize the engineering and experimental results for the competition report.
