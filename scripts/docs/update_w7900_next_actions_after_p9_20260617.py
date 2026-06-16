#!/usr/bin/env python3
from pathlib import Path
import re
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

REPL = {
    "docs/W7900_CURRENT_STATUS.md": dedent("""
        ## Next actions

        The P2--P9 W7900 validation, profiling, batch-throughput, and derived-metric
        summaries are now committed. The next stage should move from evidence
        collection to W7900-specific tuning triage:

        1. Use the derived fast-core6 metrics to investigate why `L2CTA3D`,
           `set-cover-model`, and `tpl-tub-ws1617` require more iterations under
           current even though ms/iter improved.
        2. Run targeted profiling only on representative cases rather than expanding
           the benchmark matrix blindly:
           - positive execution sample: `thk_48`
           - stable iteration-count sample: `square41`
           - convergence-regression samples: `L2CTA3D`, `set-cover-model`,
             `tpl-tub-ws1617`
        3. Prioritize changes that preserve current's per-iteration execution gains
           while recovering pre_tuning-like convergence behavior.
        4. Continue copy-reduction and rocSPARSE/SpMV profiling, but avoid changing
           residual, restart, termination, or scaling logic without explicit
           numerical validation.
        5. Keep the 8-card fast8 batch-throughput result as an independent-MPS
           throughput highlight, not as evidence that one MPS is solved jointly by
           eight GPUs.
    """).strip(),

    "docs/W7900_CURRENT_STATUS.zh-CN.md": dedent("""
        ## 下一步

        P2--P9 的 W7900 验证、profiling、批处理吞吐和派生指标分析已经提交。
        下一阶段应从“补证据”转向 W7900-specific tuning triage：

        1. 基于 fast-core6 派生指标，优先分析 `L2CTA3D`、`set-cover-model`、
           `tpl-tub-ws1617` 为什么在 current 下虽然 ms/iter 降低，但迭代数增加。
        2. 后续 profiling 不盲目扩大 benchmark 矩阵，而是选择代表性 case：
           - 正向执行效率样本：`thk_48`
           - 迭代数稳定样本：`square41`
           - 收敛迭代数回退样本：`L2CTA3D`、`set-cover-model`、`tpl-tub-ws1617`
        3. 优先寻找“保留 current 单迭代执行收益，同时恢复接近 pre_tuning 收敛行为”的改动。
        4. 继续关注 copy reduction 和 rocSPARSE/SpMV profiling，但不要在没有明确
           数值验证的情况下改动 residual、restart、termination 或 scaling 逻辑。
        5. 8-card fast8 批处理吞吐结果单独作为 independent-MPS throughput 亮点保留，
           不写成“单个 MPS 由 8 张 GPU 联合求解”。
    """).strip(),
}

def replace_next_actions(path: Path, replacement: str) -> bool:
    text = path.read_text(encoding="utf-8")

    # Replace from the existing Next actions heading to the next major section.
    patterns = [
        r"## Next actions\n.*?(?=\n## Latest W7900 experiment status / 2026-06-16)",
        r"## 下一步\n.*?(?=\n## 最新 W7900 实验状态 / 2026-06-16)",
        r"## 后续动作\n.*?(?=\n## 最新 W7900 实验状态 / 2026-06-16)",
        r"## Next actions\n.*?(?=\n## Latest W7900 figures / 2026-06-16)",
        r"## 下一步\n.*?(?=\n## 最新 W7900 图表 / 2026-06-16)",
        r"## 后续动作\n.*?(?=\n## 最新 W7900 图表 / 2026-06-16)",
    ]

    for pat in patterns:
        new_text, n = re.subn(pat, replacement, text, count=1, flags=re.S)
        if n:
            path.write_text(new_text, encoding="utf-8")
            print(f"[OK] updated {path.relative_to(ROOT)}")
            return True

    raise RuntimeError(f"Could not find Next actions block in {path}")

def main():
    for rel, replacement in REPL.items():
        replace_next_actions(ROOT / rel, replacement)

if __name__ == "__main__":
    main()
