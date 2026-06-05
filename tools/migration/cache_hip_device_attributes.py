#!/usr/bin/env python3
from pathlib import Path

path = Path("cupdlp/hip/cupdlp_hip_linalg.cpp")
if not path.exists():
    raise SystemExit(f"missing file: {path}")

text = path.read_text(encoding="utf-8")

old_nblocks = """inline int nBlocks256(int n) {
  constexpr int BLOCKS_PER_SM = 32;
  int numSMs;
  CHECK_HIP_IGNORE(hipDeviceGetAttribute(&numSMs, hipDeviceAttributeMultiprocessorCount, 0))
  return std::min((n + 256 - 1) / 256, BLOCKS_PER_SM * numSMs);
}
"""

new_nblocks = """inline int cupdlp_get_hip_device_attribute_cached(hipDeviceAttribute_t attr,
                                                 int fallback) {
  int value = fallback;
  CHECK_HIP_IGNORE(hipDeviceGetAttribute(&value, attr, 0))
  return value > 0 ? value : fallback;
}

inline int cupdlp_get_hip_num_sms() {
  static const int numSMs = cupdlp_get_hip_device_attribute_cached(
      hipDeviceAttributeMultiprocessorCount, 1);
  return numSMs;
}

inline int cupdlp_get_hip_warp_size() {
  static const int warpSize = cupdlp_get_hip_device_attribute_cached(
      hipDeviceAttributeWarpSize, 32);
  return warpSize;
}

inline int nBlocks256(int n) {
  constexpr int BLOCKS_PER_SM = 32;
  return std::min((n + 256 - 1) / 256, BLOCKS_PER_SM * cupdlp_get_hip_num_sms());
}
"""

if old_nblocks in text:
    text = text.replace(old_nblocks, new_nblocks, 1)
elif "inline int cupdlp_get_hip_num_sms()" in text:
    print("skip nBlocks256 cache block: already applied")
else:
    raise SystemExit("could not find nBlocks256 block to replace")

old_warp = """  int warpSize;
  CHECK_HIP_IGNORE(hipDeviceGetAttribute(&warpSize, hipDeviceAttributeWarpSize, 0))
  if (warpSize != 32) {
"""

new_warp = """  int warpSize = cupdlp_get_hip_warp_size();
  if (warpSize != 32) {
"""

if old_warp in text:
    text = text.replace(old_warp, new_warp, 1)
elif "int warpSize = cupdlp_get_hip_warp_size();" in text:
    print("skip warpSize cache use: already applied")
else:
    raise SystemExit("could not find warpSize query block to replace")

path.write_text(text, encoding="utf-8")
print(f"updated {path}")
