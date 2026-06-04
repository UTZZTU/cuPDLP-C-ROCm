# Migration helper scripts

This directory contains helper scripts used during the CUDA-to-ROCm/HIP migration of cuPDLP-C.

These scripts are not required for normal users who only want to build and run the ROCm version.

Normal users should use:

- `BUILD_ROCM=ON`
- `scripts/build_rocm.sh` once available
- `scripts/run_validation.sh` once available

The scripts in this directory are kept for transparency, reproducibility, and future maintenance of the porting process.
