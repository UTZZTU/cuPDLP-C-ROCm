# W7900 Docker / container skeleton

> 中文: [README_DOCKER_W7900.zh-CN.md](README_DOCKER_W7900.zh-CN.md)

This directory contains a lightweight container skeleton for final-submission environment documentation.

## Scope

The current W7900 benchmark and validation numbers were produced on the contest-provided W7900 environment, which uses a pre-installed ROCm/Python SDK layout. Therefore, this Dockerfile is not claimed as the source of the committed W7900 performance numbers.

Its purpose is to document the expected build environment shape and to make final packaging easier.

## What is included

- Ubuntu 24.04 base image.
- Generic build tools: CMake, Ninja, GCC/G++, Python, Git.
- Repository source copy.

## What is intentionally not included

- Raw `.mps` benchmark data.
- Raw profiler trace directories.
- Contest-provided ROCm/Python SDK binaries.
- Large benchmark outputs.

## Current reproduction path

Use the repository reproducibility guide first:

```text
docs/REPRODUCIBILITY.md
```

For W7900, the primary path is still the documented bootstrap workflow on the contest-provided machine:

```bash
bash scripts/bootstrap_w7900_workspace.sh
```

## Future work

Before final submission, this skeleton can be extended into a stricter Docker/Containerfile if the final ROCm runtime layout is fixed and redistributable.
