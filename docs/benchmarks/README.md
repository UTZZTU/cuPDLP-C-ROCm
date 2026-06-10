# Benchmark documents / Benchmark 文档索引

This directory collects curated benchmark explanation documents.  
本目录保存整理后的 benchmark 解释文档。原始大规模 `.mps` 文件不提交；CSV 汇总保存在 `results/benchmarks/`。

## Baseline documents / Baseline 文档

| Topic / 主题 | English | 中文 | Raw CSV / 原始汇总 |
|---|---|---|---|
| Large MPS CUDA/ROCm baseline | [large_mps_cuda_rocm_baseline_20260610.md](large_mps_cuda_rocm_baseline_20260610.md) | [large_mps_cuda_rocm_baseline_20260610.zh-CN.md](large_mps_cuda_rocm_baseline_20260610.zh-CN.md) | [platform summary](../../results/benchmarks/large_mps_platform_summary_20260610.csv), [per-case timing](../../results/benchmarks/large_mps_per_case_timing_summary_20260610.csv) |

## Solver comparison documents / Solver 对比文档

| Topic / 主题 | English | 中文 | Raw CSV / 原始汇总 |
|---|---|---|---|
| cuPDLPx vs cuPDLP-C, RTX 4090D short13 | [cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md](cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md) | [cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md](cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md) | [comparison CSV](../../results/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.csv) |

## Interpretation policy / 解释口径

- cuPDLP-C CUDA/ROCm baseline results describe the current migration baseline.
- cuPDLPx results are a separate solver/algorithm comparison and should not be mixed into the cuPDLP-C ROCm baseline without explanation.
- If a benchmark document cites derived metrics, it must link to the CSV used to compute those metrics.
- If a Chinese or English benchmark document is updated, update the counterpart document in the same commit.
