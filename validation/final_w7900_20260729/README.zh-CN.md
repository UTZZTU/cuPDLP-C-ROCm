# W7900 最终正式 compact evidence（2026-07-29）

> English: [README.md](README.md)
> 结果解释：[W7900 最终结果](../../docs/W7900_FINAL_RESULTS_20260729.zh-CN.md)

本目录保存最后一轮 W7900 正式实验的可提交 compact 数据。原始 MPS、raw
profiler trace、完整资源时间序列和大归档不进入 Git。

## 身份

```text
branch=rocm-w7900-gfx1100
solver=735764807d8698ff30811d1a6fcc45d4a3fd4817
harness=b5b9a6ffc1a041a48a0e051568d0134a3822556c
Window1=d2ce13091072a7c40c2c89bdd988e94c2fca36772da38e0af87de6332e7cd94a
Window2=7f8fbcd45591f4dbe0899d18df76329b1f9a17ff433b6dcd3c06d743aaead0db
```

## 正式覆盖

| 阶段 | 数量 | 状态 |
|---|---:|---|
| baseline23 | 46 | 46/46 `VALIDATED_OPTIMAL` |
| precision | 30 | 30/30 `VALIDATED_OPTIMAL` |
| profiles | 5 | 5/5 `PASS` |
| static features | 23 | 23/23 `PASS` |
| 正式 solver 合计 | 76 | 76/76 |

## 文件说明

### 身份与 QC

- `formal_experiment_identity.json`
- `formal_experiments_complete.json`
- `final_analysis_released.json`
- `window1_qc_summary.json`
- `window2_qc_summary.json`
- `static_feature_validation_report.json`
- `files.sha256`

### 基线

- `baseline_aggregated.csv`：23 例双重复聚合；
- `baseline_repeats.csv`：46 条重复级结果；
- `throughput_summary.csv`：完整两轮吞吐；
- `baseline_resource_summary.csv`：资源采样聚合。

### 目标精度

- `precision_matrix.csv`：30 条正式原始行；
- `precision_aggregated.csv`：15 个 case×tolerance 聚合点；
- `precision_sensitivity.csv`：`1e-5 / 1e-3` 成本倍率；
- `precision_resource_summary.csv`：资源采样聚合。

### Profiling

- `profile_summary.csv`：5/5 采集和 trace 完整性；
- 具体热点继续引用历史 P10 compact 表，raw trace 不提交。

### 静态结构与分析

- `nonhard23_mps_structural_features.csv`
- `nonhard23_feature_dictionary.csv`
- `static_performance_spearman.csv`
- `static_association_leave_one_out.csv`
- `final_claims_review.csv`
- `final_summary.csv`

## 快速验证

```bash
python3 ../../scripts/analysis/generate_final_w7900_release.py --check-only
```

预期：

```text
FINAL_W7900_RELEASE_DATA_PASS
```

## 关键边界

- 该目录是 compact evidence，不是 raw archive；
- 单卡 throughput 是顺序独立 MPS；
- precision 只覆盖五例；
- static correlation 是探索性；
- session2 profile summary 证明采集完整，不生成新的热点百分比；
- hard3 不属于本目录的正式 nonhard23 主矩阵。
