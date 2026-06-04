from pathlib import Path

targets = [
    Path("cupdlp/hip/cupdlp_hip_linalg.cpp"),
    Path("cupdlp/hip/cupdlp_hip_linalg.h"),
]

replacements = [
    # Restore exported cross-language function names.
    # Host-side C files still call these legacy names.
    ("hip_csc_Ax", "cuda_csc_Ax"),
    ("hip_csr_Ax", "cuda_csr_Ax"),
    ("hip_csc_ATy", "cuda_csc_ATy"),
    ("hip_csr_ATy", "cuda_csr_ATy"),
    ("hip_alloc_MVbuffer", "cuda_alloc_MVbuffer"),
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
