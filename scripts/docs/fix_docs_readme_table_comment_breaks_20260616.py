#!/usr/bin/env python3
from pathlib import Path

p = Path("docs/README.md")
text = p.read_text()

# These marker comments were useful for earlier scripted insertion,
# but inside Markdown tables they can break GitHub table rendering.
remove_markers = [
    "<!-- REPRODUCIBILITY_20260614_BEGIN -->",
    "<!-- REPRODUCIBILITY_20260614_END -->",
    "<!-- COMPETITION_README_20260614_BEGIN -->",
    "<!-- COMPETITION_README_20260614_END -->",
    "<!-- W7900_LARGE_MPS_HARD3_NOTES_20260614_BEGIN -->",
    "<!-- W7900_LARGE_MPS_HARD3_NOTES_20260614_END -->",
    "<!-- W7900_OPTIMIZATION_BASELINES_20260614_BEGIN -->",
    "<!-- W7900_OPTIMIZATION_BASELINES_20260614_END -->",
    "<!-- W7900_ROCM_PROFILING_PLAN_20260614_BEGIN -->",
    "<!-- W7900_ROCM_PROFILING_PLAN_20260614_END -->",
    "<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_BEGIN -->",
    "<!-- W7900_PERFORMANCE_BEHAVIOR_20260614_END -->",
    "<!-- W7900_CURRENT_STATUS_20260614_BEGIN -->",
    "<!-- W7900_CURRENT_STATUS_20260614_END -->",
    "<!-- W7900_NONHARD23_20260614_BEGIN -->",
    "<!-- W7900_NONHARD23_20260614_END -->",
    "<!-- LARGE_MPS_CUDA_ROCM_BASELINE_20260614_BEGIN -->",
    "<!-- LARGE_MPS_CUDA_ROCM_BASELINE_20260614_END -->",
]

changed = False
for marker in remove_markers:
    if marker in text:
        text = text.replace(marker + "\n", "")
        text = text.replace(marker, "")
        changed = True

if not changed:
    print("docs/README.md: no table-breaking markers found")
else:
    p.write_text(text)
    print("docs/README.md: removed table-breaking marker comments")
