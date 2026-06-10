# Documentation map / 文档地图

This page is the central index for project-maintained documentation.  
本页是项目维护文档的总索引，目的是避免文档存在但没有入口的问题。

## Main entry points / 主入口

| Topic / 主题 | English | 中文 | Notes / 说明 |
|---|---|---|---|
| Repository homepage / 仓库主页 | [../README.md](../README.md) | [../README.zh-CN.md](../README.zh-CN.md) | Main project overview |
| ROCm 890M quick README | [../README_ROCM_gfx1150.md](../README_ROCM_gfx1150.md) | [../README_ROCM_gfx1150.zh-CN.md](../README_ROCM_gfx1150.zh-CN.md) | Focused quick-start page for the gfx1150 milestone |
| Benchmark index / Benchmark 索引 | [benchmarks/README.md](benchmarks/README.md) | [benchmarks/README.md](benchmarks/README.md) | Benchmark docs and CSV links |
| Upstream reference / 上游参考 | [../README_UPSTREAM.md](../README_UPSTREAM.md) | — | Intentionally preserved as upstream snapshot; not translated |

## Workflow, validation, and build semantics / 工作流、验证与构建语义

| Topic / 主题 | English | 中文 |
|---|---|---|
| Daily ROCm workflow / 日常 ROCm 工作流 | [ROCM_WORKFLOW.md](ROCM_WORKFLOW.md) | [ROCM_WORKFLOW.zh-CN.md](ROCM_WORKFLOW.zh-CN.md) |
| Validation semantics / 验证语义 | [VALIDATION.md](VALIDATION.md) | [VALIDATION.zh-CN.md](VALIDATION.zh-CN.md) |
| Backend modes and naming / 后端模式与命名 | [BACKEND_MODES_AND_NAMING.md](BACKEND_MODES_AND_NAMING.md) | [BACKEND_MODES_AND_NAMING.zh-CN.md](BACKEND_MODES_AND_NAMING.zh-CN.md) |
| ROCm porting guide / ROCm porting 指南 | [ROCM_PORTING_GUIDE.md](ROCM_PORTING_GUIDE.md) | [ROCM_PORTING_GUIDE.zh-CN.md](ROCM_PORTING_GUIDE.zh-CN.md) |
| CUDA to ROCm case study / CUDA 到 ROCm 迁移案例 | [CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md) | [CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md](CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md) |

## Benchmarks and numerical behavior / Benchmark 与数值行为

| Topic / 主题 | English | 中文 | Raw data / 原始汇总数据 |
|---|---|---|---|
| Netlib cross-device benchmarks / Netlib 跨设备 benchmark | [CROSS_DEVICE_BENCHMARKS.md](CROSS_DEVICE_BENCHMARKS.md) | [CROSS_DEVICE_BENCHMARKS.zh-CN.md](CROSS_DEVICE_BENCHMARKS.zh-CN.md) | [validation/cross_device_summary.csv](../validation/cross_device_summary.csv) if present |
| Large MPS benchmark plan / large MPS benchmark 计划 | [LARGE_MPS_BENCHMARK_PLAN.md](LARGE_MPS_BENCHMARK_PLAN.md) | [LARGE_MPS_BENCHMARK_PLAN.zh-CN.md](LARGE_MPS_BENCHMARK_PLAN.zh-CN.md) | See benchmark docs below |
| Large MPS CUDA/ROCm baseline / large MPS CUDA/ROCm baseline | [benchmarks/large_mps_cuda_rocm_baseline_20260610.md](benchmarks/large_mps_cuda_rocm_baseline_20260610.md) | [benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md](benchmarks/large_mps_cuda_rocm_baseline_20260610.zh-CN.md) | [platform summary](../results/benchmarks/large_mps_platform_summary_20260610.csv), [per-case timing](../results/benchmarks/large_mps_per_case_timing_summary_20260610.csv) |
| cuPDLPx vs cuPDLP-C short13 / cuPDLPx 对比 | [benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md](benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.md) | [benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md](benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.zh-CN.md) | [comparison CSV](../results/benchmarks/cupdlpx_vs_cupdlp_c_4090d_short13_20260610.csv) |
| greenbea numerical behavior / greenbea 数值行为 | [NUMERICAL_BEHAVIOR_GREENBEA.md](NUMERICAL_BEHAVIOR_GREENBEA.md) | [NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md](NUMERICAL_BEHAVIOR_GREENBEA.zh-CN.md) | Case-specific notes |

## Profiling and tuning / Profiling 与调优

| Topic / 主题 | English | 中文 |
|---|---|---|
| ROCm profiling notes / ROCm profiling 记录 | [ROCM_PROFILING_NOTES.md](ROCM_PROFILING_NOTES.md) | [ROCM_PROFILING_NOTES.zh-CN.md](ROCM_PROFILING_NOTES.zh-CN.md) |
| ROCm tuning history / ROCm tuning 历史 | [ROCM_TUNING_HISTORY.md](ROCM_TUNING_HISTORY.md) | [ROCM_TUNING_HISTORY.zh-CN.md](ROCM_TUNING_HISTORY.zh-CN.md) |
| ROCm tuning guide / ROCm tuning 指南 | [TUNING_GUIDE_ROCM.md](TUNING_GUIDE_ROCM.md) | [TUNING_GUIDE_ROCM.zh-CN.md](TUNING_GUIDE_ROCM.zh-CN.md) |

## Maintenance rules / 维护规则

- Keep `README.md`, `README.zh-CN.md`, and this file as the main navigation hubs.
- Benchmark documents should link to their CSV files.
- If an English project document is updated, update the matching Chinese document.
- If a Chinese project document is updated first, update the matching English document.
- Keep `README_UPSTREAM.md` as an upstream reference snapshot.
