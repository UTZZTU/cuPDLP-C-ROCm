# W7900 rocprof starter3 summary

Result directory: `/app/cupdlp_w7900/results/w7900_rocprof/w7900_rocprof_starter3_20260616_172230_20260616_172230`

This is a compact summary of the W7900 `rocprof` starter3 run. Raw profiler trace files are intentionally not committed because they are large.

## Solver summary

| case | runtime_status | exit_code | wall_seconds | terminationCode | nIter | dSolvingTime | DeviceMatVecProdTime | dRelDualityGap |
|---|---|---|---|---|---|---|---|---|
| s100 | TIMEOUT | 124 | 1346.557205 | TIMELIMIT_OR_ITERLIMIT | 531801 | 900.001351 | 6.794763 | 0.00049412556371 |
| set-cover-model | DONE | 0 | 37.152275 | OPTIMAL | 7480 | 12.00398 | 0.206424 | 9.3551367e-06 |
| square41 | DONE | 0 | 153.478395 | OPTIMAL | 128360 | 114.964398 | 1.657856 | 9.463231177e-05 |

## Runtime summary

| case | status | exit_code | wall_seconds |
|---|---|---|---|
| set-cover-model.mps | DONE | 0 | 37.152275 |
| square41.mps | DONE | 0 | 153.478395 |
| s100.mps | TIMEOUT | 124 | 1346.557205 |

## Key interpretation

- `set-cover-model` and `square41` reached `OPTIMAL` under the profiling run.
- `s100` reached the solver time limit at about 900 seconds with relative duality gap around `4.94e-04`; its profiler stats files are available, but the external profiler wrapper ended with timeout code `124` during trace finalization.
- Raw HIP API and kernel trace files are large and should stay outside Git. Commit only the compact CSV and Markdown summaries.

## Top HIP API stats: `set-cover-model`

| rank | name | calls | total_ms | percentage | avg_us |
|---|---|---|---|---|---|
| 1 | hipMemcpy | 8289 | 10411.011801 | 84.49 | 1256.003354 |
| 2 | hipLaunchKernel | 116630 | 813.300736 | 6.60 | 6.973341 |
| 3 | hipMemcpyAsync | 13671 | 617.115003 | 5.01 | 45.140443 |
| 4 | hipGetDevice | 4 | 297.344889 | 2.41 | 74336.222250 |
| 5 | hipStreamSynchronize | 5925 | 126.014680 | 1.02 | 21.268300 |

## Top kernel stats: `set-cover-model`

| rank | name | calls | total_ms | percentage | avg_us |
|---|---|---|---|---|---|
| 1 | void rocsparse::csrmvn_general_kernel<256u, 32u, int, int, double, double, double, double, double>(bool, int, rocsparse::const_host_device_scalar<d... | 7943 | 4960.796325 | 47.42 | 624.549455 |
| 2 | void rocsparse::csrmvn_general_kernel<256u, 16u, int, int, double, double, double, double, double>(bool, int, rocsparse::const_host_device_scalar<d... | 7943 | 4200.934840 | 40.16 | 528.885162 |
| 3 | primal_grad_step_kernel(double*, double const*, double const*, double const*, double const*, double const*, double, int) | 7745 | 446.963966 | 4.27 | 57.710002 |
| 4 | movement_1_kernel(double*, double*, double const*, double const*, double const*, double const*, int) | 7745 | 376.417645 | 3.60 | 48.601374 |
| 5 | sum_kernel(double*, double const*, int) | 38725 | 98.193174 | 0.9386 | 2.535653 |

## Top HIP API stats: `square41`

| rank | name | calls | total_ms | percentage | avg_us |
|---|---|---|---|---|---|
| 1 | hipMemcpy | 136533 | 96806.169107 | 86.44 | 709.031290 |
| 2 | hipLaunchKernel | 1692265 | 6963.364678 | 6.22 | 4.114819 |
| 3 | hipMemcpyAsync | 220359 | 5925.914642 | 5.29 | 26.892093 |
| 4 | hipStreamSynchronize | 90471 | 1849.295051 | 1.65 | 20.440750 |
| 5 | hipGetDevice | 4 | 200.683344 | 0.1792 | 50170.836000 |

## Top kernel stats: `square41`

| rank | name | calls | total_ms | percentage | avg_us |
|---|---|---|---|---|---|
| 1 | void rocsparse::csrmvn_general_kernel<256u, 32u, int, int, double, double, double, double, double>(bool, int, rocsparse::const_host_device_scalar<d... | 266214 | 90660.106344 | 94.23 | 340.553488 |
| 2 | sum_kernel(double*, double const*, int) | 389661 | 928.453070 | 0.9650 | 2.382720 |
| 3 | __amd_rocclr_copyBuffer | 356874 | 891.721712 | 0.9269 | 2.498702 |
| 4 | movement_1_kernel(double*, double*, double const*, double const*, double const*, double const*, int) | 129887 | 738.915316 | 0.7680 | 5.688909 |
| 5 | primal_grad_step_kernel(double*, double const*, double const*, double const*, double const*, double const*, double, int) | 129887 | 527.450185 | 0.5482 | 4.060839 |

## Top HIP API stats: `s100`

| rank | name | calls | total_ms | percentage | avg_us |
|---|---|---|---|---|---|
| 1 | hipMemcpy | 558670 | 809796.597255 | 91.43 | 1449.507934 |
| 2 | hipMemcpyAsync | 904908 | 38038.540858 | 4.29 | 42.035810 |
| 3 | hipLaunchKernel | 6942818 | 28723.319251 | 3.24 | 4.137127 |
| 4 | hipStreamSynchronize | 373075 | 8020.967133 | 0.9056 | 21.499610 |
| 5 | __hipPopCallConfiguration | 6942818 | 413.029407 | 0.0466 | 0.059490 |

## Top kernel stats: `s100`

| rank | name | calls | total_ms | percentage | avg_us |
|---|---|---|---|---|---|
| 1 | void rocsparse::csrmvn_general_kernel<256u, 32u, int, int, double, double, double, double, double>(bool, int, rocsparse::const_host_device_scalar<d... | 545139 | 763301.913495 | 93.24 | 1400.196855 |
| 2 | void rocsparse::csrmvn_general_kernel<256u, 4u, int, int, double, double, double, double, double>(bool, int, rocsparse::const_host_device_scalar<do... | 545139 | 20675.814255 | 2.53 | 37.927601 |
| 3 | primal_grad_step_kernel(double*, double const*, double const*, double const*, double const*, double const*, double, int) | 531832 | 7133.498187 | 0.8714 | 13.413067 |
| 4 | movement_1_kernel(double*, double*, double const*, double const*, double const*, double const*, int) | 531832 | 6549.148768 | 0.8000 | 12.314319 |
| 5 | sum_kernel(double*, double const*, int) | 1595496 | 3937.567907 | 0.4810 | 2.467927 |
