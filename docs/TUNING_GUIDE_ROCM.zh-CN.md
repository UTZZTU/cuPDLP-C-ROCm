# ROCm 调优指南

> English: [TUNING_GUIDE_ROCM.md](TUNING_GUIDE_ROCM.md)

本文说明如何在不削弱数值可靠性的前提下调优 ROCm/HIP 后端。内容反映已经完成的 890M 与 W7900 证据，不再把旧计划写成当前任务。

## 当前平台策略

| 项目 | 当前值 |
|---|---|
| 主要 ROCm 分支 | `rocm-w7900-gfx1100` |
| 主要 ROCm 平台 | Radeon PRO W7900 / `gfx1100` |
| 早期调优里程碑 | Radeon 890M / `gfx1150` |
| 当前 SpMV 默认 | `HIPSPARSE_SPMV_CSR_ALG1` |
| 回退 | `CUPDLP_HIP_SPMV_ALG=csr_alg2` |
| 主要可执行文件 | `plc` |

该后端仍属于研究和工程验证路径，不是生产级认证求解器发行版。

## 核心规则

一个性能 patch 只有在以下三个问题都有可靠答案时才可接受：

1. 输出是否仍然有效？
2. 收敛轨迹是否足够稳定？
3. 代表性 case 上的加速是否可重复？

只看 kernel 时间不够。

## 为什么求解器调优不同

端到端求解时间近似为：

```text
solve time ≈ per-iteration cost × iteration count
```

每次迭代更快，可能被更多迭代抵消。浮点顺序、reduction、sparse-library policy 和 synchronization 都可能影响 PDHG 路径。

必须同时记录：

- termination status；
- primal/dual feasibility；
- relative gap；
- `nIter`；
- wall/solve time；
- 代表性 profiler metrics。

## 固定 baseline

修改前记录：

```bash
git rev-parse HEAD
git status
```

固定并保存：

- before commit；
- 相同 case list；
- iteration 与 timeout limits；
- environment variables；
- compiler 与 ROCm versions；
- GPU architecture；
- warm-up 与 repeat counts。

W7900 before/current 比较应使用 `ae3b683 / pre_tuning` 作为真正 before anchor。不能把当前 post-890M-tuning 分支写成“未优化 baseline”。

## 验证阶梯

| 修改类型 | 必要证据 |
|---|---|
| 文档或命名 | Markdown/link 检查 |
| Runtime query 或 setup cleanup | Smoke 与代表性验证 |
| Copy、同步或 launch 修改 | Smoke、Netlib subset、重复计时 |
| Sparse/BLAS algorithm policy | Smoke、targeted cases、iteration/residual 检查、rollback |
| Reduction 或算法相关代码 | Broad validation 与 trajectory diagnostics |
| 新架构 | Fresh build、smoke、代表性 large cases、profiling |

当修改可能影响操作顺序或浮点 reduction 时，应提高验证等级。

## Profiling workflow

W7900 targeted 入口：

```bash
bash scripts/run_w7900_p10_current_targeted_rocprof.sh
```

P10 cases：

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

通用 smoke profiling：

```bash
RESULT_ROOT=profiling/results/current \
  bash scripts/profile_rocm_smoke.sh
```

Raw traces 不进入 Git，只提交 compact tables 与解释。

## 根据证据选择 patch

好的 first patch 应：

- 局部；
- 可回退；
- 易验证；
- 来自已测热点；
- 尽量不改变数学语义。

890M sequence 遵循该原则，先减少同步、稳定 runtime query、重复 AXPY launch 和 scalar copy，再考虑更深层 kernel 修改。

W7900 P10 识别出 SpMV 主要热点，因此 P11 比较 hipSPARSE 已支持的算法，而不是直接整体替换 hipSPARSE。

## 当前 SpMV switch

| 模式 | 配置 |
|---|---|
| 当前默认 | 不设置环境变量；`HIPSPARSE_SPMV_CSR_ALG1` |
| 回退旧策略 | `CUPDLP_HIP_SPMV_ALG=csr_alg2` |
| 尝试 library default | `CUPDLP_HIP_SPMV_ALG=default` |

示例：

```bash
CUPDLP_HIP_SPMV_ALG=csr_alg2 \
  ./build-rocm-w7900/bin/plc \
  -fname /path/to/case.mps \
  -out /tmp/case.json \
  -nIterLim 200000000
```

日志与结果 metadata 中应保留环境设置。

## 正确做重复计时

性能结论应：

1. 使用相同 binary/case configuration；
2. 必要时先 warm-up；
3. 收集多个 measured repeats；
4. 报告 median 或 geomean speedup；
5. 展示 per-case 结果，而不只展示 aggregate；
6. 核对迭代数与数值字段。

P14-A1 是当前模板：quick6 repeated current-vs-pre-tuning，current 6/6 胜出，geomean 1.18889，median 1.19502，迭代数不变。

## 拒绝标准

以下情况应拒绝或暂缓 patch：

- status 改变；
- feasibility/gap 超出验证合同；
- 迭代数变化且缺少合理解释与足够收益；
- repeats 中加速不稳定；
- 小 case 加速但代表性 large case 退化；
- 平台敏感 policy 没有 rollback；
- profiler 证据不能支持 patch 动机。

P12 是标准 negative example：buffer-algorithm consistency 修改让 `set-cover-model` 从 7480 变为 7600 iterations，因此被拒绝。

## 记录要求

每个接受或拒绝的实验应记录：

```text
before reference
after reference
平台与软件环境
case list 与 limits
status 与数值比较
iteration counts
timing repeats
profiler evidence
decision
rollback method
```

Raw run directories 保留在 Git 外，只提交 curated CSV/Markdown summaries。

## 当前终点与可选工作

当前 W7900 tuning 证据链已经完成：

- P10 targeted profiling；
- P11 accepted SpMV policy；
- P12 rejected execution-layer experiment；
- P14-A1 repeated before/current confirmation。

未来工作应回答明确的新问题，例如 repeated ALG1-vs-ALG2、reduction-path profiling、scalar-readback analysis 或新 AMD 架构验证。它们是增强项，不是未完成的核心范围。

## 相关文档

- [ROCm profiling 记录](ROCM_PROFILING_NOTES.zh-CN.md)
- [ROCm 调优历史](ROCM_TUNING_HISTORY.zh-CN.md)
- [验证语义](VALIDATION.zh-CN.md)
- [W7900 当前状态](W7900_CURRENT_STATUS.zh-CN.md)
