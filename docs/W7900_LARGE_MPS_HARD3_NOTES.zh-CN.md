# W7900 large-MPS hard3 记录

> English: [W7900_LARGE_MPS_HARD3_NOTES.md](W7900_LARGE_MPS_HARD3_NOTES.md)

本文记录为什么剩余 3 个 large-MPS case 要从 W7900 non-hard23 baseline 中单独拆出。

## Hard3 cases

- `dlr1.mps`
- `Dual2_5000.mps`
- `fhnw-binschedule1.mps`

## 当前策略

在完成单独的收敛轨迹分析前，这些 case 不应混入 W7900 主要 large-MPS baseline。

当前主 baseline 是：

- `initial17_safe`：17/17 `OPTIMAL`
- `watchlist6`：4/6 在 900 秒内达到 `OPTIMAL`
- `near_optimal2`：watchlist 剩余 2 个 case 在 1800 秒内达到 `OPTIMAL`
- 合并后的 `non-hard23`：23/23 `OPTIMAL`

## 为什么单独拆出 hard3

PDLP 总耗时同时取决于单次迭代开销和迭代次数：

```text
total time ≈ per-iteration cost × number of iterations
```

对于困难 LP/MPS 实例，GPU 单次迭代可能很快，但仍可能需要大量迭代，或出现 gap 轨迹不稳定。因此 hard3 应作为数值/收敛行为单独报告，而不是简单归为普通 benchmark failure。

## 后续用途

在 ROCm/gfx1100 调优前，hard3 只用于短时间诊断和收敛轨迹记录。等调优稳定后，再把 hard3 作为单独的最终压力测试组。
