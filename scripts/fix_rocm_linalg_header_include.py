from pathlib import Path

path = Path("cupdlp/cupdlp_linalg.h")

if not path.exists():
    raise SystemExit(f"missing file: {path}")

text = path.read_text()
old_text = text

patterns = [
    (
        '''#if !(CUPDLP_CPU)
#include "cuda/cupdlp_cudalinalg.cuh"
#endif''',
        '''#if defined(CUPDLP_USE_HIP)
#include "hip/cupdlp_hip_linalg.h"
#elif !(CUPDLP_CPU)
#include "cuda/cupdlp_cudalinalg.cuh"
#endif'''
    ),
    (
        '''#if !(CUPDLP_CPU)
#include "cuda/cupdlp_cudalinalg.cuh"
#endif  // !(CUPDLP_CPU)''',
        '''#if defined(CUPDLP_USE_HIP)
#include "hip/cupdlp_hip_linalg.h"
#elif !(CUPDLP_CPU)
#include "cuda/cupdlp_cudalinalg.cuh"
#endif  // GPU backend'''
    ),
]

changed = False

for old, new in patterns:
    if old in text:
        text = text.replace(old, new)
        changed = True

if not changed:
    print("Known include block not found. Current first 40 lines:")
    print("-" * 60)
    print("\n".join(text.splitlines()[:40]))
    print("-" * 60)
    raise SystemExit("Please inspect cupdlp/cupdlp_linalg.h manually.")

path.write_text(text)

print(f"updated: {path}")
