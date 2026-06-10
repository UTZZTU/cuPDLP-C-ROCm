#!/usr/bin/env bash
set -e

export ROCM_PY_HOME=/opt/python
export ROCM_PY_CORE=/opt/python/lib/python3.12/site-packages/_rocm_sdk_core
export ROCM_PY_DEVEL=/opt/python/lib/python3.12/site-packages/_rocm_sdk_devel

export PATH=/opt/python/bin:${PATH}
export LD_LIBRARY_PATH=${ROCM_PY_DEVEL}/lib:${ROCM_PY_CORE}/lib:${LD_LIBRARY_PATH:-}

echo "Using W7900 Python ROCm SDK environment"
echo "hipcc: $(which hipcc)"
echo "rocm_agent_enumerator: $(which rocm_agent_enumerator)"
echo "ROCM_PY_CORE: ${ROCM_PY_CORE}"
echo "ROCM_PY_DEVEL: ${ROCM_PY_DEVEL}"
echo "LD_LIBRARY_PATH: ${LD_LIBRARY_PATH}"
