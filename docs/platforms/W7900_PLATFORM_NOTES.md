# W7900 platform notes — historical environment record

> **Historical platform record**
>
> This page preserves details from the first W7900 / `gfx1100` environment bring-up. It is not the current project-status page and its machine-specific paths must not be treated as portable defaults.
>
> Current status: [W7900_CURRENT_STATUS.md](../W7900_CURRENT_STATUS.md)
>
> Reproduction workflow: [REPRODUCIBILITY.md](../REPRODUCIBILITY.md)

## Recorded platform role

| Item | Recorded value |
|---|---|
| GPU | AMD Radeon PRO W7900 |
| Architecture | `gfx1100` |
| Project role | First W7900 environment recovery and validation |
| Current branch focus | W7900 validation, P10 profiling, P11 tuning, P12 negative result, and P14-A1 repeats |

## Environment-specific layout

The original W7900 workspace used a nonstandard Python-packaged ROCm SDK and machine-local paths under `/app/cupdlp_w7900`. These paths describe that machine only.

Typical recorded locations included:

```text
/opt/python/bin/hipcc
/opt/python/lib/python3.12/site-packages/_rocm_sdk_core
/opt/python/lib/python3.12/site-packages/_rocm_sdk_devel
/app/cupdlp_w7900
```

For a fresh machine, use the maintained bootstrap and reproduction documentation instead of copying paths blindly:

```bash
RUN_BUILD=1 RUN_SMOKE=1 \
  bash scripts/bootstrap_w7900_workspace.sh
```

## Current interpretation

The first-port stage documented by this page has been superseded by:

- W7900 smoke and Netlib validation;
- non-hard23 23/23 `OPTIMAL`;
- P10 targeted profiling;
- P11 accepted SpMV policy;
- P12 rejected execution-layer experiment;
- P14-A1 repeated before/current validation.

No “next step” in this historical note should override the current-status documents.

## Related evidence

- [W7900 first-port record](../W7900_FIRST_PORT.md)
- [W7900 current status](../W7900_CURRENT_STATUS.md)
- [ROCm profiling notes](../ROCM_PROFILING_NOTES.md)
- [ROCm tuning history](../ROCM_TUNING_HISTORY.md)
- [Validation index](../../validation/README.md)
