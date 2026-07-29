# Reproducibility

> 中文：[REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)
> Full final guide: [FINAL_REPRODUCTION_GUIDE.md](FINAL_REPRODUCTION_GUIDE.md)

This page summarizes reproduction levels. Exact commands, formal matrices,
acceptance markers, and troubleshooting are maintained in the
[final reproduction guide](FINAL_REPRODUCTION_GUIDE.md).

## Reproduction levels

| Level | Work | Hardware |
|---|---|---|
| Compact evidence inspection | CSV/JSON identity, QC, figures, links | Any Linux host |
| Offline analysis regeneration | Statistics and final figures | Linux + Python |
| CPU build/smoke | CPU backend and one-case execution | C/C++ build environment |
| W7900 build/smoke | Real ROCm/HIP build and minimum validation | W7900 / `gfx1100` |
| Full formal matrix | baseline23, session2, resources, profiles, archive | W7900 plus external MPS |

A non-W7900 host can inspect evidence, but that is not a new W7900 benchmark.

## Formal identity

```text
branch=rocm-w7900-gfx1100
solver=735764807d8698ff30811d1a6fcc45d4a3fd4817
harness=b5b9a6ffc1a041a48a0e051568d0134a3822556c
```

## Recommended evidence check

```bash
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```

## Regenerate figures

```bash
python3 -m pip install pandas numpy matplotlib
python3 scripts/analysis/generate_final_w7900_release.py
```

## Minimal W7900 workflow

```bash
bash scripts/prepare_w7900_final_sprint.sh setup
bash scripts/prepare_w7900_final_sprint.sh build
bash scripts/prepare_w7900_final_sprint.sh smoke
```

## Full formal rerun

- mini gate;
- `baseline23`: 23 × 2 = 46;
- `session2`: 5 × 3 × 2 = 30 plus five profiles;
- archive, SHA256, and receiving-host verification.

See the [final reproduction guide](FINAL_REPRODUCTION_GUIDE.md).

## Data policy

Committed: source, scripts, case lists, manifests, compact CSV/JSON, Markdown,
small SVG/PNG.
Excluded: raw MPS, raw traces, local builds, cookies, SSH keys, and tokens.

## Interpretation boundaries

- historical fast8 is independent-task throughput;
- hard3 remains separate;
- tolerance results cover five cases;
- static correlation is non-causal;
- Docker is an environment skeleton.
