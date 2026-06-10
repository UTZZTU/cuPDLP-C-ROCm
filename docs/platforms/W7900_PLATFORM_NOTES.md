# Radeon PRO W7900 Platform Notes

Date: 2026-06-10
Host: nb-d2799099
Project branch: rocm-w7900-gfx1100
Base branch: rocm-gfx1150

## Goal

Port the existing cuPDLP-C ROCm/HIP backend from the gfx1150 validation target to the Radeon PRO W7900 / gfx1100 platform.

This first stage focuses only on buildability and correctness smoke validation. Performance tuning is intentionally deferred.

## Directory layout

Project root on this machine:

/root/cupdlp_w7900

Repository path:

/root/cupdlp_w7900/src/cuPDLP-C-ROCm

Suggested local layout:

/root/cupdlp_w7900/
- src/
- build/
- datasets/
- logs/
- notes/
- results/

## CPU and memory

Observed platform:

- CPU: 2x AMD EPYC 9334 32-Core Processor
- Logical CPUs: 128
- Sockets: 2
- Cores per socket: 32
- Threads per core: 2
- NUMA nodes: 2
- Memory: about 1.0 TiB

NUMA layout:

- NUMA node 0 CPUs: 0-31,64-95
- NUMA node 1 CPUs: 32-63,96-127

## GPU layout

The system exposes one onboard ASPEED VGA device and eight AMD GPUs.

- card0: ASPEED onboard VGA
- card1-card8: AMD GPUs
- AMD GPU PCI ID: 1002:744B
- AMD GPU subsystem device: 0x0e0c
- Kernel driver: amdgpu
- Expected ROCm target: gfx1100

NUMA node 0 GPUs:

| DRM card | PCI slot |
|---|---|
| card1 | 0000:03:00.0 |
| card2 | 0000:23:00.0 |
| card3 | 0000:43:00.0 |
| card4 | 0000:63:00.0 |

NUMA node 1 GPUs:

| DRM card | PCI slot |
|---|---|
| card5 | 0000:83:00.0 |
| card6 | 0000:a3:00.0 |
| card7 | 0000:c3:00.0 |
| card8 | 0000:e3:00.0 |

## Current ROCm state before repair

GPU kernel devices are visible:

- /dev/kfd exists
- /dev/dri exists
- card1-card8 are bound to amdgpu

However, the official /opt/rocm development stack is missing:

- /opt/rocm/bin/hipcc: missing
- /opt/rocm/bin/rocminfo: missing
- /opt/rocm/bin/rocm_agent_enumerator: missing
- /opt/rocm/bin/rocm-smi: missing

Currently observed ROCm-related packages are old Ubuntu runtime packages:

- libamdhip64-5 5.7.1
- libhsa-runtime64-1 5.7.1
- libhsakmt1 5.7.0
- libamd-comgr2
- libdrm-amdgpu1

The following tools exist under /opt/python/bin, but they are treated as Python/vLLM environment tools rather than the official system ROCm development stack:

- /opt/python/bin/hipcc
- /opt/python/bin/rocminfo
- /opt/python/bin/rocm_agent_enumerator
- /opt/python/bin/rocm-smi

## Git setup notes

The repository was cloned from:

https://github.com/UTZZTU/cuPDLP-C-ROCm.git

The working branch is:

rocm-w7900-gfx1100

The pybind11 submodule originally used this SSH URL:

ssh://git@ssh.github.com:443/pybind/pybind11.git

This failed on the remote machine because no GitHub SSH key was configured. The submodule URL was changed to HTTPS:

https://github.com/pybind/pybind11.git

Commit already created:

5d93812 use https URL for pybind11 submodule

## Current diagnosis

The machine has visible AMD GPU kernel devices and the amdgpu driver is bound to all eight AMD GPUs. However, the official ROCm development stack under /opt/rocm is missing.

Before building cuPDLP-C, install or repair the official ROCm userspace development environment and confirm that rocminfo and rocm_agent_enumerator report gfx1100.

## First-stage acceptance criteria

- /opt/rocm/bin/hipcc exists and reports a valid ROCm version.
- /opt/rocm/bin/rocminfo works.
- /opt/rocm/bin/rocm_agent_enumerator reports gfx1100.
- CPU baseline build succeeds.
- ROCm/HIP build succeeds with CMAKE_HIP_ARCHITECTURES=gfx1100.
- example/afiro.mps runs successfully on ROCm.
- Repository smoke validation passes.

## Next steps

1. Install or repair the official ROCm userspace development stack under /opt/rocm.
2. Confirm rocminfo and rocm_agent_enumerator report gfx1100.
3. Build CPU baseline.
4. Build ROCm/HIP version with CMAKE_HIP_ARCHITECTURES=gfx1100.
5. Run smoke validation on example/afiro.mps.
6. Run repository validation scripts.
7. Commit the W7900 platform notes, build commands, and validation results.
