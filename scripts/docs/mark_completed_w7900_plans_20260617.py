#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write(path: Path, text: str):
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] wrote {path.relative_to(ROOT)}")

def replace_many(path: Path, replacements):
    if not path.exists():
        print(f"[MISS] {path.relative_to(ROOT)}")
        return

    text = read(path)
    original = text

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            print(f"[OK] replaced in {path.relative_to(ROOT)}: {old[:90]}")
        else:
            print(f"[MISS] {path.relative_to(ROOT)}: {old[:90]}")

    if text != original:
        write(path, text)

def append_once(path: Path, section: str):
    if not path.exists():
        print(f"[MISS] {path.relative_to(ROOT)}")
        return

    text = read(path)
    heading = section.strip().splitlines()[0].strip()

    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return

    write(path, text.rstrip() + "\n\n" + section.strip() + "\n")

COMPETITION_ZH_REPL = [
    (
        "Radeon PRO W7900 / `gfx1100` | large-MPS 工作站 GPU 验证和后续 W7900-specific profiling/tuning",
        "Radeon PRO W7900 / `gfx1100` | large-MPS 工作站 GPU 验证、P10 profiling、P11 SpMV tuning 与 P12 rejected experiment 记录"
    ),
    (
        "| After | future W7900-specific tuning branch | 最终 W7900-specific optimized result |",
        "| After / accepted endpoint | P11 current W7900 tuning policy | 当前默认 `HIPSPARSE_SPMV_CSR_ALG1`，旧默认可用 `CUPDLP_HIP_SPMV_ALG=csr_alg2` 回退 |"
    ),
    (
        "## 下一步计划\n\n1. 在 `set-cover-model`、`square41`、`s100` 上运行 W7900 `rocprofv3` starter3 profiling。\n2. 记录 wall time、solver time、`DeviceMatVecProdTime`、`nIter`、HIP/kernel trace 和 GPU telemetry。\n3. 对 `dlr1`、`fhnw-binschedule1` 运行 hard3 short probes。\n4. 使用 `ae3b683` vs current 跑 core6 true before/current comparison。\n5. profiling 结果定位瓶颈后再做 W7900-specific tuning。",
        "## 下一步计划状态\n\n原计划中的 W7900 starter profiling、hard3 short probes、before/current core6 comparison 和 W7900-specific tuning 已由 P10/P11/P12 证据链闭环：\n\n1. P10 targeted rocprof profiling 已完成并归档。\n2. hard3 probe2 已完成，hard3 不混入 primary non-hard23 baseline。\n3. before/current fast-core6 已完成；若要增强性能统计说服力，后续只补 representative repeated validation。\n4. P11 已完成 SpMV algorithm switch、smoke、five-case sweep，并将当前默认设为 `HIPSPARSE_SPMV_CSR_ALG1`。\n5. P12 已记录一个被拒绝的 SpMV buffer algorithm consistency patch，说明额外 execution-layer 改动经过保守验证。"
    ),
    (
        "| 演示说明 PPT | 第一轮 profiling 结果完成后制作 |",
        "| 演示说明 PPT | 可基于 W7900 current status、P10 targeted profiling、P11 SpMV tuning、P12 rejected finding 和 cuPDLPx positioning 制作 |"
    ),
]

COMPETITION_EN_REPL = [
    (
        "Radeon PRO W7900 / `gfx1100` | large-MPS workstation GPU validation and future W7900-specific profiling/tuning",
        "Radeon PRO W7900 / `gfx1100` | large-MPS workstation GPU validation, P10 profiling, P11 SpMV tuning, and P12 rejected experiment record"
    ),
    (
        "| After | future W7900-specific tuning branch | final W7900-specific optimized result |",
        "| After / accepted endpoint | P11 current W7900 tuning policy | current default `HIPSPARSE_SPMV_CSR_ALG1`, rollback with `CUPDLP_HIP_SPMV_ALG=csr_alg2` |"
    ),
]

