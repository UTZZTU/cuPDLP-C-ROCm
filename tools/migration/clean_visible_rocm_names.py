from pathlib import Path

REPLACEMENTS = {
    "cupdlp/hip/cupdlp_hip_kernels.h": [
        ("CUPDLP_CUDA_KERNALS_H", "CUPDLP_HIP_KERNELS_H"),
        ("CUDA API failed", "HIP API failed"),
        ("CUBLAS API failed", "hipBLAS API failed"),
        ("CUSPARSE API failed", "hipSPARSE API failed"),
    ],
    "cupdlp/hip/cupdlp_hip_linalg.h": [
        ("CUPDLP_CUDA_LINALG_H", "CUPDLP_HIP_LINALG_H"),
        ("// cublas", "// hipBLAS"),
        ("// cudaMalloc, cudaMemcpy, etc.", "// hipMalloc, hipMemcpy, etc."),
        ("// hipsparseSpMV", "// hipSPARSE SpMV"),
    ],
    "cupdlp/hip/cupdlp_hip_linalg.cpp": [
        ("v_cuda_driver", "v_hip_driver"),
        ("v_cusparse", "v_hipsparse"),
        ("cusparseSpSVAlg_t", "hipsparseSpSVAlg_t"),
        ("CUSPARSE_SPSV_ALG_DEFAULT", "HIPSPARSE_SPSV_ALG_DEFAULT"),
    ],
    "cupdlp/cupdlp_linalg.h": [
        ("// functions in cublas", "// functions in hipBLAS"),
        ("// functions not in cublas", "// functions not in hipBLAS"),
    ],
    "cupdlp/cupdlp_linalg.c": [
        ("// functions in cublas", "// functions in hipBLAS"),
        ("// functions not in cublas", "// functions not in hipBLAS"),
    ],
}

changed = []

for file_name, replacements in REPLACEMENTS.items():
    path = Path(file_name)

    if not path.exists():
        print(f"skip missing file: {file_name}")
        continue

    text = path.read_text()
    old_text = text

    for old, new in replacements:
        text = text.replace(old, new)

    if text != old_text:
        path.write_text(text)
        changed.append(file_name)
        print(f"updated: {file_name}")
    else:
        print(f"unchanged: {file_name}")

print("")
print("summary:")
if changed:
    for file_name in changed:
        print(f"  changed {file_name}")
else:
    print("  no files changed")
