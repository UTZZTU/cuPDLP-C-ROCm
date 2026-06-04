from pathlib import Path

files = [
    Path("README.md"),
    Path("README_ROCM_gfx1150.md"),
    Path("docs/PORTING_GUIDE_ROCM_HIP.md"),
    Path("docs/VALIDATION.md"),
    Path("docs/TUNING_GUIDE_ROCM.md"),
]

replacements = [
    ("build-hip-plc", "build-rocm-plc"),
    ("-DBUILD_HIP=ON", "-DBUILD_ROCM=ON"),
    ("BUILD_HIP=ON", "BUILD_ROCM=ON"),
    ("`BUILD_HIP`", "`BUILD_ROCM`"),
    ("including BUILD_HIP", "including BUILD_ROCM"),
    ("Added `BUILD_HIP` CMake option.", "Added `BUILD_ROCM` CMake option."),
]

changed = []

for path in files:
    if not path.exists():
        print(f"skip missing file: {path}")
        continue

    text = path.read_text()
    old_text = text

    for old, new in replacements:
        text = text.replace(old, new)

    if path.name == "README.md":
        note = (
            "\n## Build option compatibility\n\n"
            "`BUILD_ROCM=ON` is the recommended build option for the ROCm/HIP backend.\n\n"
            "`BUILD_HIP=ON` is kept as a legacy compatibility alias because the current ROCm backend is implemented with HIP, hipBLAS, and hipSPARSE.\n"
        )
        if "## Build option compatibility" not in text:
            marker = "\n## Porting notes\n"
            if marker in text:
                text = text.replace(marker, note + marker)
            else:
                text += note

    if path == Path("docs/PORTING_GUIDE_ROCM_HIP.md"):
        note = (
            "\n### BUILD_ROCM and BUILD_HIP\n\n"
            "`BUILD_ROCM=ON` is the recommended public build option for this repository.\n\n"
            "`BUILD_HIP=ON` is kept as a legacy compatibility alias. Internally, the ROCm backend is still implemented with HIP, hipBLAS, and hipSPARSE.\n"
        )
        if "### BUILD_ROCM and BUILD_HIP" not in text:
            marker = "\n## 9. Host-side code adaptation\n"
            if marker in text:
                text = text.replace(marker, note + marker)
            else:
                text += note

    if text != old_text:
        path.write_text(text)
        changed.append(str(path))
        print(f"updated: {path}")
    else:
        print(f"unchanged: {path}")

print("")
print("summary:")
if changed:
    for path in changed:
        print(f"  changed {path}")
else:
    print("  no files changed")