W7900_STATUS_ZH_REPL = [
    (
        "## ROCm profiling 与调优计划\n\n下一阶段不是盲目改 kernel，而是先固定 profiling case matrix，并记录 wall time、solver time、`DeviceMatVecProdTime`、`nIter`、HIP/kernel trace 和 GPU telemetry。\n\n详见 [W7900 ROCm profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md)。",
        "## ROCm profiling 与调优完成状态\n\n原 profiling 计划已执行并由 P10/P11/P12 证据链取代。当前不再把 starter profiling 或 W7900-specific tuning 写成 pending blocker。\n\n最终入口见 [W7900 ROCm profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md)、[P11 SpMV tuning summary](../validation/w7900_p11_spmv_tuning_summary_20260617.zh-CN.md) 和 [P12 rejected experiment note](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.zh-CN.md)。"
    ),
    (
        "## 后续动作\n\n1. 在 `set-cover-model.mps`、`square41.mps`、`s100.mps` 上运行 W7900 `rocprof` starter3。\n2. 对 `dlr1.mps` 和 `fhnw-binschedule1.mps` 运行 hard3 probe2；`Dual2_5000.mps` 先作为已有强 hard 行为记录保留，除非后续出现新证据。\n3. 运行 true before/current core6 对比：`ae3b683 / pre_tuning` 对比当前 `rocm-w7900-gfx1100`。\n4. 生成整理后的 profiling 结果摘要，只提交 compact CSV/Markdown，不提交 raw profiler traces。\n5. 只有在 profiling 数据明确瓶颈后，再决定第一轮 W7900-specific tuning 目标。",
        "## 后续动作状态\n\n以上 W7900 starter profiling、hard3 probe2、before/current core6、compact profiling summary 与第一轮 W7900-specific tuning 已完成当前阶段闭环：\n\n1. P10 targeted rocprof profiling 已归档。\n2. hard3 probe2 已归档；hard3 不混入 primary non-hard23 baseline。\n3. before/current fast-core6 已完成；若后续需要更强统计证据，只补 representative repeated validation。\n4. P11 SpMV tuning 已接受，当前默认 SpMV algorithm 为 `HIPSPARSE_SPMV_CSR_ALG1`。\n5. P12 rejected experiment note 已记录不接受的 buffer algorithm consistency patch。\n\n当前剩余内容不是 blocker，而是可选增强：P14-A current-vs-before repeated validation 与 P14-B CSR ALG1-vs-ALG2 repeated validation，等待 W7900 机器可用后再做。"
    ),
]

ROCM_WORKFLOW_ZH_REPL = [
    (
        "当前已验证 ROCm 目标是 AMD Radeon 890M / `gfx1150`。",
        "当前已验证 ROCm 目标包括 AMD Radeon 890M / `gfx1150` 和 Radeon PRO W7900 / `gfx1100`。W7900 已完成 P10 targeted profiling、P11 SpMV tuning 与 P12 rejected experiment note。"
    ),
    (
        "## 13. 当前下一步优先级\n\n1. 保持中英文文档同步。\n2. 完成 large MPS benchmark matrix。\n3. 记录 Radeon 890M pre-tuning ROCm baseline，之后记录 tuned rerun。\n4. 将 profiling 证据从 smoke case 扩展到更大 case。\n5. 准备 W7900 / `gfx1100` 迁移和 profiling。",
        "## 13. 当前下一步优先级状态\n\n原优先级已基本完成：large MPS benchmark matrix、890M tuning history、W7900 / `gfx1100` migration、profiling 和 P11 tuning 均已归档。\n\n当前剩余建议：\n\n1. 保持中英文文档和 validation 索引同步。\n2. 只在 W7900 机器可用时补 P14-A current-vs-before repeated validation。\n3. 只在 W7900 机器可用时补 P14-B CSR ALG1-vs-ALG2 repeated validation。\n4. 不再新增深层数值路径优化，除非重新设计完整验证协议。"
    ),
]

