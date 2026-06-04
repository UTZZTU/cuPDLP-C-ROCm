from pathlib import Path

targets = [
    Path("cupdlp/hip/cupdlp_hip_kernels.cpp"),
    Path("cupdlp/hip/cupdlp_hip_linalg.cpp"),
]

replacements = [
    ("CHECK_CUDA_LAST()", "CHECK_HIP_LAST()"),
    ("CHECK_CUDA_IGNORE(", "CHECK_HIP_IGNORE("),
    ("CHECK_CUDA_STRICT(", "CHECK_HIP_STRICT("),
    ("CHECK_CUDA(", "CHECK_HIP("),

    ("CHECK_CUSPARSE_IGNORE(", "CHECK_HIPSPARSE_IGNORE("),
    ("CHECK_CUSPARSE_STRICT(", "CHECK_HIPSPARSE_STRICT("),
    ("CHECK_CUSPARSE(", "CHECK_HIPSPARSE("),

    ("CHECK_CUBLAS_IGNORE(", "CHECK_HIPBLAS_IGNORE("),
    ("CHECK_CUBLAS_STRICT(", "CHECK_HIPBLAS_STRICT("),
    ("CHECK_CUBLAS(", "CHECK_HIPBLAS("),
]

changed = []

for path in targets:
    if not path.exists():
        print(f"skip missing: {path}")
        continue

    text = path.read_text(encoding="utf-8")
    old_text = text

    for old, new in replacements:
        text = text.replace(old, new)

    if text != old_text:
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))
        print(f"updated: {path}")
    else:
        print(f"unchanged: {path}")

print("")
print("changed files:")
for item in changed:
    print(f"  {item}")
