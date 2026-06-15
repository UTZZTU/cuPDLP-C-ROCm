from pathlib import Path

ASSET_DIR = Path("docs/assets/competition")
ASSET_DIR.mkdir(parents=True, exist_ok=True)
Path("scripts/docs").mkdir(parents=True, exist_ok=True)

project_architecture_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="520" viewBox="0 0 1180 520">
  <title>cuPDLP-C-ROCm project architecture</title>
  <desc>High-level project flow from CUDA upstream through ROCm/HIP migration, 890M tuning, W7900 validation, profiling, and final contest artifacts.</desc>
  <style>
    .box { fill: #f7f9fc; stroke: #2f4b7c; stroke-width: 2; rx: 12; }
    .box2 { fill: #eef7f1; stroke: #2e7d32; stroke-width: 2; rx: 12; }
    .box3 { fill: #fff8e1; stroke: #ef8f00; stroke-width: 2; rx: 12; }
    .text { font-family: Arial, Helvetica, sans-serif; font-size: 18px; fill: #1f2933; }
    .small { font-family: Arial, Helvetica, sans-serif; font-size: 14px; fill: #455a64; }
    .title { font-family: Arial, Helvetica, sans-serif; font-size: 24px; font-weight: 700; fill: #111827; }
    .arrow { stroke: #374151; stroke-width: 2.6; marker-end: url(#arrowhead); fill: none; }
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <path d="M 0 0 L 10 4 L 0 8 z" fill="#374151"/>
    </marker>
  </defs>

  <text class="title" x="40" y="42">cuPDLP-C-ROCm architecture and validation flow</text>

  <rect class="box" x="40" y="90" width="190" height="95"/>
  <text class="text" x="70" y="125">CUDA upstream</text>
  <text class="small" x="70" y="152">cuPDLP-C solver</text>
  <text class="small" x="70" y="172">CPU/CUDA reference</text>

  <path class="arrow" d="M 230 137 L 300 137"/>

  <rect class="box2" x="300" y="90" width="210" height="95"/>
  <text class="text" x="330" y="122">ROCm/HIP backend</text>
  <text class="small" x="330" y="150">HIP kernels + build path</text>
  <text class="small" x="330" y="170">hipBLAS / hipSPARSE</text>

  <path class="arrow" d="M 510 137 L 580 137"/>

  <rect class="box2" x="580" y="90" width="210" height="95"/>
  <text class="text" x="620" y="122">890M / gfx1150</text>
  <text class="small" x="620" y="150">first ROCm target</text>
  <text class="small" x="620" y="170">profiling + tuning history</text>

  <path class="arrow" d="M 790 137 L 860 137"/>

  <rect class="box2" x="860" y="90" width="245" height="95"/>
  <text class="text" x="900" y="122">W7900 / gfx1100</text>
  <text class="small" x="900" y="150">smoke + Netlib 27</text>
  <text class="small" x="900" y="170">non-hard23 large-MPS</text>

  <rect class="box3" x="120" y="285" width="225" height="110"/>
  <text class="text" x="150" y="318">Current evidence</text>
  <text class="small" x="150" y="346">23/23 non-hard OPTIMAL</text>
  <text class="small" x="150" y="366">hard3 tracked separately</text>
  <text class="small" x="150" y="386">current = post-890M tuning</text>

  <rect class="box3" x="470" y="285" width="245" height="110"/>
  <text class="text" x="505" y="318">Next W7900 runs</text>
  <text class="small" x="505" y="346">rocprof starter3</text>
  <text class="small" x="505" y="366">hard3 probe2</text>
  <text class="small" x="505" y="386">ae3b683 vs current core6</text>

  <rect class="box3" x="840" y="285" width="245" height="110"/>
  <text class="text" x="875" y="318">Contest artifacts</text>
  <text class="small" x="875" y="346">paper / PPT / video</text>
  <text class="small" x="875" y="366">reproducibility + Docker skeleton</text>
  <text class="small" x="875" y="386">curated CSV / Markdown</text>

  <path class="arrow" d="M 982 185 C 982 245, 245 235, 232 285"/>
  <path class="arrow" d="M 345 340 L 470 340"/>
  <path class="arrow" d="M 715 340 L 840 340"/>
</svg>
"""

evidence_map_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="620" viewBox="0 0 1180 620">
  <title>cuPDLP-C-ROCm evidence map</title>
  <desc>Repository evidence map linking contest requirements to source, validation, benchmark, reproducibility, and future profiling artifacts.</desc>
  <style>
    .hub { fill: #e8f0fe; stroke: #1a73e8; stroke-width: 2.5; rx: 16; }
    .node { fill: #ffffff; stroke: #5f6368; stroke-width: 2; rx: 12; }
    .future { fill: #fff8e1; stroke: #ef8f00; stroke-width: 2; rx: 12; }
    .text { font-family: Arial, Helvetica, sans-serif; font-size: 17px; fill: #202124; }
    .small { font-family: Arial, Helvetica, sans-serif; font-size: 13px; fill: #5f6368; }
    .title { font-family: Arial, Helvetica, sans-serif; font-size: 24px; font-weight: 700; fill: #111827; }
    .edge { stroke: #6b7280; stroke-width: 2; fill: none; }
  </style>

  <text class="title" x="40" y="42">Repository evidence map for ROCm/Radeon contest review</text>

  <rect class="hub" x="430" y="250" width="320" height="115"/>
  <text class="text" x="475" y="285">General ROCm/HIP project</text>
  <text class="small" x="475" y="314">cuPDLP-C migration, validation,</text>
  <text class="small" x="475" y="334">benchmarking, reproducibility</text>

  <rect class="node" x="60" y="90" width="275" height="100"/>
  <text class="text" x="95" y="122">Implementation evidence</text>
  <text class="small" x="95" y="150">source tree, HIP backend,</text>
  <text class="small" x="95" y="170">ROCm workflow, porting guide</text>

  <rect class="node" x="455" y="90" width="275" height="100"/>
  <text class="text" x="490" y="122">Validation evidence</text>
  <text class="small" x="490" y="150">smoke, Netlib 27, non-hard23,</text>
  <text class="small" x="490" y="170">curated CSV / Markdown</text>

  <rect class="node" x="845" y="90" width="275" height="100"/>
  <text class="text" x="880" y="122">Performance evidence</text>
  <text class="small" x="880" y="150">cross-device references,</text>
  <text class="small" x="880" y="170">W7900 behavior, tuning history</text>

  <rect class="node" x="60" y="430" width="275" height="105"/>
  <text class="text" x="95" y="462">Reproducibility evidence</text>
  <text class="small" x="95" y="490">bootstrap workflow, data policy,</text>
  <text class="small" x="95" y="510">Docker skeleton, case lists</text>

  <rect class="future" x="455" y="430" width="275" height="105"/>
  <text class="text" x="490" y="462">Pending W7900 evidence</text>
  <text class="small" x="490" y="490">rocprof starter3, hard3 probe2,</text>
  <text class="small" x="490" y="510">ae3b683/current core6</text>

  <rect class="node" x="845" y="430" width="275" height="105"/>
  <text class="text" x="880" y="462">Submission evidence</text>
  <text class="small" x="880" y="490">competition README, scorecard,</text>
  <text class="small" x="880" y="510">submission checklist, final report</text>

  <path class="edge" d="M 335 140 C 405 150, 410 260, 430 280"/>
  <path class="edge" d="M 592 190 L 592 250"/>
  <path class="edge" d="M 845 140 C 775 150, 770 260, 750 280"/>
  <path class="edge" d="M 335 485 C 405 470, 410 360, 430 335"/>
  <path class="edge" d="M 592 430 L 592 365"/>
  <path class="edge" d="M 845 485 C 775 470, 770 360, 750 335"/>
</svg>
"""

ASSET_DIR.joinpath("project_architecture.svg").write_text(project_architecture_svg)
ASSET_DIR.joinpath("evidence_map.svg").write_text(evidence_map_svg)

def add_after_line(path, anchor_line, new_lines):
    p = Path(path)
    lines = p.read_text().splitlines(keepends=True)
    if all(any(line.strip() == nl.strip() for line in lines) for nl in new_lines):
        print(f"{path}: already linked")
        return
    for i, line in enumerate(lines):
        if line.strip() == anchor_line.strip():
            insert = [nl if nl.endswith("\n") else nl + "\n" for nl in new_lines]
            lines[i + 1:i + 1] = insert
            p.write_text("".join(lines))
            print(f"{path}: linked")
            return
    raise SystemExit(f"{path}: anchor not found")

add_after_line(
    "docs/COMPETITION_README.md",
    "| Submission checklist | [Submission checklist](SUBMISSION_CHECKLIST.md) |",
    ["| Architecture assets | [project architecture](assets/competition/project_architecture.svg), [evidence map](assets/competition/evidence_map.svg) |"],
)

add_after_line(
    "docs/COMPETITION_README.zh-CN.md",
    "| 提交清单 | [提交清单](SUBMISSION_CHECKLIST.zh-CN.md) |",
    ["| 架构与证据图 | [项目架构图](assets/competition/project_architecture.svg), [证据地图](assets/competition/evidence_map.svg) |"],
)

add_after_line(
    "docs/SUBMISSION_CHECKLIST.md",
    "| Docker/container skeleton | Done as skeleton | [../docker/Dockerfile.w7900](../docker/Dockerfile.w7900), [../docker/README_DOCKER_W7900.md](../docker/README_DOCKER_W7900.md). This is an environment declaration skeleton, not the source of current W7900 performance numbers. |",
    ["| Project architecture and evidence map | Done | [project architecture](assets/competition/project_architecture.svg), [evidence map](assets/competition/evidence_map.svg) |"],
)

add_after_line(
    "docs/SUBMISSION_CHECKLIST.zh-CN.md",
    "| Docker/container 骨架 | 已提供骨架 | [../docker/Dockerfile.w7900](../docker/Dockerfile.w7900), [../docker/README_DOCKER_W7900.zh-CN.md](../docker/README_DOCKER_W7900.zh-CN.md)。这是环境声明骨架，不是当前 W7900 性能数字来源。 |",
    ["| 项目架构图与证据地图 | 已完成 | [项目架构图](assets/competition/project_architecture.svg), [证据地图](assets/competition/evidence_map.svg) |"],
)

print("wrote docs/assets/competition/project_architecture.svg")
print("wrote docs/assets/competition/evidence_map.svg")
print("done")