VALIDATION_ZH_REPL = [
    (
        "## 已验证 ROCm 目标\n\n| 项目 | 值 |\n|---|---|\n| GPU/APU | AMD Radeon 890M |\n| 架构 | `gfx1150` |\n| ROCm | 7.2.1 |\n| HIP compiler | ROCm Clang 22.0.0 |\n| Solver 可执行文件 | `build-rocm-plc/bin/plc` |\n| CPU baseline 可执行文件 | `build-cpu/bin/plc` |",
        "## 已验证 ROCm 目标\n\n| 项目 | 890M / `gfx1150` | W7900 / `gfx1100` |\n|---|---|---|\n| GPU/APU | AMD Radeon 890M | AMD Radeon PRO W7900 |\n| ROCm | 7.2.1 | W7900 ROCm SDK environment |\n| HIP compiler | ROCm Clang 22.0.0 | `/opt/python/bin/hipcc` / ROCm SDK |\n| Solver 可执行文件 | `build-rocm-plc/bin/plc` | `build-rocm-w7900/bin/plc` |\n| 状态 | smoke、Netlib、benchmark、890M tuning history 已归档 | smoke、Netlib、large-MPS baseline、P10 profiling、P11 tuning、P12 rejected finding 已归档 |\n| CPU baseline 可执行文件 | `build-cpu/bin/plc` | `build-cpu/bin/plc` |"
    ),
]

ROCM_PORTING_GUIDE_ZH_REPL = [
    (
        "## 14. 当前限制\n\n- ROCm/HIP backend 仍是实验性。\n- `gfx1150` 是当前已验证 AMD 目标。\n- `gfx1100` / W7900 需要单独 validation pass。\n- 部分内部 CUDA-style 名称因兼容性仍保留。\n- Broad large MPS validation 正在进行中。\n- 尚无 ROCm CI.\n\n## 15. 推荐下一步\n\n1. 保持用户可见 CUDA wording 清理，同时保留必要兼容符号。\n2. 完成 large MPS benchmark matrix。\n3. 记录 Radeon 890M pre-tuning 和 tuned ROCm 结果。\n4. 添加 W7900 / `gfx1100` 构建和验证说明。\n5. 将 profiling 从 smoke case 扩展到更大 LP 实例。",
        "## 14. 当前限制与完成状态\n\n- ROCm/HIP backend 仍是实验性，不应描述为生产级 solver release。\n- `gfx1150` / 890M 与 `gfx1100` / W7900 都已有验证记录。\n- W7900 validation pass 已完成当前阶段闭环：smoke、Netlib、large-MPS baseline、P10 profiling、P11 SpMV tuning、P12 rejected experiment note。\n- 部分内部 CUDA-style 名称因 C/HIP 兼容边界仍保留。\n- Broad large MPS validation 已有 curated summaries；raw MPS 和 raw logs 仍不提交到 Git。\n- 尚无 ROCm CI。\n\n## 15. 推荐下一步状态\n\n原推荐下一步已基本完成。当前只保留两个可选增强：\n\n1. W7900 P14-A：current-vs-before representative repeated validation。\n2. W7900 P14-B：CSR ALG1-vs-ALG2 representative repeated validation。\n\n除此之外，不建议继续新增深层数值路径优化，除非重新设计完整验证协议。"
    ),
]

