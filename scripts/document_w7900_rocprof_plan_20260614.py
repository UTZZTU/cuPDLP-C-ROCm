#!/usr/bin/env python3
from pathlib import Path

PLAN_EN = Path("docs/W7900_ROCM_PROFILING_PLAN.md")
PLAN_ZH = Path("docs/W7900_ROCM_PROFILING_PLAN.zh-CN.md")
RUNNER = Path("scripts/run_w7900_rocprof_smoke_matrix.sh")

BLOCK_BEGIN = "<!-- W7900_ROCM_PROFILING_PLAN_20260614_BEGIN -->"
BLOCK_END = "<!-- W7900_ROCM_PROFILING_PLAN_20260614_END -->"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")
    print("[ok] wrote", path)


def insert_or_replace(path, block, anchors):
    p = Path(path)
    if not p.exists():
        print("[skip] missing", path)
        return
    s = p.read_text()
    if BLOCK_BEGIN in s and BLOCK_END in s:
        before = s.split(BLOCK_BEGIN)[0].rstrip()
        after = s.split(BLOCK_END, 1)[1].lstrip()
        p.write_text(before + "\n\n" + block.rstrip() + "\n\n" + after)
        print("[ok] replaced block in", path)
        return
    for anchor in anchors:
        if anchor in s:
            p.write_text(s.replace(anchor, block.rstrip() + "\n\n" + anchor, 1))
            print("[ok] inserted block in", path)
            return
    p.write_text(s.rstrip() + "\n\n" + block.rstrip() + "\n")
    print("[ok] appended block in", path)


def plan_en():
    return r"""# W7900 ROCm profiling plan

> 中文: [W7900_ROCM_PROFILING_PLAN.zh-CN.md](W7900_ROCM_PROFILING_PLAN.zh-CN.md)

This document defines the profiling plan before W7900 / `gfx1100` tuning. It should be used after the baseline documentation is stable and before making kernel-level changes.

## Current baseline state

The profiling stage starts from a documented baseline:

- smoke validation: completed
- Netlib 27-case validation: completed
- large-MPS `initial17_safe`: completed
- large-MPS `watchlist6` + `near_optimal2`: completed
- combined large-MPS `non-hard23`: 23/23 `OPTIMAL`
- `hard3`: separated for convergence-trajectory analysis

The goal of profiling is not to re-prove correctness. The goal is to identify where the W7900 path spends time and which bottlenecks are worth tuning.

## Profiling case matrix

| Group | Cases | Purpose |
|---|---|---|
| fast representative | `set-cover-model`, `supportcase10`, `L2CTA3D` | Check fixed overhead, HIP API overhead, setup cost, and short-run kernel profile |
| competitive representative | `square41`, `thk_48`, `tpl-tub-ws1617` | Study cases where W7900 can approach or exceed high-end references in wall time |
| slow-but-solvable | `s100`, `Primal2_1000` | Study high-iteration behavior and gap trajectory after confirmed `OPTIMAL` follow-up |
| hard3 diagnostic | `dlr1`, `Dual2_5000`, `fhnw-binschedule1` | Short diagnostic only; do not mix into primary baseline before separate analysis |

## Tooling

Use a layered profiling workflow:

1. Baseline runtime JSON from the solver.
2. GPU telemetry using `rocm-smi` or AMD SMI.
3. HIP/kernel trace and statistics using `rocprofv3` when available.
4. Optional counter collection after the first trace identifies target kernels.

## Metrics to record

| Metric | Why it matters |
|---|---|
| `wall_seconds` | End-to-end user-visible performance |
| `dSolvingTime` | Solver-side compute time |
| `DeviceMatVecProdTime` | SpMV-related device time |
| `nIter` | Separates per-iteration speed from convergence behavior |
| relative primal/dual/gap | Indicates numerical progress and near-tolerance stalls |
| HIP API time | Shows launch/copy/runtime overhead |
| kernel statistics | Shows dominant kernels and repeated dispatch patterns |
| GPU power/temperature/utilization | Helps distinguish compute bottlenecks from environment issues |

## Profiling stages

### Stage 0: environment and tool detection

Record:

```bash
command -v rocprofv3 rocprof rocm-smi amd-smi hipcc || true
rocminfo | grep -E "Name:|Marketing Name|gfx" || true
rocm-smi || true
```

### Stage 1: no-profiler baseline rerun

Run the selected case without profiler first and save:

- JSON output
- terminal log
- `runtime_summary.csv`
- `rocm-smi` snapshot before and after

This gives the reference before profiler overhead.

### Stage 2: HIP and kernel trace

Preferred command form when `rocprofv3` is available:

```bash
rocprofv3 --stats --hip-trace --kernel-trace --output-format csv --output-directory "$OUT/rocprofv3" -- "$PLC" -fname "$MPS" -out "$JSON" -nIterLim "$ITER_LIMIT" -dTimeLim "$TIME_LIMIT"
```

Fallback command form if only legacy `rocprof` is available should be added after checking the installed version on the machine.

### Stage 3: analyze top kernels and overhead

For each case, produce:

- top kernels by total time
- top kernels by call count
- HIP API overhead summary
- ratio of `DeviceMatVecProdTime / dSolvingTime`
- relationship between `nIter` and total solve time

### Stage 4: choose tuning targets

Do not tune all code paths blindly. Use the profiling data to decide between:

- SpMV/kernel optimization
- reduction optimization
- avoiding unnecessary host-device copies
- lowering HIP setup or launch overhead
- tuning solver control path only if convergence behavior changes

## Expected interpretation

W7900 can be fast when:

- the case has enough work to amortize setup/launch overhead;
- SpMV and vector operations dominate;
- convergence is stable;
- memory bandwidth and VRAM capacity matter.

W7900 can be slow when:

- iteration count dominates;
- gap stalls close to tolerance;
- restart/step-size path differs from CUDA references;
- small cases are dominated by fixed overhead;
- current ROCm/gfx1100 kernels are not yet tuned.

## Output policy

Raw large MPS files and raw profiler trace directories should not be committed.

Commit only:

- scripts
- curated CSV summaries
- Markdown summaries
- small SVG charts
- selected compact profiler summaries

Recommended output root:

```text
/app/cupdlp_w7900/results/w7900_rocprof/
```

Recommended committed summaries:

```text
validation/w7900_rocprof_case_matrix_*.csv
validation/w7900_rocprof_kernel_top_*.csv
validation/w7900_rocprof_hip_api_top_*.csv
docs/W7900_ROCM_PROFILING_PLAN.md
```

## First profiling run recommendation

Start with three cases:

1. `set-cover-model` — fast/representative, useful for overhead and kernel dispatch analysis.
2. `square41` — competitive case, useful for showing W7900 strength.
3. `s100` — slow-but-solvable, useful for separating iteration count from per-iteration cost.

Do not start with hard3. Hard3 should be used only after the profiling workflow is stable.
"""


