# W7900 8-card fast8 批处理吞吐摘要

8 卡并发结果目录：`/app/cupdlp_w7900/results/w7900_8card_batch_fast8_rocr_only_900s_fast8_rocr_only_20260616_191934`
单 GPU 顺序结果目录：`/app/cupdlp_w7900/results/w7900_single_gpu_sequential_fast8_900s_fast8_seq_gpu0_20260616_192355`

本文是 W7900 independent-MPS batch throughput 实验的 compact summary。实验对比了 8 个独立 MPS case 在 8 张 W7900 上并发运行，与同一组 8 个 case 在单张 W7900 上顺序运行的总完成时间。

## Case list

- `set-cover-model.mps`
- `square41.mps`
- `thk_48.mps`
- `tpl-tub-ws1617.mps`
- `L2CTA3D.mps`
- `rmine15.mps`
- `qap15.mps`
- `graph40-40.mps`

## 吞吐摘要

| 指标 | 数值 |
|---|---:|
| 8 卡并发 makespan 秒数 | 146 |
| 单 GPU 顺序 makespan 秒数 | 558 |
| makespan speedup | 3.821918x |
| 8 卡效率 | 0.477740 |
| 并发 cases per hour | 197.260274 |
| 顺序 cases per hour | 51.612903 |

## 单 case 对比

| case | concurrent_gpu | concurrent_status | sequential_status | concurrent_wall_seconds | sequential_wall_seconds | concurrent_termination | sequential_termination |
|---|---|---|---|---|---|---|---|
| L2CTA3D | 4 | DONE | DONE | 93 | 75 | OPTIMAL | OPTIMAL |
| graph40-40 | 7 | DONE | DONE | 4 | 5 | OPTIMAL | OPTIMAL |
| qap15 | 6 | DONE | DONE | 1 | 1 | OPTIMAL | OPTIMAL |
| rmine15 | 5 | DONE | DONE | 31 | 31 | OPTIMAL | OPTIMAL |
| set-cover-model | 0 | DONE | DONE | 38 | 46 | OPTIMAL | OPTIMAL |
| square41 | 1 | DONE | DONE | 123 | 126 | OPTIMAL | OPTIMAL |
| thk_48 | 2 | DONE | DONE | 146 | 155 | OPTIMAL | OPTIMAL |
| tpl-tub-ws1617 | 3 | DONE | DONE | 123 | 119 | OPTIMAL | OPTIMAL |

## 结果解释

- 8 卡并发运行和单 GPU 顺序运行都在 8 个 case 上达到 `OPTIMAL`。
- 实测 batch makespan 从 `558s` 降到 `146s`，对应 `3.82x` 的 makespan speedup。
- 这说明 8x W7900 节点适合面向独立 LP/MPS 工作负载的批处理吞吐场景。
- 这是 independent-task throughput 结果，不表示单个 MPS 实例被 8 张 GPU 联合加速。
- GPU 绑定使用 `ROCR_VISIBLE_DEVICES` only；此前同时设置 HIP 和 ROCR visibility filter 的尝试失败，不作为正式结果总结。

## 仓库策略

只提交 compact CSV 和 Markdown summary。raw large-MPS 文件和大型运行目录保存在 Git 外部。