FIRST_PORT_ZH_REPL = [
    (
        "## 9. 已知限制\n\n当前阶段仅完成 first-port smoke validation，尚未完成:\n\n* extended Netlib validation\n* large MPS benchmark\n* W7900 profiling\n* W7900 单卡调优\n* 8 GPU 并发吞吐实验\n* 跨设备 benchmark matrix 更新\n\n因此当前状态应描述为:\n\n```text\nW7900 / gfx1100 first-port smoke validation passed.\nExtended validation and tuning are in progress.\n```\n\n不应描述为完整生产级验证完成。\n\n## 10. 下一步计划\n\n后续计划:\n\n1. 固化 W7900 CPU/ROCm 构建脚本。\n2. 补充英文版 `W7900_FIRST_PORT.md`。\n3. 更新 README 中 W7900 的状态描述。\n4. 跑 W7900 smoke validation 脚本。\n5. 跑 extended Netlib validation。\n6. 使用 ROCm profiling 工具定位 W7900 单卡瓶颈。\n7. 基于 profile 结果进行单卡调优。\n8. 做 8 GPU single-GPU sweep 与多任务并发吞吐实验。\n9. 将结果汇总到比赛报告。",
        "## 9. 已知限制与当前完成状态\n\n本文是 W7900 / `gfx1100` first-port smoke milestone 的历史记录。文中原始限制已经由后续文档取代：\n\n* extended Netlib validation：已完成。\n* large MPS benchmark：non-hard23 baseline 已完成，hard3 单独记录。\n* W7900 profiling：P10 targeted rocprof 已归档。\n* W7900 单卡调优：P11 SpMV tuning 已完成，当前默认 `HIPSPARSE_SPMV_CSR_ALG1`。\n* 8 GPU 并发吞吐实验：fast8 batch throughput 已归档。\n* 跨设备 benchmark matrix：已有 curated summaries。\n\n当前仍不应描述为生产级 solver release，但已超过 first-port smoke 阶段。权威状态见 [W7900_CURRENT_STATUS.zh-CN.md](W7900_CURRENT_STATUS.zh-CN.md)。\n\n## 10. 后续计划状态\n\n原下一步计划已基本完成。当前仅保留可选增强：\n\n1. W7900 P14-A：current-vs-before representative repeated validation。\n2. W7900 P14-B：CSR ALG1-vs-ALG2 representative repeated validation。\n\n其他深层数值路径优化不纳入当前项目终点。"
    ),
]

TUNING_HISTORY_ZH_SECTION = dedent("""
    ## 后续计划完成标记 / 2026-06-17

    本文早期“后续计划”中的多项工作已经完成或被新的 W7900 文档取代：

    - W7900 / `gfx1100` 平台实测：已完成 smoke、Netlib、large-MPS baseline。
    - W7900 profiling：已由 P10 targeted rocprof 归档。
    - W7900 平台化调优：已由 P11 SpMV tuning 闭环。
    - 额外 execution-layer 小改动：P12 已记录一个被拒绝实验。
    - cuPDLP-C 与 cuPDLPx 对比：short13 已单独成文档，并已补最终定位说明。

    仍可选增强：

    - P14-A：W7900 current-vs-before representative repeated validation。
    - P14-B：W7900 CSR ALG1-vs-ALG2 representative repeated validation。
""").strip()

def append_once(path: Path, section: str):
    text = path.read_text(encoding="utf-8")
    heading = section.splitlines()[0].strip()
    if heading in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already has {heading}")
        return
    path.write_text(text.rstrip() + "\n\n" + section + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] appended {path.relative_to(ROOT)}")

def main():
    for rel, reps in [
        ("docs/COMPETITION_README.zh-CN.md", COMPETITION_ZH_REPL),
        ("docs/COMPETITION_README.md", COMPETITION_EN_REPL),
        ("docs/W7900_CURRENT_STATUS.zh-CN.md", W7900_STATUS_ZH_REPL),
        ("docs/ROCM_WORKFLOW.zh-CN.md", ROCM_WORKFLOW_ZH_REPL),
        ("docs/VALIDATION.zh-CN.md", VALIDATION_ZH_REPL),
        ("docs/ROCM_PORTING_GUIDE.zh-CN.md", ROCM_PORTING_GUIDE_ZH_REPL),
        ("docs/W7900_FIRST_PORT.zh-CN.md", FIRST_PORT_ZH_REPL),
    ]:
        replace_many(ROOT / rel, reps)

    append_once(ROOT / "docs/ROCM_TUNING_HISTORY.zh-CN.md", TUNING_HISTORY_ZH_SECTION)

    print("[DONE] marked completed W7900 plans as superseded")

if __name__ == "__main__":
    main()
