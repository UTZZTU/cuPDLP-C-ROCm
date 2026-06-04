#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

fail=0

check_absent() {
  local pattern="$1"
  shift
  if grep -RInE "$pattern" "$@" >/tmp/rocm_hygiene_match.txt 2>/dev/null; then
    echo "FAIL: unexpected pattern found: $pattern"
    cat /tmp/rocm_hygiene_match.txt
    fail=1
  else
    echo "PASS: absent as expected: $pattern"
  fi
}

check_present() {
  local pattern="$1"
  shift
  if grep -RInE "$pattern" "$@" >/tmp/rocm_hygiene_match.txt 2>/dev/null; then
    echo "PASS: required pattern present: $pattern"
  else
    echo "FAIL: required pattern missing: $pattern"
    fail=1
  fi
}

echo "== ROCm port hygiene checks =="

check_absent 'CHECK_CUDA|CHECK_CUSPARSE|CHECK_CUBLAS' \
  cupdlp/hip/*.cpp

check_absent 'plchip' \
  CMakeLists.txt cupdlp/CMakeLists.txt interface/CMakeLists.txt

check_absent 'CUDA_LIBRARY-NOTFOUND' \
  CMakeLists.txt cupdlp/CMakeLists.txt interface/CMakeLists.txt

check_present 'CHECK_HIP_STRICT' \
  cupdlp/hip/cupdlp_hip_kernels.h

check_present 'cuda_csr_Ax' \
  cupdlp/hip/cupdlp_hip_linalg.h cupdlp/hip/cupdlp_hip_linalg.cpp

check_present 'cuda_csc_ATy' \
  cupdlp/hip/cupdlp_hip_linalg.h cupdlp/hip/cupdlp_hip_linalg.cpp

check_present 'cuda_alloc_MVbuffer' \
  cupdlp/hip/cupdlp_hip_linalg.h cupdlp/hip/cupdlp_hip_linalg.cpp

if [[ "$fail" -ne 0 ]]; then
  echo "== ROCm port hygiene: FAIL =="
  exit 1
fi

echo "== ROCm port hygiene: PASS =="
