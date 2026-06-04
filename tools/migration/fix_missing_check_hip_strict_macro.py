from pathlib import Path

path = Path("cupdlp/hip/cupdlp_hip_kernels.h")
text = path.read_text(encoding="utf-8")
old_text = text

# Rename the primary strict HIP runtime macro definition if it is still using
# the legacy CUDA-style name.
text = text.replace(
    "#define CHECK_CUDA_STRICT(res) \\",
    "#define CHECK_HIP_STRICT(res) \\"
)

# If the non-strict and ignore HIP macros exist but strict is somehow missing,
# insert CHECK_HIP_STRICT after CHECK_HIP.
if "#define CHECK_HIP_STRICT(res)" not in text and "#define CHECK_HIP(res)" in text:
    marker = "#define CHECK_HIP_IGNORE(res)"
    strict_block = (
        "#define CHECK_HIP_STRICT(res) \\\n"
        "  { if (check_hip_call(res, __FILE__, __LINE__) != hipSuccess) \\\n"
        "    exit(EXIT_FAILURE); }\n\n"
    )
    text = text.replace(marker, strict_block + marker)

# Add legacy alias for CHECK_CUDA_STRICT if missing.
if "#define CHECK_CUDA_STRICT(res) CHECK_HIP_STRICT(res)" not in text:
    marker = (
        "#ifndef CHECK_CUDA_IGNORE\n"
        "#define CHECK_CUDA_IGNORE(res) CHECK_HIP_IGNORE(res)\n"
        "#endif\n"
    )
    replacement = (
        "#ifndef CHECK_CUDA_STRICT\n"
        "#define CHECK_CUDA_STRICT(res) CHECK_HIP_STRICT(res)\n"
        "#endif\n\n"
        + marker
    )
    text = text.replace(marker, replacement)

if text != old_text:
    path.write_text(text, encoding="utf-8")
    print(f"updated {path}")
else:
    print("no changes made")
