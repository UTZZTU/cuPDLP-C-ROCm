# cuPDLP-C-ROCm

> 中文：[README.md](README.md)
> Documentation map: [docs/README.md](docs/README.md)
> Final W7900 results: [docs/W7900_FINAL_RESULTS_20260729.md](docs/W7900_FINAL_RESULTS_20260729.md)
> Final reproduction guide: [docs/FINAL_REPRODUCTION_GUIDE.md](docs/FINAL_REPRODUCTION_GUIDE.md)

`cuPDLP-C-ROCm` is the ROCm/HIP port, validation, and performance-analysis
branch of upstream [cuPDLP-C](README_UPSTREAM.md). It preserves CPU and
upstream-compatible CUDA paths while adding an AMD GPU backend. The contribution
is engineering migration, numerical validation, profiling, and evidence
management—not a new linear-programming algorithm.

## Final release status

| Item | Final status |
|---|---|
| Default branch | `rocm-w7900-gfx1100` |
| Frozen solver source | `735764807d8698ff30811d1a6fcc45d4a3fd4817` |
| Formal experiment harness | `b5b9a6ffc1a041a48a0e051568d0134a3822556c` |
| Main ROCm platform | Radeon PRO W7900 / `gfx1100` |
| Formal W7900 runs | **76/76 `VALIDATED_OPTIMAL`** |
| Evidence state | `FORMAL_W7900_EXPERIMENTS_COMPLETE`, `FINAL_ANALYSIS_RELEASED` |
| Release character | Research and engineering validation; not a production-grade general solver release |

The solver-source boundary is frozen across `CMakeLists.txt`, `cmake/`,
`cupdlp/`, and `interface/`. The final harness commit adds experiment,
validation, and archival support without changing that frozen solver source.

## Formal W7900 results

| Evidence | Formal result | Scope |
|---|---:|---|
| nonhard23 baseline | 23 cases × 2 repeats, 46/46 validated | One GPU, sequential independent MPS cases |
| Complete-repeat total time | 2950.626 s / 2950.675 s | Full 23-case repeat |
| Single-card throughput | 28.061842 / 28.061379 cases/hour | Mean **28.061611** |
| Tolerance sensitivity | 5 cases × 3 tolerances × 2 repeats, 30/30 validated | `1e-3`, `1e-4`, `1e-5` |
| Profiling | 5/5 `PASS` | Non-empty trace CSV and kernel trace per case |
| Static structure analysis | 23/23 validated | Rows, columns, nnz, density, irregularity |
| Numerical quality | 30/30 achieved errors do not exceed requested tolerance | Maximum `error/tolerance=0.998079` |

Key findings:

- `s100`, `Primal2_1000`, and `thk_63` account for **82.22%**
  of complete baseline total time;
- median total-time CV is **0.377%**; **22/23**
  cases are below 2%, and all 23 cases have identical iteration counts across
  the two repeats;
- tightening from `1e-3` to `1e-5` costs
  **1.01×–
  4.01×** in total time and
  **2.02×–
  11.58×** in iterations;
- the exploratory Spearman correlation between `matrix_nnz` and sampled peak
  VRAM is **0.882**; association is not causation.

See the [final results page](docs/W7900_FINAL_RESULTS_20260729.md) for compact
data, figures, and claim boundaries.

## Inspect the committed final evidence

A W7900 is not required to inspect the committed compact evidence:

```bash
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```

Expected markers:

```text
FINAL_W7900_RELEASE_DATA_PASS
FINAL_REPOSITORY_RELEASE_PASS
```

Regenerate the committed result figures with:

```bash
python3 scripts/analysis/generate_final_w7900_release.py
```

## Build and minimal execution

### CPU

```bash
cmake -S . -B build-cpu -G Ninja   -DCMAKE_BUILD_TYPE=Release   -DBUILD_CUDA=OFF   -DBUILD_ROCM=OFF
cmake --build build-cpu -j"$(nproc)"
```

### W7900 / ROCm

On a matching W7900 environment:

```bash
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

For fresh-machine recovery, dataset identity, mini gate, `baseline23`,
`session2`, archiving, and troubleshooting, use the
[final reproduction guide](docs/FINAL_REPRODUCTION_GUIDE.md).

## Repository data policy

Committed:

- case lists, manifests, and checksums;
- compact curated CSV/JSON;
- Markdown summaries;
- small PNG/SVG figures;
- validation, analysis, and reproduction scripts.

Not committed:

- raw MPS inputs;
- raw profiler traces;
- local build and temporary run directories;
- cookies, SSH keys, or other credentials.

## Claim boundaries

- Single-card throughput means sequential independent MPS cases, not one LP
  distributed across multiple GPUs.
- Historical fast8 means eight independent jobs, not a distributed LP method.
- Tolerance conclusions cover only the five targeted cases.
- Static correlations are exploratory and non-causal.
- hard3 remains separate from nonhard23.
- Docker files are an environment skeleton; formal numbers came from a real
  W7900 host.
- Presolve-off is the primary validation contract; nontrivial postsolve and
  original-variable recovery are not part of the formal release evidence.

## Documentation entry points

| Need | Document |
|---|---|
| Final results | [W7900 final results](docs/W7900_FINAL_RESULTS_20260729.md) |
| Authoritative status | [W7900 current status](docs/W7900_CURRENT_STATUS.md) |
| Reproduction | [Final reproduction guide](docs/FINAL_REPRODUCTION_GUIDE.md) |
| Validation semantics | [Validation](docs/VALIDATION.md) |
| Performance interpretation | [Performance behavior](docs/W7900_PERFORMANCE_BEHAVIOR.md) |
| Profiling | [Profiling notes](docs/ROCM_PROFILING_NOTES.md) |
| Compact evidence | [Final validation package](validation/final_w7900_20260729/README.md) |
| Competition review | [Competition entry](docs/COMPETITION_README.md) |
| Full navigation | [Documentation map](docs/README.md) |

## Upstream and license

The upstream README snapshot is retained in
[README_UPSTREAM.md](README_UPSTREAM.md). Unless a file states otherwise, this
repository follows the [MIT License](LICENSE).
