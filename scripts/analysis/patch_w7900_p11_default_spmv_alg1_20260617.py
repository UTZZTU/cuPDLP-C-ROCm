#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "cupdlp" / "hip" / "cupdlp_hip_linalg.cpp"

FUNC_NAME = "static hipsparseSpMVAlg_t cupdlp_hip_spmv_alg(void)"

NEW_HELPER = r'''static hipsparseSpMVAlg_t cupdlp_hip_spmv_alg(void) {
  const char *env = std::getenv("CUPDLP_HIP_SPMV_ALG");

  // W7900 P11 sweep showed csr_alg1 was slightly faster than csr_alg2
  // on most long targeted cases while preserving solver status and iteration
  // count. Keep csr_alg2 available as an explicit rollback mode.
  if (env == nullptr || env[0] == '\0' ||
      std::strcmp(env, "csr_alg1") == 0 ||
      std::strcmp(env, "CSR_ALG1") == 0 ||
      std::strcmp(env, "alg1") == 0 ||
      std::strcmp(env, "ALG1") == 0) {
    return HIPSPARSE_SPMV_CSR_ALG1;
  }

  if (std::strcmp(env, "csr_alg2") == 0 ||
      std::strcmp(env, "CSR_ALG2") == 0 ||
      std::strcmp(env, "alg2") == 0 ||
      std::strcmp(env, "ALG2") == 0) {
    return HIPSPARSE_SPMV_CSR_ALG2;
  }

  if (std::strcmp(env, "default") == 0 ||
      std::strcmp(env, "DEFAULT") == 0) {
    return HIPSPARSE_SPMV_ALG_DEFAULT;
  }

  static bool warned = false;
  if (!warned) {
    warned = true;
    fprintf(stderr,
            "[cuPDLP][HIP] unknown CUPDLP_HIP_SPMV_ALG=%s; "
            "falling back to HIPSPARSE_SPMV_CSR_ALG1\n",
            env);
  }

  return HIPSPARSE_SPMV_CSR_ALG1;
}'''

def find_function_bounds(text: str, marker: str):
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Could not find function marker: {marker}")

    brace_start = text.find("{", start)
    if brace_start < 0:
        raise RuntimeError("Could not find opening brace for helper")

    depth = 0
    for idx in range(brace_start, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return start, idx + 1

    raise RuntimeError("Could not find closing brace for helper")

def main():
    text = SRC.read_text(encoding="utf-8")

    start, end = find_function_bounds(text, FUNC_NAME)
    old_helper = text[start:end]

    if "HIPSPARSE_SPMV_CSR_ALG2" not in old_helper:
        raise RuntimeError("Helper found, but it does not mention HIPSPARSE_SPMV_CSR_ALG2; inspect manually")

    if "CUPDLP_HIP_SPMV_ALG" not in old_helper:
        raise RuntimeError("Helper found, but it does not mention CUPDLP_HIP_SPMV_ALG; inspect manually")

    new_text = text[:start] + NEW_HELPER + text[end:]
    SRC.write_text(new_text, encoding="utf-8", newline="\n")

    print(f"[OK] updated {SRC.relative_to(ROOT)}")
    print("[DONE] default HIP SpMV algorithm is now CSR_ALG1")
    print("[INFO] rollback old default with CUPDLP_HIP_SPMV_ALG=csr_alg2")

if __name__ == "__main__":
    main()
