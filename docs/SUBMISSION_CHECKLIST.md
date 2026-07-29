# Final Submission Checklist

> 中文：[SUBMISSION_CHECKLIST.zh-CN.md](SUBMISSION_CHECKLIST.zh-CN.md)

## In-repository material

| Item | Status | Entry |
|---|---|---|
| Chinese and English homepages | Updated | Root READMEs |
| Documentation map | Updated | `docs/README.md` |
| Final formal results | Complete | `W7900_FINAL_RESULTS_20260729*` |
| Current W7900 status | Updated | `W7900_CURRENT_STATUS*` |
| Final reproduction guide | Complete | `FINAL_REPRODUCTION_GUIDE*` |
| Validation semantics | Final contract added | `VALIDATION*` |
| Performance/workload analysis | Updated | `W7900_PERFORMANCE_BEHAVIOR*` |
| Profiling notes | Updated | `ROCM_PROFILING_NOTES*` |
| Validation indexes | Updated | `validation/README*` |
| Final compact evidence | Complete | `validation/final_w7900_20260729/` |
| Final PNG/SVG | Generated | `docs/assets/w7900/final20260729/` |
| Analysis and verification scripts | Added | `scripts/analysis/`, `scripts/docs/` |
| Release notes | Added | `RELEASE_NOTES_FINAL_20260729.md` |

## Evidence closure

- [x] formal branch `rocm-w7900-gfx1100`
- [x] frozen solver `735764807d8698ff30811d1a6fcc45d4a3fd4817`
- [x] formal harness `b5b9a6ffc1a041a48a0e051568d0134a3822556c`
- [x] Window 1: 46/46
- [x] Window 2 precision: 30/30
- [x] Window 2 profiles: 5/5
- [x] dataset and internal checksums PASS
- [x] resource coverage for every solver row
- [x] final analysis released
- [x] no raw MPS, raw traces, or credentials in Git

## External-material review

- [ ] Paper uses final figures and final numbers.
- [ ] Slides do not mix the June single-run results with the July formal repeats.
- [ ] Poster defines throughput as sequential independent MPS cases.
- [ ] Video distinguishes real W7900 execution from offline evidence inspection.
- [ ] Defense does not call fast8 one-LP distributed solving.
- [ ] Tolerance conclusions remain limited to five cases.
- [ ] Static correlations are described as exploratory.
- [ ] Repository paths and commit references resolve.

## Before push

```bash
git diff --check
python3 scripts/docs/check_markdown_links.py
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```