def plan_zh():
    return r"""# W7900 ROCm profiling 计划

> English: [W7900_ROCM_PROFILING_PLAN.md](W7900_ROCM_PROFILING_PLAN.md)

本文定义 W7900 / `gfx1100` 调优前的 profiling 计划。它应在 baseline 文档稳定之后、kernel 级修改之前使用。

## 当前 baseline 状态

profiling 阶段基于以下已记录 baseline：

- smoke validation：已完成
- Netlib 27-case validation：已完成
- large-MPS `initial17_safe`：已完成
- large-MPS `watchlist6` + `near_optimal2`：已完成
- 合并后的 large-MPS `non-hard23`：23/23 `OPTIMAL`
- `hard3`：单独用于收敛轨迹分析

profiling 的目标不是重新证明正确性，而是定位 W7900 路径的耗时来源，并判断哪些瓶颈值得调优。

## Profiling case matrix

| 分组 | Cases | 目的 |
|---|---|---|
| fast representative | `set-cover-model`, `supportcase10`, `L2CTA3D` | 检查固定开销、HIP API overhead、setup cost 和短运行 kernel profile |
| competitive representative | `square41`, `thk_48`, `tpl-tub-ws1617` | 分析 W7900 在 wall time 上接近或超过高端参考设备的 case |
| slow-but-solvable | `s100`, `Primal2_1000` | 分析高迭代次数和 gap trajectory |
| hard3 diagnostic | `dlr1`, `Dual2_5000`, `fhnw-binschedule1` | 只做短诊断；在单独分析前不混入主 baseline |

## 工具层次

使用分层 profiling 流程：

1. solver runtime JSON baseline。
2. `rocm-smi` 或 AMD SMI 记录 GPU telemetry。
3. 有 `rocprofv3` 时使用 HIP/kernel trace 和 statistics。
4. 第一轮 trace 找到目标 kernel 后，再考虑 counter collection。

## 需要记录的指标

| 指标 | 意义 |
|---|---|
| `wall_seconds` | 端到端用户可见性能 |
| `dSolvingTime` | solver 内部计算时间 |
| `DeviceMatVecProdTime` | SpMV 相关设备端时间 |
| `nIter` | 区分单次迭代速度和收敛行为 |
| relative primal/dual/gap | 判断数值进展和 near-tolerance stall |
| HIP API time | 判断 launch/copy/runtime overhead |
| kernel statistics | 找主要 kernel 和高频 dispatch |
| GPU power/temperature/utilization | 排除环境或功耗温度问题 |

## Profiling 阶段

### Stage 0：环境与工具检测

记录：

```bash
command -v rocprofv3 rocprof rocm-smi amd-smi hipcc || true
rocminfo | grep -E "Name:|Marketing Name|gfx" || true
rocm-smi || true
```

### Stage 1：无 profiler baseline rerun

先不挂 profiler 跑选定 case，保存：

- JSON output
- terminal log
- `runtime_summary.csv`
- 跑前/跑后的 `rocm-smi` snapshot

这是 profiler overhead 之前的参考。

### Stage 2：HIP 和 kernel trace

有 `rocprofv3` 时优先使用：

```bash
rocprofv3 --stats --hip-trace --kernel-trace --output-format csv --output-directory "$OUT/rocprofv3" -- "$PLC" -fname "$MPS" -out "$JSON" -nIterLim "$ITER_LIMIT" -dTimeLim "$TIME_LIMIT"
```

如果机器上只有 legacy `rocprof`，应先检查本机版本后再补 fallback。

### Stage 3：分析 top kernels 和 overhead

每个 case 输出：

- total time 排名前列的 kernel
- call count 排名前列的 kernel
- HIP API overhead summary
- `DeviceMatVecProdTime / dSolvingTime`
- `nIter` 与 solve time 的关系

### Stage 4：确定调优目标

不要盲目调所有路径。根据 profiling 数据决定优先级：

- SpMV/kernel 优化
- reduction 优化
- 减少不必要 host-device copy
- 降低 HIP setup 或 launch overhead
- 只有在收敛行为改变时才调 solver control path

## 预期解释

W7900 快的场景：

- case 规模足够大，可以摊薄 setup/launch overhead；
- SpMV 和 vector operation 占主导；
- 收敛稳定；
- 显存带宽和 VRAM 容量能发挥作用。

W7900 慢的场景：

- 迭代次数主导；
- gap 在阈值附近停滞；
- restart/step-size 路径与 CUDA 参考不同；
- 小 case 被固定开销主导；
- 当前 ROCm/gfx1100 kernel 还没调优。

## 输出策略

raw large MPS 和 raw profiler trace directory 不进 git。

只提交：

- scripts
- curated CSV summaries
- Markdown summaries
- 小型 SVG charts
- 精简 profiler summaries

建议输出根目录：

```text
/app/cupdlp_w7900/results/w7900_rocprof/
```

建议提交的 summary：

```text
validation/w7900_rocprof_case_matrix_*.csv
validation/w7900_rocprof_kernel_top_*.csv
validation/w7900_rocprof_hip_api_top_*.csv
docs/W7900_ROCM_PROFILING_PLAN.md
```

## 第一轮 profiling 建议

先从三个 case 开始：

1. `set-cover-model`：fast/representative，用于分析 overhead 和 kernel dispatch。
2. `square41`：competitive case，用于展示 W7900 强项。
3. `s100`：slow-but-solvable，用于区分迭代次数和单次迭代成本。

不要从 hard3 开始。hard3 应等 profiling workflow 稳定后再用。
"""


