# ROCm Tuning Guide

This document records profiling and tuning notes for the ROCm/HIP port of cuPDLP-C.

The current verified target is:

- AMD Radeon 890M
- `gfx1150`
- ROCm 7.2.1

## Current status

The current ROCm/HIP version builds and runs `example/afiro.mps`.

No performance tuning has been completed yet.

The current priority is:

1. correctness
2. validation coverage
3. profiling
4. tuning

## Why tuning is needed

PDLP relies heavily on sparse matrix-vector products and vector operations.

Important operations include:

- `Ax`
- `Aty`
- hipSPARSE SpMV
- vector updates
- reductions
- projection kernels
- host/device synchronization
- memory allocation and data transfer

Small cases such as `afiro.mps` are useful for correctness validation, but they are too small to represent real GPU performance.

## Profiling targets

Solver-level metrics:

- total solve time
- iteration count
- iterations per second
- `Ax` time
- `Aty` time
- device matrix-vector product time
- memory allocation and copy time

Runtime-level metrics:

- HIP kernel launch count
- HIP memory copy time
- HIP synchronization overhead
- hipSPARSE SpMV time
- hipBLAS vector operation time

Kernel-level metrics:

- occupancy
- memory bandwidth
- wavefront behavior
- reduction overhead
- register usage
- LDS usage, if applicable

## Recommended profiling tools

Recommended ROCm tools:

- `rocprof`
- `rocprofv3`
- ROCprofiler-SDK
- `rocm-smi`

Exact profiling commands will be added after the validation suite is stable.

## General ROCm tuning direction

For integrated GPUs and APUs:

- reduce unnecessary host/device copies
- avoid excessive synchronization
- prefer reusing device buffers
- watch shared memory bandwidth pressure
- avoid overinterpreting very small benchmark cases

For discrete GPUs:

- reduce PCIe transfers
- batch small kernels where possible
- reduce kernel launch overhead
- profile sparse matrix-vector product performance
- keep data resident on device across iterations

For all ROCm GPUs:

- validate correctness before tuning
- profile before changing kernels
- tune SpMV and reductions first
- compare CPU and ROCm outputs with tolerances
- avoid architecture-specific assumptions unless documented

## gfx1150-specific notes

TBD.

Items to investigate:

- HIP wavefront behavior
- shuffle/reduction performance
- sparse matrix-vector performance
- block size choices
- memory copy overhead on AMD Radeon 890M
- interaction between APU shared memory and solver performance

## TODO

- Add first `rocprof` command
- Add profiling output example
- Add analysis of `afiro.mps`
- Add analysis of larger MPS cases
- Add recommended tuning parameters
- Add per-architecture notes
