# Cross-device benchmark notes

This document summarizes the current cross-device benchmark workflow for the ROCm/HIP port of cuPDLP-C.

## Goal

The goal is to compare the upstream CUDA baseline and the ROCm/HIP port using the same LP case list and the same high-level solver settings.

The benchmark matrix covers:

* RTX 3090, upstream cuPDLP-C CUDA baseline
* RTX 4090D, upstream cuPDLP-C CUDA baseline
* AMD Radeon 890M / gfx1150, cuPDLP-C-ROCm

Each device records both local CPU and GPU/ROCm runs.

## Benchmark setup

Common settings:

* Case source: Netlib MPS cases plus `afiro`, `sc50b`, and `lotfi`
* Iteration limit: `nIterLim = 200000000`
* Per-run wall-clock timeout: `3600s`
* HiGHS version: 1.6.0
* Main comparison fields:

  * termination status
  * iteration count
  * solve time
  * relative primal feasibility
  * relative dual feasibility
  * relative duality gap
  * GPU timing breakdown where available

Large raw result directories, downloaded MPS files, and tar archives are kept as local artifacts and are not intended to be committed to Git.

## Summary

| Device             |                                   CPU result | GPU/ROCm result | Notes                                                      |
| ------------------ | -------------------------------------------: | --------------: | ---------------------------------------------------------- |
| RTX 3090 / CUDA    | 28/28 OPTIMAL after greenbea 200M supplement |   27/28 OPTIMAL | greenbea CUDA reached the solver internal 3600s time limit |
| RTX 4090D / CUDA   |                                28/28 OPTIMAL |   27/28 OPTIMAL | greenbea CUDA hit the external 3600s timeout               |
| Radeon 890M / ROCm |                                28/28 OPTIMAL |   27/28 OPTIMAL | greenbea ROCm hit the external 3600s timeout               |

## Interpretation

The benchmark shows that the ROCm/HIP port is functionally capable of solving the shared benchmark set on Radeon 890M. Except for `greenbea`, all tested ROCm cases reached `OPTIMAL`.

The small cases are usually slower on GPU/ROCm than on CPU. This is expected because the GPU path pays extra overhead from device initialization, kernel launches, synchronization, and vector update operations. This behavior is also visible in the upstream CUDA baselines, so small-case slowdown should not be interpreted as a ROCm-specific failure.

Some larger or more GPU-friendly cases show GPU advantage. For example, on RTX 4090D, cases such as `80bau3b`, `fit2d`, `greenbeb`, `maros-r7`, and `pilot87` are faster on CUDA than on CPU. On Radeon 890M, cases such as `80bau3b` and `maros-r7` are close to or faster than CPU.

The `greenbea` case should be kept as a convergence-sensitive case. On RTX 3090, the CPU run reached `OPTIMAL` in the 200M supplement, while CUDA reached the solver internal 3600s time limit with `TIMELIMIT_OR_ITERLIMIT`. This demonstrates that the difficult GPU convergence behavior is already present in the upstream CUDA backend. Therefore, the `greenbea` timeout on RTX 4090D and Radeon 890M should be documented as a backend numerical trajectory / convergence sensitivity issue rather than a ROCm porting failure.

## Current conclusion

The current ROCm/HIP port has passed the cross-device functional benchmark stage on Radeon 890M / gfx1150. The implementation is still not a performance-tuned ROCm solver. The next stage should focus on profiling and optimization of the ROCm backend, especially:

* reducing launch and synchronization overhead on small cases
* improving GPU update kernels
* analyzing sparse matvec performance
* studying convergence-sensitive cases such as `greenbea`
* expanding automated validation and benchmark reporting
