#!/usr/bin/env python3
from pathlib import Path

root = Path(".")
linalg_cpp = root / "cupdlp/hip/cupdlp_hip_linalg.cpp"
kernels_cpp = root / "cupdlp/hip/cupdlp_hip_kernels.cpp"
kernels_h = root / "cupdlp/hip/cupdlp_hip_kernels.h"

for path in (linalg_cpp, kernels_cpp, kernels_h):
    if not path.exists():
        raise SystemExit(f"missing file: {path}")

# 1) Add kernel declaration.
h = kernels_h.read_text(encoding="utf-8")

decl_anchor = "__global__ void sum_kernel(cupdlp_float * __restrict__ res, const cupdlp_float * __restrict__ x, int n);\n"
decl_new = (
    decl_anchor
    + "\n__global__ void save_movement_xy_kernel(cupdlp_float * __restrict__ dst,\n"
    + "                                       const cupdlp_float * __restrict__ x_norm,\n"
    + "                                       const cupdlp_float * __restrict__ interaction);\n"
)

if "save_movement_xy_kernel" not in h:
    if decl_anchor not in h:
        raise SystemExit("could not find sum_kernel declaration anchor in cupdlp_hip_kernels.h")
    h = h.replace(decl_anchor, decl_new, 1)
    kernels_h.write_text(h, encoding="utf-8")
    print(f"updated {kernels_h}")
else:
    print(f"skip {kernels_h}: save_movement_xy_kernel already present")

# 2) Add kernel definition.
cpp = kernels_cpp.read_text(encoding="utf-8")

definition = """
__global__ void save_movement_xy_kernel(cupdlp_float * __restrict__ dst,
                                        const cupdlp_float * __restrict__ x_norm,
                                        const cupdlp_float * __restrict__ interaction) {
  dst[0] = x_norm[0];
  dst[1] = interaction[0];
}
"""

if "save_movement_xy_kernel" not in cpp:
    sum_def_start = cpp.find("__global__ void sum_kernel(")
    if sum_def_start == -1:
        raise SystemExit("could not find sum_kernel definition anchor in cupdlp_hip_kernels.cpp")

    next_global = cpp.find("\n__global__ void", sum_def_start + 1)
    if next_global == -1:
        cpp = cpp.rstrip() + "\n" + definition + "\n"
    else:
        cpp = cpp[:next_global] + "\n" + definition + cpp[next_global:]

    kernels_cpp.write_text(cpp, encoding="utf-8")
    print(f"updated {kernels_cpp}")
else:
    print(f"skip {kernels_cpp}: save_movement_xy_kernel already present")

# 3) Replace only the first two scalar D2D copies in cupdlp_movement_interaction_cuda.
l = linalg_cpp.read_text(encoding="utf-8")

old = """  CHECK_HIP_STRICT(hipMemcpyAsync(buf_5 + 0, buf_1, sizeof(cupdlp_float), hipMemcpyDeviceToDevice))
  CHECK_HIP_STRICT(hipMemcpyAsync(buf_5 + 1, buf_2, sizeof(cupdlp_float), hipMemcpyDeviceToDevice))

  nBlocks = nBlocksRows;
"""

new = """  save_movement_xy_kernel<<<1, 1>>>(buf_5, buf_1, buf_2);

  nBlocks = nBlocksRows;
"""

if old in l:
    l = l.replace(old, new, 1)
elif "save_movement_xy_kernel<<<1, 1>>>(buf_5, buf_1, buf_2);" in l:
    print(f"skip {linalg_cpp}: movement xy copy replacement already applied")
else:
    raise SystemExit("could not find first two scalar D2D copy block in cupdlp_hip_linalg.cpp")

# Defensive check: keep the third D2D copy and final D2H copy in place.
required = [
    "CHECK_HIP_STRICT(hipMemcpyAsync(buf_5 + 2, buf_1, sizeof(cupdlp_float), hipMemcpyDeviceToDevice))",
    "CHECK_HIP_STRICT(hipMemcpy(res, buf_5, 3 * sizeof(cupdlp_float), hipMemcpyDeviceToHost))",
]
missing = [item for item in required if item not in l]
if missing:
    raise SystemExit("defensive check failed; expected final y/result copies to remain unchanged")

linalg_cpp.write_text(l, encoding="utf-8")
print(f"updated {linalg_cpp}")
print("done")
