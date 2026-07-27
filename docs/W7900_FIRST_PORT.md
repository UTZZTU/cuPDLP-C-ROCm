# W7900 / gfx1100 First-Port Notes

<!-- DOCUMENT_STATUS_NOTICE_BEGIN -->
> **Historical first-port snapshot**
>
> This document records the initial W7900 bring-up state. It is preserved as migration evidence and does not represent the current endpoint. See [W7900 current status](W7900_CURRENT_STATUS.md).
<!-- DOCUMENT_STATUS_NOTICE_END -->

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

## 9. Known limitations and current completion status

This document is kept as the historical W7900 / `gfx1100` first-port smoke
milestone. The original first-port limitations have been superseded by later
W7900 validation and tuning documents:

* extended Netlib validation: completed.
* large MPS benchmark: non-hard23 baseline completed; hard3 tracked separately.
* W7900 profiling: P10 targeted rocprof archived.
* W7900 single-GPU tuning: P11 SpMV tuning completed, with current default
  `HIPSPARSE_SPMV_CSR_ALG1`.
* 8-GPU concurrent throughput experiment: fast8 batch throughput archived.
* cross-device benchmark matrix: curated summaries are available.

The project still should not be described as a production-certified ROCm
solver release, but it has moved beyond the first-port smoke stage. The
authoritative status is [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md).

## 10. Next-step status

The original next-step list is now mostly completed. The only remaining
optional enhancements are:

1. W7900 P14-A: current-vs-before representative repeated validation.
2. W7900 P14-B: CSR ALG1-vs-ALG2 representative repeated validation.

Deeper numerical-path optimization is not part of the current project endpoint.
