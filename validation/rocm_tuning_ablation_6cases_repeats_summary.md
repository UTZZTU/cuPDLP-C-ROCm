# ROCm tuning ablation 6-case repeated summary

Run dir: `/home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/validation/results/tuning_ablation_6cases_repeats_20260607_211933`

Primary metric: median solve time across repeated runs.

## Milestones

| milestone | commit | meaning |
|---|---|---|
| cache_attrs | `8fed073` | cache HIP device attributes |
| current | `c65a20083d8e03ca167164f4142a5c58f863ffbb` | current HEAD |
| fused_average | `fa7e860` | fuse ROCm average iterate axpy updates |
| pre_tuning | `ae3b683` | pre-tuning baseline |
| reduce_scalar_copies | `b44c7ab` | reduce movement interaction scalar copies |
| remove_sync | `f9d7f0d` | remove redundant HIP device synchronize |

## Median solve time by tuning milestone

| milestone | afiro | sc50b | lotfi | 80bau3b | maros-r7 | pilot87 |
|---|---:|---:|---:|---:|---:|---:|
| cache_attrs | 0.06028 | 0.069627 | 3.986371 | 0.912363 | 0.117736 | 8.218034 |
| current | 0.0529 | 0.066839 | 3.646848 | 0.874944 | 0.121077 | 7.820457 |
| fused_average | 0.05314 | 0.069351 | 3.825229 | 0.90184 | 0.117184 | 8.000284 |
| pre_tuning | 0.052744 | 0.072827 | 4.537407 | 0.970653 | 0.124608 | 8.690948 |
| reduce_scalar_copies | 0.052801 | 0.066655 | 3.61529 | 0.869338 | 0.116324 | 7.820215 |
| remove_sync | 0.059098 | 0.071003 | 3.997434 | 0.91549 | 0.120013 | 8.179166 |

## Mean solve time by tuning milestone

| milestone | afiro | sc50b | lotfi | 80bau3b | maros-r7 | pilot87 |
|---|---:|---:|---:|---:|---:|---:|
| cache_attrs | 0.0584082 | 0.0706474 | 3.9881558 | 0.9149718 | 0.120286 | 8.2111882 |
| current | 0.0532954 | 0.0694806 | 3.6383716 | 0.8775436 | 0.1215804 | 7.8135036 |
| fused_average | 0.056253 | 0.0706036 | 3.8154068 | 0.9009322 | 0.1185348 | 7.9954642 |
| pre_tuning | 0.0527388 | 0.0760864 | 4.5333052 | 0.9658306 | 0.1241038 | 8.675136 |
| reduce_scalar_copies | 0.0526232 | 0.0657898 | 3.6195412 | 0.8695778000000001 | 0.1198684 | 7.8037468 |
| remove_sync | 0.059706 | 0.0745364 | 4.0018926 | 0.917134 | 0.1185098 | 8.184247000000001 |

## CV of solve time by tuning milestone

| milestone | afiro | sc50b | lotfi | 80bau3b | maros-r7 | pilot87 |
|---|---:|---:|---:|---:|---:|---:|
| cache_attrs | 0.11000049030372262 | 0.048951905584750204 | 0.0046095446434982305 | 0.009798597151144523 | 0.04958685490801539 | 0.00467830925238153 |
| current | 0.030558418365031665 | 0.10072950448296773 | 0.010165894295982742 | 0.009827905950920632 | 0.07006894223612423 | 0.005286862407476883 |
| fused_average | 0.16019950841242836 | 0.06628176950531578 | 0.005524964805187489 | 0.010715874564387873 | 0.028433330191367113 | 0.003244921549080023 |
| pre_tuning | 0.029592005982480935 | 0.0823528079414532 | 0.00801815273354516 | 0.01010947745077386 | 0.018821420935992393 | 0.007063009322609298 |
| reduce_scalar_copies | 0.025580635756000895 | 0.021296234611384395 | 0.010714028151496585 | 0.001844547032721013 | 0.0724504274222668 | 0.004734014488806523 |
| remove_sync | 0.12030852947518138 | 0.09486799490307637 | 0.005270775906675435 | 0.006265244540678379 | 0.024825614724948698 | 0.00286879150786513 |

## Median DeviceMatVecProdTime by tuning milestone

| milestone | afiro | sc50b | lotfi | 80bau3b | maros-r7 | pilot87 |
|---|---:|---:|---:|---:|---:|---:|
| cache_attrs | 0.022485 | 0.020762 | 0.224449 | 0.043925 | 0.020229 | 0.242991 |
| current | 0.020111 | 0.021583 | 0.233689 | 0.047721 | 0.020473 | 0.222489 |
| fused_average | 0.019422 | 0.022065 | 0.220678 | 0.047636 | 0.020546 | 0.233992 |
| pre_tuning | 0.019731 | 0.021287 | 0.283484 | 0.050591 | 0.01983 | 0.262654 |
| reduce_scalar_copies | 0.020542 | 0.020963 | 0.218564 | 0.046652 | 0.020861 | 0.231445 |
| remove_sync | 0.020783 | 0.022891 | 0.235519 | 0.042941 | 0.019717 | 0.226007 |
