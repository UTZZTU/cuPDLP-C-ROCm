from pathlib import Path

replacements = {
    "CMakeLists.txt": [
        (
            'option(BUILD_HIP "<BUILD_HIP_OR_NOT_LEGACY_ALIAS>" OFF)',
            'option(BUILD_HIP "<LEGACY_ALIAS_FOR_BUILD_ROCM>" OFF)',
        ),
        (
            'message(NOTICE "-- Sets build with HIP backend ${BUILD_HIP}")',
            'message(NOTICE "-- Sets build with ROCm/HIP backend ${BUILD_HIP}")',
        ),
        (
            'set(BUILD_HIP ON CACHE BOOL "Enable HIP backend implementation for ROCm" FORCE)',
            'set(BUILD_HIP ON CACHE BOOL "Enable ROCm/HIP backend implementation" FORCE)',
        ),
    ],
    "cupdlp/CMakeLists.txt": [
        (
            'message(NOTICE "- HIP version PDLP")',
            'message(NOTICE "- ROCm/HIP version PDLP")',
        ),
    ],
    "interface/CMakeLists.txt": [
        (
            'message(NOTICE "- HIP version PDLP")',
            'message(NOTICE "- ROCm/HIP version PDLP")',
        ),
    ],
}

changed_files = []

for file_name, reps in replacements.items():
    path = Path(file_name)
    if not path.exists():
        print(f"skip missing file: {file_name}")
        continue

    text = path.read_text(encoding="utf-8")
    old_text = text

    for old, new in reps:
        if old in text:
            text = text.replace(old, new)
        else:
            print(f"not found in {file_name}: {old}")

    if text != old_text:
        path.write_text(text, encoding="utf-8")
        changed_files.append(file_name)
        print(f"updated: {file_name}")
    else:
        print(f"unchanged: {file_name}")

print("")
print("summary:")
if changed_files:
    for file_name in changed_files:
        print(f"  changed {file_name}")
else:
    print("  no files changed")
