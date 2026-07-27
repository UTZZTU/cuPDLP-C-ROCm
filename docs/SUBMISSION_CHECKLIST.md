# Submission checklist

> 中文: [SUBMISSION_CHECKLIST.zh-CN.md](SUBMISSION_CHECKLIST.zh-CN.md)

This checklist separates repository-verifiable material from external submission artifacts. The actual status of the paper, slides, and video is maintained by the project owner at submission time so that the repository does not preserve stale “not started” or “in progress” claims.

## Repository engineering material

| Item | Status | Entry |
|---|---|---|
| English and Chinese homepages | Available | [English](../README.en.md), [中文](../README.md) |
| Documentation map | Available | [docs/README.md](README.md) |
| W7900 current status | Available | [W7900_CURRENT_STATUS.md](W7900_CURRENT_STATUS.md) |
| Reproducibility guide | Available | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Validation evidence index | Available | [validation/README.md](../validation/README.md) |
| Competition reviewer path | Available | [COMPETITION_README.md](COMPETITION_README.md) |
| Score mapping | Available; update when rules change | [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md) |
| Architecture and evidence maps | Available | [architecture](assets/competition/project_architecture.svg), [evidence map](assets/competition/evidence_map.svg) |
| Docker/container | Environment skeleton | [Docker notes](../docker/README_DOCKER_W7900.md) |
| Raw-data policy | Defined | `.mps` files and raw traces stay outside Git |

## W7900 evidence closure

| Item | Status | Evidence |
|---|---|---|
| build and smoke | Closed for current stage | [smoke summary](../validation/w7900_smoke_summary_20260611.md) |
| Netlib / 27-case | Complete | [27-case baseline](../validation/w7900_27cases_baseline_20260611.md) |
| non-hard23 | 23/23 `OPTIMAL` | [summary](../validation/w7900_large_mps_nonhard23_20260613.md) |
| hard3 | Reported separately | [notes](W7900_LARGE_MPS_HARD3_NOTES.md) |
| P10 profiling | Complete | [summary](../validation/w7900_p10_current_targeted_rocprof_20260617_summary.md) |
| P11 tuning | `CSR_ALG1` default accepted | [summary](../validation/w7900_p11_spmv_tuning_summary_20260617.md) |
| P12 negative result | Patch rejected and documented | [negative finding](../validation/w7900_p12_spmv_buffer_alg_consistency_negative_20260617.md) |
| P14-A1 repeats | current wins 6/6 | [summary](../validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_summary.md) |
| 8-card fast8 | independent-MPS throughput | [summary](../validation/w7900_8card_batch_fast8_summary_20260616.md) |

## External submission artifacts

The owner completes these checks before final submission; their status is not permanently hard-coded in the repository:

| Artifact | Final check |
|---|---|
| Technical paper | Title, contribution boundaries, numbers, figures, and repository citations agree |
| Presentation slides | Do not overclaim algorithmic novelty or describe eight-card throughput as one-problem multi-GPU |
| Demo video | Show an actual build/run or explicitly identify committed-evidence inspection |
| Submission form | Branch, commit, environment, dataset source, and license are accurate |
| Optional container | Clearly distinguish an environment skeleton from a fully validated reproduction image |

## Final consistency checks

- [ ] Main branch and commit are recorded.
- [ ] English and Chinese homepages agree with the W7900 current-status pages.
- [ ] non-hard23 is reported as 23/23 `OPTIMAL`, with hard3 separate.
- [ ] The current default is `HIPSPARSE_SPMV_CSR_ALG1`; fallback is `CUPDLP_HIP_SPMV_ALG=csr_alg2`.
- [ ] The rejected P12 experiment remains discoverable.
- [ ] P14-A1 is reported as 6/6 current wins, geometric mean 1.18889, median 1.19502.
- [ ] Eight-card results are described as eight independent MPS jobs.
- [ ] No claim is made of a new PDLP algorithm.
- [ ] No claim is made that W7900 beats CUDA on every case.
- [ ] Raw MPS, raw traces, build directories, and credentials are not staged.
- [ ] `git diff --check` and Markdown/link checks pass.
- [ ] Repository links and file paths cited by submission materials are accessible.
