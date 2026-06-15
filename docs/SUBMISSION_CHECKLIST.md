# Submission checklist

> 中文: [SUBMISSION_CHECKLIST.zh-CN.md](SUBMISSION_CHECKLIST.zh-CN.md)

This checklist tracks contest-facing deliverables without turning the repository into a contest-only project. The repository remains a general ROCm/HIP migration, validation, and benchmarking project.

## Repository delivery

| Item | Status | Evidence / next step |
|---|---|---|
| General project README | Done | [../README.md](../README.md), [../README.zh-CN.md](../README.zh-CN.md) |
| Documentation map | Done | [README.md](README.md) |
| Competition reviewer path | Done | [COMPETITION_README.md](COMPETITION_README.md), [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md) |
| Reproducibility guide | Done | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| W7900 current status | Done | [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md) |
| W7900 performance interpretation | Done | [W7900_PERFORMANCE_BEHAVIOR.md](W7900_PERFORMANCE_BEHAVIOR.md) |
| W7900 optimization-baseline policy | Done | [W7900_OPTIMIZATION_BASELINES.md](W7900_OPTIMIZATION_BASELINES.md) |
| Docker/container skeleton | Done as skeleton | [../docker/Dockerfile.w7900](../docker/Dockerfile.w7900), [../docker/README_DOCKER_W7900.md](../docker/README_DOCKER_W7900.md). This is an environment declaration skeleton, not the source of current W7900 performance numbers. |
| Project architecture and evidence map | Done | [project architecture](assets/competition/project_architecture.svg), [evidence map](assets/competition/evidence_map.svg) |
| Curated validation summaries | Done for current milestone | See [../validation/README.md](../validation/README.md) |
| Raw MPS data policy | Done | Raw `.mps` files stay outside Git. |

## W7900 experiment items

| Item | Status | Notes |
|---|---|---|
| W7900 smoke validation | Done | Current repository documents completed smoke validation. |
| W7900 Netlib 27-case validation | Done | Current repository documents completed Netlib validation. |
| W7900 non-hard large-MPS baseline | Done | `non-hard23`: 23/23 `OPTIMAL`; hard3 tracked separately. |
| W7900 `rocprof` starter3 | Pending W7900 machine | Cases: `set-cover-model.mps`, `square41.mps`, `s100.mps`. |
| hard3 probe2 | Pending W7900 machine | Cases: `dlr1.mps`, `fhnw-binschedule1.mps`. |
| true before/current core6 | Pending W7900 machine | `ae3b683 / pre_tuning` versus current `rocm-w7900-gfx1100`. |
| W7900-specific tuning | Pending profiling evidence | Do not tune blindly; choose the first target after profiler results. |
| W7900 profiling result summary | Pending W7900 machine | Commit compact CSV/Markdown only, not raw profiler traces. |

## Contest submission materials

| Material | Status | Repository support |
|---|---|---|
| Technical paper | Not started | Use `COMPETITION_README`, `COMPETITION_SCORECARD`, `REPRODUCIBILITY`, W7900 status/performance docs, and future profiling results. |
| Presentation slides | Not started | Build after paper outline and W7900 profiling results. |
| Demo video | Not started | Should show repository structure, reproducibility workflow, W7900 run/profiling evidence if available, and result summaries. |
| Engineering code repository | In progress, mostly ready | Current branch: `rocm-w7900-gfx1100`. |
| Docker image / container package | Skeleton present | Strict final image remains future packaging work. |
| Example inputs and expected outputs | Mostly ready | Validation case lists and committed CSV/Markdown summaries are present. |

## Final cautions

- Do not describe current W7900 non-hard23 as an unoptimized baseline.
- Do not mix hard3 cases into the primary non-hard23 baseline.
- Do not commit raw `.mps` data or raw profiler trace directories.
- Do not claim W7900-specific bottlenecks have been optimized before `rocprof` results exist.
- Keep English and Chinese documents synchronized.