def runner_script():
    return r"""#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
DATA_ROOT="${DATA_ROOT:-/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark}"
MPS_DIR="${MPS_DIR:-${DATA_ROOT}/mps}"

CASE_LIST="${CASE_LIST:-${REPO_ROOT}/validation/cases_w7900_rocprof_starter3.txt}"
RUN_TAG="${RUN_TAG:-w7900_rocprof_starter3}"
ITER_LIMIT="${ITER_LIMIT:-1000000000}"
TIME_LIMIT="${TIME_LIMIT:-900}"
EXTERNAL_TIMEOUT="${EXTERNAL_TIMEOUT:-960}"
HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES:-0}"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_ROOT="${OUT_ROOT:-${WORK_ROOT}/results/w7900_rocprof/${RUN_TAG}_${STAMP}}"
LOG_DIR="${OUT_ROOT}/logs"
JSON_DIR="${OUT_ROOT}/json"
PROF_DIR="${OUT_ROOT}/profiler"
SMI_DIR="${OUT_ROOT}/smi"

mkdir -p "${LOG_DIR}" "${JSON_DIR}" "${PROF_DIR}" "${SMI_DIR}"

cd "${REPO_ROOT}"

if [[ -f "${WORK_ROOT}/activate_w7900.sh" ]]; then
  source "${WORK_ROOT}/activate_w7900.sh"
fi

PLC="${REPO_ROOT}/build-rocm-w7900/bin/plc"

if [[ ! -x "${PLC}" ]]; then
  echo "[error] plc not found: ${PLC}" >&2
  echo "Run bootstrap/build first." >&2
  exit 1
fi

if [[ ! -f "${CASE_LIST}" ]]; then
  echo "[info] creating starter case list: ${CASE_LIST}"
  cat > "${CASE_LIST}" <<'EOF'
set-cover-model.mps
square41.mps
s100.mps
EOF
fi

echo "case,status,exit_code,wall_seconds,json,log,profiler_dir" > "${OUT_ROOT}/runtime_summary.csv"

{
  echo "repo=${REPO_ROOT}"
  echo "out_root=${OUT_ROOT}"
  echo "case_list=${CASE_LIST}"
  echo "HIP_VISIBLE_DEVICES=${HIP_VISIBLE_DEVICES}"
  echo "ITER_LIMIT=${ITER_LIMIT}"
  echo "TIME_LIMIT=${TIME_LIMIT}"
  echo "EXTERNAL_TIMEOUT=${EXTERNAL_TIMEOUT}"
  echo
  echo "== tools =="
  command -v rocprofv3 rocprof rocm-smi amd-smi hipcc || true
  echo
  echo "== git =="
  git rev-parse HEAD || true
} | tee "${OUT_ROOT}/run_info.txt"

PROFILE_TOOL=""
if command -v rocprofv3 >/dev/null 2>&1; then
  PROFILE_TOOL="rocprofv3"
elif command -v rocprof >/dev/null 2>&1; then
  PROFILE_TOOL="rocprof"
fi

echo "[info] profiling tool: ${PROFILE_TOOL:-none}"

while IFS= read -r case_name; do
  [[ -z "${case_name}" ]] && continue
  [[ "${case_name}" =~ ^# ]] && continue

  base="${case_name%.mps}"
  mps="${MPS_DIR}/${case_name}"
  json="${JSON_DIR}/${base}.json"
  log="${LOG_DIR}/${base}.log"
  case_prof="${PROF_DIR}/${base}"

  if [[ ! -f "${mps}" ]]; then
    echo "[warn] missing ${mps}"
    echo "${case_name},MISSING,999,0,${json},${log},${case_prof}" >> "${OUT_ROOT}/runtime_summary.csv"
    continue
  fi

  mkdir -p "${case_prof}"

  echo
  echo "============================================================"
  echo "[case] ${case_name}"
  echo "============================================================"

  if command -v rocm-smi >/dev/null 2>&1; then
    rocm-smi > "${SMI_DIR}/${base}_before.txt" 2>&1 || true
  elif command -v amd-smi >/dev/null 2>&1; then
    amd-smi static > "${SMI_DIR}/${base}_before.txt" 2>&1 || true
  fi

  start="$(date +%s.%N)"
  set +e

  if [[ "${PROFILE_TOOL}" == "rocprofv3" ]]; then
    HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES}" timeout --foreground "${EXTERNAL_TIMEOUT}s" \
      rocprofv3 --stats --hip-trace --kernel-trace --output-format csv --output-directory "${case_prof}" -- \
      "${PLC}" -fname "${mps}" -out "${json}" -nIterLim "${ITER_LIMIT}" -dTimeLim "${TIME_LIMIT}" \
      2>&1 | tee "${log}"
    rc="${PIPESTATUS[0]}"
  elif [[ "${PROFILE_TOOL}" == "rocprof" ]]; then
    echo "[warn] legacy rocprof detected. Running without rocprof command until local syntax is confirmed." | tee "${log}"
    HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES}" timeout --foreground "${EXTERNAL_TIMEOUT}s" \
      "${PLC}" -fname "${mps}" -out "${json}" -nIterLim "${ITER_LIMIT}" -dTimeLim "${TIME_LIMIT}" \
      2>&1 | tee -a "${log}"
    rc="${PIPESTATUS[0]}"
  else
    echo "[warn] no profiler detected. Running baseline only." | tee "${log}"
    HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES}" timeout --foreground "${EXTERNAL_TIMEOUT}s" \
      "${PLC}" -fname "${mps}" -out "${json}" -nIterLim "${ITER_LIMIT}" -dTimeLim "${TIME_LIMIT}" \
      2>&1 | tee -a "${log}"
    rc="${PIPESTATUS[0]}"
  fi

  set -e
  end="$(date +%s.%N)"

  if command -v rocm-smi >/dev/null 2>&1; then
    rocm-smi > "${SMI_DIR}/${base}_after.txt" 2>&1 || true
  elif command -v amd-smi >/dev/null 2>&1; then
    amd-smi static > "${SMI_DIR}/${base}_after.txt" 2>&1 || true
  fi

  wall="$(python3 - <<PY
start = float("${start}")
end = float("${end}")
print(f"{end - start:.6f}")
PY
)"

  if [[ "${rc}" == "0" ]]; then
    status="DONE"
  elif [[ "${rc}" == "124" ]]; then
    status="TIMEOUT"
  else
    status="ERROR"
  fi

  echo "${case_name},${status},${rc},${wall},${json},${log},${case_prof}" >> "${OUT_ROOT}/runtime_summary.csv"
  echo "[done] ${case_name}: status=${status}, rc=${rc}, wall=${wall}s"

done < "${CASE_LIST}"

echo
echo "[done] profiling matrix finished"
echo "[done] output: ${OUT_ROOT}"
echo "[done] runtime summary: ${OUT_ROOT}/runtime_summary.csv"
"""


