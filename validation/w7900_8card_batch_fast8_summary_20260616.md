# W7900 8-card fast8 batch throughput summary

Concurrent result directory: `/app/cupdlp_w7900/results/w7900_8card_batch_fast8_rocr_only_900s_fast8_rocr_only_20260616_191934`
Single-GPU sequential result directory: `/app/cupdlp_w7900/results/w7900_single_gpu_sequential_fast8_900s_fast8_seq_gpu0_20260616_192355`

This is a compact summary of the W7900 independent-MPS batch throughput experiment. The experiment compares 8 independent MPS cases executed concurrently on 8 W7900 GPUs against the same 8 cases executed sequentially on one W7900 GPU.

## Case list

- `set-cover-model.mps`
- `square41.mps`
- `thk_48.mps`
- `tpl-tub-ws1617.mps`
- `L2CTA3D.mps`
- `rmine15.mps`
- `qap15.mps`
- `graph40-40.mps`

## Throughput summary

| Metric | Value |
|---|---:|
| 8-card concurrent makespan seconds | 146 |
| single-GPU sequential makespan seconds | 558 |
| makespan speedup | 3.821918x |
| 8-card efficiency | 0.477740 |
| concurrent cases per hour | 197.260274 |
| sequential cases per hour | 51.612903 |

## Per-case comparison

| case | concurrent_gpu | concurrent_status | sequential_status | concurrent_wall_seconds | sequential_wall_seconds | concurrent_termination | sequential_termination |
|---|---|---|---|---|---|---|---|
| L2CTA3D | 4 | DONE | DONE | 93 | 75 | OPTIMAL | OPTIMAL |
| graph40-40 | 7 | DONE | DONE | 4 | 5 | OPTIMAL | OPTIMAL |
| qap15 | 6 | DONE | DONE | 1 | 1 | OPTIMAL | OPTIMAL |
| rmine15 | 5 | DONE | DONE | 31 | 31 | OPTIMAL | OPTIMAL |
| set-cover-model | 0 | DONE | DONE | 38 | 46 | OPTIMAL | OPTIMAL |
| square41 | 1 | DONE | DONE | 123 | 126 | OPTIMAL | OPTIMAL |
| thk_48 | 2 | DONE | DONE | 146 | 155 | OPTIMAL | OPTIMAL |
| tpl-tub-ws1617 | 3 | DONE | DONE | 123 | 119 | OPTIMAL | OPTIMAL |

## Interpretation

- Both the 8-card concurrent run and the single-GPU sequential run solved all 8 cases to `OPTIMAL`.
- The measured batch makespan improved from `558s` to `146s`, giving a measured makespan speedup of `3.82x`.
- This demonstrates the throughput value of the 8x W7900 node for batches of independent LP/MPS workloads.
- This is an independent-task throughput result, not a claim that one MPS instance is accelerated across 8 GPUs.
- GPU binding used `ROCR_VISIBLE_DEVICES` only; the earlier attempt that combined HIP and ROCR visibility filters failed and is intentionally not summarized as a result.

## Repository policy

Commit only compact CSV and Markdown summaries. Raw large-MPS files and raw run directories stay outside Git.
