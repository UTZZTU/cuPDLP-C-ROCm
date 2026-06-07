# Cross-device benchmark notes

This document summarizes the current cross-device benchmark workflow for the ROCm/HIP port of cuPDLP-C.

## Goal

The CUDA backend is retained in this repository as the upstream-compatible NVIDIA baseline. The ROCm/HIP backend is the AMD target backend. This makes the benchmark matrix a three-mode comparison rather than a CPU-vs-ROCm-only workflow.

The goal is to compare the upstream CUDA baseline and the ROCm/HIP port using the same LP case list and the same high-level solver settings.

The benchmark matrix covers:

* RTX 3090, upstream cuPDLP-C CUDA baseline
* RTX 4090D, upstream cuPDLP-C CUDA baseline
* AMD Radeon 890M / gfx1150, cuPDLP-C-ROCm

Each device records both local CPU and GPU/ROCm runs.

## Benchmark setup

Common settings:

| Setting                    | Value                                               |
| -------------------------- | --------------------------------------------------- |
| Case source                | Netlib MPS cases plus `afiro`, `sc50b`, and `lotfi` |
| Iteration limit            | `nIterLim = 200000000`                              |
| Per-run wall-clock timeout | `3600s`                                             |
| HiGHS version              | 1.6.0                                               |
| Result style               | local CPU + GPU/ROCm runs on each device            |

Main comparison fields:

* termination status,
* iteration count,
* solve time,
* relative primal feasibility,
* relative dual feasibility,
* relative duality gap,
* GPU timing breakdown where available.

Large raw result directories, downloaded MPS files, and tar archives are kept as local artifacts and are not intended to be committed to Git.

## Device-level status

| Device             |                                     CPU result | GPU/ROCm result | Exception                                           |
| ------------------ | ---------------------------------------------: | --------------: | --------------------------------------------------- |
| RTX 3090 / CUDA    | 28/28 OPTIMAL after `greenbea` 200M supplement |   27/28 OPTIMAL | `greenbea` CUDA reached solver internal 3600s limit |
| RTX 4090D / CUDA   |                                  28/28 OPTIMAL |   27/28 OPTIMAL | `greenbea` CUDA hit external 3600s timeout          |
| Radeon 890M / ROCm |                                  28/28 OPTIMAL |   27/28 OPTIMAL | `greenbea` ROCm hit external 3600s timeout          |

## Representative performance cases

| Case       | RTX 3090 CPU / CUDA time | RTX 4090D CPU / CUDA time | Radeon 890M CPU / ROCm time | Notes                                           |
| ---------- | -----------------------: | ------------------------: | --------------------------: | ----------------------------------------------- |
| `afiro`    |    0.000581s / 0.035574s |     0.000228s / 0.033316s |       0.000223s / 0.055775s | Tiny case; GPU overhead dominates               |
| `sc50b`    |    0.002908s / 0.066647s |     0.000761s / 0.058011s |       0.000703s / 0.066212s | Tiny case; GPU overhead dominates               |
| `lotfi`    |    0.721584s / 7.221900s |     0.541828s / 6.371220s |       0.339811s / 3.587740s | GPU path slower despite convergence             |
| `80bau3b`  |    1.941090s / 1.058330s |     1.675210s / 0.873151s |       0.908968s / 0.887086s | GPU/ROCm becomes competitive                    |
| `fit2d`    |    1.824550s / 0.430777s |     1.981560s / 0.376708s |       1.004250s / 1.187790s | CUDA clearly faster; 890M ROCm close but slower |
| `greenbeb` |      117.688s / 81.6909s |       103.155s / 72.3501s |         54.0035s / 152.025s | CUDA faster; ROCm slower on 890M                |
| `maros-r7` |    0.277859s / 0.074724s |     0.289098s / 0.061516s |       0.157686s / 0.116644s | GPU/ROCm faster or competitive                  |
| `pilot87`  |      15.3384s / 7.98787s |       14.9857s / 8.00709s |         7.69941s / 7.91001s | CUDA faster; ROCm roughly tied                  |

## Cases where GPU/ROCm is faster than CPU

| Device             | Faster GPU/ROCm cases                                                                         |
| ------------------ | --------------------------------------------------------------------------------------------- |
| RTX 3090 / CUDA    | `80bau3b`, `fit2d`, `greenbea` in 5M iteration-limited run, `greenbeb`, `maros-r7`, `pilot87` |
| RTX 4090D / CUDA   | `80bau3b`, `fit2d`, `greenbeb`, `maros-r7`, `pilot87`                                         |
| Radeon 890M / ROCm | `80bau3b`, `maros-r7`                                                                         |

## `greenbea` convergence-sensitive behavior

| Device             | CPU result                                             | GPU/ROCm result                                                      | Interpretation                                                          |
| ------------------ | ------------------------------------------------------ | -------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| RTX 3090 / CUDA    | CPU reached OPTIMAL in 1286.92s in the 200M supplement | CUDA reached solver internal 3600s time limit after 41.6M iterations | Upstream CUDA already shows GPU convergence sensitivity                 |
| RTX 4090D / CUDA   | CPU reached OPTIMAL in 1178.48s                        | CUDA hit external 3600s timeout before writing JSON                  | Same difficult case on a newer CUDA GPU                                 |
| Radeon 890M / ROCm | CPU reached OPTIMAL in 592.58s                         | ROCm hit external 3600s timeout before writing JSON                  | Should be tracked as convergence-sensitive, not as a ROCm build failure |

## Interpretation

The benchmark shows that the ROCm/HIP port is functionally capable of solving the shared benchmark set on Radeon 890M. Except for `greenbea`, all tested ROCm cases reached `OPTIMAL`.

The small cases are usually slower on GPU/ROCm than on CPU. This is expected because the GPU path pays extra overhead from device initialization, kernel launches, synchronization, and vector update operations. This behavior is also visible in the upstream CUDA baselines, so small-case slowdown should not be interpreted as a ROCm-specific failure.

Some larger or more GPU-friendly cases show GPU advantage. For example, on RTX 4090D, cases such as `80bau3b`, `fit2d`, `greenbeb`, `maros-r7`, and `pilot87` are faster on CUDA than on CPU. On Radeon 890M, cases such as `80bau3b` and `maros-r7` are close to or faster than CPU.

The `greenbea` case should be kept as a convergence-sensitive case. On RTX 3090, the CPU run reached `OPTIMAL` in the 200M supplement, while CUDA reached the solver internal 3600s time limit with `TIMELIMIT_OR_ITERLIMIT`. This demonstrates that the difficult GPU convergence behavior is already present in the upstream CUDA backend. Therefore, the `greenbea` timeout on RTX 4090D and Radeon 890M should be documented as a backend numerical trajectory / convergence sensitivity issue rather than a ROCm porting failure.

## Current conclusion

The current ROCm/HIP port has passed the cross-device functional benchmark stage on Radeon 890M / gfx1150. The implementation is still not a performance-tuned ROCm solver. The next stage should focus on profiling and optimization of the ROCm backend, especially:

* reducing launch and synchronization overhead on small cases,
* improving GPU update kernels,
* analyzing sparse matvec performance,
* studying convergence-sensitive cases such as `greenbea`,
* expanding automated validation and benchmark reporting.

## Files

The benchmark workflow uses:

```text
validation/cases_benchmark_200m.txt
scripts/run_benchmark_890m_full.sh
scripts/summarize_benchmark.py
validation/cross_device_summary.csv
```

The following are local generated artifacts and should not be committed:

```text
validation/netlib/
validation/results/
*.tar.gz
```
