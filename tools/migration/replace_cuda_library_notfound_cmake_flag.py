from pathlib import Path

top = Path("CMakeLists.txt")
cupdlp = Path("cupdlp/CMakeLists.txt")
interface = Path("interface/CMakeLists.txt")

# Top-level CMakeLists.txt
s = top.read_text(encoding="utf-8")
old = s

marker = "list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})\n"
insert = (
    "list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})\n\n"
    "# Internal selector for the legacy CUDA backend.\n"
    "# CPU and ROCm/HIP builds keep this OFF.\n"
    "set(CUPDLP_USE_LEGACY_CUDA OFF)\n"
)

if "set(CUPDLP_USE_LEGACY_CUDA OFF)" not in s:
    s = s.replace(marker, insert)

s = s.replace(
    "include(FindCUDAConf.cmake)",
    "include(FindCUDAConf.cmake)\n    set(CUPDLP_USE_LEGACY_CUDA ON)"
)

# These old assignments were used as an inverted CPU/non-CUDA selector.
# They are no longer needed after introducing CUPDLP_USE_LEGACY_CUDA.
s = s.replace("    set(CUDA_LIBRARY-NOTFOUND true)\n", "")

if s != old:
    top.write_text(s, encoding="utf-8")
    print("updated CMakeLists.txt")
else:
    print("unchanged CMakeLists.txt")

# Subdirectory CMakeLists files
for path in [cupdlp, interface]:
    s = path.read_text(encoding="utf-8")
    old = s

    s = s.replace(
        "elseif (${CUDA_LIBRARY-NOTFOUND})",
        "elseif (NOT CUPDLP_USE_LEGACY_CUDA)"
    )

    if s != old:
        path.write_text(s, encoding="utf-8")
        print(f"updated {path}")
    else:
        print(f"unchanged {path}")
