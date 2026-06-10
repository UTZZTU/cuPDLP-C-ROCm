# Documentation validation links patch

Add this block to `docs/README.md` under the validation/benchmark section if not already present:

```markdown
## Validation data directory

| Topic / 主题 | English | 中文 | Raw CSV / 原始汇总 |
|---|---|---|---|
| validation directory index / validation 目录索引 | [../validation/README.md](../validation/README.md) | [../validation/README.zh-CN.md](../validation/README.zh-CN.md) | See validation index |
| current vs reduce repeated comparison | [../validation/rocm_current_vs_reduce_27cases_repeats_comparison.md](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.md) | [../validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md) | [comparison CSV](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.csv) |
| rocprof tuning milestones | [../validation/rocm_prof_tuning_milestones_summary.md](../validation/rocm_prof_tuning_milestones_summary.md) | [../validation/rocm_prof_tuning_milestones_summary.zh-CN.md](../validation/rocm_prof_tuning_milestones_summary.zh-CN.md) | [summary CSV](../validation/rocm_prof_tuning_milestones_summary.csv) |
| tuning ablation 6-case repeats | [../validation/rocm_tuning_ablation_6cases_repeats_summary.md](../validation/rocm_tuning_ablation_6cases_repeats_summary.md) | [../validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md](../validation/rocm_tuning_ablation_6cases_repeats_summary.zh-CN.md) | [summary CSV](../validation/rocm_tuning_ablation_6cases_repeats_summary.csv) |
```
