#!/usr/bin/env bash
set -e

export ROCM_PY_HOME=/opt/python
export ROCM_PY_CORE=/opt/python/lib/python3.12/site-packages/_rocm_sdk_core
export ROCM_PY_DEVEL=/opt/python/lib/python3.12/site-packages/_rocm_sdk_devel

export HIGHS_HOME=${HIGHS_HOME:-/app/cupdlp_w7900/deps/install/highs-1.6.0}

export PATH=/opt/python/bin:${PATH}
export LD_LIBRARY_PATH=${ROCM_PY_DEVEL}/lib:${ROCM_PY_CORE}/lib:${HIGHS_HOME}/lib:${LD_LIBRARY_PATH:-}
export CMAKE_PREFIX_PATH=${ROCM_PY_DEVEL}:${CMAKE_PREFIX_PATH:-}

export W7900_ROCM_CMAKE_FLAGS="-DCMAKE_PREFIX_PATH=${ROCM_PY_DEVEL} -DCMAKE_C_FLAGS=-I${ROCM_PY_DEVEL}/include -DCMAKE_CXX_FLAGS=-I${ROCM_PY_DEVEL}/include -DCMAKE_HIP_FLAGS=-I${ROCM_PY_DEVEL}/include"

echo "Using W7900 Python ROCm SDK environment"
echo "hipcc: $(which hipcc)"
echo "rocm_agent_enumerator: $(which rocm_agent_enumerator)"
echo "ROCM_PY_CORE: ${ROCM_PY_CORE}"
echo "ROCM_PY_DEVEL: ${ROCM_PY_DEVEL}"
echo "HIGHS_HOME: ${HIGHS_HOME}"
echo "CMAKE_PREFIX_PATH: ${CMAKE_PREFIX_PATH}"
