# cuPDLPx vs cuPDLP-C: RTX 4090D short13 comparison

Date: 2026-06-10  
Platform: RTX 4090D, physical GPU 2  
Dataset: 13 short/medium representative cases selected from the 26 large MPS benchmark set.

## Context

cuPDLP-C is the main baseline and ROCm/HIP porting target in this repository. cuPDLPx is a newer GPU LP solver from MIT-Lu-Lab based on restarted Halpern PDHG with additional practical improvements. This short13 experiment checks whether cuPDLPx shows enough practical advantage on our MPS set to justify further evaluation.

## Configuration

cuPDLP-C source result:

```text
run_dir = /home/omnisky/cuPDLP-C/test_data_large_mps/large_mps_4090_upstream_26cases_niter1b_dtimelim7200_20260610_162424
nIterLim = 1000000000
dTimeLim = 7200
external timeout = 7500s
```

cuPDLPx source result:

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

The original cuPDLPx script's `status_guess/time_guess/gap_guess` fields were broad grep guesses and are not used for conclusions. This document uses the final `Solution Summary` block in each `logs/*_cupdlpx.log` file.

## Summary

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

## Per-case performance comparison

`solve speedup` and `wall speedup` are `cuPDLP-C time / cuPDLPx time`; values above 1 mean cuPDLPx is faster.

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

## cuPDLPx solution quality

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

## Preliminary conclusion

cuPDLPx solved all 13 short/medium cases. It is faster than cuPDLP-C on 10/13 cases by solver time, with a median solve-time speedup of about 1.55x and a geometric mean solve-time speedup of about 1.60x. It is also faster on 10/13 cases by wall time, although small-case wall time is affected by presolve, I/O, and startup overhead.

These results justify further evaluation of cuPDLPx as a future algorithmic direction, but they do not replace the cuPDLP-C ROCm migration baseline. cuPDLPx should next be tested on the larger cases before any porting decision is made.
