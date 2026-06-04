from pathlib import Path

path = Path("cupdlp/hip/cupdlp_hip_kernels.h")

text = path.read_text(encoding="utf-8")
old_text = text

# Rename function-like helper names only inside the HIP backend header.
replacements = [
    ("check_cuda_call", "check_hip_call"),
    ("check_cuda_last", "check_hip_last"),
    ("check_cusparse_call", "check_hipsparse_call"),
    ("check_cublas_call", "check_hipblas_call"),

    ("CHECK_CUDA(res)", "CHECK_HIP(res)"),
    ("CHECK_CUDA_IGNORE(res)", "CHECK_HIP_IGNORE(res)"),
    ("CHECK_CUDA_LAST()", "CHECK_HIP_LAST()"),

    ("CHECK_CUSPARSE(res)", "CHECK_HIPSPARSE(res)"),
    ("CHECK_CUSPARSE_STRICT(res)", "CHECK_HIPSPARSE_STRICT(res)"),
    ("CHECK_CUSPARSE_IGNORE(res)", "CHECK_HIPSPARSE_IGNORE(res)"),

    ("CHECK_CUBLAS(res)", "CHECK_HIPBLAS(res)"),
    ("CHECK_CUBLAS_STRICT(res)", "CHECK_HIPBLAS_STRICT(res)"),
    ("CHECK_CUBLAS_IGNORE(res)", "CHECK_HIPBLAS_IGNORE(res)"),
]

for old, new in replacements:
    text = text.replace(old, new)

# Add legacy aliases after the new HIP macro definitions.
alias_block = r"""
/*
 * Legacy CUDA-style macro aliases.
 *
 * These aliases keep existing host-side call sites working while the ROCm/HIP
 * port is being cleaned up incrementally. New HIP backend code should prefer
 * CHECK_HIP, CHECK_HIPSPARSE, and CHECK_HIPBLAS.
 */
#ifndef CHECK_CUDA
#define CHECK_CUDA(res) CHECK_HIP(res)
#endif
#ifndef CHECK_CUDA_IGNORE
#define CHECK_CUDA_IGNORE(res) CHECK_HIP_IGNORE(res)
#endif
#ifndef CHECK_CUDA_LAST
#define CHECK_CUDA_LAST() CHECK_HIP_LAST()
#endif

#ifndef CHECK_CUSPARSE
#define CHECK_CUSPARSE(res) CHECK_HIPSPARSE(res)
#endif
#ifndef CHECK_CUSPARSE_STRICT
#define CHECK_CUSPARSE_STRICT(res) CHECK_HIPSPARSE_STRICT(res)
#endif
#ifndef CHECK_CUSPARSE_IGNORE
#define CHECK_CUSPARSE_IGNORE(res) CHECK_HIPSPARSE_IGNORE(res)
#endif

#ifndef CHECK_CUBLAS
#define CHECK_CUBLAS(res) CHECK_HIPBLAS(res)
#endif
#ifndef CHECK_CUBLAS_STRICT
#define CHECK_CUBLAS_STRICT(res) CHECK_HIPBLAS_STRICT(res)
#endif
#ifndef CHECK_CUBLAS_IGNORE
#define CHECK_CUBLAS_IGNORE(res) CHECK_HIPBLAS_IGNORE(res)
#endif
"""

if "Legacy CUDA-style macro aliases." not in text:
    # Insert before the final include guard close if possible.
    lines = text.splitlines()
    insert_at = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("#endif"):
            insert_at = i
            break

    if insert_at is None:
        text = text.rstrip() + "\n" + alias_block + "\n"
    else:
        lines.insert(insert_at, alias_block)
        text = "\n".join(lines) + "\n"

if text != old_text:
    path.write_text(text, encoding="utf-8")
    print(f"updated {path}")
else:
    print("no changes made")