def update_indexes():
    docs_block = f"""{BLOCK_BEGIN}
| W7900 ROCm profiling plan / W7900 ROCm profiling 计划 | [W7900_ROCM_PROFILING_PLAN.md](W7900_ROCM_PROFILING_PLAN.md) | [W7900_ROCM_PROFILING_PLAN.zh-CN.md](W7900_ROCM_PROFILING_PLAN.zh-CN.md) | Profiling case matrix, metrics, tools, and output policy before ROCm/gfx1100 tuning |
{BLOCK_END}"""
    insert_or_replace(
        "docs/README.md",
        docs_block,
        ["| W7900 performance behavior / W7900 性能行为分析", "## Benchmarks and numerical behavior / Benchmark 与数值行为"],
    )

    status_block_en = f"""{BLOCK_BEGIN}
## ROCm profiling and tuning plan

The next stage is not blind kernel editing. It starts with a fixed profiling case matrix and records wall time, solver time, `DeviceMatVecProdTime`, `nIter`, HIP/kernel trace, and GPU telemetry.

See [W7900 ROCm profiling plan](W7900_ROCM_PROFILING_PLAN.md).
{BLOCK_END}"""
    insert_or_replace(
        "docs/W7900_CURRENT_STATUS.md",
        status_block_en,
        ["## Next documentation tasks", "## Related performance behavior analysis"],
    )

    status_block_zh = f"""{BLOCK_BEGIN}
## ROCm profiling 与调优计划

下一阶段不是盲目改 kernel，而是先固定 profiling case matrix，并记录 wall time、solver time、`DeviceMatVecProdTime`、`nIter`、HIP/kernel trace 和 GPU telemetry。

详见 [W7900 ROCm profiling 计划](W7900_ROCM_PROFILING_PLAN.zh-CN.md)。
{BLOCK_END}"""
    insert_or_replace(
        "docs/W7900_CURRENT_STATUS.zh-CN.md",
        status_block_zh,
        ["## 下一步文档任务", "## 相关性能行为分析"],
    )


def ensure_case_list():
    p = Path("validation/cases_w7900_rocprof_starter3.txt")
    if not p.exists():
        p.write_text("set-cover-model.mps\nsquare41.mps\ns100.mps\n")
        print("[ok] wrote", p)


def main():
    write(PLAN_EN, plan_en())
    write(PLAN_ZH, plan_zh())
    write(RUNNER, runner_script())
    ensure_case_list()
    update_indexes()
    print("[done] W7900 ROCm profiling plan generated")


if __name__ == "__main__":
    main()
