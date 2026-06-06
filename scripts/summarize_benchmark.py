#!/usr/bin/env python3
import csv
import json
import pathlib
import sys

root = pathlib.Path.home() / "rocm_dir/pdlp/cuPDLP-C-ROCm"

if len(sys.argv) > 1:
    run_dir = pathlib.Path(sys.argv[1]).expanduser()
else:
    latest_file = root / "validation/results/latest_run.txt"
    run_dir = pathlib.Path(latest_file.read_text().strip())

rows = []

for case_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
    name = case_dir.name
    cpu_json = case_dir / f"{name}_cpu.json"
    gpu_json = case_dir / f"{name}_rocm.json"

    def load(path):
        if not path.exists():
            return {}
        return json.loads(path.read_text())

    cpu = load(cpu_json)
    gpu = load(gpu_json)

    row = {
        "case": name,
        "cpu_status": cpu.get("terminationCode", ""),
        "rocm_status": gpu.get("terminationCode", ""),
        "cpu_iter": cpu.get("nIter", ""),
        "rocm_iter": gpu.get("nIter", ""),
        "cpu_time": cpu.get("dSolvingTime", ""),
        "rocm_time": gpu.get("dSolvingTime", ""),
        "cpu_over_rocm": "",
        "rocm_over_cpu": "",
        "cpu_rel_primal": cpu.get("dRelPrimalFeas", ""),
        "rocm_rel_primal": gpu.get("dRelPrimalFeas", ""),
        "cpu_rel_dual": cpu.get("dRelDualFeas", ""),
        "rocm_rel_dual": gpu.get("dRelDualFeas", ""),
        "cpu_rel_gap": cpu.get("dRelDualityGap", ""),
        "rocm_rel_gap": gpu.get("dRelDualityGap", ""),
        "rocm_matvec_time": gpu.get("DeviceMatVecProdTime", ""),
        "rocm_copy_mat_time": gpu.get("AllocMem_CopyMatToDeviceTime", ""),
        "rocm_copy_vec_time": gpu.get("CopyVecToDeviceTime", ""),
    }

    try:
        ct = float(row["cpu_time"])
        gt = float(row["rocm_time"])
        if gt > 0:
            row["cpu_over_rocm"] = ct / gt
        if ct > 0:
            row["rocm_over_cpu"] = gt / ct
    except Exception:
        pass

    rows.append(row)

out_csv = run_dir / "summary.csv"
out_md = run_dir / "summary.md"

fields = [
    "case",
    "cpu_status",
    "rocm_status",
    "cpu_iter",
    "rocm_iter",
    "cpu_time",
    "rocm_time",
    "cpu_over_rocm",
    "rocm_over_cpu",
    "cpu_rel_primal",
    "rocm_rel_primal",
    "cpu_rel_dual",
    "rocm_rel_dual",
    "cpu_rel_gap",
    "rocm_rel_gap",
    "rocm_matvec_time",
    "rocm_copy_mat_time",
    "rocm_copy_vec_time",
]

with out_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

def fmt(x):
    if x == "":
        return ""
    if isinstance(x, float):
        return f"{x:.6g}"
    return str(x)

with out_md.open("w") as f:
    f.write("# Benchmark summary\n\n")
    f.write(f"Run dir: `{run_dir}`\n\n")
    f.write("| case | CPU status | ROCm status | CPU iter | ROCm iter | CPU time | ROCm time | CPU/ROCm | ROCm/CPU slowdown |\n")
    f.write("|---|---|---|---:|---:|---:|---:|---:|---:|\n")
    for r in rows:
        f.write(
            f"| {r['case']} | {r['cpu_status']} | {r['rocm_status']} | "
            f"{r['cpu_iter']} | {r['rocm_iter']} | "
            f"{fmt(r['cpu_time'])} | {fmt(r['rocm_time'])} | "
            f"{fmt(r['cpu_over_rocm'])} | {fmt(r['rocm_over_cpu'])} |\n"
        )

print(f"summary csv: {out_csv}")
print(f"summary md:  {out_md}")
